# ----------------------------------------------------------------------
# |
# |  TypeResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-28 12:52:57
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

from typing import Dict, Generator, List, Optional, Tuple, TYPE_CHECKING

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....ParserInfos.Types.TypeResolvers import TypeResolver as TypeResolverBase

    from ...Namespaces import Namespace, ParsedNamespace

    from ....Common import MiniLanguageHelpers
    from ....Error import CreateError, ErrorException

    from ....ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ....ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ....ParserInfos.Expressions.NestedTypeExpressionParserInfo import NestedTypeExpressionParserInfo
    from ....ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ....ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo
    from ....ParserInfos.Expressions.TypeCheckExpressionParserInfo import OperatorType as TypeCheckExpressionOperatorType
    from ....ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo

    from ....ParserInfos.ParserInfo import CompileTimeInfo

    from ....ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ....ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ....ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ....ParserInfos.Statements.StatementParserInfo import StatementParserInfo

    from ....ParserInfos.Traits.NamedTrait import NamedTrait

    from ....ParserInfos.Types.ClassTypes.ConcreteClassType import ConcreteClassType

    from ....ParserInfos.Types.ConcreteType import ConcreteType
    from ....ParserInfos.Types.GenericTypes import GenericStatementType
    from ....ParserInfos.Types.NoneTypes import ConcreteNoneType
    from ....ParserInfos.Types.TupleTypes import ConcreteTupleType
    from ....ParserInfos.Types.VariantTypes import ConcreteVariantType

    if TYPE_CHECKING:
        from .ConcreteTypeResolver import ConcreteTypeResolver  # pylint: disable=unused-import


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

InvisibleNestedTypeError                    = CreateError(
    "The type '{type}' is valid but not visible in the current context",
    type=str,
)


