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

from typing import Any, List, Generator, Optional, TYPE_CHECKING

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ParserInfo import ParserInfo
    from .Traits.NamedTrait import NamedTrait

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
@dataclass(frozen=True, eq=False)
class Type(Interface.Interface):
    # ----------------------------------------------------------------------
    _parser_info: ParserInfo

    _entity_resolver: Optional["EntityResolver"]        = field(init=False, default=None)
    _instantiated_class: Optional["ClassType"]          = field(init=False, default=None)

    _is_initialized: bool                               = field(init=False, default=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert isinstance(self._parser_info, NamedTrait), self._parser_info

    # ----------------------------------------------------------------------
    def Init(
        self,
        entity_resolver: "EntityResolver",
        instantiated_class: Optional["ClassType"],
    ) -> None:
        # There is a chicken and egg problem here, which results in the need for 2-phase
        # construction (yuck!). The EntityResolver needs the created type to set its context,
        # and this type needs that entity resolver.
        assert self._is_initialized is False

        object.__setattr__(self, "_entity_resolver", entity_resolver)
        object.__setattr__(self, "_instantiated_class", instantiated_class)

        object.__setattr__(self, "_is_initialized", True)

    # ----------------------------------------------------------------------
    def __eq__(
        self,
        other: "Type",
    ) -> bool:
        assert isinstance(self._parser_info, NamedTrait), self._parser_info
        assert isinstance(other._parser_info, NamedTrait), other._parser_info  # pylint: disable=protected-access

        return (
            self._parser_info.name == other._parser_info.name  # pylint: disable=protected-access
            and self._parser_info.translation_unit__ == other._parser_info.translation_unit__  # pylint: disable=protected-access
        )

    # ----------------------------------------------------------------------
    def __ne__(
        self,
        other: "Type",
    ) -> bool:
        return not self == other

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> ParserInfo:
        return self._parser_info

    @property
    def entity_resolver(self) -> "EntityResolver":
        assert self._is_initialized
        assert self._entity_resolver is not None
        return self._entity_resolver

    @property
    def instantiated_class(self) -> Optional["ClassType"]:
        assert self._is_initialized
        return self._instantiated_class

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def EnumAliases(self) -> Generator["Type", None, None]:
        yield self

    # ----------------------------------------------------------------------
    def ResolveAliases(self) -> "Type":
        *_, last = self.EnumAliases()
        return last

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Finalize() -> None:
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
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
    @Interface.override
    def Finalize(self) -> None:
        self.FinalizePass1()
        self.FinalizePass2()

    # ----------------------------------------------------------------------
    def FinalizePass1(self) -> None:
        assert self.instantiated_class is not None
        self.concrete_class.FinalizePass1(self)

    # ----------------------------------------------------------------------
    def FinalizePass2(self) -> None:
        assert self.instantiated_class is not None
        self.concrete_class.FinalizePass2(self)


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class FuncDefinitionType(Type):
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
    def Finalize(self) -> None:
        self.concrete_func_definition.Finalize(self)


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
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
    @Interface.override
    def Finalize(self) -> None:
        self.resolved_type.Finalize()


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class NoneType(Type):
    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "NoneExpressionParserInfo", self.parser_info

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "NoneExpressionParserInfo":
        return self._parser_info  # type: ignore

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Finalize() -> None:
        # Nothing to do here
        pass


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
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
    @Interface.override
    def Finalize(self) -> None:
        for the_type in self.types:
            the_type.Finalize()


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
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

    # ----------------------------------------------------------------------
    @Interface.override
    def Finalize(self) -> None:
        for the_type in self.types:
            the_type.Finalize()
