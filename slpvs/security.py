"""Security controls described in Section 3.7.1: RBAC matrix, hash-chained
append-only audit log, and plate-image retention policy."""
import hashlib
import json
from datetime import datetime, timedelta, timezone

PERMISSIONS = ["read_events", "write_decisions", "manage_users", "view_audit_logs", "own_records"]

# Table 4 of the manuscript. Only the Auditor can read audit logs (separation of duties).
RBAC = {
    "Field Warden":                      dict(read_events=True,  write_decisions=False, manage_users=False, view_audit_logs=False, own_records=False),
    "Enforcement Supervisor":            dict(read_events=True,  write_decisions=True,  manage_users=False, view_audit_logs=False, own_records=False),
    "Traffic Management Officer":        dict(read_events=True,  write_decisions=False, manage_users=False, view_audit_logs=False, own_records=False),
    "System Administrator":              dict(read_events=False, write_decisions=False, manage_users=True,  view_audit_logs=False, own_records=False),
    "Auditor":                           dict(read_events=True,  write_decisions=False, manage_users=False, view_audit_logs=True,  own_records=False),
    "PwD User":                          dict(read_events=False, write_decisions=False, manage_users=False, view_audit_logs=False, own_records=True),
    "Operating Company Representative":  dict(read_events=True,  write_decisions=False, manage_users=False, view_audit_logs=False, own_records=False),
}


def allowed(role: str, permission: str) -> bool:
    return bool(RBAC.get(role, {}).get(permission, False))


class AuditLog:
    """Append-only log; each entry stores SHA-256(prev_hash || canonical entry)."""
    GENESIS = "0" * 64

    def __init__(self):
        self._entries = []

    def append(self, actor: str, event: str, payload: dict):
        prev = self._entries[-1]["hash"] if self._entries else self.GENESIS
        body = dict(ts=datetime.now(timezone.utc).isoformat(), actor=actor, event=event, payload=payload)
        digest = hashlib.sha256((prev + json.dumps(body, sort_keys=True)).encode()).hexdigest()
        self._entries.append(dict(body=body, prev=prev, hash=digest))
        return digest

    def read(self, role: str):
        if not allowed(role, "view_audit_logs"):
            raise PermissionError(f"{role} may not read audit logs")
        return list(self._entries)

    def verify(self) -> bool:
        prev = self.GENESIS
        for e in self._entries:
            h = hashlib.sha256((prev + json.dumps(e["body"], sort_keys=True)).encode()).hexdigest()
            if e["prev"] != prev or e["hash"] != h:
                return False
            prev = h
        return True


# Plate-image retention policy
RETENTION = {
    "AUTHORIZED": timedelta(hours=24),     # S1, S2, S7
    "UNCONFIRMED": timedelta(days=90),     # S6 and other manual reviews, or until review closes
    "UNAUTHORIZED": timedelta(days=90),    # S3, S4; extended only while an appeal is open
}


def purge_due(decision: str, captured_at: datetime, now: datetime, appeal_open: bool = False) -> bool:
    if appeal_open:
        return False
    return now - captured_at >= RETENTION[decision]
