from typing import Tuple
import datetime
import math

from ... import logfile


def render(logs: logfile.LogFile):
    """Prints a human-readable summary of `logs`."""
    total_time = datetime.timedelta(0)
    day_total: Tuple[datetime.date, datetime.timedelta] | None = None
    for entry in logs.entries:
        if (
            day_total is not None
            and entry.check_in.timestamp.date() != day_total[0]
        ):
            pretty_date = day_total[0].strftime("%h %d")
            print(f"{pretty_date} SUBTOTAL\t\t({day_total[1]})")
            day_total = None

        if day_total is None:
            day_total = (entry.check_in.timestamp.date(), datetime.timedelta())

        day_total = (day_total[0], day_total[1] + entry.duration)
        total_time += entry.duration

        pretty_timestamp = datetime.datetime.strftime(
            entry.check_in.timestamp, "%h %d @ %I:%M %p"
        )

        print(
            f"{pretty_timestamp}\t{entry.duration}\t{entry.account}: {entry.task}"
        )

    if logs.pending:
        check_in = logs.pending

        if day_total is None:
            day_total = (check_in.timestamp.date(), datetime.timedelta())

        duration = datetime.datetime.now() - check_in.timestamp
        duration = datetime.timedelta(
            seconds=math.floor(duration.total_seconds())
        )

        day_total = (day_total[0], day_total[1] + duration)
        total_time += duration

        pretty_timestamp = datetime.datetime.strftime(
            check_in.timestamp, "%h %d @ %I:%M %p"
        )

        print(
            f"{pretty_timestamp}\t{duration}*\t{check_in.account}: {check_in.task}"
        )

    if day_total is not None:
        pretty_date = day_total[0].strftime("%h %d")
        print(f"{pretty_date} SUBTOTAL\t\t({day_total[1]})")

    total_time_in_hours = total_time.total_seconds() / 60**2
    print(f"TOTAL TIME: {total_time_in_hours:.2f}h")
