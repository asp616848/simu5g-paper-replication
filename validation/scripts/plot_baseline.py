#!/usr/bin/env python3
"""Stage 2 validation: distance vs SINR / throughput / delay for the baseline scenario."""
import csv
import io
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIST = {0: 50, 1: 150, 2: 300, 3: 450, 4: 400}  # ue index -> distance to gNB [m] (see baseline.ini)
OFFERED_MBPS = 2.0
WANT = ("measuredSinrDl:mean", "cbrReceivedThroughput:simu5g_rateavg", "cbrFrameDelay:mean", "cbrFrameLoss:mean")


def load():
    rows = []
    for sca in sorted((ROOT / "results/Baseline").glob("*.sca")):
        flt = " OR ".join(f'name =~ "{w}"' for w in WANT)
        out = subprocess.run(["opp_scavetool", "x", "-f", f"({flt}) AND module =~ \"*.ue*\"", str(sca),
                              "-F", "CSV-R", "-o", "-"], capture_output=True, text=True, check=True).stdout
        for r in csv.DictReader(io.StringIO(out)):
            if r["type"] == "scalar" and r["module"].count("ue[") == 1:
                ue = int(r["module"].split("ue[")[1].split("]")[0])
                rows.append((sca.stem, ue, r["name"].split(":")[0], float(r["value"])))
    df = pd.DataFrame(rows, columns=["run", "ue", "stat", "value"])
    df = df.groupby(["run", "ue", "stat"]).value.mean().unstack().reset_index()  # nrMac/nrChannelModel duplicates
    df["dist"] = df.ue.map(DIST)
    return df


def main():
    df = load()
    g = df.drop(columns=["run", "ue"]).groupby("dist").agg(["mean", "std"])
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.4))
    d = sorted(DIST.values())
    for a, col, lab in zip(ax, ["measuredSinrDl", "cbrReceivedThroughput", "cbrFrameDelay"],
                           ["DL SINR [dB]", "Received throughput [B/s]", "CBR end-to-end delay [s]"]):
        m = g[col]["mean"].reindex(d)
        s = g[col]["std"].reindex(d)
        a.errorbar(d, m, yerr=s, marker="o", capsize=3, color="tab:blue")
        a.set(xlabel="UE-gNB distance [m]", ylabel=lab)
        a.grid(alpha=0.4)
    ax[1].axhline(OFFERED_MBPS * 1e6 / 8, ls="--", color="tab:red", label="offered load")
    ax[1].legend(fontsize=8)
    fig.suptitle("Stage 2 baseline: single gNB, NR SA, 3.5 GHz / 20 MHz, DL CBR 2 Mbit/s per UE")
    fig.tight_layout()
    out = ROOT / "figures/stage2_baseline.png"
    fig.savefig(out, dpi=150)
    print(g.round(4).to_string())
    print("->", out)


if __name__ == "__main__":
    main()
