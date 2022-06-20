# ----------------------------------------------------------------------
# |
# |  ExpressionsMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-14 12:19:57
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

from contextlib import contextmanager

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from .. import MiniLanguageHelpers

    from ...Error import CreateError

    from ...ParserInfos.ParserInfo import ParserInfoType, VisitResult

    from ...ParserInfos.Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo
    from ...ParserInfos.Expressions.BooleanExpressionParserInfo import BooleanExpressionParserInfo
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ...ParserInfos.Expressions.TernaryExpressionParserInfo import TernaryExpressionParserInfo
    from ...ParserInfos.Expressions.TypeCheckExpressionParserInfo import TypeCheckExpressionParserInfo
    from ...ParserInfos.Expressions.UnaryExpressionParserInfo import UnaryExpressionParserInfo
    from ...ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo
    from ...ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo


# ----------------------------------------------------------------------
InvalidBinaryOperatorError                  = CreateError(
    "'{operator}' is not a valid binary operator for compile-time expressions",
    operator=str,
)


# ----------------------------------------------------------------------
class ExpressionsMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @contextmanager
    def OnBinaryExpressionParserInfo(
        self,
        parser_info: BinaryExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            self._FlagAsProcessed(parser_info)

            operator = parser_info.operator.ToMiniLanguageOperatorType()
            if operator is None:
                self._errors.append(
                    InvalidBinaryOperatorError.Create(
                        region=parser_info.regions__.operator,
                        operator=parser_info.operator.name,
                    ),
                )

                yield VisitResult.SkipAll
                return

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnBooleanExpressionParserInfo(
        self,
        parser_info: BooleanExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            self._FlagAsProcessed(parser_info)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncOrTypeExpressionParserInfo(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            self._FlagAsProcessed(parser_info)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnNoneExpressionParserInfo(
        self,
        parser_info: NoneExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            self._FlagAsProcessed(parser_info)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTernaryExpressionParserInfo(
        self,
        parser_info: TernaryExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            self._FlagAsProcessed(parser_info)

            condition_result = MiniLanguageHelpers.EvalExpression(
                parser_info.condition_expression,
                [self._configuration_info],
            )

            condition_result = condition_result.type.ToBoolValue(condition_result.value)

            if condition_result:
                parser_info.false_expression.Disable()
            else:
                parser_info.true_expression.Disable()

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTypeCheckExpressionParserInfo(
        self,
        parser_info: TypeCheckExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            self._FlagAsProcessed(parser_info)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnUnaryExpressionParserInfo(
        self,
        parser_info: UnaryExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            self._FlagAsProcessed(parser_info)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnVariableExpressionParserInfo(
        self,
        parser_info: VariableExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            self._FlagAsProcessed(parser_info)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnVariantExpressionParserInfo(
        self,
        parser_info: VariantExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            self._FlagAsProcessed(parser_info)

        yield
