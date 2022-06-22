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

import os

from typing import (
    Any,
    Callable,
    cast,
    Dict,
    List,
    Optional,
    Set,
    Type as TypingType,
    TypeVar as TypingTypeVar,
    Union,
)

from dataclasses import dataclass, fields

import CommonEnvironment
from CommonEnvironment.DoesNotExist import DoesNotExist

from CommonEnvironmentEx.LazyContainer import LazyContainer
from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import CallHelpers

    from ..Error import CreateError, ErrorException
    from ..GlobalRegion import GlobalRegion

    from ..MiniLanguage.Expressions.BinaryExpression import BinaryExpression
    from ..MiniLanguage.Expressions.EnforceExpression import EnforceExpression
    from ..MiniLanguage.Expressions.ErrorExpression import ErrorExpression
    from ..MiniLanguage.Expressions.Expression import Expression as MiniLanguageExpression
    from ..MiniLanguage.Expressions.IdentityExpression import IdentityExpression
    from ..MiniLanguage.Expressions.IsDefinedExpression import IsDefinedExpression
    from ..MiniLanguage.Expressions.TernaryExpression import TernaryExpression
    from ..MiniLanguage.Expressions.TypeCheckExpression import TypeCheckExpression
    from ..MiniLanguage.Expressions.UnaryExpression import UnaryExpression
    from ..MiniLanguage.Expressions.VariableExpression import VariableExpression

    from ..MiniLanguage.Types.BooleanType import BooleanType
    from ..MiniLanguage.Types.CharacterType import CharacterType
    from ..MiniLanguage.Types.ExternalType import ExternalType
    from ..MiniLanguage.Types.IntegerType import IntegerType
    from ..MiniLanguage.Types.NoneType import NoneType
    from ..MiniLanguage.Types.NumberType import NumberType
    from ..MiniLanguage.Types.StringType import StringType
    from ..MiniLanguage.Types.Type import Type as MiniLanguageType
    from ..MiniLanguage.Types.VariantType import VariantType

    from ..ParserInfos.Expressions.BinaryExpressionParserInfo import (
        BinaryExpressionParserInfo,
        OperatorType as BinaryExpressionOperatorType,
    )

    from ..ParserInfos.Expressions.BooleanExpressionParserInfo import BooleanExpressionParserInfo
    from ..ParserInfos.Expressions.CallExpressionParserInfo import CallExpressionParserInfo
    from ..ParserInfos.Expressions.CharacterExpressionParserInfo import CharacterExpressionParserInfo
    from ..ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ..ParserInfos.Expressions.IntegerExpressionParserInfo import IntegerExpressionParserInfo
    from ..ParserInfos.Expressions.NestedTypeExpressionParserInfo import NestedTypeExpressionParserInfo
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
class CompileTimeInfo(object):
    type: MiniLanguageType
    value: Any
    region: Optional[GlobalRegion] # BugBug: Is this ever used?


# ----------------------------------------------------------------------
InvalidCompileTimeTypeError                 = CreateError(
    "Invalid compile-time type",
)

InvalidCompileTimeExpressionError           = CreateError(
    "Invalid compile-time expression",
)

InvalidVariableNameError                    = CreateError(
    "'{name}' is not a defined compile-time variable",
    name=str,
)

InvalidFunctionError                        = CreateError(
    "Invalid compile-time function",
)

InvalidFunctionNameError                    = CreateError(
    "'{name}' is not a defined compile-time function",
    name=str,
)


# ----------------------------------------------------------------------
def _AugmentEnforceExpressionArguments(*args, **kwargs):
    return __AugmentEnforceExpressionArguments(*args, **kwargs)

def _AugmentErrorExpressionArguments(*args, **kwargs):
    return __AugmentErrorExpressionArguments(*args, **kwargs)

