from typing import Tuple, List, Dict
import datetime
import math
from tabulate import tabulate

from ..args import ParsedArgs

from ... import logfile
from ...logfile.entry import Entry
from ._shared import pretty_duration


def floor_delta(delta: datetime.timedelta) -> datetime.timedelta:
    return datetime.timedelta(seconds=math.floor(delta.total_seconds()))


def scale(duration: datetime.timedelta, multiplier: float) -> datetime.timedelta:
    return datetime.timedelta(seconds=duration.total_seconds() * multiplier)


def render(logs: logfile.LogFile, args: ParsedArgs.RegisterArgs):
    """Prints a human-readable summary of `logs`."""
    total_time = datetime.timedelta(0)
    day_total: Tuple[datetime.date, datetime.timedelta] | None = None
    rows: List[Dict[str, str]] = []
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

        multiplier = float(entry.metadata.get("Multiplier", 1.0))

        if args.show_unscaled_time:
            scaled_duration = duration
        else:
            scaled_duration = floor_delta(scale(duration, multiplier))

        if day_total is not None and check_in.timestamp.date() != day_total[0]:
            pretty_date = day_total[0].strftime("%h %d")
            rows.append(
                {
                    "timestamp": f"{pretty_date} SUBTOTAL",
                    "duration": pretty_duration(day_total[1]),
                }
            )
            rows.append({})
            day_total = None

        if day_total is None:
            day_total = (check_in.timestamp.date(), datetime.timedelta())

        day_total = (day_total[0], day_total[1] + scaled_duration)
        total_time += scaled_duration

        pretty_timestamp = datetime.datetime.strftime(
            check_in.timestamp, "%h %d @ %I:%M %p"
        )

        if multiplier == 1.0:
            pretty_multiplier = ""
        elif args.show_unscaled_time:
            pretty_multiplier = f" * {multiplier:1.1f}"
        else:
            pretty_multiplier = f" / {multiplier:1.1f}"

        rows.append(
            {
                "timestamp": pretty_timestamp,
                "duration": f"{pretty_duration(scaled_duration)}{pretty_multiplier}{status}",
                "account": entry.account,
                "task": entry.task,
            }
        )

    if day_total is not None:
        pretty_date = day_total[0].strftime("%h %d")
        rows.append(
            {
                "timestamp": f"{pretty_date} SUBTOTAL",
                "duration": pretty_duration(day_total[1]),
            }
        )

    rows.append(
        {
            "timestamp": "TOTAL TIME",
            "duration": pretty_duration(total_time),
        }
    )

    print(tabulate(rows, headers="keys"))
