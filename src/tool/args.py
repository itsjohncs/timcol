import argparse
import typing
import os


class ParsedArgs:
    class RegisterArgs(typing.NamedTuple):
        show_unscaled_time: bool

    class CsvArgs(typing.NamedTuple):
        rate: float
        allow_rate_override: bool

    class HtmlArgs(typing.NamedTuple):
        rate: float
        allow_rate_override: bool

    class StartArgs(typing.NamedTuple):
        account: str
        description: str

    def __init__(self, args: argparse.Namespace):
        sub_command: str = {"register": "reg", "sync": "upload"}.get(
            args.sub_command, args.sub_command
        )
        assert sub_command in {
            "reg",
            "csv",
            "edit",
            "start",
            "cancel",
            "html",
            "log-path",
            "upload",
            "switch",
        }
        self.sub_command = sub_command

        self.log_file: str | None = args.file

        self.register_args: ParsedArgs.RegisterArgs | None = None
        if self.sub_command == "reg":
            self.register_args = ParsedArgs.RegisterArgs(
                getattr(args, "unscaled", False)
            )

        self.csv_args: ParsedArgs.CsvArgs | None = None
        if self.sub_command == "csv":
            self.csv_args = ParsedArgs.CsvArgs(
                args.rate, args.allow_rate_override
            )

        self.html_args: ParsedArgs.HtmlArgs | None = None
        if self.sub_command == "html":
            self.html_args = ParsedArgs.HtmlArgs(
                args.rate, args.allow_rate_override
            )

        self.start_args: ParsedArgs.StartArgs | None = None
        if self.sub_command in ("start", "swap"):
            self.start_args = ParsedArgs.StartArgs(
                args.account, args.description
            )


def parse_args(raw_args: list[str]) -> ParsedArgs:
    parser = argparse.ArgumentParser(
        prog=os.environ.get("TIMCOL_NAME", "timcol"),
        description="Prints time entries.",
    )

    parser.add_argument("-f", "--file", help="Location of log file.")

    subparsers = parser.add_subparsers(title="SUB COMMANDS", dest="sub_command")
    subparsers.default = "register"

    subparsers.add_parser("edit", help="Open ledger for editing.")

    register_parser = subparsers.add_parser(
        "register", aliases=["reg"], help="Human friendly format."
    )
    register_parser.add_argument(
        "-u", "--unscaled", action="store_true", help="Show unscaled totals."
    )

    csv_parser = subparsers.add_parser("csv", help="CSV-formatted invoice.")
    csv_parser.add_argument(
        "rate", type=float, help="Hourly rate to bill in USD."
    )
    csv_parser.add_argument(
        "--allow-rate-override",
        action="store_true",
        help="Allows directives to override their rate.",
    )

    csv_parser = subparsers.add_parser("html", help="HTML-formatted invoice.")
    csv_parser.add_argument(
        "rate", type=float, help="Hourly rate to bill in USD."
    )
    csv_parser.add_argument(
        "--allow-rate-override",
        action="store_true",
        help="Allows directives to override their rate.",
    )

    start_parser = subparsers.add_parser(
        "start",
        aliases=["swap"],
        help="Start a new task (use swap to stop and immediately start a new task)",
    )
    start_parser.add_argument("account", help="Account name.")
    start_parser.add_argument("description", help="Description of work.")

    subparsers.add_parser("resume", help="Restart the last task.")
    subparsers.add_parser("stop", help="Stop current task.")
    subparsers.add_parser("cancel", help="Delete current task.")

    subparsers.add_parser(
        "upload",
        aliases=["sync"],
        help="Execute the file `upload` in the directory the log file is in.",
    )
    subparsers.add_parser(
        "log-path", help="Print the path of the log file then exit."
    )

    return ParsedArgs(parser.parse_args(raw_args))
