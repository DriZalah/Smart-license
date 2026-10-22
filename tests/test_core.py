import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from slpvs import SimConfig, generate, evaluate
from slpvs.lpr import plate_confidence, consensus
from slpvs.eligibility import eligibility, authorisation, AUTHORIZED, UNAUTHORIZED, UNCONFIRMED
from slpvs.decision import violation_score, outcome
from slpvs.metrics import scores, wfer
from slpvs.plates import synth_plate
from slpvs.security import AuditLog, allowed, purge_due
from slpvs.workload import erlang_c


def test_geometric_mean():
    assert abs(plate_confidence([0.9] * 7) - 0.9) < 1e-12
    assert plate_confidence([1.0, 0.25]) == 0.5


def test_consensus():
    assert consensus("A", 0.9, "A", 0.95, 0.85) == ("A", 0.95)
    assert consensus("A", 0.8, "A", 0.7, 0.85)[0] is None


def test_eligibility_states():
    assert authorisation(False, False, True, True)
    assert eligibility(True, False, False, False) == AUTHORIZED
    assert eligibility(False, False, False, False) == UNAUTHORIZED
    assert eligibility(True, False, False, False, holder_absent=True) == UNCONFIRMED
    assert eligibility(False, False, True, True, tourist_link_failed=True) == UNCONFIRMED


def test_score_and_outcome():
    assert violation_score(0, 1, 1) == 1.5
    assert violation_score(1, 1, 0) == 0.0
    assert outcome(1, UNCONFIRMED) == "Manual review"
    assert outcome(0, AUTHORIZED) == "N/A"


def test_metrics():
    s = scores(877, 3, 5, 1112)
    assert round(s["accuracy"], 3) == 0.996
    assert wfer(252, 3) == (249 / 252) * 100


def test_plate_format():
    ar, en = synth_plate(np.random.default_rng(0))
    num = int(en.split()[0])
    assert 1000 <= num <= 9999 and len(en.split()[1]) == 3


def test_audit_log_and_rbac():
    log = AuditLog()
    log.append("Field Warden", "login", {})
    log.append("Supervisor", "decision", {"event": 1})
    assert log.verify()
    log._entries[0]["body"]["event"] = "tampered"
    assert not log.verify()
    assert allowed("Auditor", "view_audit_logs")
    assert not allowed("System Administrator", "view_audit_logs")


def test_retention():
    t0 = datetime(2026, 1, 1)
    assert purge_due("AUTHORIZED", t0, t0 + timedelta(hours=25))
    assert not purge_due("UNAUTHORIZED", t0, t0 + timedelta(days=30))
    assert not purge_due("UNAUTHORIZED", t0, t0 + timedelta(days=100), appeal_open=True)


def test_erlang_c_bounds():
    assert 0 <= erlang_c(100, 1 / 0.15, 40) <= 1


def test_reproducible():
    a = generate(SimConfig(n_records=300, seed=42))
    b = generate(SimConfig(n_records=300, seed=42))
    assert a.equals(b)
    r = evaluate(a)
    assert r["n_auto"] + r["n_manual"] == r["n_accessible"]
