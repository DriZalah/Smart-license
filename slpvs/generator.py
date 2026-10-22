"""Synthetic parking-enforcement dataset (Section 3.6, Table 3)."""
import numpy as np
import pandas as pd

from .config import CITIES, VEHICLE_TYPES, SimConfig
from .plates import synth_plate
from .lpr import recognise
from .eligibility import eligibility, authorisation, AUTHORIZED, UNAUTHORIZED, UNCONFIRMED
from .decision import violation_score, outcome, scenario, action


def _pick(rng, table):
    names = list(table)
    probs = np.array([table[k][0] for k in names], dtype=float)
    k = names[rng.choice(len(names), p=probs / probs.sum())]
    return k, table[k]


def _latency(rng, cfg, n_captures, rental, tourist):
    tier, (_, lo, hi) = _pick(rng, cfg.device_tiers)
    net, (_, nlo, nhi) = _pick(rng, cfg.networks)
    t_lpr = sum(rng.uniform(lo, hi) for _ in range(n_captures))
    n_queries = 2 + int(rental) + int(tourist)       # MOI + APD (+ rental API) (+ visa)
    t_db = float(np.sum(rng.lognormal(np.log(cfg.query_median), cfg.query_sigma, n_queries)))
    t_net = rng.uniform(nlo, nhi)
    return tier, net, t_lpr + t_net + t_db + cfg.ui_time


def generate(cfg: SimConfig = SimConfig()) -> pd.DataFrame:
    rng = np.random.default_rng(cfg.seed)
    names = list(CITIES)
    w = np.array([CITIES[c][1] for c in names])
    w = w / w.sum()
    rows = []
    for i in range(cfg.n_records):
        city = names[rng.choice(len(names), p=w)]
        region = CITIES[city][0]
        ar, en = synth_plate(rng)
        tourist = rng.random() < cfg.p_tourist
        if tourist:
            D, G = False, False
            DT = rng.random() < cfg.p_disabled
            rental = True
        else:
            D = rng.random() < cfg.p_disabled
            G = (not D) and (rng.random() < cfg.p_guardian)
            DT = False
            rental = rng.random() < cfg.p_rental
        A = authorisation(D, G, tourist, DT)
        S = rng.random() < cfg.p_accessible
        holder_absent = A and (rng.random() < cfg.p_holder_absent)
        multi = A and (rng.random() < cfg.p_multi_permit)
        sticker = rng.random() < (cfg.p_sticker_auth if A else cfg.p_sticker_unauth)
        fake = sticker and not A
        link_fail = tourist and DT and (rng.random() < cfg.p_tourist_mismatch)
        stale = rng.random() < cfg.registry_staleness

        accepted, conf, n_cap = recognise(rng, cfg, en)

        # Proposed system: registry view (stale record flips the permit status)
        if not accepted:
            E = UNCONFIRMED
        else:
            E = eligibility(D, G, tourist, DT, holder_absent, link_fail)
            if stale and E != UNCONFIRMED:
                E = UNAUTHORIZED if E == AUTHORIZED else AUTHORIZED

        # Legacy sticker system (independent draws)
        wrongful_old = A and (rng.random() < cfg.p_wrongful_old)
        fake_detected_old = fake and (rng.random() < cfg.p_fake_detect_old)
        if A:
            old_dec = UNAUTHORIZED if wrongful_old else AUTHORIZED
        else:
            old_dec = UNAUTHORIZED if (not sticker or fake_detected_old) else AUTHORIZED

        tier, net, t_ver = _latency(rng, cfg, n_cap, rental, tourist)
        t_manual = rng.uniform(cfg.t_manual_min, cfg.t_manual_max)

        out = outcome(int(S), E)
        e_auth = int(E == AUTHORIZED)
        fraud_flag = bool(S and fake and E == UNAUTHORIZED)
        if out == "Violation":
            fine = int(rng.integers(10, 16) * 100) if fake else int(rng.integers(5, 16) * 100)
        else:
            fine = 0
        rows.append(dict(
            record_id=i + 1, plate_ar=ar, plate_en=en, city=city, region=region,
            vehicle_type=VEHICLE_TYPES[int(rng.integers(0, len(VEHICLE_TYPES)))],
            vehicle_year=int(rng.integers(2015, 2026)), rental_flag=rental, tourist_flag=tourist,
            disability_registered=D, guardian=G, tourist_disability_linked=DT,
            authorized_truth=A, multi_permit=multi, holder_absent=holder_absent,
            accessible_space=S, sticker_present=sticker, sticker_fake=fake,
            lpr_confidence=round(conf, 4), lpr_captures=n_cap, lpr_accepted=accepted,
            registry_stale=stale, tourist_link_failed=link_fail,
            eligibility_proposed=E, scenario=scenario(S, E, sticker, multi),
            action_proposed=action(S, E, sticker), outcome_proposed=out,
            violation_score=violation_score(e_auth, int(S), int(fake)),
            decision_old=old_dec, wrongful_fine_old=bool(S and wrongful_old),
            fraud_flag=fraud_flag, fine_amount_sar=fine,
            device_tier=tier, network=net,
            verification_time_s=round(t_ver, 3), manual_time_s=round(t_manual, 1),
        ))
    return pd.DataFrame(rows)
