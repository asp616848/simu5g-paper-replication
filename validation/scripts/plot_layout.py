#!/usr/bin/env python3
"""Fig. 14 replication: the simulated 3GPP Urban Macro layout (57 cells, UE drop of repetition 0)."""
import math
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, Wedge

ROOT = Path(__file__).resolve().parent.parent
ISD = 500.0


def main(rep=0):
    ue = re.findall(r"ue\[(\d+)\]\.mobility\.initial([XY]) = ([\d.]+)m", (ROOT / f"positions/rep{rep}.ini").read_text())
    pos = {}
    for i, ax_, v in ue:
        pos.setdefault(int(i), {})[ax_] = float(v)
    lay = (ROOT / "config/layout.ini").read_text()
    sites = []
    for x, y in re.findall(r"extCell\[\d+\]\.positionX = ([\d.]+)m\n\*\.extCell\[\d+\]\.positionY = ([\d.]+)m", lay):
        if (float(x), float(y)) not in sites:
            sites.append((float(x), float(y)))
    centre = (1200.0, 1200.0)
    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    for (x, y) in [centre] + sites:
        ax.add_patch(RegularPolygon((x, y), 6, radius=ISD / math.sqrt(3), orientation=0,
                                    fill=(x, y) == centre, fc="#d5f0d5", ec="gray", lw=0.8, alpha=0.9))
        for a in (30, 150, 270):
            ax.add_patch(Wedge((x, y), 110, a - 32.5, a + 32.5, fc="tab:red" if (x, y) == centre else "tab:blue",
                               alpha=0.55, ec="none"))
        ax.plot(x, y, "k^", ms=5)
    xs = [pos[i]["X"] for i in sorted(pos)]
    ys = [pos[i]["Y"] for i in sorted(pos)]
    ax.scatter(xs, ys, c="k", s=22, zorder=5, label=f"UEs ({len(xs)}, 80% indoor in the channel model)")
    ax.scatter([], [], marker="^", c="tab:red", label="full-stack gNB sectors (3)")
    ax.scatter([], [], marker="^", c="tab:blue", label="light cells (54, 100% load)")
    ax.set(xlim=(0, 2400), ylim=(0, 2400), aspect="equal", xlabel="x [m]", ylabel="y [m]",
           title="Simulated 3GPP Urban Macro layout: 19 sites x 3 sectors = 57 cells, ISD 500 m")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    out = ROOT / "figures/fig14_layout.png"
    fig.savefig(out, dpi=140)
    print("->", out)


if __name__ == "__main__":
    main()
