# ----------------------------------------------------------------------
# |
# |  TypeAliasResolvers.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-28 13:32:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains Resolvers that have knowledge of type aliases"""

import os

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl.ConcreteTypeResolver import ConcreteTypeResolver
    from .Impl.GenericTypeResolver import GenericTypeResolver
    from .Impl.GenericStatementTypeMixin import GenericStatementTypeMixin

    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ...ParserInfos.Types.ConcreteType import ConcreteType
    from ...ParserInfos.Types.GenericTypes import GenericType


# ----------------------------------------------------------------------
class TypeAliasGenericTypeResolver(GenericTypeResolver):
    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(TypeAliasGenericTypeResolver, self).__init__(
            _TypeAliasGenericStatementType,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConcreteTypeImpl(
        self,
        updated_resolver: ConcreteTypeResolver,
    ) -> ConcreteType:
        assert isinstance(self.namespace.parser_info, TypeAliasStatementParserInfo), self.namespace.parser_info
        return updated_resolver.EvalConcreteType(self.namespace.parser_info.type)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _TypeAliasGenericStatementType(GenericStatementTypeMixin[TypeAliasStatementParserInfo]):
    # ----------------------------------------------------------------------
    @Interface.override
    def IsSameType(
        self,
        other: GenericType,
    ) -> bool:
        return False # BugBug
