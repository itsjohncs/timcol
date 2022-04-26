import datetime
import re

# pylint: disable=too-few-public-methods

METADATA_RE = re.compile(r"^    ; ([^:]+):(.+?)$")


def line_to_metadata(line):
    match = METADATA_RE.match(line)
    if match:
        return (match.group(1), match.group(2))

    return None


class Event:
    CHECKIN_RE = re.compile(
        r"^i ([^ ]+ [^ ]+ (?:AM|PM)) (.+?)  (.+?)$", re.MULTILINE
    )
    CHECKOUT_RE = re.compile(r"^o ([^ ]+ [^ ]+ (?:AM|PM))$", re.MULTILINE)

    def __init__(self, *, is_start, timestamp, account, task, metadata=None):
        self.is_start = is_start
        self.timestamp = timestamp
        self.account = account
        self.task = task
        self.metadata = metadata or {}

    @classmethod
    def from_directive(cls, string):
        """Creates an event from the directive `string`.

        Example of a directive:

        ```
        i 2021/10/13 01:38:00 PM Foo  Initial phone call
        ```

        This does not deal with any of the metadata in following lines.
        """
        checkin_match = cls.CHECKIN_RE.match(string)
        if checkin_match:
            return Event(
                is_start=True,
                timestamp=datetime.datetime.strptime(
                    checkin_match.group(1), "%Y/%m/%d %I:%M:%S %p"
                ),
                account=checkin_match.group(2),
                task=checkin_match.group(3),
            )

        checkout_match = cls.CHECKOUT_RE.match(string)
        if checkout_match:
            return Event(
                is_start=False,
                timestamp=datetime.datetime.strptime(
                    checkout_match.group(1), "%Y/%m/%d %I:%M:%S %p"
                ),
                account=None,
                task=None,
            )

        return None


def events_from_lines(lines):
    """Converts lines of text into a stream of `Event`s.

    One checkin or checkout will be one event. No attempt is made to pair them
    up yet. Any line with unrecognized syntax will be ignored.
    """
    last_event = None
    for i in lines:
        event = Event.from_directive(i)
        if event:
            if last_event:
                yield last_event

            last_event = event

        metadata = line_to_metadata(i)
        if metadata:
            key, value = metadata
            last_event.metadata[key] = value

    if last_event:
        yield last_event


class Log:
    def __init__(self, *, start_timestamp, duration, account, task, metadata):
        self.start_timestamp = start_timestamp
        self.duration = duration
        self.account = account
        self.task = task
        self.metadata = metadata

    @classmethod
    def from_event_pair(cls, checkin, checkout):
        if not checkin.is_start or checkout.is_start:
            raise ValueError("Bad checking or checkout event provided.")

        return Log(
            start_timestamp=checkin.timestamp,
            duration=checkout.timestamp - checkin.timestamp,
            account=checkin.account,
            task=checkin.task,
            metadata={**checkin.metadata, **checkout.metadata},
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
