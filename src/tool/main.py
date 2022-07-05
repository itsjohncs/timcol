import os

from . import args
from . import view_renderer
import logfile


def find_log_path(parsed_args: args.ParsedArgs) -> str:
    if parsed_args.log_file:
        return parsed_args.log_file

    if os.environ.get("TIMCOL_HOME"):
        return os.path.join(os.environ["TIMCOL_HOME"], "ledger.dat")

    return os.path.join(os.getcwd(), "ledger.dat")


def main(argv: list[str]):
    parsed_args = args.parse_args(argv[1:])

    with open(find_log_path(parsed_args), encoding="utf8") as f:
        log = logfile.parse_file(f)

    view_renderer.render(log, parsed_args)
