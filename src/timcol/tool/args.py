import argparse
import typing
import os
import datetime
import re

import dateparser


def parse_duration(text: str) -> datetime.timedelta:
    duration = datetime.timedelta()
    to_parse = text
    while to_parse:
        part = re.search(r"^([0-9]+(?:\.[0-9]+)?)([hms])(?:$|\s)", to_parse)
        if part is None:
            raise ValueError("Could not parse.")

        to_parse = to_parse[len(part.group(0)) :]

        unit = typing.cast(typing.Literal["h", "m", "s"], part.group(2))
        quantity = float(part.group(1))

        match unit:
            case "h":
                duration += datetime.timedelta(hours=quantity)
            case "m":
                duration += datetime.timedelta(minutes=quantity)
            case "s":
                duration += datetime.timedelta(seconds=quantity)

    return duration


def parse_datetime(text: str) -> datetime.datetime:
    result = dateparser.parse(text)
    if result is None:
        raise ValueError()

    return result


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

    class BackfillArgs(typing.NamedTuple):
        account: str
        description: str
        start: datetime.datetime
        duration: datetime.timedelta

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
            "resume",
            "swap",
            "stop",
            "sync",
            "backfill",
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
            self.csv_args = ParsedArgs.CsvArgs(args.rate, args.allow_rate_override)

        self.html_args: ParsedArgs.HtmlArgs | None = None
        if self.sub_command == "html":
            self.html_args = ParsedArgs.HtmlArgs(args.rate, args.allow_rate_override)

        self.start_args: ParsedArgs.StartArgs | None = None
        if self.sub_command in ("start", "swap"):
            self.start_args = ParsedArgs.StartArgs(args.account, args.description)

        self.backfill_args: ParsedArgs.BackfillArgs | None = None
        if self.sub_command == "backfill":
            self.backfill_args = ParsedArgs.BackfillArgs(
                args.account, args.description, args.start, args.duration
            )


def parse_args(raw_args: list[str]) -> ParsedArgs:
    parser = argparse.ArgumentParser(
        prog=os.environ.get("TIMCOL_NAME", "timcol"),
        description="Tracks time in a plaintext ledger format compatible with Ledger-CLI.",
        epilog="$TIMCOL_NAME can be set to change the name of timcol in help text. This allows easy renaming of timcol via an alias like `alias t='TIMCOL_NAME=t timcol'`",
    )

    parser.add_argument(
        "-f",
        "--file",
        help=(
            "Location of log file. Defaults to $TIMCOL_HOME/ledger.dat if "
            "TIMCOL_HOME is set, otherwise defaults to ./ledger.dat."
        ),
    )

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
    csv_parser.add_argument("rate", type=float, help="Hourly rate to bill in USD.")
    csv_parser.add_argument(
        "--allow-rate-override",
        action="store_true",
        help="Allows directives to override their rate.",
    )

    csv_parser = subparsers.add_parser("html", help="HTML-formatted invoice.")
    csv_parser.add_argument("rate", type=float, help="Hourly rate to bill in USD.")
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

    start_parser = subparsers.add_parser(
        "backfill",
        help="Record a complete task given its timestamp and duration.",
    )
    start_parser.add_argument("account", help="Account name.")
    start_parser.add_argument("description", help="Description of work.")
    start_parser.add_argument(
        "start",
        type=parse_datetime,
        help="When the task started. Accepts a wide-range of formats.",
    )
    start_parser.add_argument(
        "duration",
        type=parse_duration,
        help="How long the task went for. Examples of correct values: '3h 2m 1s', '1h', '300m'.",
    )

    subparsers.add_parser("resume", help="Restart the last task.")
    subparsers.add_parser("stop", help="Stop current task.")
    subparsers.add_parser("cancel", help="Delete current task.")

    subparsers.add_parser(
        "upload",
        aliases=["sync"],
        help="Execute the file `upload` in the directory the log file is in.",
    )
    subparsers.add_parser("log-path", help="Print the path of the log file then exit.")

    return ParsedArgs(parser.parse_args(raw_args))
