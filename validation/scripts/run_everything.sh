#!/bin/bash
# All Stage-3 production runs, sized to stay gentle on a laptop (4 jobs, lowest priority; ~2-3 h).
#   UrbanMacro        : Delta=0 x 50 reps, Delta=3,5,7 x 25 reps
#   UrbanMacroNoFading: 4 Deltas x 10 reps
#   UrbanMacroFull    : Delta=5 x 10 reps, 6 s (1 s warm-up)
cd "$(dirname "$0")/.."
MAXREP=25 scripts/run_all.sh UrbanMacro omnetpp.ini 50 199
MAXREP=50 scripts/run_all.sh UrbanMacro omnetpp.ini 0 49
MAXREP=10 scripts/run_all.sh UrbanMacroNoFading omnetpp.ini 0 199
MAXREP=10 scripts/run_all.sh UrbanMacroFull full.ini 100 149 --sim-time-limit=6s
echo "ALL DONE"
