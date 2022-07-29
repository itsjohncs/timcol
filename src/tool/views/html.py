import datetime
import sys
from typing import List, Dict
import importlib.resources

import pystache

from ... import logfile
from ..args import ParsedArgs


def total_hours(duration: datetime.timedelta) -> float:
    return duration.total_seconds() / 60**2


def render(logs: logfile.LogFile, args: ParsedArgs.HtmlArgs) -> None:
    tasks: List[Dict[str, str]] = []
    total_cost = 0
    for i in logs.entries:
        seconds = i.duration.total_seconds()

        base_rate = (
            float(i.metadata.get("Rate", args.rate))
            if args.allow_rate_override
            else args.rate
        )
        multiplier = float(i.metadata.get("Multiplier", 1.0))
        rate = base_rate * multiplier

        cost = total_hours(i.duration) * rate
        total_cost += cost

        tasks.append(
            {
                "date": i.check_in.timestamp.strftime("%Y/%m/%d"),
                "duration": (
                    f"{seconds // 60 // 60:02.0f}:"
                    f"{(seconds // 60) % 60:02.0f}:"
                    f"{seconds % 60:02.0f}"
                ),
                "hourly_rate": f"${rate:.2f}",
                "cost": f"${cost:.2f}",
                "description": i.task,
            }
        )

    data = {
        "date": datetime.date.today().strftime("%Y/%m/%d"),
        "cost": f"${total_cost:,.2f}",
        "tasks": tasks,
    }

    with importlib.resources.open_text(
        __package__, "invoice_template.htm.mustache"
    ) as template:
        sys.stdout.write(pystache.render(template.read(), data))
