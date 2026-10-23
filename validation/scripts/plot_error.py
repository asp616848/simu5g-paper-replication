#!/usr/bin/env python3
"""Fig. 16 / Fig. 17 replication: first-transmission HARQ error rate vs receiver offset Delta."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

ROOT = Path(__file__).resolve().parent.parent
DELTAS = [0, 3, 5, 7]
COL = {0: "tab:blue", 3: "tab:red", 5: "tab:green", 7: "tab:orange"}
# values read off the bars of Fig. 16 of the paper (approximate, +-0.01)
PAPER_FIG16 = {0: 0.275, 3: 0.155, 5: 0.115, 7: 0.100}


def main(cfg=None):
    cfg = cfg or (sys.argv[1] if len(sys.argv) > 1 else "UrbanMacro")
    u = pd.read_csv(ROOT / "results/extracted" / cfg / "ue_stats.csv").dropna(subset=["harq1_err"])
    per_rep = u.groupby(["delta", "rep"]).harq1_err.mean().reset_index()  # average over UEs, per run
    stat = per_rep.groupby("delta").harq1_err.agg(["mean", "std", "count"])
    stat["ci95"] = 1.96 * stat["std"] / np.sqrt(stat["count"])

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    a = ax[0]
    x = np.arange(len(DELTAS))
    a.bar(x - 0.18, [stat.loc[d, "mean"] for d in DELTAS], 0.36, yerr=[stat.loc[d, "ci95"] for d in DELTAS],
          capsize=4, color=[COL[d] for d in DELTAS], label="this replication (95% CI)")
    a.bar(x + 0.18, [PAPER_FIG16[d] for d in DELTAS], 0.36, color="lightgray", edgecolor="k", hatch="//",
          label="paper Fig. 16 (read from plot)")
    a.axhline(0.10, ls=":", color="k")
    a.text(3.45, 0.103, "3GPP target 10%", ha="right", fontsize=8)
    a.set_xticks(x, [f"Δ={d} dB" for d in DELTAS])
    a.set(ylabel="avg HARQ 1st-TX error rate", title=f"Fig. 16: average error rate after 1st TX\n({cfg})")
    a.legend(fontsize=8)
    a.grid(axis="y", alpha=0.4)

    a = ax[1]
    grid = np.linspace(0, 1, 201)
    for d in DELTAS:
        v = np.sort(u[u.delta == d].harq1_err.values)
        a.plot(grid, np.searchsorted(v, grid, side="right") / len(v), color=COL[d], label=f"Δ={d} dB")
    a.set(xlabel="per-UE 1st-TX error rate", ylabel="CDF", xlim=(0, 1), ylim=(0, 1),
          title="Fig. 17: CDF of error rate after 1st TX")
    a.grid(alpha=0.4)
    a.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    out = ROOT / f"figures/fig16_17_error_rate_{cfg}.png"
    fig.savefig(out, dpi=160)

    rows = []
    for d in DELTAS:
        v = u[u.delta == d].harq1_err.values
        rows.append((d, round(stat.loc[d, "mean"], 3), round(stat.loc[d, "ci95"], 3), PAPER_FIG16[d],
                     round(float(np.median(v)), 3), round(float((v > 0.2).mean()), 3)))
    tab = pd.DataFrame(rows, columns=["delta_dB", "mean_err", "ci95", "paper_mean_err", "median_ue_err",
                                      "frac_UEs_err>20%"])
    print(cfg); print(tab.to_string(index=False))
    tab.to_csv(ROOT / f"results/error_rate_{cfg}.csv", index=False)
    print("->", out)


if __name__ == "__main__":
    main()
