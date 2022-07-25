# ----------------------------------------------------------------------
# |
# |  GenericType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-22 14:25:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GenericType object"""

import os

from typing import Generator, Optional, TYPE_CHECKING

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo

    from ..ParserInfo import ParserInfo

    if TYPE_CHECKING:
        from .ConcreteType import ConcreteType  # pylint: disable=unused-import


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class GenericType(Interface.Interface):
    """Type that has not yet been associated with a set of template parameters"""

    # TODO: Create a wrapper, where the actual type can only be used within a generator, where
    #       any exceptions are decorated with all of the aliases. Should be impossible to use the
    #       underlying type outside of that generator.

    # ----------------------------------------------------------------------
    _definition_parser_info: ParserInfo

    # ----------------------------------------------------------------------
    @property
    def definition_parser_info(self) -> ParserInfo:
        return self._definition_parser_info

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def EnumAliases(self) -> Generator["GenericType", None, None]:
        yield self

    # ----------------------------------------------------------------------
    def ResolveAliases(self) -> "GenericType":
        *_, last = self.EnumAliases()
        return last

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def CreateConcreteType() -> "ConcreteType":
        raise Exception("Abstract method")  # pragma: no cover
