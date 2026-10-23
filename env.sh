# Source this file to set up the toolchain:  source env.sh
#   OMNETPP_ROOT  OMNeT++ 6.x install            (default: ~/Acads/omnetpp-6.4.0)
#   INET_ROOT     built INET 4.5+ (release lib)   (default: ~/Acads/samples/inet-4.7.0)
# Simu5G is built locally in ./simu5g by setup.sh and is never installed system-wide.
export WORK="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
# OMNeT++'s link post-processing breaks on spaces: prefer a space-free symlink to this dir if one exists
if [[ "$WORK" == *" "* && -d "$HOME/Acads/s5g-work" && "$(cd "$HOME/Acads/s5g-work" && pwd -P)" == "$(cd "$WORK" && pwd -P)" ]]; then
  export WORK="$HOME/Acads/s5g-work"
fi
export OMNETPP_ROOT="${OMNETPP_ROOT:-$HOME/Acads/omnetpp-6.4.0}"
export INET_ROOT="${INET_ROOT:-$HOME/Acads/samples/inet-4.7.0}"
export SIMU5G_ROOT="$WORK/simu5g"
pushd "$OMNETPP_ROOT" >/dev/null && source ./setenv >/dev/null 2>&1; popd >/dev/null
