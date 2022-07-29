import argparse
import typing
import os


class ParsedArgs:
    class InvoiceArgs(typing.NamedTuple):
        rate: float
        allow_rate_override: bool

    class StartArgs(typing.NamedTuple):
        account: str
        description: str

    def __init__(self, args: argparse.Namespace):
        self.sub_command: typing.Literal[  # type: ignore
            "reg", "csv", "edit", "start", "cancel"
        ] = {"register": "reg"}.get(args.sub_command, args.sub_command)
        self.log_file: str | None = args.file

        self.invoice_args: ParsedArgs.InvoiceArgs | None = None
        if self.sub_command == "csv":
            self.invoice_args = ParsedArgs.InvoiceArgs(
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

    subparsers.add_parser(
        "register", aliases=["reg"], help="Human friendly format."
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

    return ParsedArgs(parser.parse_args(raw_args))
