# ----------------------------------------------------------------------
# |
# |  GenericTypeResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-28 13:04:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GenericTypeResolver object"""

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
    from .ConcreteTypeResolver import ConcreteTypeResolver
    from .TypeResolver import TypeResolver
    from . import MatchTemplateCall
    from .UpdateCacheImpl import UpdateCacheImpl

    from ....ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from ....ParserInfos.ParserInfo import CompileTimeInfo

    from ....ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ....ParserInfos.Types.ConcreteType import ConcreteType

    from ....ParserInfos.Types.TypeResolvers import GenericTypeResolver as GenericTypeResolverInterface


# ----------------------------------------------------------------------
class GenericTypeResolver(GenericTypeResolverInterface, TypeResolver):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        generic_statement_class,
        *args,
        **kwargs,
    ):
        TypeResolver.__init__(self, *args, **kwargs)

        self.generic_type                   = generic_statement_class(self)

        self._concrete_cache_lock                                               = threading.Lock()
        self._concrete_cache: Dict[int, Union[threading.Event, ConcreteType]]   = {}

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> ConcreteType:
        assert self.is_finalized is True

        assert isinstance(self.namespace.parser_info, TemplatedStatementTrait), self.namespace.parser_info

        # Resolve the template arguments to get the concrete cache key
        resolved_template_arguments: Optional[MatchTemplateCall.ResolvedArguments] = None

        if self.namespace.parser_info.templates:
            resolved_template_arguments = MatchTemplateCall.Match(
                self.namespace.parser_info.templates,
                parser_info.templates,
                self.namespace.parser_info.name,
                self.namespace.parser_info.regions__.self__,
                parser_info.regions__.self__,
                self,
            )

        elif parser_info.templates:
            raise Exception("Error: Templates where none were expected")

        # ----------------------------------------------------------------------
        def CreateConcreteType() -> ConcreteType:
            if resolved_template_arguments is None:
                compile_time_info = self.compile_time_info
            else:
                new_compile_time_info_item: Dict[str, CompileTimeInfo] = {}

                for parameter_parser_info, arg in resolved_template_arguments.types:
                    pass # BugBug

                for parameter_parser_info, arg in resolved_template_arguments.decorators:
                    assert parameter_parser_info.name not in new_compile_time_info_item, parameter_parser_info.name

                    new_compile_time_info_item[parameter_parser_info.name] = CompileTimeInfo(
                        arg.type,
                        arg.value,
                    )

                compile_time_info = self.compile_time_info + [new_compile_time_info_item, ]

            resolved_constraint_arguments = None # BugBug

            concrete_resolver = ConcreteTypeResolver(
                self.parent,
                self.namespace,
                self.fundamental_namespace,
                compile_time_info,
                self.root_type_resolvers,
            )

            concrete_type = self._CreateConcreteTypeImpl(concrete_resolver)

            concrete_resolver.SetConcreteType(concrete_type)

            return concrete_type

        # ----------------------------------------------------------------------

        return UpdateCacheImpl(
            self._concrete_cache_lock,
            self._concrete_cache,
            resolved_template_arguments.cache_key if resolved_template_arguments is not None else None,
            CreateConcreteType,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateConcreteTypeImpl(
        updated_resolver: ConcreteTypeResolver,
    ) -> ConcreteType:
        raise Exception("Abstract method")  # pragma: no cover
