"""Recognition confidence (Eq. 1) and bilingual consensus (Eq. 2)."""
import numpy as np


def plate_confidence(char_conf):
    """Eq. 1: C_LPR = (prod_i c_i)^(1/n), the geometric mean of character confidences."""
    c = np.clip(np.asarray(char_conf, dtype=float), 1e-12, 1.0)
    return float(np.exp(np.log(c).mean()))


def consensus(p_ar, c_ar, p_en, c_en, theta):
    """Eq. 2: dual-track decision.

    Returns (plate, confidence) or (None, max_conf) when neither track reaches theta,
    in which case the plate is re-captured (and, after the last attempt, keyed in
    manually by the warden; no automatic fine is issued).
    """
    if c_ar >= theta and c_en >= theta and p_ar == p_en:
        return p_ar, max(c_ar, c_en)
    if c_ar >= theta and c_ar > c_en:
        return p_ar, c_ar
    if c_en >= theta and c_en > c_ar:
        return p_en, c_en
    return None, max(c_ar, c_en)


def sample_track_confidence(rng, cfg, q):
    chars = q * rng.beta(cfg.a_c, cfg.b_c, size=cfg.n_chars)
    return plate_confidence(chars)


def recognise(rng, cfg, plate_key):
    """Simulate up to cfg.max_captures captures. Returns (accepted, C_LPR, n_captures)."""
    conf = 0.0
    for k in range(1, cfg.max_captures + 1):
        q = rng.beta(cfg.a_q, cfg.b_q)          # image-quality factor of this capture
        c_ar = sample_track_confidence(rng, cfg, q)
        c_en = sample_track_confidence(rng, cfg, q)
        plate, conf = consensus(plate_key, c_ar, plate_key, c_en, cfg.theta_accept)
        if plate is not None:
            return True, conf, k
    return False, conf, cfg.max_captures
