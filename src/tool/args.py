import argparse
import typing
import os


class ParsedArgs:
    class InvoiceArgs(typing.NamedTuple):
        rate: float
        allow_rate_override: bool

    def __init__(self, args: argparse.Namespace):
        self.sub_command: typing.Literal[
            "reg", "invoice", "edit"
        ] = args.sub_command
        self.log_file: str | None = args.file

        self.invoice_args: ParsedArgs.InvoiceArgs | None = None
        if self.sub_command == "invoice":
            self.invoice_args = ParsedArgs.InvoiceArgs(
                args.rate, args.allow_rate_override
            )


def parse_args(raw_args: list[str]) -> ParsedArgs:
    parser = argparse.ArgumentParser(
        prog=os.environ.get("TIMCOL_NAME", "timcol"),
        description="Prints time entries.",
    )

    parser.add_argument("-f", "--file", help="Location of log file.")

    subparsers = parser.add_subparsers(
        title="SUB COMMANDS", dest="sub_command", required=True
    )

    subparsers.add_parser("edit", help="Open ledger for editing.")

    subparsers.add_parser("reg", help="Human friendly format.")

    csv_parser = subparsers.add_parser("invoice", help="CSV-formatted invoice.")
    csv_parser.add_argument(
        "rate", type=float, help="Hourly rate to bill in USD."
    )
    csv_parser.add_argument(
        "--allow-rate-override",
        action="store_true",
        help="Allows directives to override their rate.",
    )

    return ParsedArgs(parser.parse_args(raw_args))
