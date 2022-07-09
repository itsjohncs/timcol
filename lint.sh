#!/usr/bin/env bash

SCRIPT_DIR="$(
    cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
    pwd -P
)"
ROOT_DIR="$(realpath --relative-to="$PWD" "$SCRIPT_DIR")"

ANY_FAILED=0

echo "# shellcheck"
if ! (find "$ROOT_DIR" \( -name "*.sh" -o -path "*/git-hooks/*" \) -print0 | xargs -0t shellcheck --shell bash); then
    ANY_FAILED=1
fi

echo "# pylint"
if ! pylint --rcfile "$ROOT_DIR/pylintrc" "$ROOT_DIR/src"; then
    ANY_FAILED=1
fi

echo "# pyright"
if ! pyright --pythonversion 3.11 "$ROOT_DIR/src"; then
    ANY_FAILED=1
fi

if ! PRETTIFY_CHECK=1 "$ROOT_DIR/prettify.sh"; then
    ANY_FAILED=1
fi

if [[ $ANY_FAILED -ne 0 ]]; then
    echo "LINT FAILED"
fi
exit $ANY_FAILED
