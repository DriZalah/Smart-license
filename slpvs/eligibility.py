"""Eligibility function E(P) (Eq. 3) and authorisation indicator (Eq. 6).

The responsible person R is the registered owner, or the renter when the vehicle
is under an active rental contract. Driver identity is NOT verified by the system.
"""
AUTHORIZED = "AUTHORIZED"
UNAUTHORIZED = "UNAUTHORIZED"
UNCONFIRMED = "UNCONFIRMED"


def authorisation(D: bool, G: bool, T: bool, DT: bool) -> bool:
    """Eq. 6: A = D(R) or G(R) or (T(R) and D_T(R))."""
    return bool(D or G or (T and DT))


def eligibility(D, G, T, DT, holder_absent=False, tourist_link_failed=False):
    """Eq. 3 with the UNCONFIRMED state.

    UNCONFIRMED is returned when (i) the vehicle is linked to an eligible person but
    the warden reports that this person is not present (S6), or (ii) a disabled
    tourist's visa record cannot be linked to the rental contract.
    """
    if T and DT and tourist_link_failed:
        return UNCONFIRMED
    if authorisation(D, G, T, DT):
        return UNCONFIRMED if holder_absent else AUTHORIZED
    return UNAUTHORIZED
