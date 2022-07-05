from . import directive


class Entry:
    def __init__(
        self, check_in: directive.CheckIn, check_out: directive.CheckOut
    ) -> None:
        self.check_in = check_in
        self.check_out = check_out

    @property
    def duration(self):
        return self.check_out.timestamp - self.check_in.timestamp

    @property
    def account(self):
        return self.check_in.account

    @property
    def task(self):
        return self.check_in.task

    # @classmethod
    # def from_event_pair(cls, checkin, checkout):
    #     if not checkin.is_start or checkout.is_start:
    #         raise ValueError("Bad checking or checkout event provided.")
    #
    #     return cls(
    #         start_timestamp=checkin.timestamp,
    #         duration=checkout.timestamp - checkin.timestamp,
    #         account=checkin.account,
    #         task=checkin.task,
    #         metadata={**checkin.metadata, **checkout.metadata},
    #     )
