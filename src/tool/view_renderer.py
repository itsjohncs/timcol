import argparse

from . import args
from .views import register
import logfile


def render(logs: logfile.LogFile, parsed_args: args.ParsedArgs) -> None:
    register.render(logs)
