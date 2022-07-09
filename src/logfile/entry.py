import collections
from datetime import timedelta
from typing import ChainMap

from . import directive


class Entry:
    def __init__(
        self, check_in: directive.CheckIn, check_out: directive.CheckOut
    ) -> None:
        self.check_in = check_in
        self.check_out = check_out

    @property
    def duration(self) -> timedelta:
        return self.check_out.timestamp - self.check_in.timestamp

    @property
    def account(self) -> str:
        return self.check_in.account

    @property
    def task(self) -> str:
        return self.check_in.task

    @property
    def metadata(self) -> ChainMap[str, str]:
        return collections.ChainMap(
            self.check_in.metadata, self.check_out.metadata
        )
