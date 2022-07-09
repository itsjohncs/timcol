from .. import logfile
from . import args
from .views import register, invoice


def render(logs: logfile.LogFile, parsed_args: args.ParsedArgs) -> None:
    if parsed_args.sub_command == "reg":
        register.render(logs)
    elif parsed_args.sub_command == "invoice":
        assert parsed_args.invoice_args is not None
        invoice.render(logs, parsed_args.invoice_args)
    else:
        raise NotImplementedError()
