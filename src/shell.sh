#!/usr/bin/env bash

set -e

if [[ -z ${TIMCOL_HOME-} && $# -eq 0 ]]; then
    echo "USAGE: $0 HOME"
    echo "  HOME can also be specified via \$TIMCOL_HOME"
    exit 1
fi

SCREEN_VERSION="$(screen --version | grep -Eo '[0-9]{1,2}.[0-9]{2}\.[0-9]{2}')"
if [[ $SCREEN_VERSION < "4.01.00" ]]; then
    echo "FATAL: You need a newer version of screen (minimum 4.01.x)"
    exit 1
fi

SCRIPT_DIR="$( cd "$(dirname "$(readlink "${BASH_SOURCE[0]}")")" || exit 1 ; pwd -P )"

export PATH="$SCRIPT_DIR/shell-bin:$PATH"
export TIMCOL_REPO="$SCRIPT_DIR/.."
export TIMCOL_HOME="${TIMCOL_HOME-$1}"
screen -c "$SCRIPT_DIR/screenrc"
