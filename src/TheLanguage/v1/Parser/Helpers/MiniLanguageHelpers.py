# ----------------------------------------------------------------------
# |
# |  MiniLanguageHelpers.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 10:56:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when extracting MiniLanguage information"""

import os

from typing import (
    Any,
    Callable,
    cast,
    Dict,
    List,
    Optional,
    Tuple,
    Type as TypingType,
    Union,
)

from dataclasses import fields

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import CallHelpers

    from ..ParserInfos.ParserInfo import CompileTimeValue, ParserInfoType

    from ..ParserInfos.Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo
    from ..ParserInfos.Expressions.BooleanExpressionParserInfo import BooleanExpressionParserInfo
    from ..ParserInfos.Expressions.CallExpressionParserInfo import CallExpressionParserInfo
    from ..ParserInfos.Expressions.CharacterExpressionParserInfo import CharacterExpressionParserInfo
    from ..ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ..ParserInfos.Expressions.IntegerExpressionParserInfo import IntegerExpressionParserInfo
    from ..ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ..ParserInfos.Expressions.NumberExpressionParserInfo import NumberExpressionParserInfo
    from ..ParserInfos.Expressions.StringExpressionParserInfo import StringExpressionParserInfo
    from ..ParserInfos.Expressions.TernaryExpressionParserInfo import TernaryExpressionParserInfo
    from ..ParserInfos.Expressions.TypeCheckExpressionParserInfo import TypeCheckExpressionParserInfo
    from ..ParserInfos.Expressions.UnaryExpressionParserInfo import UnaryExpressionParserInfo
    from ..ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo
    from ..ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo

    from ..Error import CreateError, ErrorException

    from ..MiniLanguage.Expressions.BinaryExpression import BinaryExpression
    from ..MiniLanguage.Expressions.EnforceExpression import EnforceExpression
    from ..MiniLanguage.Expressions.ErrorExpression import ErrorExpression
    from ..MiniLanguage.Expressions.Expression import Expression as MiniLanguageExpression
    from ..MiniLanguage.Expressions.IsDefinedExpression import IsDefinedExpression
    from ..MiniLanguage.Expressions.LiteralExpression import LiteralExpression
    from ..MiniLanguage.Expressions.TernaryExpression import TernaryExpression
    from ..MiniLanguage.Expressions.TypeCheckExpression import TypeCheckExpression
    from ..MiniLanguage.Expressions.UnaryExpression import UnaryExpression
    from ..MiniLanguage.Expressions.VariableExpression import VariableExpression

    from ..MiniLanguage.Types.BooleanType import BooleanType
    from ..MiniLanguage.Types.CharacterType import CharacterType
    from ..MiniLanguage.Types.IntegerType import IntegerType
    from ..MiniLanguage.Types.NoneType import NoneType
    from ..MiniLanguage.Types.NumberType import NumberType
    from ..MiniLanguage.Types.StringType import StringType
    from ..MiniLanguage.Types.Type import Type as MiniLanguageType
    from ..MiniLanguage.Types.VariantType import VariantType


# ----------------------------------------------------------------------
InvalidParserInfoTypeError                  = CreateError(
    "Invalid compile-time expression",
)

InvalidBinaryOperatorError                  = CreateError(
    "'{operator}' is not a valid binary operator for compile-time expressions",
    operator=str,
)

InvalidFunctionError                        = CreateError(
    "'{name}' is not a valid compile-time function",
    name=str,
)

InvalidVariableNameError                    = CreateError(
    "'{name}' is not a valid compile-time variable",
    name=str,
)

InvalidParserInfoExpressionError            = CreateError(
    "Invalid compile-time expression",
)

InvalidTypeNameError                        = CreateError(
    "'{name}' is not a valid compile-time type",
    name=str,
)

InvalidParserInfoMiniLanguageTypeError      = CreateError(
    "Invalid compile-time type expression",
)


# ----------------------------------------------------------------------
def _AugmentEnforceExpressionArguments(*args, **kwargs):                    return __AugmentEnforceExpressionArguments(*args, **kwargs)  # pylint: disable=multiple-statements
def _AugmentErrorExpressionArguments(*args, **kwargs):                      return __AugmentErrorExpressionArguments(*args, **kwargs)  # pylint: disable=multiple-statements

FUNCTION_MAP: Dict[
    str,                                                # Name of the function
    Tuple[
        TypingType[MiniLanguageExpression],             # Expression to evaluate.
        Optional[                                       # Opportunity to augment kwargs mapped to the
            Callable[                                   #   creation of the Expression.
                [
                    CallExpressionParserInfo,
                    Dict[str, CallHelpers.ArgumentInfo],
                ],
                Dict[str, CallHelpers.ArgumentInfo],
            ]
        ],
    ]
]                                           = {
    "Enforce!" : (EnforceExpression, _AugmentEnforceExpressionArguments),
    "Error!" : (ErrorExpression, _AugmentErrorExpressionArguments),
    "IsDefined!" : (IsDefinedExpression, None),
}

