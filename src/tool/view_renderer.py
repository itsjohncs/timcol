from .. import logfile
from . import args
from .views import register, csv, html


def render(logs: logfile.LogFile, parsed_args: args.ParsedArgs) -> None:
    if parsed_args.sub_command == "reg":
        register.render(logs)
    elif parsed_args.sub_command == "csv":
        assert parsed_args.csv_args is not None
        csv.render(logs, parsed_args.csv_args)
    elif parsed_args.sub_command == "html":
        assert parsed_args.html_args is not None
        html.render(logs, parsed_args.html_args)
    else:
        raise NotImplementedError()
