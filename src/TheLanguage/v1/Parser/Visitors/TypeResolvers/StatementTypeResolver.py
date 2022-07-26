# ----------------------------------------------------------------------
# |
# |  StatementTypeResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-25 08:18:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeResolver object"""

import os
import threading

from contextlib import ExitStack
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

import CommonEnvironment
from CommonEnvironment.DoesNotExist import DoesNotExist
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeResolver import TypeResolver

    from .Impl import MatchConstraintCall
    from .Impl import MatchTemplateCall

    from ..Namespaces import ParsedNamespace

    from ...ParserInfos.ParserInfo import CompileTimeInfo, ParserInfoType

    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ...ParserInfos.Statements.Traits.ConstrainedStatementTrait import ConstrainedStatementTrait
    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ...ParserInfos.Types.ConcreteType import ConcreteType


# ----------------------------------------------------------------------
class StatementTypeResolver(TypeResolver, Interface.Interface):
    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(StatementTypeResolver, self).__init__(*args, **kwargs)

        self._children_lock                                                         = threading.Lock()
        self._children: Dict[int, Union[threading.Event, StatementTypeResolver]]    = {}

        self._concrete_cache_lock                                               = threading.Lock()
        self._concrete_cache: Dict[Any, Union[threading.Event, ConcreteType]]   = {}

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Clone(
        compile_time_info: List[Dict[str, CompileTimeInfo]],
    ) -> "StatementTypeResolver":
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    def GetOrCreateNestedResolver(
        self,
        namespace: ParsedNamespace,
    ) -> "StatementTypeResolver":
        # ----------------------------------------------------------------------
        def CreateTypeResolver() -> "StatementTypeResolver":
            if isinstance(namespace.parser_info, ClassStatementParserInfo):
                from .Impl.Resolvers.ClassTypeResolver import ClassTypeResolver

                resolver_type = ClassTypeResolver

            elif isinstance(namespace.parser_info, FuncDefinitionStatementParserInfo):
                from .Impl.Resolvers.FuncDefinitionTypeResolver import FuncDefinitionTypeResolver

                resolver_type = FuncDefinitionTypeResolver

            elif isinstance(namespace.parser_info, TypeAliasStatementParserInfo):
                from .Impl.Resolvers.TypeAliasTypeResolver import TypeAliasTypeResolver

                resolver_type = TypeAliasTypeResolver

            else:
                assert False, namespace.parser_info  # pragma: no cover

            return resolver_type(
                namespace,
                self.fundamental_namespace,
                self.compile_time_info,
                self.root_resolvers,
            )

        # ----------------------------------------------------------------------

        result = self._UpdateCachedDictImpl(
            self._children_lock,
            self._children,
            id(namespace),
            CreateTypeResolver,
        )

        assert isinstance(result, StatementTypeResolver), result
        return result

    # ----------------------------------------------------------------------
    def CreateConcreteType(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> ConcreteType:
        assert isinstance(self.namespace.parser_info, TemplatedStatementTrait), self.namespace.parser_info

        if parser_info.value == "Internal":
            BugBug = 10

        # Resolve the template arguments
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

            cache_key = resolved_template_arguments.cache_key

        else:
            if parser_info.templates:
                raise Exception("Error: Templates where none were expected")

            cache_key = None

        # ----------------------------------------------------------------------
        def CreateConcreteType():
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

            # BugBug: This part isn't right
            updated_resolver = self.Clone(compile_time_info)

            result = self._CreateConcreteTypeImpl(updated_resolver)

            # BugBug: Not sure about this here
            result.FinalizePass1()
            result.FinalizePass2()

            return result

        # ----------------------------------------------------------------------

        result = self._UpdateCachedDictImpl(
            self._concrete_cache_lock,
            self._concrete_cache,
            cache_key,
            CreateConcreteType,
        )

        assert isinstance(result, ConcreteType), result
        return result

    # ----------------------------------------------------------------------
    def ValidateDefaultInitialization(self) -> None:
        if (
            not isinstance(self.namespace.parser_info, TemplatedStatementTrait)
            or (
                self.namespace.parser_info.templates is None
                or self.namespace.parser_info.templates.is_default_initializable
            )
        ):
            concrete_type = self.CreateConcreteType(
                FuncOrTypeExpressionParserInfo.Create(
                    parser_info_type=ParserInfoType.Standard,               # type: ignore
                    regions=[
                        self.namespace.parser_info.regions__.self__,
                        self.namespace.parser_info.regions__.name,
                        None,
                    ],                                                      # type: ignore
                    value=self.namespace.parser_info.name,
                    templates=None,
                    constraints=None,
                    mutability_modifier=None,
                ),
            )

            if (
                not isinstance(self.namespace.parser_info, ConstrainedStatementTrait)
                or (
                    self.namespace.parser_info.constraints is None
                    or self.namespace.parser_info.constraints.is_default_initializable
                )
            ):
                concrete_type.CreateConstrainedType()

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _UpdateCachedDictImplT                  = TypeVar("_UpdateCachedDictImplT")

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    def _UpdateCachedDictImpl(
        lock: threading.Lock,
        cache: Dict[Any, Union[threading.Event, _UpdateCachedDictImplT]],
        cache_key: Any,
        create_value_func: Callable[[], _UpdateCachedDictImplT],
    ) -> "StatementTypeResolver._UpdateCachedDictImplT":
        wait_event: Optional[threading.Event] = None
        should_wait: Optional[bool] = None

        with lock:
            cache_result = cache.get(cache_key, DoesNotExist.instance)

            if isinstance(cache_result, DoesNotExist):
                wait_event = threading.Event()
                should_wait = False

                cache[cache_key] = wait_event

            elif isinstance(cache_result, threading.Event):
                wait_event = cache_result
                should_wait = True

            else:
                return cache_result

        assert wait_event is not None
        assert should_wait is not None

        if should_wait:
            wait_event.wait()

            with lock:
                cache_result = cache.get(cache_key, DoesNotExist.instance)

                if isinstance(cache_result, DoesNotExist):
                    raise Exception("BugBug: Error somewhere else")

                assert not isinstance(cache_result, threading.Event), cache_result
                return cache_result

        result: Union[DoesNotExist, StatementTypeResolver._UpdateCachedDictImplT] = DoesNotExist.instance

        # ----------------------------------------------------------------------
        def RestoreCacheOnError():
            with lock:
                if isinstance(result, DoesNotExist):
                    del cache[cache_key]
                else:
                    assert cache[cache_key] is wait_event
                    cache[cache_key] = result  # type: ignore

            wait_event.set()

        # ----------------------------------------------------------------------

        with ExitStack() as exit_stack:
            exit_stack.callback(RestoreCacheOnError)

            result = create_value_func()

        return result

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateConcreteTypeImpl(
        updated_type_resolver: "StatementTypeResolver",
    ) -> ConcreteType:
        raise Exception("Abstract method")  # pragma: no cover
