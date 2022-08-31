import datetime


def pretty_duration(duration: datetime.timedelta) -> str:
    sec = duration.total_seconds()
    return f"{sec // 60**2:01.0f}:{sec // 60 % 60:02.0f}:{sec % 60:02.0f}"
