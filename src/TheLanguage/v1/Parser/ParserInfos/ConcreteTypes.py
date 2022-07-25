# ----------------------------------------------------------------------
# |
# |  ConcreteTypes.py
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
"""Functionality used to define concrete types"""

import os

from typing import List, Generator, TYPE_CHECKING

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
    from .Traits.NamedTrait import NamedTrait

    if TYPE_CHECKING:
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
class ConcreteType(Interface.Interface):
    # TODO: Create a wrapper, where the actual type can only be used within a generator, where
    #       any exceptions are decorated with all of the aliases. Should be impossible to use the
    #       underlying type outside of that generator.

    # ----------------------------------------------------------------------
    _parser_info: ParserInfo

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert isinstance(self._parser_info, NamedTrait), self._parser_info

    # ----------------------------------------------------------------------
    def __eq__(
        self,
        other: "ConcreteType",
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
        other: "ConcreteType",
    ) -> bool:
        return not self == other

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> ParserInfo:
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def EnumAliases(self) -> Generator["ConcreteType", None, None]:
        yield self

    # ----------------------------------------------------------------------
    def ResolveAliases(self) -> "ConcreteType":
        *_, last = self.EnumAliases()
        return last

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def FinalizePass1() -> None:
        """Finalization for types"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def FinalizePass2() -> None:
        """Finalization for functions and methods"""
        raise Exception("Abstract method")  # pragma: no cover

    # BugBug: CreateConstrainedType


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConcreteClassType(ConcreteType):
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
    def FinalizePass1(self) -> None:
        self.concrete_class.FinalizePass1(self)

    # ----------------------------------------------------------------------
    def FinalizePass2(self) -> None:
        self.concrete_class.FinalizePass2(self)


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConcreteFuncDefinitionType(ConcreteType):
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
    def FinalizePass1(self) -> None:
        self.concrete_func_definition.FinalizePass1(self)

    # ----------------------------------------------------------------------
    @Interface.override
    def FinalizePass2(self) -> None:
        self.concrete_func_definition.FinalizePass2(self)


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConcreteTypeAliasType(ConcreteType):
    # ----------------------------------------------------------------------
    resolved_type: ConcreteType

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "TypeAliasStatementParserInfo", self._parser_info

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "TypeAliasStatementParserInfo":
        return self._parser_info  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumAliases(self) -> Generator["ConcreteType", None, None]:
        yield self
        yield from self.resolved_type.EnumAliases()

    # ----------------------------------------------------------------------
    @Interface.override
    def FinalizePass1(self) -> None:
        self.resolved_type.FinalizePass1()

    # ----------------------------------------------------------------------
    @Interface.override
    def FinalizePass2(self) -> None:
        self.resolved_type.FinalizePass2()


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConcreteNoneType(ConcreteType):
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
    def FinalizePass1() -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def FinalizePass2() -> None:
        # Nothing to do here
        pass


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConcreteTupleType(ConcreteType):
    # ----------------------------------------------------------------------
    types: List[ConcreteType]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "TupleExpressionParserInfo", self.parser_info

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "TupleExpressionParserInfo":
        return self._parser_info  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def FinalizePass1(self) -> None:
        for the_type in self.types:
            the_type.FinalizePass1()

    # ----------------------------------------------------------------------
    @Interface.override
    def FinalizePass2(self) -> None:
        for the_type in self.types:
            the_type.FinalizePass2()


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConcreteVariantType(ConcreteType):
    # ----------------------------------------------------------------------
    types: List[ConcreteType]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self._parser_info.__class__.__name__ == "VariantExpressionParserInfo", self.parser_info

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> "VariantExpressionParserInfo":
        return self._parser_info  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def FinalizePass1(self) -> None:
        for the_type in self.types:
            the_type.FinalizePass1()

    # ----------------------------------------------------------------------
    @Interface.override
    def FinalizePass2(self) -> None:
        for the_type in self.types:
            the_type.FinalizePass2()
