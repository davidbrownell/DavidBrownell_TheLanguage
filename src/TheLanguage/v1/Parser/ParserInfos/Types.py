# ----------------------------------------------------------------------
# |
# |  Types.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-07 14:28:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality used to define types"""

import os

from typing import Any, List, Generator, TYPE_CHECKING, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ParserInfo import ParserInfo

    if TYPE_CHECKING:
        from .Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo          # pylint: disable=unused-import
        from .Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo        # pylint: disable=unused-import
        from .Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo    # pylint: disable=unused-import

        from .Statements.ClassStatementParserInfo import ClassStatementParserInfo           # pylint: disable=unused-import
        from .Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo   # pylint: disable=unused-import

        from .Statements.ConcreteClass import ConcreteClass                 # pylint: disable=unused-import


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Type(object):
    # ----------------------------------------------------------------------
    _parser_info: ParserInfo

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> ParserInfo:
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def EnumAliases(self) -> Generator["Type", None, None]:
        yield self

    # ----------------------------------------------------------------------
    def ResolveAliases(self) -> "Type":
        *_, last = self.EnumAliases()
        return last


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ClassType(Type):
    # ----------------------------------------------------------------------
    concrete_class: "ConcreteClass"

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "ClassStatementParserInfo", self.parser_info
        assert self.concrete_class.__class__.__name__ == "ConcreteClass", self.concrete_class

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "ClassStatementParserInfo":
        return self._parser_info  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeAliasType(Type):
    # ----------------------------------------------------------------------
    resolved_type: Type

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "TypeAliasStatementParserInfo", self._parser_info

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "TypeAliasStatementParserInfo":
        return self._parser_info  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumAliases(self) -> Generator["Type", None, None]:
        yield self
        yield from self.resolved_type.EnumAliases()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NoneType(Type):
    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "NoneExpressionParserInfo", self.parser_info

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "NoneExpressionParserInfo":
        return self._parser_info  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TupleType(Type):
    # ----------------------------------------------------------------------
    types: List[Type]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "TupleExpressionParserInfo", self.parser_info

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "TupleExpressionParserInfo":
        return self._parser_info  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class VariantType(Type):
    # ----------------------------------------------------------------------
    types: List[Type]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "VariantExpressionParserInfo", self.parser_info

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "VariantExpressionParserInfo":
        return self._parser_info  # type: ignore
