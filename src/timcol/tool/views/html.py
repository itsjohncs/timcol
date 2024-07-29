import datetime
import sys
from typing import List, Dict
import importlib.resources

import pystache

from ... import logfile
from ..args import ParsedArgs
from ._shared import pretty_duration


def total_hours(duration: datetime.timedelta) -> float:
    return duration.total_seconds() / 60**2


def render(logs: logfile.LogFile, args: ParsedArgs.HtmlArgs) -> None:
    tasks: List[Dict[str, str]] = []
    total_cost = 0
    total_time = datetime.timedelta()
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

        total_time += i.duration

        tasks.append(
            {
                "date": i.check_in.timestamp.strftime("%Y/%m/%d"),
                "duration": pretty_duration(i.duration),
                "hourly_rate": f"${rate:.2f}",
                "cost": f"${cost:.2f}",
                "description": i.task,
            }
        )

    data = {
        "date": datetime.date.today().strftime("%Y/%m/%d"),
        "cost": f"${total_cost:,.2f}",
        "duration": pretty_duration(total_time),
        "tasks": tasks,
    }

    assert __package__
    with importlib.resources.open_text(
        __package__, "invoice_template.htm.mustache"
    ) as template:
        sys.stdout.write(pystache.render(template.read(), data))
