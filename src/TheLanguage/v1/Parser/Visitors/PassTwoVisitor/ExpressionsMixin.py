# ----------------------------------------------------------------------
# |
# |  ExpressionsMixin.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-16 10:17:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ExpressionsMixin object"""

import os

from contextlib import contextmanager, ExitStack
from typing import Optional, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from .. import MiniLanguageHelpers
    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ...Error import CreateError, ErrorException

    from ...ParserInfos.ParserInfo import ParserInfoType, VisitResult

    from ...ParserInfos.Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo

    from ...ParserInfos.Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo, OperatorType as BinaryExpressionOperatorType
    from ...ParserInfos.Expressions.BooleanExpressionParserInfo import BooleanExpressionParserInfo
    from ...ParserInfos.Expressions.CallExpressionParserInfo import CallExpressionParserInfo
    from ...ParserInfos.Expressions.CharacterExpressionParserInfo import CharacterExpressionParserInfo
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...ParserInfos.Expressions.IndexExpressionParserInfo import IndexExpressionParserInfo
    from ...ParserInfos.Expressions.IntegerExpressionParserInfo import IntegerExpressionParserInfo
    from ...ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ...ParserInfos.Expressions.NumberExpressionParserInfo import NumberExpressionParserInfo
    from ...ParserInfos.Expressions.StringExpressionParserInfo import StringExpressionParserInfo
    from ...ParserInfos.Expressions.TernaryExpressionParserInfo import TernaryExpressionParserInfo
    from ...ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo
    from ...ParserInfos.Expressions.TypeCheckExpressionParserInfo import TypeCheckExpressionParserInfo
    from ...ParserInfos.Expressions.UnaryExpressionParserInfo import UnaryExpressionParserInfo
    from ...ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo
    from ...ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo

    from ...ParserInfos.Statements.StatementParserInfo import ScopeFlag, StatementParserInfo


# ----------------------------------------------------------------------
InvalidTypeError                            = CreateError(
    "'{name}' is not a valid type",
    name=str,
)


