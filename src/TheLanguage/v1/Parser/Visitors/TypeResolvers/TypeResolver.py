# ----------------------------------------------------------------------
# |
# |  TypeResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-25 11:53:16
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

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Namespaces import Namespace, ParsedNamespace

    from ...Common import MiniLanguageHelpers
    from ...Error import CreateError, ErrorException

    from ...ParserInfos.ParserInfo import CompileTimeInfo

    from ...ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...ParserInfos.Expressions.NestedTypeExpressionParserInfo import NestedTypeExpressionParserInfo
    from ...ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ...ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo
    from ...ParserInfos.Expressions.TypeCheckExpressionParserInfo import OperatorType as TypeCheckExpressionOperatorType
    from ...ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo

    from ...ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo

    from ...ParserInfos.Types.ConcreteType import ConcreteType
    from ...ParserInfos.Types.NoneTypes import ConcreteNoneType
    from ...ParserInfos.Types.TupleTypes import ConcreteTupleType
    from ...ParserInfos.Types.VariantTypes import ConcreteVariantType

    if TYPE_CHECKING:
        from .Impl.Resolvers.RootTypeResolver import RootTypeResolver  # pylint: disable=unused-import


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


# ----------------------------------------------------------------------
class TypeResolver(object):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        namespace: ParsedNamespace,
        fundamental_namespace: Optional[Namespace],
        compile_time_info: List[Dict[str, CompileTimeInfo]],
        root_resolvers: Optional[Dict[Tuple[str, str], "RootTypeResolver"]],
    ):
        self.namespace                      = namespace
        self.fundamental_namespace          = fundamental_namespace
        self.compile_time_info              = compile_time_info

        self._is_finalized                                                          = False
        self._root_resolvers: Optional[Dict[Tuple[str, str], "RootTypeResolver"]]   = None

        if root_resolvers is not None:
            self.Finalize(root_resolvers)

    # ----------------------------------------------------------------------
    def Finalize(
        self,
        root_resolvers: Dict[Tuple[str, str], "RootTypeResolver"],
    ) -> None:
        assert self._is_finalized is False
        assert self._root_resolvers is None

        self._root_resolvers = root_resolvers
        self._is_finalized = True

    # ----------------------------------------------------------------------
    @property
    def root_resolvers(self) -> Dict[Tuple[str, str], "RootTypeResolver"]:
        assert self._is_finalized is True
        assert self._root_resolvers is not None
        return self._root_resolvers

    # ----------------------------------------------------------------------
    def EvalMiniLanguageType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageType:
        assert self._is_finalized

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
    def EvalMiniLanguageExpression(
        self,
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageExpression.EvalResult:
        assert self._is_finalized

        return MiniLanguageHelpers.EvalExpression(
            parser_info,
            self.compile_time_info,
            None,
        )

    # ----------------------------------------------------------------------
    def EvalConcreteType(
        self,
        parser_info: ExpressionParserInfo,
        *,
        no_finalize=False,
    ) -> ConcreteType:
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
                self._ResolveByNested,
                self._ResolveByNamespace,
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

        if not no_finalize:
            result.FinalizePass1()
            result.FinalizePass2()

        return result

    # ----------------------------------------------------------------------
    def EvalStatements(
        self,
        statements: List[StatementParserInfo],
    ) -> None:
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
        return None # BugBug

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

            root_resolver = self.root_resolvers.get(resolved_namespace.parser_info.translation_unit__, None)
            assert root_resolver is not None

            return (
                root_resolver
                    .GetOrCreateNestedResolver(resolved_namespace)
                    .CreateConcreteType(parser_info)
            )
