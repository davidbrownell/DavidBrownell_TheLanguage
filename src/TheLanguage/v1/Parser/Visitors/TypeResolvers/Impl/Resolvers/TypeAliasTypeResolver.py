# ----------------------------------------------------------------------
# |
# |  TypeAliasTypeResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-25 10:27:42
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeAliasTypeResolver object"""

import os

from typing import Dict, Generator, List

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...StatementTypeResolver import StatementTypeResolver

    from .....ParserInfos.ParserInfo import CompileTimeInfo

    from .....ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from .....ParserInfos.Types.ConcreteType import ConcreteType
    from .....ParserInfos.Types.ConstrainedType import ConstrainedType


# ----------------------------------------------------------------------
class TypeAliasTypeResolver(StatementTypeResolver):
    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        compile_time_info: List[Dict[str, CompileTimeInfo]],
    ) -> "TypeAliasTypeResolver":
        return TypeAliasTypeResolver(
            self.namespace,
            self.fundamental_namespace,
            compile_time_info,
            self.root_resolvers,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConcreteTypeImpl(
        self,
        updated_type_resolver: StatementTypeResolver,
    ) -> ConcreteType:
        assert isinstance(self.namespace.parser_info, TypeAliasStatementParserInfo), self.namespace.parser_info

        return _ConcreteType(
            self.namespace.parser_info,
            updated_type_resolver.EvalConcreteType(self.namespace.parser_info.type),
        )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _ConcreteType(ConcreteType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: TypeAliasStatementParserInfo,
        concrete_type: ConcreteType,
    ):
        super(_ConcreteType, self).__init__(parser_info)

        self._concrete_type                 = concrete_type

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> TypeAliasStatementParserInfo:
        assert isinstance(self._parser_info, TypeAliasStatementParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumAliases(self) -> Generator[ConcreteType, None, None]:
        yield self
        yield from self._concrete_type.EnumAliases()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        self._concrete_type.FinalizePass1()

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        self._concrete_type.FinalizePass2()

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(self) -> ConstrainedType:
        return self._concrete_type.CreateConstrainedType()
