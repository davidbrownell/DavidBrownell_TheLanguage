# ----------------------------------------------------------------------
# |
# |  MiniLanguageHelpers.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-03 08:51:02
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

import copy
import os

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type as TypingType,
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
    from . import CallHelpers

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
    from ..MiniLanguage.Types.CustomType import CustomType
    from ..MiniLanguage.Types.IntegerType import IntegerType
    from ..MiniLanguage.Types.NoneType import NoneType
    from ..MiniLanguage.Types.NumberType import NumberType
    from ..MiniLanguage.Types.StringType import StringType
    from ..MiniLanguage.Types.Type import Type as MiniLanguageType
    from ..MiniLanguage.Types.VariantType import VariantType

    from ..ParserInfos.ParserInfo import ParserInfoType

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
    from ..ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo
    from ..ParserInfos.Expressions.TypeCheckExpressionParserInfo import TypeCheckExpressionParserInfo
    from ..ParserInfos.Expressions.UnaryExpressionParserInfo import UnaryExpressionParserInfo
    from ..ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo
    from ..ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class CompileTimeValue(object):
    type: MiniLanguageType
    value: Any


# ----------------------------------------------------------------------
InvalidParserInfoTypeError                  = CreateError(
    "This expression is not a valid '{type}' type expression as it is currently written",
    type=str,
)

InvalidParserInfoMiniLanguageTypeError      = CreateError(
    "Invalid '{type}' type expression",
    type=str,
)

InvalidParserInfoExpressionError            = CreateError(
    "Invalid '{type}' expression",
    type=str,
)

InvalidBinaryOperatorError                  = CreateError(
    "'{operator}' is not a valid binary operator for '{type}' expressions",
)

InvalidVariableNameError                    = CreateError(
    "'{name}' is not a defined '{type}' variable",
    type=str,
    name=str,
)

InvalidFunctionError                        = CreateError(
    "'{name}' is not a valid '{type}' function",
    type=str,
    name=str,
)


# ----------------------------------------------------------------------
def _AugmentEnforceExpressionArguments(*args, **kwargs):                    return __AugmentEnforceExpressionArguments(*args, **kwargs)
def _AugmentErrorExpressionArguments(*args, **kwargs):                      return __AugmentErrorExpressionArguments(*args, **kwargs)

COMPILE_TIME_FUNCTION_MAP: Dict[
    str,                                                # Name of the function.
    Tuple[
        TypingType[MiniLanguageExpression],             # Expression to evaluate.
        Optional[                                       # Opportunity to augment kwargs mapped to the
            Callable[                                   #    creation of the expression.
                [
                    CallExpressionParserInfo,
                    Dict[str, CallHelpers.ArgumentInfo],
                ],
                Dict[str, CallHelpers.ArgumentInfo],
            ]
        ],
    ],
]                                           = {
    "Enforce!" : (EnforceExpression, _AugmentEnforceExpressionArguments),
    "Error!" : (ErrorExpression, _AugmentErrorExpressionArguments),
    "IsDefined!" : (IsDefinedExpression, None),
}

del _AugmentEnforceExpressionArguments
del _AugmentErrorExpressionArguments


# ----------------------------------------------------------------------
def ToConfigurationType(
    parser_info: ExpressionParserInfo,
    compile_time_values: Dict[str, CompileTimeValue],
) -> MiniLanguageType:
    return _ToTypeImpl(
        parser_info,
        compile_time_values,
        ParserInfoType.Configuration,
        lambda parser_info: parser_info.ValidateAsConfigurationType(),
    )


# ----------------------------------------------------------------------
def ToTypeCustomizationType(
    parser_info: ExpressionParserInfo,
    compile_time_values: Dict[str, CompileTimeValue],
) -> MiniLanguageType:
    return _ToTypeImpl(
        parser_info,
        compile_time_values,
        ParserInfoType.TypeCustomization,
        lambda parser_info: parser_info.ValidateAsCustomizationType(),
    )


