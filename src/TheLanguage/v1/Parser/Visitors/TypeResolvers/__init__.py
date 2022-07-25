# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-20 11:58:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when resolving types"""

import itertools
import os
import threading

from contextlib import ExitStack
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl import MatchConstraintCall
    from .Impl import MatchTemplateCall

    from .Impl.Types.ClassType import GenericClassType
    # BugBug from .Impl.Types.FuncDefinitionType import GenericFuncDefinitionType
    from .Impl.Types.NoneTypes import GenericNoneType
    from .Impl.Types.TupleTypes import GenericTupleType
    # BugBug from .Impl.Types.TypeAliasType import GenericTypeAliasType
    from .Impl.Types.VariantTypes import GenericVariantType

    from ..Namespaces import Namespace, ParsedNamespace

    from ...Common import MiniLanguageHelpers
    from ...Error import CreateError, ErrorException

    from ...ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
    from ...ParserInfos.Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo

    from ...ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...ParserInfos.Expressions.NestedTypeExpressionParserInfo import NestedTypeExpressionParserInfo
    from ...ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ...ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo
    from ...ParserInfos.Expressions.TypeCheckExpressionParserInfo import OperatorType as TypeCheckExpressionOperatorType
    from ...ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo

    from ...ParserInfos.ParserInfo import CompileTimeInfo, ParserInfo

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ...ParserInfos.Statements.ConcreteClass import ConcreteClass, TypeResolver as ClassTypeResolverBase
    from ...ParserInfos.Statements.ConcreteFuncDefinition import ConcreteFuncDefinition, TypeResolver as FuncDefinitionTypeResolverBase

    from ...ParserInfos.Statements.Traits.ConstrainedStatementTrait import ConstrainedStatementTrait
    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ...ParserInfos.Types.ConcreteType import ConcreteType
    from ...ParserInfos.Types.ConstrainedType import ConstrainedType
    from ...ParserInfos.Types.GenericType import GenericType

    from ...ParserInfos.Traits.NamedTrait import NamedTrait

    from ...TranslationUnitRegion import TranslationUnitRegion


# ----------------------------------------------------------------------
UnexpectedStandardTypeError                 = CreateError(
    "A standard type was not expected in this context",
)

UnexpectedMiniLanguageTypeError             = CreateError(
    "A compile-time type was not expected in this context",
)

InvalidNamedTypeError                       = CreateError(
    "'{name}' is not a recognized type",
    name=str,
)

InvalidTypeReferenceError                   = CreateError(
    "'{name}' is defined via an ordered statement; it can only be used after it is defined",
    name=str,
    defined_region=TranslationUnitRegion,
)

InvalidVisibilityError                      = CreateError(
    "'{name}' exists, but is not visible in the current context",
    name=str,
    defined_region=TranslationUnitRegion,
)


