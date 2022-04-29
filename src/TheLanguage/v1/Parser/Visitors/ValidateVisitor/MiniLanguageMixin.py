# ----------------------------------------------------------------------
# |
# |  MiniLanguageMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-27 15:01:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MiniLanguageMixin object"""

import os

from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
    Tuple,
    Type as TypingsType,
    Union,
)

from dataclasses import dataclass, fields

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import ArgumentInfo, BaseMixin, ParameterInfo, StateMaintainer

    from ...MiniLanguage.Expressions.BinaryExpression import BinaryExpression
    from ...MiniLanguage.Expressions.Expression import Expression
    from ...MiniLanguage.Expressions.IsDefinedExpression import IsDefinedExpression
    from ...MiniLanguage.Expressions.LiteralExpression import LiteralExpression
    from ...MiniLanguage.Expressions.TernaryExpression import TernaryExpression
    from ...MiniLanguage.Expressions.TypeCheckExpression import TypeCheckExpression
    from ...MiniLanguage.Expressions.UnaryExpression import UnaryExpression
    from ...MiniLanguage.Expressions.VariableExpression import VariableExpression

    from ...MiniLanguage.Statements.EnforceStatement import EnforceStatement
    from ...MiniLanguage.Statements.ErrorStatement import ErrorStatement
    from ...MiniLanguage.Statements.Statement import Statement

    from ...MiniLanguage.Types.BooleanType import BooleanType
    from ...MiniLanguage.Types.CharacterType import CharacterType
    from ...MiniLanguage.Types.IntegerType import IntegerType
    from ...MiniLanguage.Types.NoneType import NoneType
    from ...MiniLanguage.Types.NumberType import NumberType
    from ...MiniLanguage.Types.StringType import StringType
    from ...MiniLanguage.Types.Type import Type as MiniLanguageType
    from ...MiniLanguage.Types.VariantType import VariantType

    from ...ParserInfos.ParserInfo import ParserInfoType

    from ...ParserInfos.Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo
    from ...ParserInfos.Expressions.BooleanExpressionParserInfo import BooleanExpressionParserInfo
    from ...ParserInfos.Expressions.CallExpressionParserInfo import CallExpressionParserInfo
    from ...ParserInfos.Expressions.CharacterExpressionParserInfo import CharacterExpressionParserInfo
    from ...ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...ParserInfos.Expressions.IntegerExpressionParserInfo import IntegerExpressionParserInfo
    from ...ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ...ParserInfos.Expressions.NumberExpressionParserInfo import NumberExpressionParserInfo
    from ...ParserInfos.Expressions.StringExpressionParserInfo import StringExpressionParserInfo
    from ...ParserInfos.Expressions.TernaryExpressionParserInfo import TernaryExpressionParserInfo
    from ...ParserInfos.Expressions.TypeCheckExpressionParserInfo import TypeCheckExpressionParserInfo
    from ...ParserInfos.Expressions.UnaryExpressionParserInfo import UnaryExpressionParserInfo
    from ...ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo

    from ...ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo

    from ...ParserInfos.Types.StandardTypeParserInfo import StandardTypeParserInfo
    from ...ParserInfos.Types.TypeParserInfo import TypeParserInfo
    from ...ParserInfos.Types.VariantTypeParserInfo import VariantTypeParserInfo

    from ...Error import CreateError, Error, ErrorException
    from ...Region import Location, Region


# ----------------------------------------------------------------------
InvalidCompileTimeStatementError            = CreateError(
    "Invalid compile-time statement",
)

InvalidCompileTimeFunctionExpressionError   = CreateError(
    "Invalid compile-time function invocation",
)

InvalidCompileTimeFunctionError             = CreateError(
    "'{name}' is not a valid compile-time function",
    name=str,
)

InvalidExpressionError                      = CreateError(
    "Invalid compile-time expression",
)