# ----------------------------------------------------------------------
def ToStandardType(
    parser_info: ExpressionParserInfo,
    compile_time_values: Dict[str, CompileTimeValue],
) -> MiniLanguageType:
    return _ToTypeImpl(
        parser_info,
        compile_time_values,
        ParserInfoType.Standard,
        lambda parser_info: parser_info.ValidateAsStandardType(),
    )


# ----------------------------------------------------------------------
def EvalExpression(
    expression_or_parser_info: Union[MiniLanguageExpression, ExpressionParserInfo],
    compile_time_values: Dict[str, CompileTimeValue],
) -> MiniLanguageExpression.EvalResult:
    if isinstance(expression_or_parser_info, MiniLanguageExpression):
        expression = expression_or_parser_info
    elif isinstance(expression_or_parser_info, ExpressionParserInfo):
        expression = ToExpression(expression_or_parser_info, compile_time_values)
    else:
        assert False, expression_or_parser_info  # pragma: no cover

    # We are splitting the values here, as evaluating the expression may alter the types dictionary;
    # we don't want that change to be visible outside of this method (unless used explicitly be the
    # return value of this method).
    types: Dict[str, MiniLanguageType] = {}
    values: Dict[str, Any] = {}

    for k, v in compile_time_values.items():
        types[k] = v.type
        values[k] = v.value

    return expression.Eval(values, types)


