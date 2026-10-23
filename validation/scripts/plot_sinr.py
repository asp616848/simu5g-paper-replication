#!/usr/bin/env python3
"""Fig. 15 replication: CDF of the DL SINR measured by the UEs vs the 3GPP reference.

Usage: plot_sinr.py [delta]   (default 5; pools all repetitions of every available configuration)
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DELTA = int(sys.argv[1]) if len(sys.argv) > 1 else 5
GRID = np.arange(-25, 40.01, 0.25)
CONFIGS = {  # config -> (label, colour, linestyle)
    "UrbanMacro": ("Simu5G, 3 gNB + 54 light cells (paper setup)", "tab:green", "-"),
    "UrbanMacroFull": ("Simu5G, 57 full gNBs (variant)", "tab:blue", "-"),
    "UrbanMacroNoFading": ("Simu5G, paper setup, no fast fading", "tab:purple", ":"),
}
Q = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]


def ecdf(x, grid=GRID):
    x = np.sort(np.asarray(x))
    return np.searchsorted(x, grid, side="right") / len(x)


def main():
    ref = pd.read_csv(ROOT / "reference/fig15_3gpp_reference_digitized.csv")
    ref_cdf = np.interp(GRID, ref.sinr_db, ref.cdf, left=0.0, right=1.0)
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    rows = {"quantile": Q, "reference_dB": np.interp(Q, ref.cdf, ref.sinr_db).round(2)}
    ks = {}
    for cfg, (label, col, ls) in CONFIGS.items():
        f = ROOT / "results/extracted" / cfg / "sinr_samples.csv"
        if not f.exists():
            f = f.with_suffix(".csv.gz")  # the repository ships the compressed samples
        if not f.exists():
            continue
        s = pd.read_csv(f)
        s = s[s.delta == DELTA]
        if s.empty:
            continue
        per_rep = np.array([ecdf(g.sinr_db) for _, g in s.groupby("rep")])
        mean = per_rep.mean(0)
        half = 1.96 * per_rep.std(0, ddof=1) / np.sqrt(len(per_rep)) if len(per_rep) > 1 else 0 * mean
        pooled = ecdf(s.sinr_db)
        ks[cfg] = np.abs(pooled - ref_cdf).max()
        ax.plot(GRID, mean, ls, color=col, lw=2, label=f"{label}  [{len(per_rep)} reps, KS={ks[cfg]:.2f}]")
        ax.fill_between(GRID, mean - half, mean + half, color=col, alpha=0.2)
        rows[cfg] = np.quantile(s.sinr_db, Q).round(2)
    ax.plot(GRID, ref_cdf, "--", color="tab:red", lw=2, label="3GPP reference (digitized from paper Fig. 15)")
    ax.set(xlim=(-25, 40), ylim=(0, 1), xlabel="SINR [dB]", ylabel="CDF",
           title=f"Urban Macro (UMa, 700 MHz, ISD 500 m), 30 UEs, Δ = {DELTA} dB")
    ax.grid(alpha=0.4)
    ax.legend(loc="lower right", fontsize=7.5)
    fig.tight_layout()
    out = ROOT / "figures/fig15_sinr_cdf.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=160)
    tab = pd.DataFrame(rows)
    print(tab.to_string(index=False))
    print("KS distance to reference:", {k: round(v, 3) for k, v in ks.items()}, "->", out)
    tab.to_csv(ROOT / "results/sinr_quantiles.csv", index=False)


if __name__ == "__main__":
    main()
