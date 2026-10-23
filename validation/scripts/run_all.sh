#!/bin/bash
# Production batch.  Usage: run_all.sh <config> <ini> <first-run> <last-run> [extra opp_run args]
# Run number = delta_index*50 + repetition (OMNeT++ iterates the repetition innermost).
# MAXREP (default 50) limits the repetitions per Delta.
# Gentle on the machine: JOBS (default 4) parallel runs at lowest CPU priority; finished runs are skipped.
cd "$(dirname "$0")/.."
CFG=$1; export INI=$2; A=$3; B=$4; shift 4
EXTRA="$*"
export JOBS=${JOBS:-4} CFG EXTRA MAXREP
mkdir -p results/logs/$CFG results/$CFG
one() {
  r=$1; [ $(( r % 50 )) -ge "${MAXREP:-50}" ] && return 0
  d=$(( r / 50 )); delta=$(echo 0 3 5 7 | cut -d' ' -f$(( d + 1 )))
  [ -f "results/$CFG/delta${delta}-rep$(( r % 50 )).sca" ] && return 0
  nice -n 19 scripts/sim.sh "$CFG" "$r" $EXTRA > "results/logs/$CFG/run$r.log" 2>&1
}
export -f one
seq "$A" "$B" | xargs -P "$JOBS" -I{} bash -c 'one {}'
echo "$CFG runs $A..$B finished"
