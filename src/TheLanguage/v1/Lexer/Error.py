# ----------------------------------------------------------------------
# |
# |  Error.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-01 14:48:31
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Error object"""

import os

from typing import Optional, Type

from dataclasses import dataclass, field, make_dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Location import Location


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Error(Exception, Interface.Interface):
    location: Location
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
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def CreateError(
    message_template: str,
    **args: Type,
) -> Type[Error]:
    dynamic_fields_class = make_dataclass(
        "DynamicFields",
        args.items(),
        bases=(Error,),
        frozen=True,
        repr=False,
    )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class Final(dynamic_fields_class):  # type: ignore
        MessageTemplate                     = Interface.DerivedProperty(message_template)

    # ----------------------------------------------------------------------

    return Final
