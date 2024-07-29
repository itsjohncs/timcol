from . import entry, directive


class LogFile:
    def __init__(
        self, entries: list[entry.Entry], pending: directive.CheckIn | None
    ) -> None:
        self.entries = entries
        self.pending = pending