InvalidVariableNameError                    = CreateError(
    "'{name}' is not a valid compile-time variable",
    name=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class UnionType(object):
    types: List[TypingsType]


# ----------------------------------------------------------------------
class MiniLanguageMixin(BaseMixin):
    FUNCTION_MAP                            = {
        "Enforce!": EnforceStatement,
        "Error!": ErrorStatement,
        "IsDefined!": IsDefinedExpression,
    }

    # ----------------------------------------------------------------------
    def ExecuteMiniLanguageFunctionStatement(
        self,
        parser_info: CallExpressionParserInfo,
    ):
        assert parser_info.parser_info_type__.value < ParserInfoType.Standard.value, parser_info.parser_info_type__  # type: ignore

        expression_or_statement = self.CreateMiniLanguageExpression(parser_info)
        if isinstance(expression_or_statement, Error):
            self._errors.append(expression_or_statement)
            return False

        if isinstance(expression_or_statement, Expression):
            assert False, "BugBug!!!!"

        if isinstance(expression_or_statement, Statement):
            result = expression_or_statement.Execute(*self._CreateCompileTimeState())

            self._errors += result.errors
            self._warnings += result.warnings
            self._infos += result.infos

    # ----------------------------------------------------------------------
    def EvalMiniLanguageExpression(
        self,
        parser_info: ExpressionParserInfo,
    ) -> Union[Tuple[Any, MiniLanguageType], Error]:
        result = self.CreateMiniLanguageExpression(parser_info)
        if isinstance(result, Error):
            return result

        result = result.Eval(*self._CreateCompileTimeState())
        if isinstance(result, Error):
            return result

        return result.value, result.type

    # ----------------------------------------------------------------------
    def CreateMiniLanguageExpression(
        self,
        parser_info: ExpressionParserInfo,
    ) -> Union[Expression, Error]:
        if isinstance(parser_info, BinaryExpressionParserInfo):
            left_expression = self.CreateMiniLanguageExpression(parser_info.left_expression)
            if isinstance(left_expression, Error):
                return left_expression

            right_expression = self.CreateMiniLanguageExpression(parser_info.right_expression)
            if isinstance(right_expression, Error):
                return right_expression

            return BinaryExpression(
                left_expression,
                parser_info.operator,
                right_expression,
                parser_info.left_expression.regions__.self__,
            )

        elif isinstance(parser_info, CallExpressionParserInfo):
            if not isinstance(parser_info.expression, FuncOrTypeExpressionParserInfo):
                return InvalidCompileTimeFunctionExpressionError.Create(
                    region=parser_info.expression.regions__.self__,
                )

            func_name = parser_info.expression.name

            # Get the MiniLanguage statement
            minilanguage_statement_type = self.__class__.FUNCTION_MAP.get(func_name, None)
            if minilanguage_statement_type is None:
                return InvalidCompileTimeFunctionError.Create(
                    region=parser_info.expression.regions__.self,
                    name=func_name,
                )

            # Extract the parameters for this function
            parameter_infos: List[ParameterInfo] = []
            none_type = type(None)

            for field in fields(minilanguage_statement_type):
                parameter_infos.append(
                    ParameterInfo(
                        field.name,
                        None,
                        is_optional=none_type in getattr(field, "__args__", []),
                        is_variadic=False,
                    ),
                )

            # Extract the arguments
            positional_arguments: List[ArgumentInfo] = []
            keyword_arguments: Dict[str, ArgumentInfo] = {}

            if not isinstance(parser_info.arguments, bool):
                for argument in parser_info.arguments.arguments:
                    result = self.CreateMiniLanguageExpression(argument.expression)
                    if isinstance(result, Error):
                        return result

                    argument_info = ArgumentInfo(result, argument.regions__.self__)

                    if argument.keyword is None:
                        positional_arguments.append(argument_info)
                    else:
                        assert argument.keyword not in keyword_arguments, argument.keyword # pragma: no cover
                        keyword_arguments[argument.keyword] = argument_info

            # Map the arguments to the parameters
            argument_map = self._CreateArgumentMap(
                func_name,
                None,
                [],
                parameter_infos,
                [],
                positional_arguments,
                keyword_arguments,
            )

            # We don't need to check argument types, as they are all expressions
            argument_map = {k: cast(ArgumentInfo, v).value for k, v in argument_map.items()}

            # Create an instance of the statement or expression
            return minilanguage_statement_type(**argument_map)

        elif isinstance(parser_info, BooleanExpressionParserInfo):
            return LiteralExpression(BooleanType(), parser_info.value)

        elif isinstance(parser_info, CharacterExpressionParserInfo):
            return LiteralExpression(CharacterType(), parser_info.value)

        elif isinstance(parser_info, IntegerExpressionParserInfo):
            return LiteralExpression(IntegerType(), parser_info.value)

        elif isinstance(parser_info, NoneExpressionParserInfo):
            return LiteralExpression(NoneType(), None)

        elif isinstance(parser_info, NumberExpressionParserInfo):
            return LiteralExpression(NumberType(), parser_info.value)

        elif isinstance(parser_info, StringExpressionParserInfo):
            return LiteralExpression(StringType(), parser_info.value)

        elif isinstance(parser_info, TernaryExpressionParserInfo):
            condition_expression = self.CreateMiniLanguageExpression(parser_info.condition_expression)
            if isinstance(condition_expression, Error):
                return condition_expression

            true_expression = self.CreateMiniLanguageExpression(parser_info.true_expression)
            if isinstance(true_expression, Error):
                return true_expression

            false_expression = self.CreateMiniLanguageExpression(parser_info.false_expression)
            if isinstance(false_expression, Error):
                return false_expression

            return TernaryExpression(condition_expression, true_expression, false_expression)

        elif isinstance(parser_info, TypeCheckExpressionParserInfo):
            pass # TODO

        elif isinstance(parser_info, UnaryExpressionParserInfo):
            expression = self.CreateMiniLanguageExpression(parser_info.expression)
            if isinstance(expression, Error):
                return expression

            return UnaryExpression(
                parser_info.operator,
                expression,
                parser_info.expression.regions__.self__,
            )

        elif isinstance(parser_info, VariableExpressionParserInfo):
            compile_time_var = self._compile_time_info.GetItemNoThrow(parser_info.name)  # type: ignore
            if isinstance(compile_time_var, StateMaintainer.DoesNotExist):
                return InvalidVariableNameError.Create(
                    region=parser_info.regions__.name,
                    name=parser_info.name,
                )

            assert isinstance(compile_time_var.type, MiniLanguageType), compile_time_var.type

            return VariableExpression(
                compile_time_var.type,
                parser_info.name,
                parser_info.regions__.name,
            )

        return InvalidExpressionError.Create(
            region=parser_info.regions__.self__,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _CreateCompileTimeState(
        self,
    ) -> Tuple[Dict[str, Any], Dict[str, MiniLanguageType]]:
        values: Dict[str, Any] = {}
        types: Dict[str, MiniLanguageType] = {}

        for variable_name, snapshot_values in self._compile_time_info.CreateSnapshot().items():
            assert len(snapshot_values) == 1, snapshot_values

            values[variable_name] = snapshot_values[0].value

            assert isinstance(snapshot_values[0].type, MiniLanguageType), snapshot_values[0].type
            types[variable_name] = snapshot_values[0].type

        return values, types

    # ----------------------------------------------------------------------
    @classmethod
    def _ParserInfoTypeToMiniLanguageType(
        cls,
        parser_info: TypeParserInfo,
    ) -> MiniLanguageType:
        if isinstance(parser_info, StandardTypeParserInfo):
            assert len(parser_info.items) == 1, parser_info.items
            item = parser_info.items[0]

            if item.name == "Bool":
                return BooleanType()
            elif item.name == "Char":
                return CharacterType()
            elif item.name == "Int":
                return IntegerType()
            elif item.name == "None":
                return NoneType()
            elif item.name == "Num":
                return NumberType()
            elif item.name == "Str":
                return StringType()

            assert False, item.name  # pragma: no cover

        elif isinstance(parser_info, VariantTypeParserInfo):
            return VariantType([cls._ParserInfoTypeToMiniLanguageType(type_item) for type_item in parser_info.types])

        assert False, parser_info  # pragma: no cover
