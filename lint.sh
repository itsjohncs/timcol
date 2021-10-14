#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1 ; pwd -P )"

# Get short relative path so output is nicer
ROOT_DIR="$(realpath --relative-to="$PWD" "$SCRIPT_DIR")"

find "$ROOT_DIR" -name ".?*" -prune -o -name "*.sh" -print0 | \
    xargs -0t shellcheck --shell bash
