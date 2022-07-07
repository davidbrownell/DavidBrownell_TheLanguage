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

from typing import Any, List, TYPE_CHECKING, Union

from dataclasses import dataclass

import CommonEnvironment

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

        from .Statements.ConcreteInfo.ConcreteClass import ConcreteClass                    # pylint: disable=unused-import


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
@dataclass(frozen=True)
class ConcreteClassType(Type):
    # ----------------------------------------------------------------------
    _concrete_class: Any

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "ClassStatementParserInfo", self.parser_info
        assert self._concrete_class.__class__.__name__ == "ConcreteClass", self._concrete_class

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "ClassStatementParserInfo":
        return self._parser_info  # type: ignore

    @property
    def concrete_class(self) -> "ConcreteClass":
        return self._concrete_class  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ConcreteTypeAliasType(Type):
    # ----------------------------------------------------------------------
    resolved_type: Union[ConcreteClassType, "ConcreteTypeAliasType"]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "TypeAliasStatementParserInfo", self._parser_info

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "TypeAliasStatementParserInfo":
        return self._parser_info  # type: ignore


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
