#!/usr/bin/env python3

import collections
import datetime
import re
import sys


EVENT_RE = re.compile(r"^([io]) ([^ ]+ [^ \n]+)(?: (.+?)  (.*))?$", re.MULTILINE)
Event = collections.namedtuple("Event", [
    "is_start",
    "timestamp",
    "account",
    "task",
])


def lex(ledger_file):
    for i in ledger_file:
        match = EVENT_RE.match(i)
        if match:
            yield Event(
                is_start=match.group(1) == "i",
                timestamp=datetime.datetime.strptime(
                    match.group(2), "%Y/%m/%d %H:%M:%S"),
                account=match.group(3),
                task=match.group(4))


Log = collections.namedtuple("Log", [
    "start_timestamp",
    "duration",
    "account",
    "task",
])


def parse(events):
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
                task=unresolved_event.task)
            unresolved_event = None


def print_logs(logs):
    total_time = datetime.timedelta(0)
    for i in logs:
        total_time += i.duration

        pretty_timestamp = datetime.datetime.strftime(
            i.start_timestamp, "%h %d @ %I:%M %p")
        minutes = i.duration.total_seconds() / 60
        print(f"{pretty_timestamp}\t{minutes:.1f}m\t{i.account}: {i.task}")

    total_time_in_hours = total_time.total_seconds() / 60 ** 2
    print(f"TOTAL TIME: {total_time_in_hours:.2f}h")


if __name__ == "__main__":
    print_logs(parse(lex(sys.stdin)))
