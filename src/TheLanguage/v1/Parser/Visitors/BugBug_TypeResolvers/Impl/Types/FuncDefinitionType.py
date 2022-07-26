# ----------------------------------------------------------------------
# |
# |  FuncDefinitionType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-22 14:01:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains func-related types"""

import os

from typing import Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....Namespaces import ParsedNamespace

    from .....ParserInfos.Types.ConcreteType import ConcreteType
    from .....ParserInfos.Types.ConstrainedType import ConstrainedType
    from .....ParserInfos.Types.GenericType import GenericType

    from .....ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from .....ParserInfos.Statements.ConcreteFuncDefinition import ConcreteFuncDefinition, TypeResolver
    from .....ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class GenericFuncDefinitionType(GenericType):
    # ----------------------------------------------------------------------
    _namespace: ParsedNamespace
    _type_resolver: TypeResolver

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert isinstance(self._namespace.parser_info, FuncDefinitionStatementParserInfo), self._namespace.parser_info

    # ----------------------------------------------------------------------
    @property
    def
# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConcreteClassType(ConcreteType):
    # ----------------------------------------------------------------------
    concrete_func: ConcreteFuncDefinition

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        self.concrete_func.FinalizePass1(self)

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        self.concrete_func.FinalizePass2(self)

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(
        self,
        constraint_arguments_parser_info: Optional[ConstraintArgumentsParserInfo],
    ) -> "ConstrainedFuncDefinitionType":
        return ConstrainedFuncDefinitionType(self)


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConstrainedFuncDefinitionType(ConstrainedType):
    pass
