# ----------------------------------------------------------------------
# |
# |  Target.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-19 08:19:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Target object"""

import os

from semantic_version import Version as SemVer

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Parser.RootParserInfo import RootParserInfo


# ----------------------------------------------------------------------
class Target(Interface.Interface):
    """Abstract base class for a target"""

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def Name(self) -> str:
        """Name of the target"""
        raise Exception("Abstract property")  # pragma: no cover

    @Interface.abstractproperty
    def Version(self) -> SemVer:
        """Version of the target implementation"""
        raise Exception("Abstract property")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Invoke(
        fully_qualified_name: str,
        parser_info: RootParserInfo,
    ) -> None:
        """Invokes the derived Target's functionality with the provided information"""
        raise Exception("Abstract method")  # pragma: no cover
