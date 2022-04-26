#!/usr/bin/env bash

SCRIPT_DIR="$(
    cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
    pwd -P
)"
ROOT_DIR="$(realpath --relative-to="$PWD" "$SCRIPT_DIR")"

ANY_FAILED=0

if [[ $PRETTIFY_CHECK -eq 1 ]]; then
    SHFMT_FLAGS=(-l)
    BLACK_FLAGS=(--check)
else
    SHFMT_FLAGS=(-w)
    BLACK_FLAGS=()
fi

echo "# shfmt"
if ! (find "$ROOT_DIR" -name "*.sh" -print0 | xargs -0t shfmt -i=4 -sr "${SHFMT_FLAGS[@]}"); then
    ANY_FAILED=1
fi

echo "# black"
if ! (find "$ROOT_DIR" -name "*.py" -print0 | xargs -0t black --line-length 80 "${BLACK_FLAGS[@]}"); then
    ANY_FAILED=1
fi

exit $ANY_FAILED
