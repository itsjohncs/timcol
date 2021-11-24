#!/usr/bin/env python3

import argparse
import collections
import csv
import datetime
import json
import re
import sys

CHECKIN_RE = re.compile(r"^i ([^ ]+ [^ ]+) (.+?)(?:  ([^;]*?)(?:  ;(.*?))?)?$",
                        re.MULTILINE)
CHECKOUT_RE = re.compile(r"^([oO]) ([^ ]+? [^ ]+?)$", re.MULTILINE)
Event = collections.namedtuple("Event", [
    "is_start",
    "timestamp",
    "account",
    "task",
    "note",
    "cleared",
])


def lex(ledger_file):
    """Converts `ledger_file` into a stream of `Event`s.

    One checkin or checkout will be one event. No attempt is made to pair them
    up yet. Any line with unrecognized syntax will be ignored.
    """
    def strip_or_none(val):
        if val is None:
            return None

        return val.strip()

    for i in ledger_file:
        checkin_match = CHECKIN_RE.match(i)
        if checkin_match:
            yield Event(
                is_start=True,
                timestamp=datetime.datetime.strptime(
                    checkin_match.group(1), "%Y/%m/%d %H:%M:%S"),
                account=checkin_match.group(2),
                task=checkin_match.group(3),
                note=strip_or_none(checkin_match.group(4)),
                cleared=None)
            continue

        checkout_match = CHECKOUT_RE.match(i)
        if checkout_match:
            yield Event(
                is_start=False,
                timestamp=datetime.datetime.strptime(
                    checkout_match.group(2), "%Y/%m/%d %H:%M:%S"),
                account=None,
                task=None,
                note=None,
                cleared=checkout_match.group(1) == "O")
            continue


Log = collections.namedtuple("Log", [
    "start_timestamp",
    "duration",
    "account",
    "task",
    "note",
    "is_cleared",
])


def parse(events):
    """Converts a stream of `Event`s into a stream of `Log`s.

    A `Log` represents a checkin and checkout. If there is an unpaired
    checkin remaining at the end of the stream, it will be ignored.
    """
    unresolved_event = None
    for i in events:
        if unresolved_event is None:
            assert i.is_start
            unresolved_event = i
        else:
            assert not i.is_start
            yield Log(
                start_timestamp=unresolved_event.timestamp,
                duration=i.timestamp - unresolved_event.timestamp,
                account=unresolved_event.account,
                task=unresolved_event.task,
                note=unresolved_event.note,
                is_cleared=i.cleared)
            unresolved_event = None


def print_register(logs):
    """Prints a human readable summary of `logs`."""
    total_time = datetime.timedelta(0)
    total_uncleared_time = datetime.timedelta(0)
    for i in logs:
        total_time += i.duration

        if not i.is_cleared:
            total_uncleared_time += i.duration

        pretty_timestamp = datetime.datetime.strftime(
            i.start_timestamp, "%h %d @ %I:%M %p")

        seconds = i.duration.total_seconds()
        pretty_duration = f"{seconds // 60:.0f}m.{seconds % 60:.0f}s"

        status = " *" if i.is_cleared else ""
        maybe_note = f" ({i.note.strip()})" if i.note else ""
        print(f"{pretty_timestamp}{status}\t{pretty_duration}\t{i.account}: "
              f"{i.task}{maybe_note}")

    total_uncleared_time_in_hours = (
        total_uncleared_time.total_seconds() / 60 ** 2)
    print(f"TOTAL UNCLEARED TIME: {total_uncleared_time_in_hours:.2f}h")

    total_time_in_hours = total_time.total_seconds() / 60 ** 2
    print(f"TOTAL TIME: {total_time_in_hours:.2f}h")


def print_json(logs):
    """Prints a JSON object for each log."""
    print("[")

    for i in logs:
        serialized = {
            "start_timestamp": i.start_timestamp.timestamp(),
            "duration": i.duration.total_seconds(),
            "account": i.account,
            "task": i.task,
            "note": i.note,
            "is_cleared": i.is_cleared,
        }
        json.dump(serialized, sys.stdout, sort_keys=True)
        print(",")

    print("]")


RATE_TAG_RE = re.compile(r"(?:^|\s)Rate: ([^\s;]+)")


def print_transactions(logs, *, default_hourly_rate, account_rates,
                       only_uncleared):
    """Prints a Ledger transaction for each `Log`."""
    writer = csv.DictWriter(sys.stdout, fieldnames=[
        "Date",
        "Duration",
        "Rate",
        "Cost",
        "Description",
    ])
    writer.writeheader()

    total_cost = 0
    for i in logs:
        if only_uncleared and i.is_cleared:
            continue

        seconds = i.duration.total_seconds()

        rate = default_hourly_rate
        if i.note and RATE_TAG_RE.search(i.note):
            rate = float(RATE_TAG_RE.search(i.note).group(1))
        elif i.account in account_rates:
            rate = account_rates[i.account]

        hours = i.duration.total_seconds() / 60 ** 2
        cost = hours * rate
        total_cost += cost

        writer.writerow({
            "Date": datetime.datetime.strftime(i.start_timestamp, "%Y/%m/%d"),
            "Duration": f"{seconds // 60:.0f}:{seconds % 60:02.0f}",
            "Rate": f"${rate:.2f}",
            "Cost": f"${cost:.2f}",
            "Description": i.task,
        })

    writer.writerow({
        "Cost": f"${total_cost:.2f}",
        "Description": "TOTAL COST",
    })


ACCOUNT_RE = re.compile(r"^account (.+?)$(?:\n    ; Rate: (.+?)$|\n    .+?$)+",
                        re.MULTILINE)


def get_account_rates(ledger_as_str):
    """Gets the per-account rates defined in the Ledger file.

    A per-account rate can be defined alongside the account definition,
    like so:

        account Best Client
            ; Rate: 20
    """
    account_rates = {}
    for match in ACCOUNT_RE.finditer(ledger_as_str):
        try:
            account_rates[match.group(1)] = float(match.group(2))
        except ValueError as err:
            raise RuntimeError(
                f"Expected float for Rate of account {match.group(1)}, got "
                f"{match.group(2)}") from err

    return account_rates


def parse_args(args):
    parser = argparse.ArgumentParser(description="Prints time entries.")

    subparsers = parser.add_subparsers(title="FORMATS", dest="format")

    subparsers.add_parser("register", help="Human friendly format.")
    subparsers.add_parser("json")
    csv_parser = subparsers.add_parser("csv")
    csv_parser.add_argument(
        "-r", "--rate", type=float,
        help="Hourly rate to bill if not specified.")
    csv_parser.add_argument(
        "--only-uncleared", action="store_true",
        help="Ignore cleared transactions.")

    return parser.parse_args(args)


if __name__ == "__main__":
    parsed_args = parse_args(sys.argv[1:])
    if parsed_args.format == "register":
        print_register(parse(lex(sys.stdin)))
    elif parsed_args.format == "csv":
        all_input = sys.stdin.read()
        print_transactions(
            parse(lex(all_input.splitlines(True))),
            default_hourly_rate=parsed_args.rate,
            only_uncleared=parsed_args.only_uncleared,
            account_rates=get_account_rates(all_input))
    elif parsed_args.format == "json":
        print_json(parse(lex(sys.stdin)))
