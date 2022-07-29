# ----------------------------------------------------------------------
# |
# |  ConcreteTypeResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-29 09:27:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ConcreteTypeResolver object"""

import os
import threading

from typing import Dict, Optional, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeResolver import TypeResolver
    from .UpdateCacheImpl import UpdateCacheImpl

    from ...Namespaces import ParsedNamespace

    from ....ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ....ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ....ParserInfos.Statements.StatementParserInfo import StatementParserInfo
    from ....ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ....ParserInfos.Types.ConcreteType import ConcreteType
    from ....ParserInfos.Types.GenericTypes import GenericStatementType
    from ....ParserInfos.Types.TypeResolvers import ConcreteTypeResolver as ConcreteTypeResolverInterface


# ----------------------------------------------------------------------
class ConcreteTypeResolver(ConcreteTypeResolverInterface, TypeResolver):
    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        TypeResolver.__init__(self, *args, **kwargs)

        self._concrete_type: Optional[ConcreteType]     = None

        self._generic_cache_lock                                                        = threading.Lock()
        self._generic_cache: Dict[int, Union[threading.Event, GenericStatementType]]    = {}

    # ----------------------------------------------------------------------
    def SetConcreteType(
        self,
        concrete_type: ConcreteType,
    ) -> None:
        assert self._concrete_type is None
        self._concrete_type = concrete_type

    # ----------------------------------------------------------------------
    @property
    def has_concrete_type(self) -> bool:
        return self._concrete_type is not None

    @property
    def concrete_type(self) -> ConcreteType:
        assert self._concrete_type
        return self._concrete_type

    # ----------------------------------------------------------------------
    def GetOrCreateNestedGenericTypeViaNamespace(
        self,
        namespace: ParsedNamespace,
    ) -> GenericStatementType:
        assert self.is_finalized is True

        # ----------------------------------------------------------------------
        def CreateGenericType() -> GenericStatementType:
            if isinstance(namespace.parser_info, ClassStatementParserInfo):
                from ..ClassResolvers import ClassGenericTypeResolver

                generic_type_resolver_class = ClassGenericTypeResolver

            elif isinstance(namespace.parser_info, FuncDefinitionStatementParserInfo):
                from ..FuncDefinitionResolvers import FuncDefinitionGenericTypeResolver

                generic_type_resolver_class = FuncDefinitionGenericTypeResolver

            elif isinstance(namespace.parser_info, TypeAliasStatementParserInfo):
                from ..TypeAliasResolvers import TypeAliasGenericTypeResolver

                generic_type_resolver_class = TypeAliasGenericTypeResolver

            else:
                assert False, namespace.parser_info  # pragma: no cover

            generic_resolver = generic_type_resolver_class(
                parent=self,
                namespace=namespace,
                fundamental_namespace=self.fundamental_namespace,
                compile_time_info=self.compile_time_info,
                root_type_resolvers=self.root_type_resolvers,
            )

            return generic_resolver.generic_type

        # ----------------------------------------------------------------------

        return UpdateCacheImpl(
            self._generic_cache_lock,
            self._generic_cache,
            id(namespace),
            CreateGenericType,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def GetOrCreateNestedGenericType(
        self,
        parser_info: StatementParserInfo,
    ) -> GenericStatementType:
        assert self.is_finalized is True

        namespace: Optional[ParsedNamespace] = None

        for namespace_or_namespaces in self.namespace.EnumChildren():
            if isinstance(namespace_or_namespaces, list):
                potential_namespaces = namespace_or_namespaces
            else:
                potential_namespaces = [namespace_or_namespaces, ]

            for potential_namespace in potential_namespaces:
                assert isinstance(potential_namespace, ParsedNamespace), potential_namespace

                if potential_namespace.parser_info is parser_info:
                    namespace = potential_namespace
                    break

        assert namespace is not None
        return self.GetOrCreateNestedGenericTypeViaNamespace(namespace)
