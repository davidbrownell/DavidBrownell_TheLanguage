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
    Dict,
    List,
    Optional,
    Tuple,
    Type as TypingsType,
    Union,
)

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin, StateMaintainer

    from ...MiniLanguage.Expressions.BinaryExpression import BinaryExpression
    from ...MiniLanguage.Expressions.Expression import Expression
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
    # ----------------------------------------------------------------------
    def ExecuteMiniLanguageFunctionStatement(
        self,
        parser_info: CallExpressionParserInfo,
    ):
        return # TODO

        assert parser_info.parser_info_type__ == ParserInfoType.CompileTime, parser_info.parser_info_type__  # type: ignore

        if not isinstance(parser_info.expression, FuncOrTypeExpressionParserInfo):
            self._errors.append(
                InvalidCompileTimeFunctionExpressionError.Create(
                    region=parser_info.expression.regions__.self__,
                ),
            )
            return

        func_name = parser_info.expression.name

        # Get the MiniLanguage statement
        if func_name in ["Enforce", "Enforce!"]:
            minilanguage_statement_type = EnforceStatement

        elif func_name in ["Error", "Error!"]:
            minilanguage_statement_type = ErrorStatement

        else:
            self._errors.append(
                InvalidCompileTimeFunctionError.Create(
                    region=parser_info.expression.regions__.self__,
                    name=func_name,
                ),
            )
            return

        # Extract the arguments
        positional_arguments: List[Expression] = []
        keyword_arguments: Dict[str, Expression] = {}

        if not isinstance(parser_info.arguments, bool):
            for argument in parser_info.arguments.arguments:
                result = self.CreateMiniLanguageExpression(argument.expression)
                if isinstance(result, Error):
                    self._errors.append(result)
                    return

                if argument.keyword is None:
                    positional_arguments.append(result)
                else:
                    keyword_arguments[argument.keyword] = result

        # Create the statement
        statement = minilanguage_statement_type.Create(*positional_arguments, **keyword_arguments)
        if isinstance(statement, Error):
            self._errors.append(statement)
            return

        # Prepare the information that will be used during argument execution
        values: Dict[str, Any] = {}
        types: Dict[str, MiniLanguageType] = {}

        for variable_name, snapshot_values in self._compile_time_info.CreateSnapshot().items():
            assert len(snapshot_values) == 1, snapshot_values

            values[variable_name] = snapshot_values[0].value

            assert isinstance(snapshot_values[0].type, MiniLanguageType), snapshot_values[0].type
            types[variable_name] = snapshot_values[0].type

        # Execute the statement
        result = statement.Execute(*self._CreateCompileTimeState())

        self._errors += result.errors       # type: ignore
        self._warnings += result.warnings   # type: ignore
        self._infos += result.infos         # type: ignore

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