# ----------------------------------------------------------------------
class ExpressionsMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @contextmanager
    def OnBinaryExpressionParserInfo(
        self,
        parser_info: BinaryExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())

        # BugBug (TODO): if (
        # BugBug (TODO):     parser_info.operator == BinaryExpressionOperatorType.Access
        # BugBug (TODO):     or parser_info.operator == BinaryExpressionOperatorType.AccessReturnSelf
        # BugBug (TODO): ):
        # BugBug (TODO):     # Handle the visitation manually, as we have to modify the stack ourselves
        # BugBug (TODO):     try:
        # BugBug (TODO):         left_result = MiniLanguageHelpers.EvalExpression(
        # BugBug (TODO):             parser_info.left_expression,
        # BugBug (TODO):             self._compile_time_stack,
        # BugBug (TODO):         )
        # BugBug (TODO):
        # BugBug (TODO):         assert isinstance(left_result.value, NamespaceInfo), left_result.value
        # BugBug (TODO):
        # BugBug (TODO):         if parser_info.operator == BinaryExpressionOperatorType.Access:
        # BugBug (TODO):             self._namespaces_stack.append([left_result.value])
        # BugBug (TODO):         elif parser_info.operator == BinaryExpressionOperatorType.AccessReturnSelf:
        # BugBug (TODO):             assert False, "BugBug"
        # BugBug (TODO):         else:
        # BugBug (TODO):             assert False, parser_info.operator  # pragma: no cover
        # BugBug (TODO):
        # BugBug (TODO):         with ExitStack() as exit_stack:
        # BugBug (TODO):             exit_stack.callback(self._namespaces_stack.pop)
        # BugBug (TODO):
        # BugBug (TODO):             parser_info.right_expression.Accept(self)
        # BugBug (TODO):
        # BugBug (TODO):             # BugBug: Preserve the result of visiting the right expression
        # BugBug (TODO):
        # BugBug (TODO):     except ErrorException as ex:
        # BugBug (TODO):         self._errors += ex.errors
        # BugBug (TODO):
        # BugBug (TODO):     yield VisitResult.SkipAll
        # BugBug (TODO):     return

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnBooleanExpressionParserInfo(
        self,
        parser_info: BooleanExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())
        # BugBug parser_info.InitResolvedType(self._GetResolvedType("Bool", parser_info))

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnCallExpressionParserInfo(
        self,
        parser_info: CallExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnCharacterExpressionParserInfo(
        self,
        parser_info: CharacterExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())
        # BugBug parser_info.InitResolvedType(self._GetResolvedType("Char", parser_info))

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncOrTypeExpressionParserInfo(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())

        # BugBug if parser_info.parser_info_type__ != ParserInfoType.Configuration:
        # BugBug     if not isinstance(parser_info.value, str):
        # BugBug         assert False, "BugBug"
        # BugBug     else:
        # BugBug         parser_info.InitResolvedType(self._GetResolvedType(parser_info.value, parser_info))
        # BugBug
        # BugBug     BugBug = 10

        yield
        return # BugBUg

        if isinstance(parser_info.value, str):
            try:
                result = MiniLanguageHelpers.EvalExpression(
                    parser_info,
                    self._compile_time_stack,
                )

                # BugBug parser_info.InitValueParserInfo(result.value)

            except ErrorException as ex:
                self._errors += ex.errors

                yield VisitResult.SkipAll
                return

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIndexExpressionParserInfo(
        self,
        parser_info: IndexExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIntegerExpressionParserInfo(
        self,
        parser_info: IntegerExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())
        # BugBug parser_info.InitResolvedType(self._GetResolvedType("ArchInt", parser_info))

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnNoneExpressionParserInfo(
        self,
        parser_info: NoneExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())
        # BugBug parser_info.InitResolvedType(self._GetResolvedType("None", parser_info))

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnNumberExpressionParserInfo(
        self,
        parser_info: NumberExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())
        # BugBug parser_info.InitResolvedType(self._GetResolvedType("ArchNum", parser_info))

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnStringExpressionParserInfo(
        self,
        parser_info: StringExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())
        # BugBug parser_info.InitResolvedType(self._GetResolvedType("FixedSizeStr", parser_info))

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTernaryExpressionParserInfo(
        self,
        parser_info: TernaryExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())

        # This expression should be able to be evaluated if it isn't at the function
        # level. We can make this statement with confidence, because we aren't visiting
        # templated items.

        if parser_info.parser_info_type__ == ParserInfoType.TypeCustomization:
            # Determine if the condition is True or False
            condition_result = MiniLanguageHelpers.EvalExpression(
                parser_info.condition_expression,
                self._compile_time_stack,
            )
            condition_result = condition_result.type.ToBoolValue(condition_result.value)

            # BugBug: Not sure if I like how the false condition is not evaluated
            if condition_result:
                parser_info.false_expression.Disable()
            else:
                parser_info.true_expression.Disable()

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTupleExpressionParserInfo(
        self,
        parser_info: TupleExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTypeCheckExpressionParserInfo(
        self,
        parser_info: TypeCheckExpressionParserInfo,
    ):

        # BugBug parser_info.InitInTemplate(self._InTemplate())
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnUnaryExpressionParserInfo(
        self,
        parser_info: UnaryExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnVariableExpressionParserInfo(
        self,
        parser_info: VariableExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())

        if parser_info.parser_info_type__ == ParserInfoType.TypeCustomization:
            print("BugBug____", parser_info.name)
            # BugBug: Ensure no overwrites
            pass

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnVariantExpressionParserInfo(
        self,
        parser_info: VariantExpressionParserInfo,
    ):
        # BugBug parser_info.InitInTemplate(self._InTemplate())

        if parser_info.parser_info_type__ == ParserInfoType.TypeCustomization:
            assert all(
                ParserInfoType.IsCompileTime(type_parser_info.parser_info_type__)
                for type_parser_info in parser_info.types
            )

        yield
