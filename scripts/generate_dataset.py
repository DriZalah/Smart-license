"""Generate the 5,000-record synthetic dataset (seed 42) to data/slpvs_synthetic.csv."""
import argparse
import os
import _path  # noqa: F401
from slpvs import SimConfig, generate

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(_path.ROOT, "data", "slpvs_synthetic.csv"))
    a = ap.parse_args()
    df = generate(SimConfig(n_records=a.n, seed=a.seed))
    df.to_csv(a.out, index=False, encoding="utf-8-sig")
    print(f"wrote {len(df)} records x {df.shape[1]} attributes -> {a.out}")
