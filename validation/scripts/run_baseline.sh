#!/bin/bash
# Stage 2: run the baseline scenario (5 repetitions).
cd "$(dirname "$0")/.."
source "$(cd "$(dirname "$0")/../.." && pwd)/env.sh" >/dev/null 2>&1 || true
mkdir -p results/Baseline
for r in 0 1 2 3 4; do
  opp_run_release -u Cmdenv -c Baseline -r $r \
    -n "$PWD:$SIMU5G_ROOT/src:$SIMU5G_ROOT/simulations:$INET_ROOT/src" \
    -l "$SIMU5G_ROOT/src/simu5g" -l "$INET_ROOT/src/INET" \
    -f baseline.ini --result-dir="$PWD/results" --cmdenv-express-mode=true > "results/Baseline/run$r.log" 2>&1 \
    && echo "baseline rep $r ok" || { echo "baseline rep $r FAILED"; tail -5 "results/Baseline/run$r.log"; }
done
