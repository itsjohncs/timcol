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
if ! (find "$ROOT_DIR" -name "*.py" -print0 | xargs -0t pylint -d C0114,C0115,C0116 -s n); then
    ANY_FAILED=1
fi

echo "# black"
if ! PRETTIFY_CHECK=1 "$ROOT_DIR/prettify.sh"; then
    ANY_FAILED=1
fi

if [[ $ANY_FAILED -ne 0 ]]; then
    echo "LINT FAILED"
fi
exit $ANY_FAILED
