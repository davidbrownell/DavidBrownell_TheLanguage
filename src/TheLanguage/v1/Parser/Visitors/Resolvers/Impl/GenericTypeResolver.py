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

from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeResolver import TypeResolver
    from . import MatchTemplateCall
    from .UpdateCacheImpl import UpdateCacheImpl

    from ....ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import ExpressionParserInfo, FuncOrTypeExpressionParserInfo

    from ....ParserInfos.ParserInfo import CompileTimeInfo, ParserInfoType

    from ....ParserInfos.Statements.StatementParserInfo import StatementParserInfo
    from ....ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ....ParserInfos.Traits.NamedTrait import NamedTrait

    from ....ParserInfos.Types.ConcreteType import ConcreteType
    from ....ParserInfos.Types.GenericTypes import BoundGenericType, GenericType as GenericTypeInterface


# ----------------------------------------------------------------------
ParserInfoT                                 = TypeVar("ParserInfoT")


class GenericType(GenericTypeInterface, Generic[ParserInfoT]):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        type_resolver: TypeResolver,
    ):
        super(GenericType, self).__init__(
            type_resolver.namespace.parser_info,
            (
                not isinstance(type_resolver.namespace.parser_info, TemplatedStatementTrait)
                or type_resolver.namespace.parser_info.templates is None
                or type_resolver.namespace.parser_info.templates.is_default_initializable
            ),
        )

        self._type_resolver                 = type_resolver

        self._concrete_data_cache_lock                                      = threading.Lock()
        self._concrete_data_cache: Dict[int, Union[threading.Event, Any]]   = {}

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> ParserInfoT:
        return self._parser_info  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateBoundGenericType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> BoundGenericType:
        assert isinstance(parser_info, FuncOrTypeExpressionParserInfo), parser_info
        assert self._type_resolver.is_finalized is True

        assert isinstance(self.parser_info, TemplatedStatementTrait), self.parser_info
        assert isinstance(self.parser_info, NamedTrait), self.parser_info

        # Resolve the template arguments to get the concrete cache key
        resolved_template_arguments: Optional[MatchTemplateCall.ResolvedArguments] = None

        if self.parser_info.templates:
            resolved_template_arguments = MatchTemplateCall.Match(
                self.parser_info.templates,
                parser_info.templates,
                self.parser_info.name,
                self.parser_info.regions__.self__,
                parser_info.regions__.self__,
                self._type_resolver,
            )

        elif parser_info.templates:
            raise Exception("Error: Templates where none were expected")

        # ----------------------------------------------------------------------
        def CreateConcreteData() -> TypeResolver:
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

            concrete_data = self._CreateConcreteData(type_resolver)

            type_resolver.InitConcreteData(concrete_data)

            return concrete_data

        # ----------------------------------------------------------------------

        concrete_data = UpdateCacheImpl(
            self._concrete_data_cache_lock,
            self._concrete_data_cache,
            resolved_template_arguments.cache_key if resolved_template_arguments is not None else None,
            CreateConcreteData,
        )

        return self._CreateBoundGenericType(concrete_data, parser_info)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConcreteTypeImpl(self) -> ConcreteType:
        return self.CreateBoundGenericType(
            FuncOrTypeExpressionParserInfo.Create(
                parser_info_type=ParserInfoType.Standard,
                regions=[
                    self.parser_info.regions__.self__,
                    self.parser_info.regions__.name,
                    None,
                ],
                value=self.parser_info.name,
                templates=None,
                constraints=None,
                mutability_modifier=None,
            ),
        ).CreateConcreteType()

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateConcreteData(
        updated_resolver: "TypeResolver",
    ) -> Any:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateBoundGenericType(
        concrete_data: Any,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> BoundGenericType:
        raise Exception("Abstract method")  # pragma: no cover








# BugBug # ----------------------------------------------------------------------
# BugBug class GenericTypeResolver(GenericTypeResolverInterface, TypeResolver):
# BugBug     # ----------------------------------------------------------------------
# BugBug     def __init__(
# BugBug         self,
# BugBug         generic_type_class: Type[GenericType],
# BugBug         *args,
# BugBug         **kwargs,
# BugBug     ):
# BugBug         TypeResolver.__init__(self, *args, **kwargs)
# BugBug
# BugBug         self.generic_type                   = generic_type_class(self)
# BugBug
# BugBug         self._concrete_cache_lock                                                       = threading.Lock()
# BugBug         self._concrete_cache: Dict[int, Union[threading.Event, ConcreteTypeResolver]]   = {}
# BugBug
# BugBug     # ----------------------------------------------------------------------
# BugBug     @Interface.override
# BugBug     def CreateBoundGenericType(
# BugBug         self,
# BugBug         parser_info: ExpressionParserInfo,
# BugBug     ) -> BoundGenericType:
# BugBug         assert isinstance(parser_info, FuncOrTypeExpressionParserInfo), parser_info
# BugBug         assert self.is_finalized is True
# BugBug
# BugBug         assert isinstance(self.namespace.parser_info, TemplatedStatementTrait), self.namespace.parser_info
# BugBug
# BugBug         # Resolve the template arguments to get the concrete cache key
# BugBug         resolved_template_arguments: Optional[MatchTemplateCall.ResolvedArguments] = None
# BugBug
# BugBug         if self.namespace.parser_info.templates:
# BugBug             resolved_template_arguments = MatchTemplateCall.Match(
# BugBug                 self.namespace.parser_info.templates,
# BugBug                 parser_info.templates,
# BugBug                 self.namespace.parser_info.name,
# BugBug                 self.namespace.parser_info.regions__.self__,
# BugBug                 parser_info.regions__.self__,
# BugBug                 self,
# BugBug             )
# BugBug
# BugBug         elif parser_info.templates:
# BugBug             raise Exception("Error: Templates where none were expected")
# BugBug
# BugBug         # ----------------------------------------------------------------------
# BugBug         def CreateConcreteResolver() -> ConcreteTypeResolver:
# BugBug             if resolved_template_arguments is None:
# BugBug                 compile_time_info = self.compile_time_info
# BugBug             else:
# BugBug                 new_compile_time_info_item: Dict[str, CompileTimeInfo] = {}
# BugBug
# BugBug                 for parameter_parser_info, arg in resolved_template_arguments.types:
# BugBug                     pass # BugBug
# BugBug
# BugBug                 for parameter_parser_info, arg in resolved_template_arguments.decorators:
# BugBug                     assert parameter_parser_info.name not in new_compile_time_info_item, parameter_parser_info.name
# BugBug
# BugBug                     new_compile_time_info_item[parameter_parser_info.name] = CompileTimeInfo(
# BugBug                         arg.type,
# BugBug                         arg.value,
# BugBug                     )
# BugBug
# BugBug                 compile_time_info = self.compile_time_info + [new_compile_time_info_item, ]
# BugBug
# BugBug             return ConcreteTypeResolver(
# BugBug                 self.parent,
# BugBug                 self.namespace,
# BugBug                 self.fundamental_namespace,
# BugBug                 compile_time_info,
# BugBug                 self.root_type_resolvers,
# BugBug             )
# BugBug
# BugBug         # ----------------------------------------------------------------------
# BugBug
# BugBug         concrete_resolver = UpdateCacheImpl(
# BugBug             self._concrete_cache_lock,
# BugBug             self._concrete_cache,
# BugBug             resolved_template_arguments.cache_key if resolved_template_arguments is not None else None,
# BugBug             CreateConcreteResolver,
# BugBug         )
# BugBug
# BugBug         return self._CreateBoundGenericType(
# BugBug             concrete_resolver,
# BugBug             self.generic_type,
# BugBug             parser_info,
# BugBug         )
# BugBug
# BugBug     # ----------------------------------------------------------------------
# BugBug     # ----------------------------------------------------------------------
# BugBug     # ----------------------------------------------------------------------
# BugBug     @staticmethod
# BugBug     @Interface.abstractmethod
# BugBug     def _CreateBoundGenericType(
# BugBug         concrete_resolver: ConcreteTypeResolver,
# BugBug         generic_type: GenericType,
# BugBug         parser_info: FuncOrTypeExpressionParserInfo,
# BugBug     ) -> BoundGenericType:
# BugBug         raise Exception("Abstract method")  # pragma: no cover
# BugBug
# BugBug
# BugBug         # ----------------------------------------------------------------------
# BugBug         def CreateConcreteType() -> ConcreteType:
# BugBug             if resolved_template_arguments is None:
# BugBug                 compile_time_info = self.compile_time_info
# BugBug             else:
# BugBug                 new_compile_time_info_item: Dict[str, CompileTimeInfo] = {}
# BugBug
# BugBug                 for parameter_parser_info, arg in resolved_template_arguments.types:
# BugBug                     pass # BugBug
# BugBug
# BugBug                 for parameter_parser_info, arg in resolved_template_arguments.decorators:
# BugBug                     assert parameter_parser_info.name not in new_compile_time_info_item, parameter_parser_info.name
# BugBug
# BugBug                     new_compile_time_info_item[parameter_parser_info.name] = CompileTimeInfo(
# BugBug                         arg.type,
# BugBug                         arg.value,
# BugBug                     )
# BugBug
# BugBug                 compile_time_info = self.compile_time_info + [new_compile_time_info_item, ]
# BugBug
# BugBug             resolved_constraint_arguments = None # BugBug
# BugBug
# BugBug             concrete_resolver = ConcreteTypeResolver(
# BugBug                 self.parent,
# BugBug                 self.namespace,
# BugBug                 self.fundamental_namespace,
# BugBug                 compile_time_info,
# BugBug                 self.root_type_resolvers,
# BugBug             )
# BugBug
# BugBug             concrete_type = self._CreateConcreteTypeImpl(concrete_resolver)
# BugBug
# BugBug             concrete_resolver.SetConcreteType(concrete_type)
# BugBug
# BugBug             return concrete_type
# BugBug
# BugBug         # ----------------------------------------------------------------------
# BugBug
# BugBug         return UpdateCacheImpl(
# BugBug             self._concrete_cache_lock,
# BugBug             self._concrete_cache,
# BugBug             resolved_template_arguments.cache_key if resolved_template_arguments is not None else None,
# BugBug             CreateConcreteType,
# BugBug         )
# BugBug
# BugBug     # ----------------------------------------------------------------------
# BugBug     # ----------------------------------------------------------------------
# BugBug     # ----------------------------------------------------------------------
# BugBug     @staticmethod
# BugBug     @Interface.abstractmethod
# BugBug     def _CreateConcreteTypeImpl(
# BugBug         updated_resolver: ConcreteTypeResolver,
# BugBug     ) -> ConcreteType:
# BugBug         raise Exception("Abstract method")  # pragma: no cover
# BugBug
