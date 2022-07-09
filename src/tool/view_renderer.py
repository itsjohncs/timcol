from .. import logfile
from . import args
from .views import register


def render(logs: logfile.LogFile, _parsed_args: args.ParsedArgs) -> None:
    register.render(logs)
