# ----------------------------------------------------------------------
# |
# |  Error.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 07:27:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Error object and other functionality useful when working with and creating errors"""

import os

from typing import List, Optional, Type

from dataclasses import dataclass, field, make_dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Region import Region

# TODO: Move this to ../Error.py

# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Error(Interface.Interface):
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
class ErrorException(Exception):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        *errors: Error,
    ):
        self.errors                         = list(errors)

        super(ErrorException, self).__init__("\n".join(str(error) for error in self.errors))


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
