#!/usr/bin/env python3
"""Independent Monte-Carlo estimate of the DL geometry (wide-band SINR) of the scenario.

Uses TR 36.873 3D-UMa path loss/LOS probability, TR 36.873 sector pattern, log-normal
shadowing, O2I penetration, 57 cells, full-buffer interference, no fast fading. It is
used to cross-check the simulator's SINR chain (not part of the simulation).
Options: --no-indoor, --cable DB
"""
import math
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from gen_layout import BORESIGHTS, CENTER, sites  # noqa: E402
from gen_positions import drop_ues  # noqa: E402

ATTACH_ALL = "--attach-all" in sys.argv
FC, HBS, HUE, W, HB = 0.7, 25.0, 1.5, 20.0, 20.0
TX, GAIN_BS, GAIN_UE, NF = 46.0, 8.0, 0.0, 7.0
NOISE = -174 + 10 * math.log10(9e6) + NF  # 50 PRBs x 180 kHz = 9 MHz thermal bandwidth


def pl(d2, los, rng):
    d3 = math.hypot(d2, HBS - HUE)
    if los:
        dbp = 4 * (HBS - 1) * (HUE - 1) * FC * 1e9 / 3e8
        if d2 < max(dbp, 1):
            return 22 * math.log10(d3) + 28 + 20 * math.log10(FC)
        return 40 * math.log10(d3) + 28 + 20 * math.log10(FC) - 9 * math.log10(dbp ** 2 + (HBS - HUE) ** 2)
    n = (161.04 - 7.1 * math.log10(W) + 7.5 * math.log10(HB)
         - (24.37 - 3.7 * (HB / HBS) ** 2) * math.log10(HBS)
         + (43.42 - 3.1 * math.log10(HBS)) * (math.log10(d3) - 3) + 20 * math.log10(FC)
         - (3.2 * math.log10(17.625) ** 2 - 4.97) - 0.6 * (HUE - 1.5))
    return max(n, pl(d2, True, rng))


def plos(d):
    return 1.0 if d <= 18 else (18 / d + math.exp(-d / 63) * (1 - 18 / d))


def pattern(az_deg, ue_xy, bs_xy, d2):
    ang = math.degrees(math.atan2(ue_xy[1] - bs_xy[1], ue_xy[0] - bs_xy[0]))
    h = abs((ang - az_deg + 180) % 360 - 180)
    v = math.degrees(math.atan2(d2, HBS - HUE))  # from zenith
    return min(12 * (h / 65) ** 2 + 12 * ((v - 90) / 65) ** 2, 30)


def run(n_drops=300, indoor=True, cable=0.0, seed=1, shadow=True):
    rng = np.random.default_rng(seed)
    cells = [(s, az) for s in sites() for az in BORESIGHTS]
    out = []
    for _ in range(n_drops):
        ues = drop_ues(rng, 30)
        for k, ue in enumerate(ues):
            ind = indoor and rng.random() < 0.8
            pen = 20 + 0.5 * rng.uniform(0, 25) if ind else 0
            p = []
            for (s, az) in cells:
                d2 = max(math.hypot(ue[0] - s[0], ue[1] - s[1]), 10)
                los = rng.random() < plos(d2) if not ind else False
                sig = 4 if los else 6
                sh = rng.normal(0, sig) if shadow else 0
                p.append(TX + GAIN_BS + GAIN_UE - cable - pl(d2, los, rng) - pen * 0 - sh
                         - pattern(az, ue, s, d2) - (pen if ind else 0))
            p = np.array(p)
            sidx = int(np.argmax(p if ATTACH_ALL else p[:3]))  # best cell (all 57, or the 3 central ones)
            lin = 10 ** (p / 10)
            interf = lin.sum() - lin[sidx]
            out.append(10 * math.log10(lin[sidx] / (interf + 10 ** (NOISE / 10))))
    return np.array(out)


if __name__ == "__main__":
    ind = "--no-indoor" not in sys.argv
    cable = float(sys.argv[sys.argv.index("--cable") + 1]) if "--cable" in sys.argv else 0.0
    s = run(indoor=ind, cable=cable)
    print("indoor" if ind else "outdoor-only", "cable", cable,
          "quantiles 5/25/50/75/95:", np.round(np.quantile(s, [.05, .25, .5, .75, .95]), 1))
