from . import entry


class LogFile:
    def __init__(self, entries: list[entry.Entry]) -> None:
        self.entries = entries
