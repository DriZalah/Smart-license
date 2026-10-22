# SLPVS: Smart License Plate-Based Verification System

Simulation code for the paper *Smart License Plate-Based Verification System for Accessible Parking Enforcement: A Conceptual Framework*.

The package generates the 5,000-record synthetic enforcement dataset, runs the SLPVS decision engine and the legacy sticker-based baseline, and reproduces every table and results figure of the paper. All data are synthetic; no real persons, vehicles or enforcement records are used.

## Repository layout

```
SLPVS/
├── slpvs/
│   ├── config.py        Simulation parameters (Table 3)
│   ├── plates.py        Synthetic Saudi plates, 17-letter set (Eq. 5)
│   ├── lpr.py           Geometric-mean confidence (Eq. 1), bilingual consensus and re-capture (Eq. 2)
│   ├── eligibility.py   Eligibility function with UNCONFIRMED state (Eq. 3), authorisation (Eq. 6)
│   ├── decision.py      Violation score (Eq. 4), outcome (Eq. 7), scenarios S1 to S7 (Table 2)
│   ├── generator.py     Dataset generator (Section 3.6)
│   ├── metrics.py       Accuracy, precision, recall, F1, WFER (Eqs. 8 to 10)
│   ├── security.py      RBAC matrix (Table 4), SHA-256 hash-chained audit log, image retention policy
│   └── workload.py      M/M/c (Erlang C) back-end queueing model (Table 12)
├── scripts/
│   ├── generate_dataset.py   writes data/slpvs_synthetic.csv (5,000 x 36, seed 42)
│   ├── run_evaluation.py     Tables 5, 7 to 10 and Sections 5.1 to 5.8 -> results/evaluation.json
│   ├── run_sensitivity.py    Tables 11 and 12 -> results/sensitivity.json
│   ├── make_figures.py       Figures 7, 8, 9 -> results/figures/
│   └── make_er_diagram.py    Figure 4 (needs Graphviz `dot`)
├── tests/test_core.py        unit tests for every equation and security control
├── data/                     generated dataset (included; regenerate with scripts/generate_dataset.py)
├── results/                  generated JSON and figures (included)
├── requirements.txt
└── LICENSE
```

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Figure 4 only: install Graphviz (e.g. apt install graphviz / brew install graphviz)
```

## Reproducing the paper

```bash
python scripts/generate_dataset.py      # dataset, seed 42
python scripts/run_evaluation.py        # main results and 10-seed variability
python scripts/run_sensitivity.py       # sensitivity and workload (about 1 minute)
python scripts/make_figures.py          # Figures 7 to 9 at 800 dpi
python scripts/make_er_diagram.py       # Figure 4
pytest -q                               # unit tests
```

Expected key values (seed 42, 1,961 automatically decided accessible-bay events):

| Quantity | SLPVS | Sticker baseline |
|---|---|---|
| Confusion matrix (TP, FN, FP, TN) | 786, 5, 3, 1,167 | 555, 236, 170, 1,000 |
| Accuracy / Precision / Recall / F1 | 99.6 / 99.6 / 99.4 / 99.5 % | 79.3 / 76.6 / 70.2 / 73.2 % |
| Wrongful fines (of 791 authorised) | 5 (0.6 %) | 236 (29.8 %) |
| WFER | 97.9 % | |
| Counterfeit stickers detected | 209 of 209 | 39 of 209 |
| Manual reviews (S6 / visitor link / plate) | 44 / 1 / 4 | |
| Mean / 95th percentile verification time | 1.32 s / 2.17 s | 82.4 s (simulated) |

Results depend on the NumPy random generator; use NumPy 1.26 or later for identical streams.

## Notes

* Positive class = authorised. Events in the UNCONFIRMED state (borrowed vehicle S6, unresolved visitor link, plate not accepted after two captures) go to manual review and are excluded from the automatic-decision confusion matrix of both systems.
* Proposed-system errors come only from the modelled sources (stale registry records, visa-rental mismatches, low-confidence plates). Because ground truth and decision engine share the same eligibility rules, the accuracy figures verify the implementation of the logic; they are not field accuracy.
* All probabilities in `config.py` are modelling assumptions. Change them there, or pass keyword arguments to `SimConfig`.

## License

MIT
