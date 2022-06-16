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
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...ParserInfos.Expressions.TernaryExpressionParserInfo import TernaryExpressionParserInfo
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

            parser_info.SetValidatedFlag()

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncOrTypeExpressionParserInfo(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            assert not isinstance(parser_info.value, str), parser_info.value
            parser_info.SetValidatedFlag()

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTernaryExpressionParserInfo(
        self,
        parser_info: TernaryExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            condition_result = MiniLanguageHelpers.EvalExpression(
                parser_info.condition_expression,
                [self._configuration_info],
                [],
            )
            condition_result = condition_result.type.ToBoolValue(condition_result.value)

            if condition_result:
                parser_info.false_expression.Disable()
            else:
                parser_info.true_expression.Disable()

            parser_info.SetValidatedFlag()

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnVariableExpressionParserInfo(
        self,
        parser_info: VariableExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            # Unfortunately, we can't validate that the variable exists here as does so will break
            # statements such as `if IsDefined!(__architecture_bytes!) and __architecture_bytes! == 8: ...`
            # (as we want to lazily evaluate the existence of `__architecture_bytes!`).
            parser_info.SetValidatedFlag()

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnVariantExpressionParserInfo(
        self,
        parser_info: VariantExpressionParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            assert all(
                type_parser_info.parser_info_type__ == ParserInfoType.Configuration
                for type_parser_info in parser_info.types
            )

            parser_info.SetValidatedFlag()

        yield
