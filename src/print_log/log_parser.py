import datetime
import re

# pylint: disable=too-few-public-methods


class Event:
    CHECKIN_RE = re.compile(
        r"^i ([^ ]+ [^ ]+) (.+?)(?:  ([^;]*?)(?:  ;(.*?))?)?$", re.MULTILINE
    )
    CHECKOUT_RE = re.compile(r"^([oO]) ([^ ]+? [^ ]+?)$", re.MULTILINE)

    def __init__(self, *, is_start, timestamp, account, task, note, cleared):
        self.is_start = is_start
        self.timestamp = timestamp
        self.account = account
        self.task = task
        self.note = note
        self.cleared = cleared

    @staticmethod
    def _strip_or_none(val):
        if val is None:
            return None

        return val.strip()

    @classmethod
    def from_string(cls, string):
        checkin_match = cls.CHECKIN_RE.match(string)
        if checkin_match:
            return Event(
                is_start=True,
                timestamp=datetime.datetime.strptime(
                    checkin_match.group(1), "%Y/%m/%d %H:%M:%S"
                ),
                account=checkin_match.group(2),
                task=checkin_match.group(3),
                note=cls._strip_or_none(checkin_match.group(4)),
                cleared=None,
            )

        checkout_match = cls.CHECKOUT_RE.match(string)
        if checkout_match:
            return Event(
                is_start=False,
                timestamp=datetime.datetime.strptime(
                    checkout_match.group(2), "%Y/%m/%d %H:%M:%S"
                ),
                account=None,
                task=None,
                note=None,
                cleared=checkout_match.group(1) == "O",
            )

        return None


def events_from_lines(lines):
    """Converts lines of text into a stream of `Event`s.

    One checkin or checkout will be one event. No attempt is made to pair them
    up yet. Any line with unrecognized syntax will be ignored.
    """
    for i in lines:
        event = Event.from_string(i)
        if event:
            yield event


class Log:
    def __init__(
        self, *, start_timestamp, duration, account, task, note, is_cleared
    ):
        self.start_timestamp = start_timestamp
        self.duration = duration
        self.account = account
        self.task = task
        self.note = note
        self.is_cleared = is_cleared

    @classmethod
    def from_event_pair(cls, checkin, checkout):
        if not checkin.is_start or checkout.is_start:
            raise ValueError("Bad checking or checkout event provided.")

        return Log(
            start_timestamp=checkin.timestamp,
            duration=checkout.timestamp - checkin.timestamp,
            account=checkin.account,
            task=checkin.task,
            note=checkin.note,
            is_cleared=checkout.cleared,
        )


def logs_from_events(events):
    """Converts an iterable of `Event`s into an iterable of `Log`s.

    A `Log` represents a checkin and checkout. If there is an unpaired
    checkin remaining at the end of the iterable, it will be ignored.
    """
    unresolved_event = None
    for i in events:
        if unresolved_event is None:
            assert i.is_start
            unresolved_event = i
        else:
            assert not i.is_start
            yield Log.from_event_pair(unresolved_event, i)
            unresolved_event = None


def parse_lines(lines):
    return logs_from_events(events_from_lines(lines))
