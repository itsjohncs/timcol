import os

from .. import logfile
from . import args, view_renderer, editor, mutators


def find_log_path(parsed_args: args.ParsedArgs) -> str:
    if parsed_args.log_file:
        return parsed_args.log_file

    if os.environ.get("TIMCOL_HOME"):
        return os.path.join(os.environ["TIMCOL_HOME"], "ledger.dat")

    return os.path.join(os.getcwd(), "ledger.dat")


def main(argv: list[str]) -> None:
    parsed_args = args.parse_args(argv[1:])

    log_path = find_log_path(parsed_args)

    match parsed_args.sub_command:
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
        case _:
            with open(log_path, encoding="utf8") as file:
                log = logfile.parse_file(file)

            view_renderer.render(log, parsed_args)
