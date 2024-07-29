import datetime

from .args import ParsedArgs
from .. import logfile


def _get_pending_directive(log_path: str) -> logfile.directive.CheckIn | None:
    try:
        with open(log_path, encoding="utf8") as file:
            return logfile.parse_file(file).pending
    except FileNotFoundError:
        return None


def _get_timestamp() -> str:
    return datetime.datetime.now().strftime(logfile.directive.TIME_FORMAT)


def start(log_path: str, args: ParsedArgs.StartArgs) -> None:
    if _get_pending_directive(log_path):
        print("Task already pending.")
    else:
        with open(log_path, "a", encoding="utf8") as file:
            file.write(f"i {_get_timestamp()} {args.account}  {args.description}\n")


def stop(log_path: str) -> bool:
    if not _get_pending_directive(log_path):
        print("No task to stop.")
        return False

    with open(log_path, "a", encoding="utf8") as file:
        file.write(f"o {_get_timestamp()}\n")
    return True


def cancel(log_path: str) -> None:
    pending = _get_pending_directive(log_path)
    if not pending:
        print("No task to cancel.")
        return

    with open(log_path, "r", encoding="utf8") as file:
        lines = file.readlines()

    while lines:
        line = lines.pop().strip()

        if line:
            print(f"-{line}")
            break

    with open(log_path, "w", encoding="utf8") as file:
        file.writelines(lines)


def swap(log_path: str, args: ParsedArgs.StartArgs) -> None:
    if stop(log_path):
        start(log_path, args)


def resume(log_path: str) -> None:
    try:
        with open(log_path, encoding="utf8") as file:
            logs = logfile.parse_file(file)
    except FileNotFoundError:
        logs = None

    if not logs or not logs.entries:
        print("No task to resume.")
        return
    if logs.pending:
        print("Task already pending.")

    last_entry = logs.entries[-1]

    with open(log_path, "a", encoding="utf8") as file:
        file.write(f"i {_get_timestamp()} {last_entry.account}  {last_entry.task}\n")


def backfill(log_path: str, args: ParsedArgs.BackfillArgs) -> None:
    in_timestamp = args.start.strftime(logfile.directive.TIME_FORMAT)
    out_timestamp = (args.start + args.duration).strftime(logfile.directive.TIME_FORMAT)
    with open(log_path, "a", encoding="utf8") as file:
        file.write(f"i {in_timestamp} {args.account}  {args.description}\n")
        file.write(f"o {out_timestamp}\n")