# ----------------------------------------------------------------------
def ToExpression(
    parser_info: ExpressionParserInfo,
    compile_time_values: Dict[str, CompileTimeValue],
) -> MiniLanguageExpression:
    parser_info_type = parser_info.parser_info_type__  # type: ignore

    if parser_info_type == ParserInfoType.Configuration:
        to_type_func = ToConfigurationType
    elif parser_info_type == ParserInfoType.TypeCustomization:
        to_type_func = ToTypeCustomizationType
    elif parser_info_type in [
        ParserInfoType.Unknown,
        ParserInfoType.Standard,
    ]:
        to_type_func = ToStandardType
    else:
        assert False, parser_info_type  # pragma: no cover

    return _ToExpressionImpl(
        parser_info,
        compile_time_values,
        parser_info_type,
        to_type_func,
        set(),
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ToTypeImpl(
    parser_info: ExpressionParserInfo,
    compile_time_values: Dict[str, CompileTimeValue],
    required_parser_info_type: ParserInfoType,
    validate_func: Callable[[ExpressionParserInfo], None],
) -> MiniLanguageType:

    _ValidateParserInfoType(parser_info, required_parser_info_type)

    if isinstance(parser_info, FuncOrTypeExpressionParserInfo):
        # Do not validate this as a Configuration type if we are looking at a compile-time
        # function call. Instead, validate it as a TypeCustomization to ensure that we aren't
        # overly strict about what values are considered to be valid.
        if (
            required_parser_info_type == ParserInfoType.Configuration
            and isinstance(parser_info.value, CustomType)
            and parser_info.value.name in COMPILE_TIME_FUNCTION_MAP
        ):
            parser_info.ValidateAsCustomizationType()
        else:
            validate_func(parser_info)

        return parser_info.value

    elif isinstance(parser_info, NoneExpressionParserInfo):
        return NoneType()

    elif isinstance(parser_info, TernaryExpressionParserInfo):
        result = EvalExpression(parser_info.condition_expression, compile_time_values)
        result = result.type.ToBoolValue(result.value)

        return _ToTypeImpl(
            parser_info.true_expression if result else parser_info.false_expression,
            compile_time_values,
            required_parser_info_type,
            validate_func,
        )

    elif isinstance(parser_info, VariantExpressionParserInfo):
        validate_func(parser_info)

        return VariantType(
            [
                _ToTypeImpl(
                    type_expression,
                    compile_time_values,
                    required_parser_info_type,
                    validate_func,
                )
                for type_expression in parser_info.types
            ],
        )

    raise ErrorException(
        InvalidParserInfoMiniLanguageTypeError.Create(
            region=parser_info.regions__.self__,
            type=required_parser_info_type.name,
        ),
    )


# ----------------------------------------------------------------------
def _ToExpressionImpl(
    parser_info: ExpressionParserInfo,
    compile_time_values: Dict[str, CompileTimeValue],
    required_parser_info_type: ParserInfoType,
    to_type_func: Callable[[ExpressionParserInfo, Dict[str, CompileTimeValue]], MiniLanguageType],
    suppress_variable_warnings: Set[str],
) -> MiniLanguageExpression:

    _ValidateParserInfoType(parser_info, required_parser_info_type)

    if isinstance(parser_info, BinaryExpressionParserInfo):
        operator = parser_info.operator.ToMiniLanguageOperatorType()

        if operator is None:
            raise ErrorException(
                InvalidBinaryOperatorError.Create(
                    region=parser_info.regions__.operator,
                    operator=parser_info.operator.name,
                    type=required_parser_info_type.name,
                ),
            )

        return BinaryExpression(
            _ToExpressionImpl(
                parser_info.left_expression,
                compile_time_values,
                required_parser_info_type,
                to_type_func,
                suppress_variable_warnings,
            ),
            operator,
            _ToExpressionImpl(
                parser_info.right_expression,
                compile_time_values,
                required_parser_info_type,
                to_type_func,
                suppress_variable_warnings,
            ),
            parser_info.left_expression.regions__.self__,
        )

    elif isinstance(parser_info, BooleanExpressionParserInfo):
        return LiteralExpression(BooleanType(), parser_info.value)

    elif isinstance(parser_info, CallExpressionParserInfo):
        result = EvalExpression(parser_info.expression, compile_time_values)
        func_name = result.type.ToStringValue(result.value)

        # Get the function expression
        result = COMPILE_TIME_FUNCTION_MAP.get(func_name, None)
        if result is None:
            raise ErrorException(
                InvalidFunctionError.Create(
                    region=parser_info.expression.regions__.self__,
                    name=func_name,
                    type=required_parser_info_type.name,
                ),
            )

        expression_type, augment_kwargs_func = result

        # If we are looking at a call to IsDefined!, we want to suppress errors associated with
        # variables that are not defined downstream. Add a placeholder variable if one doesn't
        # already exist. We can't perfectly handle all scenarios, so support the most common knowing
        # that we will see type errors associated with undefined variables if we aren't able to
        # explicitly suppress them.
        if (
            func_name == "IsDefined!"
            and not isinstance(parser_info.arguments, bool)
            and len(parser_info.arguments.arguments) == 1
            and isinstance(parser_info.arguments.arguments[0].expression, VariableExpressionParserInfo)
        ):
            suppress_variable_warnings.add(parser_info.arguments.arguments[0].expression.name)

        # Get the parameters for the expression type
        param_infos: List[CallHelpers.ParameterInfo] = []

        for field in fields(expression_type):
            # I haven't found a clean way to do this programmatically based on the innards of the
            # typing module. This code doesn't work in all scenarios (for example, it can't
            # differentiate between Optional[List[int]] and List[Optional[int]], but should be
            # good enough for use here as the ParserInfo objects follow a fairly consistent
            # pattern of how lists are used (it is always Optional[List[int]]).
            type_desc = str(field.type)

            param_infos.append(
                CallHelpers.ParameterInfo(
                    field.name,
                    None,
                    is_optional="NoneType" in type_desc,
                    is_variadic="typing.List" in type_desc,
                ),
            )

        # Extract the arguments
        positional_args: List[CallHelpers.ArgumentInfo] = []
        keyword_args: Dict[str, CallHelpers.ArgumentInfo] = {}

        if not isinstance(parser_info.arguments, bool):
            for argument in parser_info.arguments.arguments:
                arg_info = CallHelpers.ArgumentInfo(
                    _ToExpressionImpl(
                        argument.expression,
                        compile_time_values,
                        required_parser_info_type,
                        to_type_func,
                        suppress_variable_warnings,
                    ),
                    argument.regions__.self__,
                )

                if argument.keyword is None:
                    positional_args.append(arg_info)
                else:
                    # No need to check for duplicate keyword names, as that was done when creating
                    # the argument ParserInfo object.
                    assert argument.keyword not in keyword_args, argument.keyword

                    keyword_args[argument.keyword] = arg_info

        if augment_kwargs_func is not None:
            keyword_args = augment_kwargs_func(parser_info, keyword_args)

        # Map the arguments provided to the parameters required by the expression type
        argument_map = CallHelpers.CreateArgumentMap(
            func_name,
            None,
            [],
            param_infos,
            [],
            positional_args,
            keyword_args,
        )

        # We don't need to check types, as all the args are MiniLanguageExpressions

        # Create the expression
        return expression_type(**argument_map)

    elif isinstance(parser_info, CharacterExpressionParserInfo):
        return LiteralExpression(CharacterType(), parser_info.value)

    elif isinstance(parser_info, FuncOrTypeExpressionParserInfo):
        the_type = to_type_func(parser_info, compile_time_values)
        return LiteralExpression(the_type, the_type.name)

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
            _ToExpressionImpl(
                parser_info.condition_expression,
                compile_time_values,
                required_parser_info_type,
                to_type_func,
                suppress_variable_warnings,
            ),
            _ToExpressionImpl(
                parser_info.true_expression,
                compile_time_values,
                required_parser_info_type,
                to_type_func,
                suppress_variable_warnings,
            ),
            _ToExpressionImpl(
                parser_info.false_expression,
                compile_time_values,
                required_parser_info_type,
                to_type_func,
                suppress_variable_warnings,
            ),
        )

    elif isinstance(parser_info, TupleExpressionParserInfo):
        raise NotImplementedError("TODO") # TODO: Implement this

    elif isinstance(parser_info, TypeCheckExpressionParserInfo):
        return TypeCheckExpression(
            parser_info.operator,
            _ToExpressionImpl(
                parser_info.expression,
                compile_time_values,
                required_parser_info_type,
                to_type_func,
                suppress_variable_warnings,
            ),
            to_type_func(parser_info.type, compile_time_values),
        )

    elif isinstance(parser_info, UnaryExpressionParserInfo):
        return UnaryExpression(
            parser_info.operator,
            _ToExpressionImpl(
                parser_info.expression,
                compile_time_values,
                required_parser_info_type,
                to_type_func,
                suppress_variable_warnings,
            ),
            parser_info.expression.regions__.self__,
        )

    elif isinstance(parser_info, VariableExpressionParserInfo):
        compile_time_value = compile_time_values.get(parser_info.name, None)
        if compile_time_value is None and parser_info.name not in suppress_variable_warnings:
            raise ErrorException(
                InvalidVariableNameError.Create(
                    region=parser_info.regions__.name,
                    name=parser_info.name,
                    type=required_parser_info_type.name,
                ),
            )

        return VariableExpression(
            compile_time_value.type if compile_time_value is not None else NoneType(),
            parser_info.name,
            parser_info.regions__.name,
        )

    # VariantExpressionParserInfo is not processed here, as it results in a type and not an expression

    raise ErrorException(
        InvalidParserInfoExpressionError.Create(
            region=parser_info.regions__.self__,
            type=required_parser_info_type.name,
        ),
    )


# ----------------------------------------------------------------------
def _ValidateParserInfoType(
    parser_info: ExpressionParserInfo,
    required_parser_info_type: ParserInfoType,
) -> None:
    this_parser_info_type = parser_info.parser_info_type__  # type: ignore

    if not ParserInfoType.IsCompileTimeValue(this_parser_info_type):
        raise ErrorException(
            InvalidParserInfoTypeError.Create(
                region=parser_info.regions__.self__,
                type=required_parser_info_type.name,
            ),
        )


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
