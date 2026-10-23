#!/bin/bash
# Reproducible build of the isolated Simu5G tree used by this project.
#   1. shallow-clone Simu5G v1.7.0 into ./simu5g (existing OMNeT++ / INET are reused read-only)
#   2. apply patches/ (OMNeT++ 6.4 / macOS arm64 build fix + ExtCell FULL_ALLOC bug fix)
#   3. build in release mode
#   4. create the python venv for the analysis scripts
# NOTE: OMNeT++'s opp_shlib_postprocess breaks on paths containing spaces. If this folder
# lives under such a path, access it through a space-free symlink:  ln -s "<this dir>" ~/s5g-work
set -e
cd "$(dirname "$0")"
case "$PWD" in *" "*) echo "path contains spaces -> use a space-free symlink (see comment above)"; exit 1;; esac
source ./env.sh
if [ ! -d simu5g ]; then
  git clone --depth 1 --branch v1.7.0 https://github.com/inet-framework/simu5g simu5g
  git -C simu5g apply ../patches/simu5g-v1.7.0-omnetpp64-extcell.patch
fi
(cd simu5g && make MODE=release -j"$(sysctl -n hw.ncpu 2>/dev/null || nproc)")
[ -d .venv ] || python3 -m venv .venv
./.venv/bin/pip install -q -r requirements.txt
echo "setup done"
