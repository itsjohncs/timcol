import datetime

from .args import ParsedArgs
from .. import logfile


def get_pending_directive(log_path: str) -> logfile.directive.CheckIn | None:
    with open(log_path, encoding="utf8") as file:
        return logfile.parse_pending_directive_in_file(file)


def get_timestamp() -> str:
    return datetime.datetime.now().strftime(logfile.directive.TIME_FORMAT)


def start(log_path: str, args: ParsedArgs.StartArgs) -> None:
    if get_pending_directive(log_path):
        print("Task already pending.")
    else:
        with open(log_path, "a", encoding="utf8") as file:
            file.write(
                f"i {get_timestamp()} {args.account}  {args.description}\n"
            )


def stop(log_path: str) -> bool:
    if not get_pending_directive(log_path):
        print("No task to stop.")
        return False

    with open(log_path, "a", encoding="utf8") as file:
        file.write(f"o {get_timestamp()}\n")
    return True


def swap(log_path: str, args: ParsedArgs.StartArgs) -> None:
    if stop(log_path):
        start(log_path, args)
