"""Synthetic Saudi plate generator (Eq. 5).

Saudi plates use a 17-letter subset of the Arabic alphabet, each with a fixed
Latin counterpart, and Arabic-Indic digits mirrored by Western digits.
"""
import numpy as np

AR_LETTERS = ["ا", "ب", "ح", "د", "ر", "س", "ص", "ط", "ع", "ق", "ك", "ل", "م", "ن", "ه", "و", "ى"]
EN_LETTERS = ["A", "B", "J", "D", "R", "S", "X", "T", "E", "G", "K", "L", "Z", "N", "H", "U", "V"]
AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"


def synth_plate(rng: np.random.Generator):
    """Return (arabic_plate, english_plate).

    d1 ~ U{1..9}, d2..d4 ~ U{0..9}  -> number in 1000-9999
    l1..l3 ~ U{17 plate letters}
    """
    digits = [int(rng.integers(1, 10))] + [int(rng.integers(0, 10)) for _ in range(3)]
    idx = rng.integers(0, len(AR_LETTERS), size=3)
    en = "".join(str(d) for d in digits) + " " + "".join(EN_LETTERS[i] for i in idx)
    ar = "".join(AR_DIGITS[d] for d in digits) + " " + " ".join(AR_LETTERS[i] for i in idx)
    return ar, en
