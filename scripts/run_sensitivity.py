"""Sensitivity and workload analysis (Tables 12 and 13): registry staleness, legacy
wrongful-fine rate, and backend request rate."""
import json
import os
import numpy as np
import _path  # noqa: F401
from slpvs import SimConfig, generate, evaluate
from slpvs.workload import mean_wait, sample_wait

SEEDS = range(1, 11)


def sweep(param, values):
    rows = []
    for v in values:
        rs = [evaluate(generate(SimConfig(seed=s, **{param: v}))) for s in SEEDS]
        rows.append(dict(value=v,
                         accuracy=float(np.mean([r["new"]["accuracy"] for r in rs]) * 100),
                         old_accuracy=float(np.mean([r["old"]["accuracy"] for r in rs]) * 100),
                         fp=float(np.mean([r["cm_new"][2] for r in rs])),
                         fn=float(np.mean([r["cm_new"][1] for r in rs])),
                         wfer=float(np.mean([r["wfer"] for r in rs]))))
    return rows


def workload(rates):
    cfg = SimConfig()
    df = generate(cfg)
    base = df.verification_time_s.values
    mu = 1.0 / cfg.service_mean
    rng = np.random.default_rng(7)
    rows = []
    for lam in rates:
        w = sample_wait(rng, lam, mu, cfg.servers, len(base))
        tot = base + w
        rows.append(dict(rate=lam, utilisation=lam / (cfg.servers * mu) * 100,
                         mean_wait=mean_wait(lam, mu, cfg.servers),
                         mean_total=float(tot.mean()), p95_total=float(np.quantile(tot, .95))))
    return rows


if __name__ == "__main__":
    res = dict(
        registry_staleness=sweep("registry_staleness", [0.001, 0.004, 0.01, 0.02, 0.05]),
        p_wrongful_old=sweep("p_wrongful_old", [0.10, 0.15, 0.20, 0.30]),
        workload=workload([50, 100, 150, 200, 240, 260, 264]),
    )
    with open(os.path.join(_path.ROOT, "results", "sensitivity.json"), "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))
