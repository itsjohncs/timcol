import datetime

import logfile


def render(logs: logfile.LogFile):
    """Prints a human-readable summary of `logs`."""
    total_time = datetime.timedelta(0)
    for entry in logs.entries:
        total_time += entry.duration

        pretty_timestamp = datetime.datetime.strftime(
            entry.check_in.timestamp, "%h %d @ %I:%M %p"
        )

        seconds = entry.duration.total_seconds()
        pretty_duration = f"{seconds // 60:.0f}m.{seconds % 60:.0f}s"

        print(
            f"{pretty_timestamp}\t{pretty_duration}\t{entry.account}: {entry.task}"
        )

    total_time_in_hours = total_time.total_seconds() / 60**2
    print(f"TOTAL TIME: {total_time_in_hours:.2f}h")
