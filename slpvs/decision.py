"""Decision engine: violation score (Eq. 4), outcome (Eq. 7), scenarios S1-S7 (Table 2)."""
from .eligibility import AUTHORIZED, UNAUTHORIZED, UNCONFIRMED

ALPHA = 1.0   # weight of an unauthorised occupation of an accessible bay
BETA = 0.5    # additional weight when a counterfeit sticker is displayed


def violation_score(E_auth: int, A_space: int, F_fraud: int, alpha=ALPHA, beta=BETA) -> float:
    """Eq. 4: V_s = alpha*(1-E_auth)*A_space + beta*F_fraud."""
    return alpha * (1 - E_auth) * A_space + beta * F_fraud


def outcome(S: int, E: str) -> str:
    """Eq. 7."""
    if not S:
        return "N/A"
    if E == UNCONFIRMED:
        return "Manual review"
    return "No violation" if E == AUTHORIZED else "Violation"


def scenario(S, E, sticker, multi_permit):
    """Map an event to the scenario rows of Table 2."""
    if not S:
        return "S5"
    if E == UNCONFIRMED:
        return "S6"
    if E == AUTHORIZED:
        if multi_permit:
            return "S7"
        return "S1" if sticker else "S2"
    return "S3" if sticker else "S4"


def action(S, E, sticker):
    if not S:
        return "Not applicable"
    if E == UNCONFIRMED:
        return "Manual warden review; logged as unconfirmed; no automatic fine"
    if E == AUTHORIZED:
        return "No action" if sticker else "No fine (digitally verified)"
    return "Issue fine + flag fraud" if sticker else "Issue fine"
