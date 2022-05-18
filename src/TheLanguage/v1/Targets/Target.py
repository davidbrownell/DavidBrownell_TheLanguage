# ----------------------------------------------------------------------
# |
# |  Target.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 10:39:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Target object"""

import os

from dataclasses import dataclass

from typing import Generator, List

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Parser.Parser import RootParserInfo


# ----------------------------------------------------------------------
class Target(Interface.Interface):
    """Abstract base class for an object that can process verified ParserInfo objects"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class EnumResult(ObjectReprImplBase):
        fully_qualified_name: str
        output_name: str
        content: str

        # ----------------------------------------------------------------------
        @classmethod
        def Create(cls, *args, **kwargs):
            """\
            This hack avoids pylint warnings associated with invoking dynamically
            generated constructors with too many methods.
            """
            return cls(*args, **kwargs)

        # ----------------------------------------------------------------------
        def __post_init__(self):
            ObjectReprImplBase.__init__(self)

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def name(self) -> str:
        raise Exception("Abstract property")  # pragma: no cover

    @Interface.abstractproperty
    def configurations(self) -> List[str]:
        raise Exception("Abstract property")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def EnumOutputs() -> Generator["Target.EnumResult", None, None]:
        """Enumerates the output of every input provided to `Invoke`"""
        raise Exception("Abstract method")  # pragma: no cover
