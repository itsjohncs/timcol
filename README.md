# timcol

`timcol` helps you track your time in a plaintext format compatible with [Ledger-CLI](https://ledger-cli.org). Similar tools exist within the [plain text accounting ecosystem](https://plaintextaccounting.org/#time-logging).

It can help you generate basic HTML or CSV invoices and even give them live updates via the flexible `upload (sync)` command.

## Installation

Releases are available on [PyPI](https://pypi.org/project/timcol/). In descending order of preference, I recommend installing it using [`uv`](https://github.com/astral-sh/uv?tab=readme-ov-file#uv), [`pipx`](https://pipx.pypa.io/stable/), or `pip`:

1. `uv tool install timcol`
2. `pipx install timcol`
3. `pip install timcol`

## Trying Out timcol

Try some `timcol` commands to get a feel for how to use it:

```console
$ timcol start Client1 "Writing email"
$ timcol cancel
-i 2024/07/29 04:28:21 PM Client1  Writing email
$ timcol backfill Client1 "Writing email" "3 hours ago" 15m
$ timcol start Client1 "Setting up project skeleton."
$ timcol swap Client1 "Implementing milestone 1"
$ timcol stop
$ timcol resume 
$ timcol reg
timestamp          duration    account    task
-----------------  ----------  ---------  ----------------------------
Jul 29 @ 01:30 PM  0:15:00     Client1    Writing email
Jul 29 @ 04:30 PM  0:00:15     Client1    Setting up project skeleton.
Jul 29 @ 04:30 PM  0:00:20     Client1    Implementing milestone 1
Jul 29 @ 04:31 PM  0:00:17*    Client1    Implementing milestone 1
Jul 29 SUBTOTAL    0:15:52
TOTAL TIME         0:15:52
```

Run `timcol edit` to open up the ledger file for direct editing.

## Configuring timcol

Depending on your preferences, you may want to set up a central git repo for your ledger file. You can do this by setting `TIMCOL_HOME` in your `.bashrc`, `.bash_profile`, or equivalent file.

```bash
export TIMCOL_HOME=/Users/johnsullivan/personal/timekeeping-ledger
```

You may also want to alias or symlink timcol to a shorter name, like `t`. If you want to use an alias to do this, timcol has an environmental variable `TIMCOL_NAME` you can set so that `--help` text matches the aliased name:

```bash
alias t='TIMCOL_NAME=t timcol'
```

## Full Help Output

```
usage: timcol [-h] [-f FILE] {edit,register,reg,csv,html,start,swap,backfill,resume,stop,cancel,upload,sync,log-path} ...

Tracks time in a plaintext ledger format compatible with Ledger-CLI.

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Location of log file. Defaults to $TIMCOL_HOME/ledger.dat if TIMCOL_HOME is set, otherwise defaults to ./ledger.dat.

SUB COMMANDS:
  {edit,register,reg,csv,html,start,swap,backfill,resume,stop,cancel,upload,sync,log-path}
    edit                Open ledger for editing.
    register (reg)      Human friendly format.
    csv                 CSV-formatted invoice.
    html                HTML-formatted invoice.
    start (swap)        Start a new task (use swap to stop and immediately start a new task)
    backfill            Record a complete task given its timestamp and duration.
    resume              Restart the last task.
    stop                Stop current task.
    cancel              Delete current task.
    upload (sync)       Execute the file `upload` in the directory the log file is in.
    log-path            Print the path of the log file then exit.

$TIMCOL_NAME can be set to change the name of timcol in help text. This allows easy renaming of timcol via an alias like `alias t='TIMCOL_NAME=t
timcol'`
```
