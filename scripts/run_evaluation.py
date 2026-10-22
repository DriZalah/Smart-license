"""Evaluate SLPVS and the sticker baseline (Tables 5, 7, 8, 9 and 10, Sections 5.1 to 5.8)."""
import json
import os
import numpy as np
import pandas as pd
import _path  # noqa: F401
from slpvs import SimConfig, generate, evaluate


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return round(float(o), 4)
    return o


if __name__ == "__main__":
    out = os.path.join(_path.ROOT, "results")
    csv = os.path.join(_path.ROOT, "data", "slpvs_synthetic.csv")
    df = pd.read_csv(csv) if os.path.exists(csv) else generate(SimConfig())
    df.to_csv(csv, index=False, encoding="utf-8-sig")
    res = evaluate(df)
    res["counts"] = dict(
        disabled=int(df.disability_registered.sum()), guardians=int(df.guardian.sum()),
        tourists=int(df.tourist_flag.sum()), authorized=int(df.authorized_truth.sum()),
        accessible=int(df.accessible_space.sum()),
        auth_in_accessible=int((df.accessible_space & df.authorized_truth).sum()),
        unauth_in_accessible=int((df.accessible_space & ~df.authorized_truth).sum()),
        fake_in_accessible=int((df.accessible_space & df.sticker_fake).sum()),
        nosticker_unauth_in_accessible=int((df.accessible_space & ~df.authorized_truth & ~df.sticker_present).sum()),
        violations_flagged=int((df.outcome_proposed == "Violation").sum()),
        wrongful_old_all=int(df.wrongful_fine_old.sum()),
        attributes=int(df.shape[1]))
    # stability across seeds
    runs = [evaluate(generate(SimConfig(seed=s))) for s in range(1, 11)]
    res["seeds"] = {k: dict(mean=float(np.mean([r["new"][k] for r in runs]) * 100),
                            std=float(np.std([r["new"][k] for r in runs], ddof=1) * 100))
                    for k in ["accuracy", "precision", "recall", "f1"]}
    res["seeds"]["wfer"] = dict(mean=float(np.mean([r["wfer"] for r in runs])),
                                std=float(np.std([r["wfer"] for r in runs], ddof=1)))
    res = _clean(res)
    with open(os.path.join(out, "evaluation.json"), "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))
