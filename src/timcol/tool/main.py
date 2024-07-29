import os
import sys

from .upload import run_upload
from .. import logfile
from . import args, view_renderer, editor, mutators


def find_log_path(parsed_args: args.ParsedArgs) -> str:
    if parsed_args.log_file:
        return parsed_args.log_file

    if os.environ.get("TIMCOL_HOME"):
        return os.path.join(os.environ["TIMCOL_HOME"], "ledger.dat")

    return os.path.join(os.getcwd(), "ledger.dat")


def main() -> None:
    parsed_args = args.parse_args(sys.argv[1:])

    log_path = find_log_path(parsed_args)

    match parsed_args.sub_command:
        case "log-path":
            print(log_path)
        case "edit":
            editor.open_in_editor(log_path)
        case "start":
            assert parsed_args.start_args
            mutators.start(log_path, parsed_args.start_args)
        case "resume":
            mutators.resume(log_path)
        case "swap":
            assert parsed_args.start_args
            mutators.swap(log_path, parsed_args.start_args)
        case "stop":
            mutators.stop(log_path)
        case "cancel":
            mutators.cancel(log_path)
        case "backfill":
            assert parsed_args.backfill_args
            mutators.backfill(log_path, parsed_args.backfill_args)
        case "upload":
            run_upload(log_path)
        case _:
            try:
                with open(log_path, encoding="utf8") as file:
                    log = logfile.parse_file(file)
            except FileNotFoundError:
                log = logfile.LogFile([], None)

            view_renderer.render(log, parsed_args)
