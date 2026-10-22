"""Simulation parameters (Table 3 of the manuscript).

Every probability below is a modelling assumption of the synthetic study,
not an empirical estimate. The sensitivity analysis (scripts/run_sensitivity.py)
varies the most influential ones.
"""
from dataclasses import dataclass, field

# Cities, administrative regions and relative sampling weights.
# Weights are approximate relative urban-population weights used only to
# make the synthetic sample geographically non-uniform; edit freely.
CITIES = {
    # city: (region, relative weight)
    "Riyadh": ("Central", 7.0),
    "Buraidah": ("Central", 0.7),
    "Jeddah": ("Western", 3.7),
    "Makkah": ("Western", 2.4),
    "Madinah": ("Western", 1.5),
    "Yanbu": ("Western", 0.3),
    "Dammam": ("Eastern", 1.4),
    "Khobar": ("Eastern", 0.6),
    "Dhahran": ("Eastern", 0.2),
    "Tabuk": ("Northern", 0.6),
    "Hail": ("Northern", 0.4),
    "Arar": ("Northern", 0.2),
    "Sakaka": ("Northern", 0.3),
    "Abha": ("Southern", 0.4),
    "Najran": ("Southern", 0.4),
    "Jazan": ("Southern", 0.2),
    "AlBaha": ("Southern", 0.1),
}

VEHICLE_TYPES = ["Sedan", "SUV", "Pickup", "Van", "Minivan", "Compact", "Luxury"]


@dataclass
class SimConfig:
    n_records: int = 5000
    seed: int = 42

    # Population attributes (Bernoulli parameters)
    p_disabled: float = 0.35          # registered PwD (D)
    p_guardian: float = 0.15          # legal guardian of a PwD (G), only if not disabled
    p_tourist: float = 0.10           # foreign visitor (T)
    p_rental: float = 0.15            # resident's vehicle is rented (tourists always rent)
    p_accessible: float = 0.40        # parked in an accessible bay (S)
    p_sticker_auth: float = 0.60      # authorised vehicle displays a physical sticker
    p_sticker_unauth: float = 0.20    # unauthorised vehicle displays a fake sticker
    p_holder_absent: float = 0.05     # S6: permit holder reported absent at inspection
    p_multi_permit: float = 0.08      # S7: >1 eligible person linked to the vehicle

    # Legacy (sticker) system
    p_wrongful_old: float = 0.30      # wrongful fine on an authorised vehicle
    p_fake_detect_old: float = 0.15   # warden visually detects a fake sticker
    t_manual_min: float = 45.0        # manual verification time (s)
    t_manual_max: float = 120.0

    # Proposed system error sources
    registry_staleness: float = 0.004  # permit record out of sync (causes FN or FP)
    p_tourist_mismatch: float = 0.035  # visa-rental cross-reference failure (manual review)

    # LPR confidence model (Eq. 1): c_i = q * Beta(a_c, b_c), q ~ Beta(a_q, b_q)
    n_chars: int = 7
    a_c: float = 40.0
    b_c: float = 1.2
    a_q: float = 25.0
    b_q: float = 1.0
    theta_accept: float = 0.85
    max_captures: int = 2

    # Latency model (seconds)
    device_tiers: dict = field(default_factory=lambda: {
        "high": (0.40, 0.25, 0.45), "mid": (0.40, 0.40, 0.80), "low": (0.20, 0.70, 1.30)})
    networks: dict = field(default_factory=lambda: {
        "5G": (0.35, 0.05, 0.15), "4G": (0.55, 0.15, 0.45), "weak": (0.10, 0.60, 1.50)})
    query_median: float = 0.12        # per registry query, lognormal median
    query_sigma: float = 0.50
    ui_time: float = 0.10

    # Backend workload model (Erlang C, M/M/c)
    servers: int = 40
    service_mean: float = 0.15        # mean backend service time per request (s)
