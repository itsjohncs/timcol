import typing
import re

from . import directive
from . import entry
from .logfile import LogFile


def _parse_directive(
    raw_directive: str,
) -> directive.CheckIn | directive.CheckOut | None:
    for t in (directive.CheckIn, directive.CheckOut):
        maybe_parsed = t.parse(raw_directive)
        if maybe_parsed:
            return maybe_parsed

    return None


def _parse_all_directives(
    f: typing.TextIO,
) -> typing.Iterable[directive.CheckIn | directive.CheckOut]:
    current_directive = None
    for i in f:
        maybe_directive = _parse_directive(i)
        if maybe_directive:
            if current_directive:
                yield current_directive
            current_directive = maybe_directive
            continue

        maybe_metadata = re.match(r"^ {4}; ([^:]+):(.+?)$", i)
        if maybe_metadata:
            current_directive.metadata[
                maybe_metadata.group(1)
            ] = maybe_metadata.group(2)
            continue

    if current_directive:
        yield current_directive


def _parse_all_entries(f: typing.TextIO) -> typing.Iterable[entry.Entry]:
    current_directive: directive.CheckIn | None = None
    for i in _parse_all_directives(f):
        if current_directive is None:
            assert isinstance(
                i, directive.CheckIn
            ), f"Expected CheckIn directive, found {i}"
            current_directive = i
        else:
            assert isinstance(
                i, directive.CheckOut
            ), f"Expected CheckOut directive, found {i}"
            yield entry.Entry(current_directive, i)
            current_directive = None


def parse_file(f: typing.TextIO) -> LogFile:
    return LogFile(list(_parse_all_entries(f)))
