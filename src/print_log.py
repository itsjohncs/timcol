#!/usr/bin/env python3

import argparse
import collections
import datetime
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
    for i in ledger_file:
        checkin_match = CHECKIN_RE.match(i)
        if checkin_match:
            yield Event(
                is_start=True,
                timestamp=datetime.datetime.strptime(
                    checkin_match.group(1), "%Y/%m/%d %H:%M:%S"),
                account=checkin_match.group(2),
                task=checkin_match.group(3),
                note=checkin_match.group(4),
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
    for i in logs:
        total_time += i.duration

        pretty_timestamp = datetime.datetime.strftime(
            i.start_timestamp, "%h %d @ %I:%M %p")
        minutes = i.duration.total_seconds() / 60

        status = " *" if i.is_cleared else ""
        maybe_note = f" ({i.note.strip()})" if i.note else ""
        print(f"{pretty_timestamp}{status}\t{minutes:.1f}m\t{i.account}: "
              f"{i.task}{maybe_note}")

    total_time_in_hours = total_time.total_seconds() / 60 ** 2
    print(f"TOTAL TIME: {total_time_in_hours:.2f}h")


TransactionOptions = collections.namedtuple("TransactionOptions", [
    "hourly_rate",

    # The account that we will deduct time from.
    "income_account",
])


def print_transactions(logs, options):
    """Prints a Ledger transaction for each `Log`."""
    for i in logs:
        date_str = datetime.datetime.strftime(i.start_timestamp, "%Y/%m/%d")
        status = " *" if i.is_cleared else ""
        print(f"{date_str}{status} {i.task}")

        if i.note:
            print(f"    ;{i.note}")
        
        checkin_timestamp = datetime.datetime.strftime(
            i.start_timestamp, "%Y/%m/%d %H:%M:%S")
        print(f"    ; CheckIn: {checkin_timestamp}")

        checkout_timestamp = datetime.datetime.strftime(
            i.start_timestamp + i.duration, "%Y/%m/%d %H:%M:%S")
        print(f"    ; CheckOut: {checkout_timestamp}")

        seconds = i.duration.total_seconds()
        hours = i.duration.total_seconds() / 60 ** 2

        print(f"    {i.account}  ${hours * options.hourly_rate:.2f}")
        print(f"    {options.income_account}"
              f"  {-hours:.4f} HOUR {{=${options.hourly_rate}}}"
              f" @ ${options.hourly_rate}"
              f"  ; {seconds // 60:.0f}m and {seconds % 60:.0f}s")
        print()


def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Prints time entries.")

    subparsers = parser.add_subparsers(title="FORMATS", dest="format")

    subparsers.add_parser("register", help="Human friendly format.")

    # create the parser for the "b" command
    transactions_parser = subparsers.add_parser(
        "transactions", help="Ledger transactions.")


    transactions_parser.add_argument(
        "-a", "--income-account", default="Income:Billable Hours",
        help="Account to deduct time from.")
    transactions_parser.add_argument(
        "-r", "--rate", required=True, type=float,
        help="Hourly rate to bill. Ex: 100")

    return parser.parse_args(args)

if __name__ == "__main__":
    parsed_args = parse_args()
    if parsed_args.format == "register":
        print_register(parse(lex(sys.stdin)))
    elif parsed_args.format == "transactions":
        print_transactions(
            parse(lex(sys.stdin)),
            TransactionOptions(
                income_account=parsed_args.income_account,
                hourly_rate=parsed_args.rate))