# ----------------------------------------------------------------------
class TypeResolver(TypeResolverBase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parent: Optional["ConcreteTypeResolver"],
        namespace: ParsedNamespace,
        fundamental_namespace: Optional[Namespace],
        compile_time_info: List[Dict[str, CompileTimeInfo]],
        root_type_resolvers: Optional[Dict[Tuple[str, str], "ConcreteTypeResolver"]],
    ):
        assert (
            parent is not None
            or isinstance(namespace.parser_info, RootStatementParserInfo)
            or not isinstance(namespace.parent, ParsedNamespace)
            or isinstance(namespace.parent.parser_info, RootStatementParserInfo)
        ), (parent, namespace)

        self.parent                         = parent
        self.namespace                      = namespace
        self.fundamental_namespace          = fundamental_namespace
        self.compile_time_info              = compile_time_info

        self.is_finalized                                                                           = False
        self._root_type_resolvers: Optional[Dict[Tuple[str, str], ConcreteTypeResolver]]     = None

        if root_type_resolvers is not None:
            self.Finalize(root_type_resolvers)

    # ----------------------------------------------------------------------
    def Finalize(
        self,
        root_type_resolvers: Dict[Tuple[str, str], "ConcreteTypeResolver"],
    ) -> None:
        assert self.is_finalized is False
        assert self._root_type_resolvers is None

        self._root_type_resolvers = root_type_resolvers
        self.is_finalized = True

    # ----------------------------------------------------------------------
    @property
    def root_type_resolvers(self) -> Dict[Tuple[str, str], "ConcreteTypeResolver"]:
        assert self.is_finalized is True
        assert self._root_type_resolvers is not None
        return self._root_type_resolvers

    # ----------------------------------------------------------------------
    @Interface.override
    def EvalMiniLanguageType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageType:
        assert self.is_finalized is True

        result = MiniLanguageHelpers.EvalTypeExpression(
            parser_info,
            self.compile_time_info,
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
    @Interface.override
    def EvalMiniLanguageExpression(
        self,
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageExpression.EvalResult:
        assert self.is_finalized is True

        return MiniLanguageHelpers.EvalExpression(
            parser_info,
            self.compile_time_info,
            None,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def EvalConcreteType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> ConcreteType:
        assert self.is_finalized is True

        type_expression = MiniLanguageHelpers.EvalTypeExpression(
            parser_info,
            self.compile_time_info,
            self._TypeCheckHelper,
        )

        if isinstance(type_expression, MiniLanguageHelpers.MiniLanguageType):
            raise ErrorException(
                UnexpectedMiniLanguageTypeError.Create(
                    region=parser_info.regions__.self__,
                ),
            )

        result: Optional[ConcreteType] = None

        if isinstance(type_expression, FuncOrTypeExpressionParserInfo):
            assert isinstance(type_expression.value, str), type_expression.value

            for resolution_algorithm in [
                # BugBug: Order should be Nested then Namespace. Reversed while testing.
                self._ResolveByNamespace,
                self._ResolveByNested,
            ]:
                result = resolution_algorithm(type_expression)

                if result is not None:
                    break

            if result is None:
                raise ErrorException(
                    InvalidNamedTypeError.Create(
                        region=type_expression.regions__.value,
                        name=type_expression.value,
                    ),
                )

        elif isinstance(type_expression, NestedTypeExpressionParserInfo):
            raise NotImplementedError("TODO: NestedTypeExpressionParserInfo")

        elif isinstance(type_expression, NoneExpressionParserInfo):
            result = ConcreteNoneType(type_expression)

        elif isinstance(type_expression, TupleExpressionParserInfo):
            result = ConcreteTupleType(
                type_expression,
                [self.EvalConcreteType(the_type) for the_type in type_expression.types],
            )

        elif isinstance(type_expression, VariantExpressionParserInfo):
            result = ConcreteVariantType(
                type_expression,
                [self.EvalConcreteType(the_type) for the_type in type_expression.types],
            )

        else:
            assert False, type_expression  # pragma: no cover

        assert result is not None
        return result

    # ----------------------------------------------------------------------
    @Interface.override
    def EvalStatements(
        self,
        statements: List[StatementParserInfo],
    ) -> None:
        assert self.is_finalized is True

        for statement in statements:
            if statement.is_disabled__:
                continue

            assert isinstance(statement, FuncInvocationStatementParserInfo), statement

            eval_result = self.EvalMiniLanguageExpression(statement.expression)
            assert isinstance(eval_result.type, MiniLanguageHelpers.NoneType), eval_result

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
    ) -> Optional[ConcreteType]:
        assert isinstance(parser_info.value, str), parser_info.value

        resolver = self

        while resolver is not None:
            if isinstance(resolver.namespace.parser_info, ClassStatementParserInfo):
                concrete_class = resolver.concrete_type  # type: ignore  # pylint: disable=no-member
                assert isinstance(concrete_class, ConcreteClassType), concrete_class

                for type_dependency in concrete_class.types.EnumContent():
                    visibility, type_info = type_dependency.ResolveDependencies()

                    if type_info.name == parser_info.value:
                        if visibility is None:
                            raise ErrorException(
                                InvisibleNestedTypeError.Create(
                                    region=parser_info.regions__.self__,
                                    type=type_info.name,
                                ),
                            )

                        return type_info.generic_type.CreateConcreteType(parser_info)

            resolver = resolver.parent

        return None

    # ----------------------------------------------------------------------
    def _ResolveByNamespace(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> Optional[ConcreteType]:
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

            if isinstance(namespace.parser_info, RootStatementParserInfo):
                continue

            resolved_namespace = namespace.ResolveImports()

            root_type_resolver = self.root_type_resolvers.get(resolved_namespace.parser_info.translation_unit__, None)
            assert root_type_resolver is not None

            # BugBug: Error on invalid order

            generic_type = root_type_resolver.GetOrCreateNestedGenericTypeViaNamespace(resolved_namespace)

            return generic_type.CreateConcreteType(parser_info)
