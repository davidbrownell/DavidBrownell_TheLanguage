# ----------------------------------------------------------------------
# |
# |  GenericTypeImpl.py
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
"""Contains the GenericTypeImpl object"""

import os
import threading

from typing import Any, Dict, Generic, Optional, TypeVar, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .CreateDefaultExpressionParserInfo import CreateDefaultExpressionParserInfo
    from . import MatchTemplateCall
    from .UpdateCacheImpl import UpdateCacheImpl

    from ..TypeResolver import TypeResolver

    from ....ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import ExpressionParserInfo, FuncOrTypeExpressionParserInfo

    from ....ParserInfos.ParserInfo import CompileTimeInfo, ParserInfoType

    from ....ParserInfos.Statements.StatementParserInfo import StatementParserInfo
    from ....ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ....ParserInfos.Traits.NamedTrait import NamedTrait

    from ....ParserInfos.Types.ConcreteType import ConcreteType
    from ....ParserInfos.Types.GenericType import GenericType as GenericTypeInterface


# ----------------------------------------------------------------------
ParserInfoT                                 = TypeVar("ParserInfoT")


class GenericTypeImpl(GenericTypeInterface, Generic[ParserInfoT]):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        type_resolver: TypeResolver,
    ):
        super(GenericTypeImpl, self).__init__(
            type_resolver.namespace.parser_info,
            is_default_initializable=(
                not isinstance(type_resolver.namespace.parser_info, TemplatedStatementTrait)
                or type_resolver.namespace.parser_info.templates is None
                or type_resolver.namespace.parser_info.templates.is_default_initializable
            ),
        )

        self._type_resolver                 = type_resolver

        self._concrete_cache_lock                                               = threading.Lock()
        self._concrete_cache: Dict[int, Union[threading.Event, ConcreteType]]   = {}

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> ParserInfoT:
        return self._parser_info  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(
        self,
        expression_parser_info: ExpressionParserInfo,
    ) -> ConcreteType:
        assert isinstance(expression_parser_info, FuncOrTypeExpressionParserInfo), expression_parser_info
        assert self._type_resolver.is_finalized is True

        assert isinstance(self.parser_info, TemplatedStatementTrait), self.parser_info
        assert isinstance(self.parser_info, NamedTrait), self.parser_info

        # Resolve the template arguments to get the concrete cache key
        cache_key: Any = None
        resolved_template_arguments: Optional[MatchTemplateCall.ResolvedArguments] = None

        if self.parser_info.templates:
            resolved_template_arguments = MatchTemplateCall.Match(
                self.parser_info.templates,
                expression_parser_info.templates,
                self.parser_info.name,
                self.parser_info.regions__.self__,
                expression_parser_info.regions__.self__,
                self._type_resolver,
            )

            cache_id = resolved_template_arguments.cache_key

        elif expression_parser_info.templates:
            raise Exception("Error: Templates where none were expected")


        # ----------------------------------------------------------------------
        def CreateConcreteType() -> ConcreteType:
            if resolved_template_arguments is None:
                compile_time_info = self._type_resolver.compile_time_info
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

                compile_time_info = self._type_resolver.compile_time_info + [new_compile_time_info_item, ]

            type_resolver = TypeResolver(
                self._type_resolver.parent,
                self._type_resolver.namespace,
                self._type_resolver.fundamental_namespace,
                compile_time_info,
                self._type_resolver.root_type_resolvers,
            )

            concrete_type = self._CreateConcreteType(type_resolver, cache_key)

            type_resolver.InitConcreteType(concrete_type)

            return concrete_type

        # ----------------------------------------------------------------------

        return UpdateCacheImpl(
            self._concrete_cache_lock,
            self._concrete_cache,
            cache_key,
            CreateConcreteType,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConcreteTypeImpl(self) -> ConcreteType:
        assert isinstance(self.parser_info, StatementParserInfo), self.parser_info
        return self.CreateConcreteType(CreateDefaultExpressionParserInfo(self.parser_info))

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateConcreteType(
        updated_resolver: TypeResolver,
        resolved_template_arguments_id: Any,
    ) -> ConcreteType:
        raise Exception("Abstract method")  # pragma: no cover
