#!/usr/bin/env bash

set -e

if [[ -z ${TIMCOL_HOME-} ]]; then
    echo "FATAL: Provide data directory with \$TIMCOL_HOME"
    exit 1
fi

if [[ ! -d $TIMCOL_HOME/screenshots ]]; then
    mkdir "$TIMCOL_HOME/screenshots"
fi

function record_screenshot {
    local TIMESTAMP CAPTURE_PATH
    TIMESTAMP="$(date +"%Y-%m-%d %p %I:%M:%S")"
    CAPTURE_PATH="$TIMCOL_HOME/screenshots/$TIMESTAMP.png"

    screencapture -x "$CAPTURE_PATH" \
        >> "$TIMCOL_HOME/capture.errorlog" 2>&1
    sips -Z 1920 "$CAPTURE_PATH" >> "$TIMCOL_HOME/capture.errorlog" 2>&1

    if [[ -f "$CAPTURE_PATH" ]]; then
        echo "CAPTURE $TIMESTAMP.png"
    else
        echo "ERROR $TIMESTAMP.png"
    fi
}

while :; do
    sleep 60
    record_screenshot
done
