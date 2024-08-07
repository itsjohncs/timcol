"""
This type stub file was generated by pyright.
"""

"""
This module supports customized (aka special or specified) template loading.

"""

class SpecLoader:
    """
    Supports loading custom-specified templates (from TemplateSpec instances).

    """
    def __init__(self, loader=...) -> None: ...
    def load(self, spec):  # -> str:
        """
        Find and return the template associated to a TemplateSpec instance.

        Returns the template as a unicode string.

        Arguments:

          spec: a TemplateSpec instance.

        """
        ...
