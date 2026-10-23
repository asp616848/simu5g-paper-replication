#!/usr/bin/env python3
"""Extract per-UE statistics from the OMNeT++ result files into compact CSVs.

Usage: extract.py <config>   (config = UrbanMacro | UrbanMacroNoFading | UrbanMacroFull)

Output (results/extracted/<config>/):
  sinr_samples.csv  : delta, rep, ue, sinr_db          (all DL SINR samples, vectors)
  ue_stats.csv      : delta, rep, ue, harq1_err, sinr_mean, cbr_loss, serving_cell
"""
import csv
import io
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = sys.argv[1] if len(sys.argv) > 1 else "UrbanMacro"
RES = ROOT / "results" / CONFIG
OUT = ROOT / "results" / "extracted" / CONFIG
UE = re.compile(r"^[A-Za-z]+\.ue\[(\d+)\]\.(.*)$")
NUM_MEASURED = 30  # UEs 0..29 are the measured UEs (the full variant has 54 more "load" UEs)


def scavetool(args):
    r = subprocess.run(["opp_scavetool", "x", *args, "-F", "CSV-R", "-o", "-"],
                       capture_output=True, text=True, check=True)
    return csv.DictReader(io.StringIO(r.stdout))


def process(sca):
    m = re.match(r"delta(\d+)-rep(\d+)", sca.stem)
    delta, rep = int(m[1]), int(m[2])
    vec = sca.with_suffix(".vec")
    stats, sinr = {}, []
    flt = ('(name =~ "harqErrorRate_1st_Dl:mean" OR name =~ "measuredSinrDl:mean" OR '
           'name =~ "cbrFrameLoss:mean") AND module =~ "*.ue[0..29].*"')
    for row in scavetool(["-f", flt, str(sca)]):
        if row["type"] != "scalar":
            continue
        mm = UE.match(row["module"])
        if not mm or int(mm[1]) >= NUM_MEASURED or not (mm[2].endswith("nrMac") or mm[2].endswith("nrChannelModel[0]") or mm[2] == "app[0]"):
            continue
        stats.setdefault(int(mm[1]), {})[row["name"].split(":")[0]] = float(row["value"])
    vflt = 'name =~ "measuredSinrDl:vector" AND module =~ "*.ue[0..29].cellularNic.nrChannelModel[0]"'
    for row in scavetool(["-f", vflt, str(vec)]):
        if row["type"] != "vector":
            continue
        ue = int(UE.match(row["module"])[1])
        sinr += [(delta, rep, ue, float(v)) for v in row["vecvalue"].split()]
    return delta, rep, stats, sinr


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(RES.glob("delta*-rep*.sca"))
    if not files:
        sys.exit("no result files found")
    with open(OUT / "ue_stats.csv", "w", newline="") as fs, open(OUT / "sinr_samples.csv", "w", newline="") as fv:
        ws, wv = csv.writer(fs), csv.writer(fv)
        ws.writerow(["delta", "rep", "ue", "harq1_err", "sinr_mean", "cbr_loss"])
        wv.writerow(["delta", "rep", "ue", "sinr_db"])
        for f in files:
            delta, rep, stats, sinr = process(f)
            for ue, s in sorted(stats.items()):
                ws.writerow([delta, rep, ue, s.get("harqErrorRate_1st_Dl"), s.get("measuredSinrDl"),
                             s.get("cbrFrameLoss")])
            wv.writerows(sinr)
            print(f"{f.name}: {len(stats)} UEs, {len(sinr)} SINR samples")


if __name__ == "__main__":
    main()
