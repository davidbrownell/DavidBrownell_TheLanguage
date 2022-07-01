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
    Tuple,
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
    from ..TranslationUnitRegion import TranslationUnitRegion

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

    from ..ParserInfos.Expressions.TypeCheckExpressionParserInfo import (
        TypeCheckExpressionParserInfo,
        OperatorType as TypeCheckExpressionOperatorType,
    )

    from ..ParserInfos.Expressions.UnaryExpressionParserInfo import UnaryExpressionParserInfo
    from ..ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo
    from ..ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo

    from ..ParserInfos.ParserInfo import CompileTimeInfo


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

MismatchedTypesError                        = CreateError(
    "Types must be all compile-time or all standard types",
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


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
TypeCheckCallbackType                       = Callable[
    [str, TypeCheckExpressionOperatorType, ExpressionParserInfo],
    bool,
]


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def EvalExpression(
    parser_info: ExpressionParserInfo,
    compile_time_info_items: List[Dict[str, CompileTimeInfo]],
    type_check_callback: Optional[TypeCheckCallbackType]=None,
) -> MiniLanguageExpression.EvalResult:
    helper = _Helper.Create(compile_time_info_items, type_check_callback)

    expression = helper.ToExpression(parser_info)
    return helper.Eval(expression)


# ----------------------------------------------------------------------
def EvalType(
    parser_info: ExpressionParserInfo,
    compile_time_info_items: List[Dict[str, CompileTimeInfo]],
    type_check_callback: Optional[TypeCheckCallbackType]=None,
) -> Union[
    MiniLanguageType,
    ExpressionParserInfo,
]:
    return _Helper.Create(compile_time_info_items, type_check_callback).ToType(parser_info)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _Helper(object):
    """Object that makes it easier to pass around all of the variables required to implement this functionality"""

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        compile_time_info_items: List[Dict[str, CompileTimeInfo]],
        type_check_callback: Optional[TypeCheckCallbackType],
    ) -> "_Helper":
        return cls(
            cls._CreateLazyValuesDict(compile_time_info_items),
            cls._CreateLazyTypesDict(compile_time_info_items),
            type_check_callback,
            set(),
        )

    # ----------------------------------------------------------------------
    def __init__(
        self,
        compile_time_values: LazyContainer[Dict[str, Any]],
        compile_time_types: LazyContainer[Dict[str, MiniLanguageType]],
        type_check_callback: Optional[TypeCheckCallbackType],
        suppress_warnings_set: Set[str],
    ):
        self._compile_time_values                       = compile_time_values
        self._compile_time_types                        = compile_time_types
        self._type_check_callback                       = type_check_callback
        self._suppress_warnings_set: Set[str]           = suppress_warnings_set

    # ----------------------------------------------------------------------
    def Clone(self) -> "_Helper":
        return self.__class__(
            self._compile_time_values.Clone(),
            self._compile_time_types.Clone(),
            self._type_check_callback,
            set(self._suppress_warnings_set),
        )

    # ----------------------------------------------------------------------
    def ToExpression(
        self,
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageExpression:
        if isinstance(parser_info, BinaryExpressionParserInfo):
            mini_language_operator = parser_info.operator.ToMiniLanguageOperatorType()
            if mini_language_operator is not None:
                return BinaryExpression(
                    self.ToExpression(parser_info.left_expression),
                    mini_language_operator,
                    self.ToExpression(parser_info.right_expression),
                    parser_info.left_expression.regions__.self__,
                )

        elif isinstance(parser_info, BooleanExpressionParserInfo):
            return IdentityExpression(BooleanType(), parser_info.value)

        elif isinstance(parser_info, CallExpressionParserInfo):
            if parser_info.is_compile_time__:
                return self._ToCallExpression(parser_info)

        elif isinstance(parser_info, CharacterExpressionParserInfo):
            return IdentityExpression(CharacterType(), parser_info.value)

        elif isinstance(parser_info, FuncOrTypeExpressionParserInfo):
            if isinstance(parser_info.value, MiniLanguageType):
                mini_language_type = parser_info.value
                value = DoesNotExist.instance
            elif isinstance(parser_info.value, str):
                mini_language_type = ExternalType(parser_info.value)
                value = DoesNotExist.instance
            else:
                mini_language_type = parser_info.value.EvalType()
                value = parser_info.value

            return IdentityExpression(mini_language_type, value)

        elif isinstance(parser_info, IntegerExpressionParserInfo):
            return IdentityExpression(IntegerType(), parser_info.value)

        elif isinstance(parser_info, NoneExpressionParserInfo):
            if parser_info.is_compile_time__:
                return IdentityExpression(NoneType(), None)

        elif isinstance(parser_info, NumberExpressionParserInfo):
            return IdentityExpression(NumberType(), parser_info.value)

        elif isinstance(parser_info, StringExpressionParserInfo):
            return IdentityExpression(StringType(), parser_info.value)

        elif isinstance(parser_info, TernaryExpressionParserInfo):
            return TernaryExpression(
                self.ToExpression(parser_info.condition_expression),
                self.ToExpression(parser_info.true_expression),
                self.ToExpression(parser_info.false_expression),
            )

        elif isinstance(parser_info, TypeCheckExpressionParserInfo):
            expression = self.ToExpression(parser_info.expression)
            the_type = self.ToType(parser_info.type)

            if isinstance(the_type, MiniLanguageType):
                return TypeCheckExpression(parser_info.operator, expression, the_type)

            elif isinstance(the_type, ExpressionParserInfo):
                if (
                    isinstance(expression, IdentityExpression)
                    and isinstance(expression.type, ExternalType)
                    and self._type_check_callback is not None
                ):
                    result = self._type_check_callback(
                        expression.type.name,
                        parser_info.operator,
                        the_type,
                    )

                    return IdentityExpression(BooleanType(), result)

            else:
                assert False, the_type  # pragma: no cover

        elif isinstance(parser_info, UnaryExpressionParserInfo):
            return UnaryExpression(
                parser_info.operator,
                self.ToExpression(parser_info.expression),
                parser_info.expression.regions__.self__,
            )

        elif isinstance(parser_info, VariableExpressionParserInfo):
            if parser_info.is_compile_time__:
                compile_time_type = self._compile_time_types.get(parser_info.name, DoesNotExist.instance)
                if compile_time_type is DoesNotExist.instance:
                    if parser_info.name not in self._suppress_warnings_set:
                        raise ErrorException(
                            InvalidVariableNameError.Create(
                                region=parser_info.regions__.name,
                                name=parser_info.name,
                            ),
                        )

                    compile_time_type = NoneType()

                return VariableExpression(
                    compile_time_type,
                    parser_info.name,
                    parser_info.regions__.name,
                )

        raise ErrorException(
            InvalidCompileTimeExpressionError(
                region=parser_info.regions__.self__,
            ),
        )

    # ----------------------------------------------------------------------
    def ToType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> Union[MiniLanguageType, ExpressionParserInfo]:
        if parser_info.IsType() is not False:
            if isinstance(parser_info, BinaryExpressionParserInfo):
                result = self._ToBinaryExpressionType(parser_info)
                if result is not None:
                    return result

            elif isinstance(parser_info, FuncOrTypeExpressionParserInfo):
                if isinstance(parser_info.value, MiniLanguageType):
                    return parser_info.value
                elif isinstance(parser_info.value, str):
                    return parser_info

            elif isinstance(parser_info, NestedTypeExpressionParserInfo):
                are_mini_language_types, contained_types = self._ProcessContainedTypes(
                    parser_info.types,
                    parser_info.regions__.self__,
                )

                if not are_mini_language_types:
                    return NestedTypeExpressionParserInfo.Create(
                        [parser_info.regions__.self__, ],
                        cast(List[ExpressionParserInfo], contained_types),
                    )

            elif isinstance(parser_info, NoneExpressionParserInfo):
                if parser_info.is_compile_time__:
                    return NoneType()

                return parser_info

            elif isinstance(parser_info, TernaryExpressionParserInfo):
                condition_result = self.Eval(self.ToExpression(parser_info.condition_expression))
                condition_result = condition_result.type.ToBoolValue(condition_result.value)

                return self.ToType(
                    parser_info.true_expression if condition_result else parser_info.false_expression,
                )

            elif isinstance(parser_info, TupleExpressionParserInfo):
                are_mini_language_types, contained_types = self._ProcessContainedTypes(
                    parser_info.types,
                    parser_info.regions__.self__,
                )

                if not are_mini_language_types:
                    return TupleExpressionParserInfo.Create(
                        [parser_info.regions__.self__, parser_info.regions__.mutability_modifier],
                        cast(List[ExpressionParserInfo], contained_types),
                        parser_info.mutability_modifier,
                    )

            elif isinstance(parser_info, VariantExpressionParserInfo):
                are_mini_language_types, contained_types = self._ProcessContainedTypes(
                    parser_info.types,
                    parser_info.regions__.self__,
                )

                if are_mini_language_types:
                    return VariantType(cast(List[MiniLanguageType], contained_types))

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
    def Eval(
        self,
        expression: MiniLanguageExpression,
    ) -> MiniLanguageExpression.EvalResult:
        return expression.Eval(
            self._compile_time_values.Clone(),          # type: ignore
            self._compile_time_types.Clone(),           # type: ignore
        )

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    _LazyDictValueT                         = TypingTypeVar("_LazyDictValueT")

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateLazyDictImpl(
        compile_time_info_items: List[Dict[str, CompileTimeInfo]],
        get_value_func: Callable[[CompileTimeInfo], _LazyDictValueT],
    ) -> Callable[[], Dict[str, "_LazyDictValueT"]]:
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
    @classmethod
    def _CreateLazyValuesDict(
        cls,
        compile_time_info_items: List[Dict[str, CompileTimeInfo]],
    ) -> LazyContainer[Dict[str, Any]]:
        return LazyContainer(cls._CreateLazyDictImpl(compile_time_info_items, lambda info_item: info_item.value))

    # ----------------------------------------------------------------------
    @classmethod
    def _CreateLazyTypesDict(
        cls,
        compile_time_info_items: List[Dict[str, CompileTimeInfo]],
    ) -> LazyContainer[Dict[str, MiniLanguageType]]:
        return LazyContainer(cls._CreateLazyDictImpl(compile_time_info_items, lambda info_item: info_item.type))

    # ----------------------------------------------------------------------
    def _ToCallExpression(
        self,
        parser_info: CallExpressionParserInfo,
    ) -> MiniLanguageExpression:
        eval_result = self.Eval(self.ToExpression(parser_info.expression))
        function_expression_type = cast(TypingType[MiniLanguageExpression], eval_result.value)

        augment_kwargs_func = COMPILE_TIME_KWARGS_AUGMENTATION_MAP.get(function_expression_type, DoesNotExist.instance)
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
            function_expression_type == IsDefinedExpression
            and not isinstance(parser_info.arguments, bool)
            and len(parser_info.arguments.arguments) == 1
            and isinstance(parser_info.arguments.arguments[0].expression, VariableExpressionParserInfo)
        ):
            self._suppress_warnings_set.add(parser_info.arguments.arguments[0].expression.name)

        # Get the parameters for the expression type
        param_infos: List[CallHelpers.ParameterInfo] = []

        for field in fields(function_expression_type):
            # I haven't found a clean way to do this programmatically based on the innards of the
            # typing module. This code doesn't work in all scenarios (for example, it can't
            # differentiate between Optional[List[int]] and List[Optional[int]], but should be
            # good enough for use here as the ParserInfo objects follow a fairly consistent
            # pattern of how lists are used (it is always Optional[List[int]]).
            type_desc = str(field.type)

            param_infos.append(
                CallHelpers.ParameterInfo(
                    field.name,
                    region=None,
                    is_optional="NoneType" in type_desc,
                    is_variadic="typing.List" in type_desc,
                    context=None,
                ),
            )

        # Extract the arguments
        positional_args: List[CallHelpers.ArgumentInfo] = []
        keyword_args: Dict[str, CallHelpers.ArgumentInfo] = {}

        if not isinstance(parser_info.arguments, bool):
            for argument in parser_info.arguments.arguments:
                arg_expression_result = self.ToExpression(argument.expression)

                arg_info = CallHelpers.ArgumentInfo(
                    argument.regions__.self__,
                    context=arg_expression_result,
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
            function_expression_type.__name__,
            None,
            [],
            param_infos,
            [],
            positional_args,
            keyword_args,
        )

        # We don't need to check types, as all the args are MiniLanguageExpressions

        # Create the expression with the arguments (we do not need the parameters)
        return function_expression_type(
            **{
                k: argument
                for k, (parameter, argument) in argument_map.items()
            }
        )

    # ----------------------------------------------------------------------
    def _ToBinaryExpressionType(
        self,
        parser_info: BinaryExpressionParserInfo,
    ) -> Union[None, MiniLanguageType, ExpressionParserInfo]:
        if parser_info.operator not in [
            BinaryExpressionOperatorType.LogicalOr,
            BinaryExpressionOperatorType.Access,
        ]:
            return None

        left_type = self.ToType(parser_info.left_expression)

        if isinstance(left_type, MiniLanguageType):
            if parser_info.operator != BinaryExpressionOperatorType.LogicalOr:
                return None

            if not isinstance(left_type, NoneType):
                return left_type

            right_type = self.ToType(parser_info.right_expression)

            return right_type if isinstance(right_type, MiniLanguageType) else None

        elif isinstance(left_type, ExpressionParserInfo):
            if parser_info.operator == BinaryExpressionOperatorType.LogicalOr:
                if not isinstance(left_type, NoneExpressionParserInfo):
                    return left_type

                right_type = self.ToType(parser_info.right_expression)

                return right_type if isinstance(right_type, ExpressionParserInfo) else None

            elif parser_info.operator == BinaryExpressionOperatorType.Access:
                right_type = self.ToType(parser_info.right_expression)

                if not isinstance(right_type, FuncOrTypeExpressionParserInfo):
                    return None

                if isinstance(left_type, NestedTypeExpressionParserInfo):
                    return NestedTypeExpressionParserInfo.Create(
                        [parser_info.regions__.self__, ],
                        left_type.types + [right_type, ],
                    )

                return NestedTypeExpressionParserInfo.Create(
                    [parser_info.regions__.self__, ],
                    [left_type, right_type, ],
                )

            else:
                assert False, parser_info.operator  # pragma: no cover

        else:
            assert False, left_type  # pragma: no cover

    # ----------------------------------------------------------------------
    def _ProcessContainedTypes(
        self,
        contained_types: List[ExpressionParserInfo],
        region: TranslationUnitRegion,
    ) -> Tuple[
        bool,
        Union[
            List[MiniLanguageType],
            List[ExpressionParserInfo],
        ]
    ]:
        results = [self.Clone().ToType(contained_type) for contained_type in contained_types]

        assert results

        is_mini_language = isinstance(results[0], MiniLanguageType)

        for result_type in results[1:]:
            if isinstance(result_type, MiniLanguageType) != is_mini_language:
                raise ErrorException(
                    MismatchedTypesError.Create(
                        region=region,
                    ),
                )

        return (
            is_mini_language,
            cast(Union[List[MiniLanguageType], List[ExpressionParserInfo]], results),
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