del _AugmentErrorExpressionArguments
del _AugmentEnforceExpressionArguments


# ----------------------------------------------------------------------
def ParserInfoToExpression(
    parser_info: ExpressionParserInfo,
    compile_time_values: Dict[str, CompileTimeValue],
) -> MiniLanguageExpression:
    if parser_info.parser_info_type__.value > ParserInfoType.MaxCompileValue.value:  # type: ignore
        raise ErrorException(
            InvalidParserInfoTypeError.Create(
                region=parser_info.regions__.self__,
            ),
        )

    if isinstance(parser_info, BinaryExpressionParserInfo):
        operator = parser_info.operator.ToMiniLanguageOperatorType()
        if operator is None:
            raise ErrorException(
                InvalidBinaryOperatorError.Create(
                    region=parser_info.regions__.operator,
                    operator=parser_info.operator.name,
                ),
            )

        return BinaryExpression(
            ParserInfoToExpression(parser_info.left_expression, compile_time_values),
            operator,
            ParserInfoToExpression(parser_info.right_expression, compile_time_values),
            parser_info.left_expression.regions__.self__,
        )

    elif isinstance(parser_info, BooleanExpressionParserInfo):
        return LiteralExpression(BooleanType(), parser_info.value)

    elif isinstance(parser_info, CallExpressionParserInfo):
        result = EvalMiniLanguageExpression(parser_info.expression, compile_time_values)
        func_name = result[1].ToStringValue(result[0])

        # Get the function expression
        result = FUNCTION_MAP.get(func_name, None)
        if result is None:
            raise ErrorException(
                InvalidFunctionError.Create(
                    region=parser_info.expression.regions__.self__,
                    name=func_name,
                ),
            )

        expression_type, augment_kwargs_func = result

        # Get the parameters for the expression type
        param_infos: List[CallHelpers.ParameterInfo] = []
        none_type = type(None)

        for field in fields(expression_type):
            field_args = getattr(field.type, "__args__", [])

            param_infos.append(
                CallHelpers.ParameterInfo(
                    field.name,
                    None,
                    is_optional=none_type in field_args,
                    is_variadic=isinstance(field_args, tuple) and len(field_args) == 1,
                ),
            )

        # Extract the arguments
        positional_args: List[CallHelpers.ArgumentInfo] = []
        keyword_args: Dict[str, CallHelpers.ArgumentInfo] = {}

        if not isinstance(parser_info.arguments, bool):
            for argument in parser_info.arguments.arguments:
                arg_info = CallHelpers.ArgumentInfo(
                    ParserInfoToExpression(argument.expression, compile_time_values),
                    argument.regions__.self__,
                )

                if argument.keyword is None:
                    positional_args.append(arg_info)
                else:
                    # We are checking for duplicate keyword names when creating the corresponding
                    # ParserInfo objects.
                    assert argument.keyword not in keyword_args, argument.keyword
                    keyword_args[argument.keyword] = arg_info

        if augment_kwargs_func:
            keyword_args = augment_kwargs_func(parser_info, keyword_args)

        # Map the arguments to the parameters
        argument_map = CallHelpers.CreateArgumentMap(
            func_name,
            None,
            [],
            param_infos,
            [],
            positional_args,
            keyword_args,
        )

        # We don't need to type check, as all args are MiniLanguage expressions
        updated_argument_map = {}

        for k, v in argument_map.items():
            if isinstance(v, list):
                v = [item.value for item in v]
            else:
                v = v.value

            updated_argument_map[k] = v

        return expression_type(**updated_argument_map)

    elif isinstance(parser_info, CharacterExpressionParserInfo):
        return LiteralExpression(CharacterType(), parser_info.value)

    elif isinstance(parser_info, FuncOrTypeExpressionParserInfo):
        # BugBug: This is a hack
        # BugBug: Need to add "CustomType" to MiniLanguage (or is it CustomExpression?)
        # BugBug: Add method to get DottedType/FullyQualifiedCustomType

        # When here, we are most likely looking at the name of a compile-time function
        parser_info.ValidateAsCompileTimeType(
            require_mini_language_type=False,
        )

        return LiteralExpression(StringType(), parser_info.name)

    elif isinstance(parser_info, IntegerExpressionParserInfo):
        return LiteralExpression(IntegerType(), parser_info.value)

    elif isinstance(parser_info, NoneExpressionParserInfo):
        return LiteralExpression(NoneType(), None)

    elif isinstance(parser_info, NumberExpressionParserInfo):
        return LiteralExpression(NumberType(), parser_info.value)

    elif isinstance(parser_info, StringExpressionParserInfo):
        return LiteralExpression(StringType(), parser_info.value)

    elif isinstance(parser_info, TernaryExpressionParserInfo):
        return TernaryExpression(
            ParserInfoToExpression(parser_info.condition_expression, compile_time_values),
            ParserInfoToExpression(parser_info.true_expression, compile_time_values),
            ParserInfoToExpression(parser_info.false_expression, compile_time_values),
        )

    elif isinstance(parser_info, TypeCheckExpressionParserInfo):
        return TypeCheckExpression(
            parser_info.operator,
            ParserInfoToExpression(parser_info.expression, compile_time_values),
            ParserInfoToType(parser_info.type, compile_time_values),
        )

    elif isinstance(parser_info, UnaryExpressionParserInfo):
        return UnaryExpression(
            parser_info.operator,
            ParserInfoToExpression(parser_info.expression, compile_time_values),
            parser_info.expression.regions__.self__,
        )

    elif isinstance(parser_info, VariableExpressionParserInfo):
        compile_time_value = compile_time_values.get(parser_info.name, None)
        if compile_time_value is None:
            raise ErrorException(
                InvalidVariableNameError.Create(
                    region=parser_info.regions__.name,
                    name=parser_info.name,
                ),
            )

        return VariableExpression(
            compile_time_value.type,
            parser_info.name,
            parser_info.regions__.name,
        )

    raise ErrorException(
        InvalidParserInfoExpressionError.Create(
            region=parser_info.regions__.self__,
        ),
    )


