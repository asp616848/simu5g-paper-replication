#!/bin/bash
# Usage: sim.sh <config> <run-number> [extra opp_run args]
# Runs one OMNeT++ run of validation/omnetpp.ini with the UE drop of repetition (run % REPS).

HERE="$(cd "$(dirname "$0")/.." && pwd)"
source "$HERE/../env.sh" >/dev/null 2>&1 || true
CFG=$1; RUN=$2; shift 2
REPS=${REPS:-50}
cd "$HERE"
exec opp_run_release -u Cmdenv -c "$CFG" -r "$RUN" \
  -n "$HERE:$SIMU5G_ROOT/src:$SIMU5G_ROOT/simulations:$INET_ROOT/src" \
  -l "$SIMU5G_ROOT/src/simu5g" -l "$INET_ROOT/src/INET" \
  -f "${INI:-omnetpp.ini}" -f "positions/rep$((RUN % REPS)).ini" \
  --result-dir="$HERE/results" \
  --cmdenv-express-mode=true --cmdenv-status-frequency=5s "$@"
