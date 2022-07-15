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
        from .EntityResolver import EntityResolver                                                  # pylint: disable=unused-import

        from .Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo                  # pylint: disable=unused-import
        from .Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo                # pylint: disable=unused-import
        from .Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo            # pylint: disable=unused-import

        from .Statements.ClassStatementParserInfo import ClassStatementParserInfo                   # pylint: disable=unused-import
        from .Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo # pylint: disable=unused-import
        from .Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo           # pylint: disable=unused-import

        from .Statements.ConcreteClass import ConcreteClass                                         # pylint: disable=unused-import
        from .Statements.ConcreteFuncDefinition import ConcreteFuncDefinition                       # pylint: disable=unused-import


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Type(Interface.Interface):
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
class ConcreteType(Type):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Finalize(
        entity_resolver: "EntityResolver",
    ) -> None:
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ClassType(ConcreteType):
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
    @Interface.override
    def Finalize(
        self,
        entity_resolver: "EntityResolver",
    ) -> None:
        self.concrete_class.Finalize(self.parser_info, entity_resolver)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FuncDefinitionType(ConcreteType):
    # ----------------------------------------------------------------------
    concrete_func_definition: "ConcreteFuncDefinition"

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "FuncDefinitionStatementParserInfo", self.parser_info
        assert self.concrete_func_definition.__class__.__name__ == "ConcreteFuncDefinition", self.concrete_func_definition

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "FuncDefinitionStatementParserInfo":
        return self._parser_info  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def Finalize(
        self,
        entity_resolver: "EntityResolver",
    ) -> None:
        self.concrete_func_definition.Finalize(entity_resolver)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeAliasType(ConcreteType):
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
    @Interface.override
    def Finalize(
        self,
        entity_resolver: "EntityResolver",
    ) -> None:
        if isinstance(self.resolved_type, ConcreteType):
            self.resolved_type.Finalize(entity_resolver)


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
