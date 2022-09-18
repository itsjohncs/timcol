# timcol

`timcol` is a command line time tracking and invoicing tool. Similar tools exist within the [plain text accounting ecosystem](https://plaintextaccounting.org/#time-logging).

```
usage: timcol [-h] [-f FILE]
              {edit,register,reg,csv,html,start,swap,resume,stop,cancel,upload,sync,log-path}
              ...

Prints time entries.

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Location of log file. Defaults to
                        $TIMCOL_HOME/ledger.dat if TIMCOL_HOME is set,
                        otherwise defaults to ./ledger.dat.

SUB COMMANDS:
  {edit,register,reg,csv,html,start,swap,resume,stop,cancel,upload,sync,log-path}
    edit                Open ledger for editing.
    register (reg)      Human friendly format.
    csv                 CSV-formatted invoice.
    html                HTML-formatted invoice.
    start (swap)        Start a new task (use swap to stop and immediately
                        start a new task)
    resume              Restart the last task.
    stop                Stop current task.
    cancel              Delete current task.
    upload (sync)       Execute the file `upload` in the directory the log
                        file is in.
    log-path            Print the path of the log file then exit.

TIMCOL_NAME can be set to change the name of timcol in help text.
```
