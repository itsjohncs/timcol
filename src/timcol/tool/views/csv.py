import datetime
import csv
import sys

from ... import logfile
from ..args import ParsedArgs
from ._shared import pretty_duration


def total_hours(duration: datetime.timedelta) -> float:
    return duration.total_seconds() / 60**2


def render(logs: logfile.LogFile, args: ParsedArgs.CsvArgs) -> None:
    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=[
            "Date",
            "Duration",
            "Rate",
            "Cost",
            "Description",
        ],
    )
    writer.writeheader()

    total_cost = 0
    for i in logs.entries:
        base_rate = (
            float(i.metadata.get("Rate", args.rate))
            if args.allow_rate_override
            else args.rate
        )
        multiplier = float(i.metadata.get("Multiplier", 1.0))
        rate = base_rate * multiplier

        cost = total_hours(i.duration) * rate
        total_cost += cost

        writer.writerow(
            {
                "Date": datetime.datetime.strftime(i.check_in.timestamp, "%Y/%m/%d"),
                "Duration": pretty_duration(i.duration),
                "Rate": f"${rate:.2f}",
                "Cost": f"${cost:.2f}",
                "Description": i.task,
            }
        )

    writer.writerow(
        {
            "Cost": f"${total_cost:.2f}",
            "Description": "TOTAL COST",
        }
    )
