import os

from .. import logfile
from . import args
from . import view_renderer
from . import editor


def find_log_path(parsed_args: args.ParsedArgs) -> str:
    if parsed_args.log_file:
        return parsed_args.log_file

    if os.environ.get("TIMCOL_HOME"):
        return os.path.join(os.environ["TIMCOL_HOME"], "ledger.dat")

    return os.path.join(os.getcwd(), "ledger.dat")


def main(argv: list[str]):
    parsed_args = args.parse_args(argv[1:])

    log_path = find_log_path(parsed_args)

    if parsed_args.sub_command == "edit":
        editor.open_in_editor(log_path)
    else:
        with open(log_path, encoding="utf8") as file:
            log = logfile.parse_file(file)

        view_renderer.render(log, parsed_args)
