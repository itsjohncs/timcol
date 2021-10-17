#!/usr/bin/env bash

set -eu

if [[ -z ${TIMCOL_HOME-} ]]; then
    echo "FATAL: Provide data directory with \$TIMCOL_HOME"
    exit 1
fi

function get_script_dir {
    (
        local CUR="${BASH_SOURCE[0]}"
        while [[ -L $CUR ]]; do
            cd "$(dirname "$CUR")"
            cd "$(pwd -P)"
            CUR="$(readlink "$CUR")"
        done
        CUR="$(realpath "$CUR")"

        ( cd "$(dirname "$CUR")"; pwd -P )
    )

}

export LEDGER_FILE="$TIMCOL_HOME/ledger.dat"

function usage {
    echo "USAGE: $0 <command>"
    echo
    echo "COMMANDS"
    echo "  start ACCOUNT TASK_DESCRIPTION"
    echo "  stop"
    echo "  status"
}

function last_directive {
    if [[ -f $LEDGER_FILE ]]; then
        printf "%s" "$(grep -o "^[io]" "$LEDGER_FILE" | tail -n 1)"
    fi
}

function get_timestamp {
    date +"%Y/%m/%d %H:%M:%S"
}

case ${1-} in

    status)
        if [[ ! -f $LEDGER_FILE ]]; then
            echo "NOTICE: No ledger file found."
            exit 0
        elif [[ $(last_directive) == "i" ]]; then
            echo "NOTICE: Task is pending"
        fi

        "$(get_script_dir)/print_log.py" < "$LEDGER_FILE"
        ;;

    stop)
        if [[ $(last_directive) != "i" ]]; then
            echo "FATAL: No task is pending."
            exit 1
        fi

        echo "o $(get_timestamp)" >> "$TIMCOL_HOME/ledger.dat"
        ;;

    start)
        if [[ $(last_directive) == "i" ]]; then
            echo "FATAL: Task is pending."
            exit 1
        elif [[ $# -ne 3 || -z $2 || -z $3 ]]; then
            usage
            exit 1
        elif ! grep -q "^account $2\$" "$LEDGER_FILE"; then
            echo "FATAL: Unknown account $2"
            exit 1
        fi


        echo "i $(get_timestamp) $2  $3" >> "$LEDGER_FILE"
        ;;

    edit)
        $EDITOR "$LEDGER_FILE"
        ;;

    *)
        usage
        exit 1
        ;;

esac
