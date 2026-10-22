"""Results figures (Figures 7-9 of the manuscript) from data/slpvs_synthetic.csv."""
import argparse
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import _path  # noqa: F401
from slpvs import SimConfig, generate, evaluate

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"],
    "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
    "axes.spines.top": False, "axes.spines.right": False,
})
C = dict(blue="#4C72B0", green="#55A868", red="#C44E52", purple="#8172B2", gold="#CCB974", grey="#8C8C8C")


def fig_distribution(df, path, dpi):
    fig, ax = plt.subplots(2, 2, figsize=(7.16, 5.6))
    city = df.city.value_counts()
    a = ax[0, 0]
    a.bar(city.index, city.values, color=C["blue"])
    a.set_title("(a) Records per city")
    a.set_ylabel("Number of records")
    a.tick_params(axis="x", rotation=60)
    for lab in a.get_xticklabels():
        lab.set_ha("right")
    a.set_ylim(0, city.max() * 1.15)
    for x, v in enumerate(city.values):
        a.text(x, v + city.max() * 0.015, str(v), ha="center", va="bottom", fontsize=6)

    reg = df.region.value_counts()
    a = ax[0, 1]
    a.bar(reg.index, reg.values, color=C["green"])
    a.set_title("(b) Records per administrative region")
    a.set_ylim(0, reg.max() * 1.18)
    for x, v in enumerate(reg.values):
        a.text(x, v + reg.max() * 0.02, f"{v}\n({v / len(df) * 100:.1f}%)", ha="center", va="bottom", fontsize=7)

    labels = ["Registered\nPwD", "Legal\nguardians", "Disabled\ntourists", "Total\nauthorised", "Total\nunauthorised"]
    vals = [int(df.disability_registered.sum()), int(df.guardian.sum()),
            int((df.tourist_flag & df.tourist_disability_linked).sum()),
            int(df.authorized_truth.sum()), int((~df.authorized_truth).sum())]
    a = ax[1, 0]
    a.bar(labels, vals, color=[C["purple"], C["purple"], C["purple"], C["green"], C["red"]])
    a.set_title("(c) Authorisation status")
    a.set_ylabel("Number of records")
    a.set_ylim(0, max(vals) * 1.2)
    for x, v in enumerate(vals):
        a.text(x, v + max(vals) * 0.02, f"{v}\n({v / len(df) * 100:.1f}%)", ha="center", va="bottom", fontsize=7)

    vt = df.vehicle_type.value_counts()
    a = ax[1, 1]
    a.bar(vt.index, vt.values, color=C["gold"])
    a.set_title("(d) Vehicle type")
    a.set_ylim(0, vt.max() * 1.15)
    a.tick_params(axis="x", rotation=30)
    for x, v in enumerate(vt.values):
        a.text(x, v + vt.max() * 0.02, str(v), ha="center", va="bottom", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def fig_wrongful(res, path, dpi):
    fig, a = plt.subplots(figsize=(3.5, 2.6))
    vals = [res["w_old"], res["w_new"]]
    rates = [res["wrongful_rate_old"], res["wrongful_rate_new"]]
    bars = a.bar(["Sticker-based\nsystem", "Proposed\nSLPVS"], vals, color=[C["red"], C["green"]], width=0.5)
    top = max(vals) * 1.35
    a.set_ylim(0, top)
    for b, v, r in zip(bars, vals, rates):
        a.text(b.get_x() + b.get_width() / 2, v + top * 0.02, f"{v} ({r:.1f}%)", ha="center", va="bottom")
    a.text(0.5, 0.93, f"WFER = {res['wfer']:.1f}%  (n = {res['n_auth_auto']} authorised events)",
           transform=a.transAxes, ha="center", va="top")
    a.set_ylabel("Wrongful fines")
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def fig_lpr(df, theta, path, dpi):
    acc = df[df.accessible_space]
    c = acc.lpr_confidence
    fig, ax = plt.subplots(1, 2, figsize=(7.16, 2.8), gridspec_kw=dict(width_ratios=[1.6, 1]))
    a = ax[0]
    a.hist(c, bins=40, color=C["blue"], edgecolor="white", linewidth=0.4)
    h1 = a.axvline(theta, color=C["red"], ls="--", lw=1.2, label=f"Acceptance threshold = {theta:.2f}")
    h2 = a.axvline(c.mean(), color="black", ls=":", lw=1.2, label=f"Mean = {c.mean():.3f}")
    a.set_xlabel("Final plate confidence $C_{LPR}$")
    a.set_ylabel("Frequency")
    a.set_title(f"(a) Histogram (n = {len(c)}, SD = {c.std():.3f})")
    a.legend(handles=[h1, h2], loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
    a = ax[1]
    parts = a.violinplot(c, showmedians=True, showextrema=True)
    for pc in parts["bodies"]:
        pc.set_facecolor(C["blue"])
        pc.set_alpha(0.6)
    a.axhline(theta, color=C["red"], ls="--", lw=1.2)
    a.set_xticks([1])
    a.set_xticklabels(["Accessible-bay events"])
    a.set_ylabel("$C_{LPR}$")
    a.set_title("(b) Violin plot")
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi", type=int, default=800)
    a = ap.parse_args()
    csv = os.path.join(_path.ROOT, "data", "slpvs_synthetic.csv")
    df = pd.read_csv(csv) if os.path.exists(csv) else generate(SimConfig())
    res = evaluate(df)
    out = os.path.join(_path.ROOT, "results", "figures")
    os.makedirs(out, exist_ok=True)
    fig_distribution(df, os.path.join(out, "fig7_dataset_distribution.png"), a.dpi)
    fig_wrongful(res, os.path.join(out, "fig8_wrongful_fines.png"), a.dpi)
    fig_lpr(df, SimConfig().theta_accept, os.path.join(out, "fig9_lpr_confidence.png"), a.dpi)
    print("figures written to", out)
