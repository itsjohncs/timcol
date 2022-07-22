from typing import Tuple
import datetime
import math

from ... import logfile
from ...logfile.entry import Entry


def floor_delta(delta: datetime.timedelta) -> datetime.timedelta:
    return datetime.timedelta(seconds=math.floor(delta.total_seconds()))


def render(logs: logfile.LogFile):
    """Prints a human-readable summary of `logs`."""
    total_time = datetime.timedelta(0)
    day_total: Tuple[datetime.date, datetime.timedelta] | None = None
    for entry in [*logs.entries, logs.pending]:
        if entry is None:
            continue

        if isinstance(entry, Entry):
            check_in = entry.check_in
            duration = entry.duration
            status = ""
        else:
            check_in = entry
            duration = floor_delta(datetime.datetime.now() - check_in.timestamp)
            status = "*"

        if day_total is not None and check_in.timestamp.date() != day_total[0]:
            pretty_date = day_total[0].strftime("%h %d")
            print(f"{pretty_date} SUBTOTAL\t\t({day_total[1]})")
            day_total = None

        if day_total is None:
            day_total = (check_in.timestamp.date(), datetime.timedelta())

        day_total = (day_total[0], day_total[1] + duration)
        total_time += duration

        pretty_timestamp = datetime.datetime.strftime(
            check_in.timestamp, "%h %d @ %I:%M %p"
        )

        print(
            f"{pretty_timestamp}\t{duration}{status}\t{entry.account}: {entry.task}"
        )

    if day_total is not None:
        pretty_date = day_total[0].strftime("%h %d")
        print(f"{pretty_date} SUBTOTAL\t\t({day_total[1]})")

    total_time_in_hours = total_time.total_seconds() / 60**2
    print(f"TOTAL TIME: {total_time_in_hours:.2f}h")