# ----------------------------------------------------------------------
class TypeResolverBase(object):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        namespace: ParsedNamespace,
        fundamental_namespace: Optional[Namespace],
        compile_time_info: List[Dict[str, CompileTimeInfo]],
        translation_unit_resolvers: Optional[Dict[Tuple[str, str], "ConcreteTypeResolver"]],
    ):
        assert isinstance(namespace.parser_info, NamedTrait), namespace.parser_info

        self.namespace                      = namespace
        self.fundamental_namespace          = fundamental_namespace
        self._compile_time_info             = compile_time_info

        self._is_finalized                                                                              = False
        self._translation_unit_resolvers_data: Optional[Dict[Tuple[str, str], ConcreteTypeResolver]]    = None

        if translation_unit_resolvers is not None:
            self.Finalize(translation_unit_resolvers)

    # ----------------------------------------------------------------------
    def Finalize(
        self,
        translation_unit_resolvers: Dict[Tuple[str, str], "ConcreteTypeResolver"],
    ) -> None:
        assert self._is_finalized is False
        assert self._translation_unit_resolvers_data is None

        self._translation_unit_resolvers_data = translation_unit_resolvers
        self._is_finalized = True

    # ----------------------------------------------------------------------
    @property
    def _translation_unit_resolvers(self) -> Dict[Tuple[str, str], "ConcreteTypeResolver"]:
        assert self._is_finalized is True
        assert self._translation_unit_resolvers_data is not None
        return self._translation_unit_resolvers_data

    # ----------------------------------------------------------------------
    def EvalMiniLanguageType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageType:
        assert self._is_finalized

        result = MiniLanguageHelpers.EvalTypeExpression(
            parser_info,
            self._compile_time_info,
            None,
        )

        # TODO: Make this more generic once all return types have region info
        if isinstance(result, ExpressionParserInfo):
            raise ErrorException(
                UnexpectedStandardTypeError.Create(
                    region=result.regions__.self__,
                ),
            )

        return result

    # ----------------------------------------------------------------------
    def EvalMiniLanguageExpression(
        self,
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageExpression.EvalResult:
        assert self._is_finalized

        return MiniLanguageHelpers.EvalExpression(
            parser_info,
            self._compile_time_info,
            None,
        )

    # ----------------------------------------------------------------------
    def EvalType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> GenericType:
        assert self._is_finalized

        type_expression = MiniLanguageHelpers.EvalTypeExpression(
            parser_info,
            self._compile_time_info,
            self._TypeCheckHelper,
        )

        if isinstance(type_expression, MiniLanguageHelpers.MiniLanguageType):
            raise ErrorException(
                UnexpectedMiniLanguageTypeError.Create(
                    region=parser_info.regions__.self__,
                ),
            )

        if isinstance(type_expression, FuncOrTypeExpressionParserInfo):
            for resolution_algorithm in [
                self._ResolveByNested,
                self._ResolveByNamespace,
            ]:
                result = resolution_algorithm(type_expression)
                if result is not None:
                    return result

            raise ErrorException(
                InvalidNamedTypeError.Create(
                    region=type_expression.regions__.value,
                    name=type_expression.value,
                ),
            )

        elif isinstance(type_expression, NestedTypeExpressionParserInfo):
            raise NotImplementedError("TODO: NestedTypeExpressionParserInfo")

        elif isinstance(type_expression, NoneExpressionParserInfo):
            return GenericNoneType(type_expression)

        elif isinstance(type_expression, TupleExpressionParserInfo):
            return GenericTupleType(
                type_expression,
                [self.EvalType(the_type) for the_type in type_expression.types],
            )

        elif isinstance(type_expression, VariantExpressionParserInfo):
            return GenericVariantType(
                type_expression,
                [self.EvalType(the_type) for the_type in type_expression.types],
            )

        else:
            assert False, type_expression  # pragma: no cover

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _TypeCheckHelper(
        self,
        type_name: str,
        operator: TypeCheckExpressionOperatorType,
        type_parser_info: ExpressionParserInfo,
    ) -> bool:
        assert False, "BugBug: TODO"
        return False

    # ----------------------------------------------------------------------
    def _ResolveByNested(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> Optional[GenericType]:
        return None # BugBug

    # ----------------------------------------------------------------------
    def _ResolveByNamespace(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> Optional[GenericType]:
        assert isinstance(parser_info.value, str), parser_info.value

        # ----------------------------------------------------------------------
        def EnumNamespaces() -> Generator[Namespace, None, None]:
            namespace = self.namespace

            while True:
                if namespace is None or namespace.name is None:
                    break

                yield namespace

                namespace = namespace.parent

            if self.fundamental_namespace:
                yield self.fundamental_namespace

        # ----------------------------------------------------------------------

        for namespace in EnumNamespaces():
            namespace = namespace.GetChild(parser_info.value)
            if namespace is None:
                continue

            assert isinstance(namespace, ParsedNamespace), namespace

            resolved_namespace = namespace.ResolveImports()

            translation_unit_resolver = self._translation_unit_resolvers.get(resolved_namespace.parser_info.translation_unit__, None)
            assert translation_unit_resolver is not None

            generic_resolver = translation_unit_resolver.GetOrCreateChild(resolved_namespace)

            if isinstance(resolved_namespace.parser_info, ClassStatementParserInfo):
                # BugBug
                adapter_type_resolver = None

                return GenericClassType(
                    parser_info,
                    parser_info.templates,
                    parser_info.constraints,
                    adapter_type_resolver,
                )

            try:
                return (
                    generic_resolver
                        .CreateConcreteResolver(
                            (parser_info.templates or parser_info).regions__.self__,
                            parser_info.templates,
                        )
                        .CreateType(
                            (parser_info.constraints or parser_info).regions__.self__,
                            parser_info.constraints,
                        )
                )

            except ErrorException as ex:
                # Capture include chain
                raise ex

        return None


# ----------------------------------------------------------------------
class ConcreteTypeResolver(TypeResolverBase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super(ConcreteTypeResolver, self).__init__(*args, **kwargs)

        if isinstance(self.namespace.parser_info, ClassStatementParserInfo):
            the_type = self._CreateClassType()
        elif isinstance(self.namespace.parser_info, FuncDefinitionStatementParserInfo):
            the_type = self._CreateFuncDefinitionType()
        elif isinstance(self.namespace.parser_info, TypeAliasStatementParserInfo):
            the_type = self._CreateTypeAliasType()
        elif isinstance(self.namespace.parser_info, RootStatementParserInfo):
            the_type = None
        else:
            assert False, self.namespace.parser_info  # pragma: no cover

        self._the_type: Optional[Type]      = the_type

        self._children_lock                                                         = threading.Lock()
        self._children: Dict[int, Union[threading.Event, "GenericTypeResolver"]]    = {}

    # ----------------------------------------------------------------------
    def GetOrCreateChild(
        self,
        namespace: ParsedNamespace,
    ) -> "GenericTypeResolver":
        dict_key = id(namespace)

        wait_event: Optional[threading.Event] = None
        should_wait: Optional[bool] = None

        with self._children_lock:
            child_result = self._children.get(dict_key, None)

            if child_result is None:
                wait_event = threading.Event()
                should_wait = False

                self._children[dict_key] = wait_event

            elif isinstance(child_result, threading.Event):
                wait_event = child_result
                should_wait = True

            else:
                return child_result

        assert wait_event is not None
        assert should_wait is not None

        if should_wait:
            print("BugBug (GetOrCreateChild)", self.namespace.parser_info.name)
            wait_event.wait()

            with self._children_lock:
                child_result = self._children.get(dict_key)
                assert isinstance(child_result, GenericTypeResolver)

                return child_result

        generic_resolver = GenericTypeResolver(
            namespace,
            self.fundamental_namespace,
            self._compile_time_info,
            self._translation_unit_resolvers,
        )

        with self._children_lock:
            assert self._children.get(dict_key) is wait_event
            self._children[dict_key] = generic_resolver

        wait_event.set()

        return generic_resolver

    # ----------------------------------------------------------------------
    def CreateType(
        self,
        invocation_region: TranslationUnitRegion,
        constraint_arguments: Optional[ConstraintArgumentsParserInfo],
    ) -> Type:
        assert self._is_finalized
        assert self._the_type is not None

        resolved_constraint_arguments: Optional[MatchConstraintCall.ResolvedArguments] = None

        if (
            isinstance(self.namespace.parser_info, ConstrainedStatementTrait)
            and self.namespace.parser_info.constraints
        ):
            pass # BugBug

            # BugBug: Do this after concrete classes are complete

            # assert isinstance(self.namespace.parser_info, NamedTrait), self.namespace.parser_info
            #
            # resolved_constraint_arguments = MatchConstraintCall.Match(
            #     self.namespace.parser_info.constraints,
            #     constraint_arguments,
            #     self.namespace.parser_info.name,
            #     self.namespace.parser_info.regions__.self__,
            #     invocation_region,
            #     self,
            # )
            #
        else:
            if constraint_arguments is not None:
                raise Exception("BugBug: Constraints where none were expected")

        result: Optional[Type] = None

        if resolved_constraint_arguments is not None:
            new_constraint_item: Dict[str, CompileTimeInfo] = {}

            for parameter_parser_info, arg in resolved_constraint_arguments.decorators:
                assert parameter_parser_info.name not in new_constraint_item, parameter_parser_info.name

                new_constraint_item[parameter_parser_info.name] = CompileTimeInfo(
                    arg.type,
                    arg.value,
                )

            # BugBug constraints = self._constraints + [new_constraint_item, ]
        else:
            pass # BugBug constraints = self._constraints

        # BugBug: This isn't right; we need to return something that is aware of constraints
        return self._the_type

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _CreateClassType(self) -> ClassType:
        # ----------------------------------------------------------------------
        class ClassTypeResolver(ClassTypeResolverBase):
            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def EvalType(
                parser_info: ExpressionParserInfo,
            ) -> Type:
                return self.EvalType(parser_info)

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def CreateGenericTypeResolver(
                parser_info: Union[ClassStatementParserInfo, FuncDefinitionStatementParserInfo, TypeAliasStatementParserInfo],
            ) -> Any:
                namespace_or_namespaces = self.namespace.GetChild(parser_info.name)
                assert namespace_or_namespaces is not None

                if isinstance(namespace_or_namespaces, list):
                    namespaces = namespace_or_namespaces
                else:
                    namespaces = [namespace_or_namespaces, ]

                for namespace in namespaces:
                    assert isinstance(namespace, ParsedNamespace)

                    if namespace.parser_info is parser_info:
                        was_cached, generic_resolver = self.GetOrCreateChild(namespace)
                        # BugBug if not was_cached:
                        # BugBug     generic_resolver.DefaultInitializationValidation()

                        return generic_resolver

                assert False, (namespaces, parser_info)  # pragma: no cover

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def EvalStatements(
                statements: Optional[List[StatementParserInfo]],
            ) -> None:
                assert statements is not None

                for statement in statements:
                    if statement.is_disabled__:
                        continue

                    assert isinstance(statement, FuncInvocationStatementParserInfo), statement

                    eval_result = self.EvalMiniLanguageExpression(statement.expression)
                    assert isinstance(eval_result.type, MiniLanguageHelpers.NoneType), eval_result.type

        # ----------------------------------------------------------------------

        assert isinstance(self.namespace.parser_info, ClassStatementParserInfo), self.namespace.parser_info

        return ClassType(
            self.namespace.parser_info,
            ConcreteClass.Create(self.namespace.parser_info, ClassTypeResolver()),
        )

    # ----------------------------------------------------------------------
    def _CreateFuncDefinitionType(self) -> FuncDefinitionType:
        # ----------------------------------------------------------------------
        class FuncDefinitionTypeResolver(FuncDefinitionTypeResolverBase):
            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def EvalType(
                parser_info: ExpressionParserInfo,
            ) -> Type:
                return self.EvalType(parser_info)

        # ----------------------------------------------------------------------

        assert isinstance(self.namespace.parser_info, FuncDefinitionStatementParserInfo), self.namespace.parser_info

        return FuncDefinitionType(
            self.namespace.parser_info,
            ConcreteFuncDefinition.Create(
                self.namespace.parser_info,
                FuncDefinitionTypeResolver(),
            ),
        )

    # ----------------------------------------------------------------------
    def _CreateTypeAliasType(self) -> TypeAliasType:
        assert isinstance(self.namespace.parser_info, TypeAliasStatementParserInfo), self.namespace.parser_info

        return TypeAliasType(
            self.namespace.parser_info,
            self.EvalType(self.namespace.parser_info.type),
        )


# ----------------------------------------------------------------------
class GenericTypeResolver(TypeResolverBase):
    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(GenericTypeResolver, self).__init__(*args, **kwargs)

        self._cache_lock                                                        = threading.Lock()
        self._cache: Dict[Any, Union[threading.Event, ConcreteTypeResolver]]    = {}

    # ----------------------------------------------------------------------
    def CreateConcreteResolver(
        self,
        invocation_region: TranslationUnitRegion,
        template_arguments: Optional[TemplateArgumentsParserInfo],
    ) -> ConcreteTypeResolver:
        assert self._is_finalized

        # Create the cache key
        resolved_template_arguments: Optional[MatchTemplateCall.ResolvedArguments] = None

        if (
            isinstance(self.namespace.parser_info, TemplatedStatementTrait)
            and self.namespace.parser_info.templates
        ):
            assert isinstance(self.namespace.parser_info, NamedTrait), self.namespace.parser_info

            resolved_template_arguments = MatchTemplateCall.Match(
                self.namespace.parser_info.templates,
                template_arguments,
                self.namespace.parser_info.name,
                self.namespace.parser_info.regions__.self__,
                invocation_region,
                self,
            )

            cache_key = resolved_template_arguments.cache_key

        else:
            if template_arguments is not None:
                raise Exception("BugBug: Templates where none were expected")

            cache_key = None

        # Consult the cache
        wait_event: Optional[threading.Event] = None
        should_wait: Optional[bool] = None

        with self._cache_lock:
            cache_result = self._cache.get(cache_key, None)

            if cache_result is None:
                wait_event = threading.Event()
                should_wait = False

                self._cache[cache_key] = wait_event

            elif isinstance(cache_result, threading.Event):
                wait_event = cache_result
                should_wait = True

            else:
                return cache_result

        assert wait_event is not None
        assert should_wait is not None

        if should_wait:
            wait_event.wait()

            with self._cache_lock:
                cache_result = self._cache.get(cache_key, None)

                if cache_result is None:
                    raise Exception("BugBug: Something went very wrong elsewhere")

                assert isinstance(cache_result, ConcreteTypeResolver)
                return cache_result

        result: Optional[ConcreteTypeResolver] = None

        # ----------------------------------------------------------------------
        def Cleanup():
            with self._cache_lock:
                assert self._cache[cache_key] is wait_event

                if result is None:
                    del self._cache[cache_key]
                else:
                    self._cache[cache_key] = result

            wait_event.set()

        # ----------------------------------------------------------------------

        with ExitStack() as exit_stack:
            exit_stack.callback(Cleanup)

            if resolved_template_arguments is not None:
                new_compile_time_info_item: Dict[str, CompileTimeInfo] = {}

                for parameter_parser_info, arg in resolved_template_arguments.types:
                    pass # BugBug

                for parameter_parser_info, arg in resolved_template_arguments.decorators:
                    assert parameter_parser_info.name not in new_compile_time_info_item, parameter_parser_info.name

                    new_compile_time_info_item[parameter_parser_info.name] = CompileTimeInfo(
                        arg.type,
                        arg.value,
                    )

                compile_time_info = self._compile_time_info + [new_compile_time_info_item, ]
            else:
                compile_time_info = self._compile_time_info

            result = ConcreteTypeResolver(
                self.namespace,
                self.fundamental_namespace,
                compile_time_info,
                self._translation_unit_resolvers,
            )

        assert result is not None
        return result

    # ----------------------------------------------------------------------
    def DefaultInitializationValidation(self):
        """Validate those types that have no/default templates and no/default constraints"""

        if (
            not isinstance(self.namespace.parser_info, TemplatedStatementTrait)
            or (
                self.namespace.parser_info.templates is None
                or self.namespace.parser_info.templates.is_default_initializable
            )
        ):
            concrete_resolver = self.CreateConcreteResolver(
                self.namespace.parser_info.regions__.self__,
                None,
            )

            if (
                not isinstance(concrete_resolver.namespace.parser_info, ConstrainedStatementTrait)
                or (
                    concrete_resolver.namespace.parser_info.constraints is None
                    or concrete_resolver.namespace.parser_info.constraints.is_default_initializable
                )
            ):
                concrete_resolver.CreateType(
                    concrete_resolver.namespace.parser_info.regions__.self__,
                    None,
                )
