# ----------------------------------------------------------------------
# |
# |  Diagnostics.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-03-01 09:44:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types useful when producing diagnostics"""

import os

from typing import Dict, List, Optional, Type

from dataclasses import dataclass, field, make_dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Region import Region

# TODO: Move this to ./Parser

# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _Diagnostic(Interface.Interface):
    """Base class for different diagnostic types"""

    region: Region
    _message: Optional[str]                 = field(init=False, default_factory=lambda: None)

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __str__(self):
        if self._message is None:
            object.__setattr__(self, "_message", self.MessageTemplate.format(**self.__dict__))

        return self._message

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def MessageTemplate(self):
        """Template used when generating the exception string"""
        raise Exception("Abstract property")  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True)  # pylint: disable=abstract-method
class Error(_Diagnostic):
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True)  # pylint: disable=abstract-method
class Warning(_Diagnostic):
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True)  # pylint: disable=abstract-method
class Info(_Diagnostic):
    pass


# ----------------------------------------------------------------------
class Diagnostics(ObjectReprImplBase):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.errors: List[Error]            = []
        self.warnings: List[Warning]        = []
        self.infos: List[Info]              = []

        ObjectReprImplBase.__init__(self)


# ----------------------------------------------------------------------
class DiagnosticsError(Exception):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        diagnostics: Diagnostics,
    ):
        super(DiagnosticsError, self).__init__("\n".join([str(diagnostic) for diagnostic in diagnostics]))

        self.diagnostics                    = diagnostics


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def CreateError(
    message_template: str,
    **args: Type,
) -> Type[Error]:
    return _CreateDiagnosticImpl(Error, message_template, args)


# ----------------------------------------------------------------------
def CreateWarning(
    message_template: str,
    **args: Type,
) -> Type[Warning]:
    return _CreateDiagnosticImpl(Warning, message_template, args)


# ----------------------------------------------------------------------
def CreateInfo(
    message_template: str,
    **args: Type,
) -> Type[Info]:
    return _CreateDiagnosticImpl(Info, message_template, args)


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
# ----------------------------------------------------------------------
def _CreateDiagnosticImpl(
    base_type: Type,
    message_template: str,
    args: Dict[str, Type],
):
    dynamic_fields_class = make_dataclass(
        "DynamicFields",
        args.items(),
        bases=(base_type, ),
        frozen=True,
    )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class Final(dynamic_fields_class):      # type: ignore
        MessageTemplate                     = Interface.DerivedProperty(message_template)

    # ----------------------------------------------------------------------

    return Final