# ----------------------------------------------------------------------
def ParserInfoToType(
    parser_info: ExpressionParserInfo,
    compile_time_values: Dict[str, CompileTimeValue],
) -> MiniLanguageType:
    if parser_info.parser_info_type__.value > ParserInfoType.MaxCompileValue.value:  # type: ignore
        raise ErrorException(
            InvalidParserInfoTypeError.Create(
                region=parser_info.regions__.self__,
            ),
        )

    if isinstance(parser_info, FuncOrTypeExpressionParserInfo):
        if not isinstance(parser_info.name, MiniLanguageType):
            raise ErrorException(
                InvalidTypeNameError.Create(
                    region=parser_info.regions__.name,
                    name=parser_info.name,
                ),
            )

        parser_info.ValidateAsCompileTimeType(
            require_mini_language_type=True,
        )

        return cast(MiniLanguageType, parser_info.name)

    elif isinstance(parser_info, NoneExpressionParserInfo):
        return NoneType()

    elif isinstance(parser_info, TernaryExpressionParserInfo):
        result = EvalMiniLanguageExpression(parser_info.condition_expression, compile_time_values)
        result = result[1].ToBoolValue(result[0])

        return ParserInfoToType(
            parser_info.true_expression if result else parser_info.false_expression,
            compile_time_values,
        )

    elif isinstance(parser_info, VariantExpressionParserInfo):
        return VariantType(
            [
                ParserInfoToType(type_expression, compile_time_values)
                for type_expression in parser_info.types
            ],
        )

    raise ErrorException(
        InvalidParserInfoMiniLanguageTypeError.Create(
            region=parser_info.regions__.self__,
        ),
    )


# ----------------------------------------------------------------------
def EvalMiniLanguageExpression(
    expression_or_parser_info: Union[MiniLanguageExpression, ExpressionParserInfo],
    compile_time_values: Dict[str, CompileTimeValue],
) -> Tuple[Any, MiniLanguageType]:
    if isinstance(expression_or_parser_info, MiniLanguageExpression):
        expression = expression_or_parser_info
    elif isinstance(expression_or_parser_info, ExpressionParserInfo):
        expression = ParserInfoToExpression(expression_or_parser_info, compile_time_values)
    else:
        assert False, expression_or_parser_info  # pragma: no cover

    types: Dict[str, MiniLanguageType] = {}
    values: Dict[str, Any] = {}

    for k, v in compile_time_values.items():
        types[k] = v.type
        values[k] = v.value

    result = expression.Eval(values, types)
    return result.value, result.type


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def __AugmentEnforceExpressionArguments(
    parser_info: CallExpressionParserInfo,
    kwargs: Dict[str, CallHelpers.ArgumentInfo],
) -> Dict[str, CallHelpers.ArgumentInfo]:
    if not isinstance(parser_info.arguments, bool):
        region = parser_info.arguments.arguments[0].regions__.self__
        kwargs["expression_region"] = CallHelpers.ArgumentInfo(region, region)

    return kwargs


# ----------------------------------------------------------------------
def __AugmentErrorExpressionArguments(
    parser_info: CallExpressionParserInfo,
    kwargs: Dict[str, CallHelpers.ArgumentInfo],
) -> Dict[str, CallHelpers.ArgumentInfo]:
    region = parser_info.regions__.self__
    kwargs["error_region"] = CallHelpers.ArgumentInfo(region, region)

    return kwargs
