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

function get_account_balances {
    ledger bal --no-total | python3 -c "$(
        echo "import sys"
        echo "print(', '.join("
        echo "    i.strip().replace('  ', ' ') for i in sys.stdin))"
    )"
}

function current_status {
    local LEDGER_FILE="$TIMCOL_HOME/ledger.dat"
    local STATUS
    if [[ -f $LEDGER_FILE ]]; then
        STATUS="$(printf "%s" "$(
            grep "^[io]" ./ledger.dat |
                tail -n 1 |
                cut -d " " -f 4- |
                sed "s/  /: /"
        )")"
    fi

    printf "%s" "${STATUS:-timcol}"
}

function handle_update_status_signal {
    if [[ -n ${SCREENSHOT_STATUS} ]]; then
        printf "%b" "\33_$(current_status) -- $(get_account_balances) -- $SCREENSHOT_STATUS\33\\"
    else
        printf "%b" "\33_$(current_status) -- $(get_account_balances)\33\\"
    fi
}
trap handle_update_status_signal USR1

printf "%b" "\33_$(current_status) -- $(get_account_balances)\33\\"
while :; do
    SLEEP_UNTIL=$(("$(date +%s)" + 60))
    while [[ "$(date +%s)" -lt $SLEEP_UNTIL ]]; do
        # Use small sleep steps so we can respond to the USR1 signal in a
        # timely fashion
        sleep 0.5
    done

    SCREENSHOT_STATUS="$(record_screenshot)"
    printf "%b" "\33_$(current_status) -- $(get_account_balances) -- $SCREENSHOT_STATUS\33\\"
done
