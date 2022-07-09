import argparse
import typing


class ParsedArgs:
    def __init__(self, args: argparse.Namespace):
        self.sub_command: typing.Literal["json"] = args.sub_command
        self.log_file: str | None = args.file


def parse_args(raw_args: list[str]) -> ParsedArgs:
    parser = argparse.ArgumentParser(description="Prints time entries.")

    parser.add_argument("-f", "--file", help="Location of log file.")

    subparsers = parser.add_subparsers(title="SUB COMMANDS", dest="sub_command")
    # subparsers.add_parser("json")
    subparsers.add_parser("reg", help="Human friendly format.")
    # csv_parser = subparsers.add_parser("csv")
    # csv_parser.add_argument(
    #     "-r", "--rate", type=float, help="Hourly rate to bill if not specified."
    # )
    # csv_parser.add_argument(
    #     "--only-uncleared",
    #     action="store_true",
    #     help="Ignore cleared transactions.",
    # )

    return ParsedArgs(parser.parse_args(raw_args))
