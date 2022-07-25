# ----------------------------------------------------------------------
# |
# |  ClassType.py
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
"""Contains class-related types"""

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
    from .....ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from .....ParserInfos.Statements.ConcreteClass import ConcreteClass, TypeResolver


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class GenericClassType(GenericType):
    # ----------------------------------------------------------------------
    _namespace: ParsedNamespace
    _type_resolver: TypeResolver

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert isinstance(self._namespace.parser_info, ClassStatementParserInfo), self._namespace.parser_info

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> FuncOrTypeExpressionParserInfo:
        result = super(GenericClassType, self).parser_info
        assert isinstance(result, FuncOrTypeExpressionParserInfo), result

        return result

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(self) -> "ConcreteClassType":
        assert isinstance(self._namespace.parser_info, ClassStatementParserInfo)
        return ConcreteClassType(self, ConcreteClass.Create(self._namespace.parser_info, self._type_resolver))


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConcreteClassType(ConcreteType):
    # ----------------------------------------------------------------------
    concrete_class: ConcreteClass

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        self.concrete_class.FinalizePass1(self)

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        self.concrete_class.FinalizePass2(self)

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(self) -> "ConstrainedClassType":
        return ConstrainedClassType(self)


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConstrainedClassType(ConstrainedType):
    pass
