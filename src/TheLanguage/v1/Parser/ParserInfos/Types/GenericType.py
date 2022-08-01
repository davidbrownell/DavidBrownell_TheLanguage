# ----------------------------------------------------------------------
# |
# |  GenericType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-25 13:48:42
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

from typing import TYPE_CHECKING

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ..ParserInfo import ParserInfo

    if TYPE_CHECKING:
        from .ConcreteType import ConcreteType  # pylint: disable=unused-import


# ----------------------------------------------------------------------
class GenericType(Interface.Interface):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: ParserInfo,
        is_default_initializable: bool,
    ):
        self._parser_info                   = parser_info
        self.is_default_initializable       = is_default_initializable

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def parser_info(self):
        """Returns the parser info with the correct type"""
        raise Exception("Abstract property")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def CreateConcreteType(
        expression_parser_info: ExpressionParserInfo,
    ) -> "ConcreteType":
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    def CreateDefaultConcreteType(self) -> "ConcreteType":
        assert self.is_default_initializable
        return self._CreateDefaultConcreteTypeImpl()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def _CreateDefaultConcreteTypeImpl() -> "ConcreteType":
        raise Exception("Abstract method")  # pragma: no cover
