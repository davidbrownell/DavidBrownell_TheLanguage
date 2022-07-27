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
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...ParserInfos.ParserInfo import ParserInfo

    if TYPE_CHECKING:
        from .ConcreteType import ConcreteType  # pylint: disable=unused-import


# ----------------------------------------------------------------------
class GenericType(Interface.Interface):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: ParserInfo,
    ):
        self._parser_info                    = parser_info

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def parser_info(self):
        """Returns the parser info with the correct type"""
        raise Exception("Abstract property")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def IsSameType(
        other: "GenericType",
    ) -> bool:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def IsDefaultInitializable() -> bool:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def CreateConcreteType(
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> "ConcreteType":
        raise Exception("Abstract method")  # pragma: no cover