COMPILE_TIME_KWARGS_AUGMENTATION_MAP: Dict[
    TypingType[MiniLanguageExpression],
    Optional[
        Callable[                               # creation of the expression.
            [
                CallExpressionParserInfo,
                Dict[str, CallHelpers.ArgumentInfo],
            ],
            Dict[str, CallHelpers.ArgumentInfo],
        ]
    ]
]                                           = {
    EnforceExpression: _AugmentEnforceExpressionArguments,
    ErrorExpression: _AugmentErrorExpressionArguments,
    IsDefinedExpression: None,
}

del _AugmentEnforceExpressionArguments
del _AugmentErrorExpressionArguments


# BugBug: Turn this into a class

# ----------------------------------------------------------------------
def EvalExpression(
    parser_info: ExpressionParserInfo,
    compile_time_info_items: List[Dict[str, CompileTimeInfo]],
) -> MiniLanguageExpression.EvalResult:
    compile_time_values = _CreateLazyValuesDict(compile_time_info_items)
    compile_time_types = _CreateLazyTypesDict(compile_time_info_items)

    expression = _ToExpression(
        parser_info,
        compile_time_values,
        compile_time_types,
        set(),
    )

    return expression.Eval(compile_time_values, compile_time_types)  # type: ignore


# ----------------------------------------------------------------------
def EvalType(
    parser_info: ExpressionParserInfo,
    compile_time_info_items: List[Dict[str, CompileTimeInfo]],
) -> Union[
    MiniLanguageType,
    ExpressionParserInfo,
]:
    return _ToType(
        parser_info,
        _CreateLazyValuesDict(compile_time_info_items),
        _CreateLazyTypesDict(compile_time_info_items),
        set(),
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
_LazyDictValueT                             = TypingTypeVar("_LazyDictValueT")

def _CreateLazyDictImpl(
    compile_time_info_items: List[Dict[str, CompileTimeInfo]],
    get_value_func: Callable[[CompileTimeInfo], _LazyDictValueT],
) -> Callable[[], Dict[str, _LazyDictValueT]]:
    # We are splitting the values here rather than taking the types and values as input parameters,
    # as evaluating the expression may alter the types dictionary; we don't want those changes to
    # be visible outside of this method (unless used explicitly be the return value of this method).

    # ----------------------------------------------------------------------
    def Impl():
        result = {}

        for compile_time_info_item in compile_time_info_items:
            for key, value in compile_time_info_item.items():
                result[key] = get_value_func(value)

        return result

    # ----------------------------------------------------------------------

    return Impl


# ----------------------------------------------------------------------
def _CreateLazyValuesDict(
    compile_time_info_items: List[Dict[str, CompileTimeInfo]],
) -> LazyContainer[Dict[str, Any]]:
    return LazyContainer(_CreateLazyDictImpl(compile_time_info_items, lambda value: value.value))


# ----------------------------------------------------------------------
def _CreateLazyTypesDict(
    compile_time_info_items: List[Dict[str, CompileTimeInfo]],
) -> LazyContainer[Dict[str, MiniLanguageType]]:
    return LazyContainer(_CreateLazyDictImpl(compile_time_info_items, lambda value: value.type))


# ----------------------------------------------------------------------
def _ToExpression(
    parser_info: ExpressionParserInfo,
    compile_time_values: LazyContainer[Dict[str, CompileTimeInfo]],
    compile_time_types: LazyContainer[Dict[str, MiniLanguageType]],
    suppress_warnings_set: Set[str],
) -> MiniLanguageExpression:
    if isinstance(parser_info, BinaryExpressionParserInfo):
        mini_language_operator = parser_info.operator.ToMiniLanguageOperatorType()
        if mini_language_operator is not None:
            return BinaryExpression(
                _ToExpression(
                    parser_info.left_expression,
                    compile_time_values,
                    compile_time_types,
                    suppress_warnings_set,
                ),
                mini_language_operator,
                _ToExpression(
                    parser_info.right_expression,
                    compile_time_values,
                    compile_time_types,
                    suppress_warnings_set,
                ),
                parser_info.left_expression.regions__.self__,
            )

    elif isinstance(parser_info, BooleanExpressionParserInfo):
        return IdentityExpression(BooleanType(), parser_info.value)

    elif isinstance(parser_info, CallExpressionParserInfo):
        if parser_info.is_compile_time__:
            return _ToCallExpression(
                parser_info,
                compile_time_values,
                compile_time_types,
                suppress_warnings_set,
            )

    elif isinstance(parser_info, CharacterExpressionParserInfo):
        return IdentityExpression(CharacterType(), parser_info.value)

    elif isinstance(parser_info, FuncOrTypeExpressionParserInfo):
        if isinstance(parser_info.value, MiniLanguageType):
            return IdentityExpression(parser_info.value, DoesNotExist.instance)
        elif isinstance(parser_info.value, str):
            return IdentityExpression(ExternalType(parser_info.value), DoesNotExist.instance)
        else:
            return IdentityExpression(parser_info.value.EvalType(), parser_info.value)

    elif isinstance(parser_info, IntegerExpressionParserInfo):
        return IdentityExpression(IntegerType(), parser_info.value)

    elif isinstance(parser_info, NoneExpressionParserInfo):
        return IdentityExpression(NoneType(), None)

    elif isinstance(parser_info, NumberExpressionParserInfo):
        return IdentityExpression(NumberType(), parser_info.value)

    elif isinstance(parser_info, StringExpressionParserInfo):
        return IdentityExpression(StringType(), parser_info.value)

    elif isinstance(parser_info, TernaryExpressionParserInfo):
        return TernaryExpression(
            _ToExpression(
                parser_info.condition_expression,
                compile_time_values,
                compile_time_types,
                suppress_warnings_set,
            ),
            _ToExpression(
                parser_info.true_expression,
                compile_time_values,
                compile_time_types,
                suppress_warnings_set,
            ),
            _ToExpression(
                parser_info.false_expression,
                compile_time_values,
                compile_time_types,
                suppress_warnings_set,
            ),
        )

    elif isinstance(parser_info, TypeCheckExpressionParserInfo):
        expression = _ToExpression(
            parser_info.expression,
            compile_time_values,
            compile_time_types,
            suppress_warnings_set,
        )

        mini_language_type = _ToType(
            parser_info.type,
            compile_time_values,
            compile_time_types,
            suppress_warnings_set,
        )

        if isinstance(mini_language_type, MiniLanguageType):
            return TypeCheckExpression(parser_info.operator, expression, mini_language_type)
        else:
            # BugBug: expression will be IdentityExpression, type will be ExternalType
            return IdentityExpression(BooleanType(), False) # BugBug: Hard-coded

    elif isinstance(parser_info, UnaryExpressionParserInfo):
        expression = _ToExpression(
            parser_info.expression,
            compile_time_values,
            compile_time_types,
            suppress_warnings_set,
        )

        return UnaryExpression(
            parser_info.operator,
            expression,
            parser_info.expression.regions__.self__,
        )

    elif isinstance(parser_info, VariableExpressionParserInfo):
        if parser_info.is_compile_time__:
            compile_time_type = compile_time_types.get(parser_info.name, DoesNotExist.instance)

            if compile_time_type is DoesNotExist.instance:
                if parser_info.name not in suppress_warnings_set:
                    raise ErrorException(
                        InvalidVariableNameError.Create(
                            region=parser_info.regions__.name,
                            name=parser_info,
                        ),
                    )

                compile_time_type = NoneType()

            return VariableExpression(
                compile_time_type,
                parser_info.name,
                parser_info.regions__.name,
            )

    raise ErrorException(
        InvalidCompileTimeExpressionError.Create(
            region=parser_info.regions__.self__,
        ),
    )


# ----------------------------------------------------------------------
def _ToCallExpression(
    parser_info: CallExpressionParserInfo,
    compile_time_values: LazyContainer[Dict[str, CompileTimeInfo]],
    compile_time_types: LazyContainer[Dict[str, MiniLanguageType]],
    suppress_warnings_set: Set[str],
) -> MiniLanguageExpression:
    expression = _ToExpression(
        parser_info.expression,
        compile_time_values,
        compile_time_types,
        suppress_warnings_set,
    )

    eval_result = expression.Eval(compile_time_values, compile_time_types)  # type: ignore

    expression_type = cast(TypingType[MiniLanguageExpression], eval_result.value)

    augment_kwargs_func = COMPILE_TIME_KWARGS_AUGMENTATION_MAP.get(expression_type, DoesNotExist.instance)
    if augment_kwargs_func is DoesNotExist.instance:
        raise ErrorException(
            InvalidFunctionError.Create(
                region=parser_info.expression.regions__.self__,
            ),
        )

    # If we are looking at a call to IsDefined!, we want to suppress errors associated with
    # variables that are not defined downstream. Add a placeholder variable if one doesn't
    # already exist. We can't perfectly handle all scenarios, so support the most common knowing
    # that we will see type errors associated with undefined variables if we aren't able to
    # explicitly suppress them.
    if (
        expression_type == IsDefinedExpression
        and not isinstance(parser_info.arguments, bool)
        and len(parser_info.arguments.arguments) == 1
        and isinstance(parser_info.arguments.arguments[0].expression, VariableExpressionParserInfo)
    ):
        suppress_warnings_set.add(parser_info.arguments.arguments[0].expression.name)

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
            arg_expression_result = _ToExpression(
                argument.expression,
                compile_time_values,
                compile_time_types,
                suppress_warnings_set,
            )

            arg_info = CallHelpers.ArgumentInfo(
                arg_expression_result,
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
        assert not isinstance(augment_kwargs_func, DoesNotExist)
        keyword_args = augment_kwargs_func(parser_info, keyword_args)

    # Map the arguments provided to the parameters required by the expression type
    argument_map = CallHelpers.CreateArgumentMap(
        expression_type.__name__,
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


# ----------------------------------------------------------------------
def _ToType(
    parser_info: ExpressionParserInfo,
    compile_time_values: LazyContainer[Dict[str, CompileTimeInfo]],
    compile_time_types: LazyContainer[Dict[str, MiniLanguageType]],
    suppress_warnings_set: Set[str],
) -> Union[MiniLanguageType, ExpressionParserInfo]:
    if parser_info.IsType() is not False:
        if isinstance(parser_info, BinaryExpressionParserInfo):
            result = _ToBinaryExpressionType(
                parser_info,
                compile_time_values,
                compile_time_types,
                suppress_warnings_set,
            )

            if result is not None:
                return result

        elif isinstance(parser_info, FuncOrTypeExpressionParserInfo):
            if isinstance(parser_info.value, MiniLanguageType):
                return parser_info.value
            elif isinstance(parser_info.value, str):
                return parser_info

        elif isinstance(parser_info, NestedTypeExpressionParserInfo):
            contained_types = [
                _ToType(
                    contained_type,
                    compile_time_values.Clone(),
                    compile_time_types.Clone(),
                    set(suppress_warnings_set),
                )
                for contained_type in parser_info.types
            ]

            if all(isinstance(contained_type, ExpressionParserInfo) for contained_type in contained_types):
                return NestedTypeExpressionParserInfo.Create(
                    [parser_info.regions__.self__, ],
                    cast(List[ExpressionParserInfo], contained_types),
                )

        elif isinstance(parser_info, NoneExpressionParserInfo):
            if parser_info.is_compile_time_strict__:
                return NoneType()

            return parser_info

        elif isinstance(parser_info, TernaryExpressionParserInfo):
            expression = _ToExpression(
                parser_info.condition_expression,
                compile_time_values,
                compile_time_types,
                suppress_warnings_set,
            )

            expression_result = expression.Eval(compile_time_values, compile_time_types)  # type: ignore
            expression_result = expression_result.type.ToBoolValue(expression_result.value)

            type_expression = parser_info.true_expression if expression_result else parser_info.false_expression

            return _ToType(
                type_expression,
                compile_time_values,
                compile_time_types,
                suppress_warnings_set,
            )

        elif isinstance(parser_info, TupleExpressionParserInfo):
            contained_types = [
                _ToType(
                    contained_type,
                    compile_time_values.Clone(),
                    compile_time_types.Clone(),
                    set(suppress_warnings_set),
                )
                for contained_type in parser_info.types
            ]

            if all(isinstance(contained_type, ExpressionParserInfo) for contained_type in contained_types):
                return TupleExpressionParserInfo.Create(
                    [parser_info.regions__.self__, parser_info.regions__.mutability_modifier],
                    cast(List[ExpressionParserInfo], contained_types),
                    parser_info.mutability_modifier,
                )

        elif isinstance(parser_info, VariantExpressionParserInfo):
            contained_types = [
                _ToType(
                    contained_type,
                    compile_time_values.Clone(),
                    compile_time_types.Clone(),
                    set(suppress_warnings_set),
                )
                for contained_type in parser_info.types
            ]

            if all(isinstance(contained_type, MiniLanguageType) for contained_type in contained_types):
                return VariantType(cast(List[MiniLanguageType], contained_types))

            if all(isinstance(contained_type, ExpressionParserInfo) for contained_type in contained_types):
                return VariantExpressionParserInfo.Create(
                    [parser_info.regions__.self__, parser_info.regions__.mutability_modifier],
                    cast(List[ExpressionParserInfo], contained_types),
                    parser_info.mutability_modifier,
                )

    raise ErrorException(
        InvalidCompileTimeTypeError.Create(
            region=parser_info.regions__.self__,
        ),
    )


# ----------------------------------------------------------------------
def _ToBinaryExpressionType(
    parser_info: BinaryExpressionParserInfo,
    compile_time_values: LazyContainer[Dict[str, CompileTimeInfo]],
    compile_time_types: LazyContainer[Dict[str, MiniLanguageType]],
    suppress_warnings_set: Set[str],
) -> Union[None, MiniLanguageType, ExpressionParserInfo]:
    if parser_info.operator not in [
        BinaryExpressionOperatorType.LogicalOr,
        BinaryExpressionOperatorType.Access,
    ]:
        return None

    left_type = _ToType(
        parser_info.left_expression,
        compile_time_values,
        compile_time_types,
        suppress_warnings_set,
    )

    if isinstance(left_type, MiniLanguageType):
        if parser_info.operator != BinaryExpressionOperatorType.LogicalOr:
            return None

        if not isinstance(left_type, NoneType):
            return left_type

        right_type = _ToType(
            parser_info.right_expression,
            compile_time_values,
            compile_time_types,
            suppress_warnings_set,
        )

        if not isinstance(right_type, MiniLanguageType):
            return None

        return right_type

    elif isinstance(left_type, ExpressionParserInfo):
        if parser_info.operator == BinaryExpressionOperatorType.LogicalOr:
            if not isinstance(left_type, NoneExpressionParserInfo):
                return left_type

            right_type = _ToType(
                parser_info.right_expression,
                compile_time_values,
                compile_time_types,
                suppress_warnings_set,
            )

            if not isinstance(right_type, ExpressionParserInfo):
                return None

            return right_type

        elif parser_info.operator == BinaryExpressionOperatorType.Access:
            right_type = _ToType(
                parser_info.right_expression,
                compile_time_values,
                compile_time_types,
                suppress_warnings_set,
            )

            if not isinstance(right_type, FuncOrTypeExpressionParserInfo):
                return None

            if isinstance(left_type, NestedTypeExpressionParserInfo):
                return NestedTypeExpressionParserInfo.Create(
                    [parser_info.regions__.self__],
                    left_type.types + [right_type, ],
                )

            return NestedTypeExpressionParserInfo.Create(
                [parser_info.regions__.self__],
                [left_type, right_type],
            )

        else:
            assert False, parser_info.operator  # pragma: no cover

    else:
        assert False, left_type  # pragma: no cover

    return None

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
