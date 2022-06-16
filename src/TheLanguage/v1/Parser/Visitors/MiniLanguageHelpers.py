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
    Union,
)

from dataclasses import dataclass, fields

import CommonEnvironment
from CommonEnvironment.DoesNotExist import DoesNotExist
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import CallHelpers
    from .NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ..Error import CreateError, ErrorException
    from ..GlobalRegion import GlobalRegion

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

    from ..ParserInfos.ParserInfo import ParserInfo, ParserInfoType

    from ..ParserInfos.Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo

    from ..ParserInfos.Expressions.BinaryExpressionParserInfo import (
        BinaryExpressionParserInfo,
        OperatorType as BinaryExpressionParserInfoOperatorType,
    )

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

    from ..ParserInfos.Statements.StatementParserInfo import StatementParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class CompileTimeInfo(object):
    type: MiniLanguageType
    value: Any
    region: Optional[GlobalRegion]


# ----------------------------------------------------------------------
InvalidParserInfoMiniLanguageTypeError      = CreateError(
    "Invalid compile-time type",
)

InvalidParserInfoExpressionError            = CreateError(
    "Invalid compile-time expression",
)

InvalidTypeError                            = CreateError(
    "'{name}' is not a defined type or function",
    name=str,
)

InvalidVariableNameError                    = CreateError(
    "'{name}' is not a defined compile-time variable",
    name=str,
)

InvalidFunctionError                        = CreateError(
    "Invalid 'compile-time function",
)

InvalidIsSupportedValueExpressionError      = CreateError(
    "Type check expressions cannot use a template as a query parameter",
)


# ----------------------------------------------------------------------
def _AugmentEnforceExpressionArguments(*args, **kwargs):                    return __AugmentEnforceExpressionArguments(*args, **kwargs)
def _AugmentErrorExpressionArguments(*args, **kwargs):                      return __AugmentErrorExpressionArguments(*args, **kwargs)

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
def EvalExpression(
    expression_or_parser_info: Union[MiniLanguageExpression, ExpressionParserInfo],
    compile_time_infos_items: List[Dict[str, CompileTimeInfo]],
    namespace_stack: List[NamespaceInfo],
) -> MiniLanguageExpression.EvalResult:
    if isinstance(expression_or_parser_info, MiniLanguageExpression):
        expression = expression_or_parser_info
    elif isinstance(expression_or_parser_info, ExpressionParserInfo):
        expression = ToExpression(expression_or_parser_info, compile_time_infos_items, namespace_stack)
    else:
        assert False, expression_or_parser_info  # pragma: no cover

    # We are splitting the values here rather than taking the types and values as input parameters,
    # as evaluating the expression may alter the types dictionary; we don't want those changes to
    # be visible outside of this method (unless used explicitly be the return value of this method).

    # BugBug: Lazily evaluate these

    types: Dict[str, MiniLanguageType] = {}
    values: Dict[str, Any] = {}

    for compile_time_infos_item in compile_time_infos_items:
        for k, v in compile_time_infos_item.items():
            types[k] = v.type
            values[k] = v.value

    return expression.Eval(values, types)


# ----------------------------------------------------------------------
def ToType(
    parser_info: ExpressionParserInfo,
    compile_time_infos_items: List[Dict[str, CompileTimeInfo]],
    namespace_stack: List[NamespaceInfo],
) -> MiniLanguageType:
    assert ParserInfoType.IsCompileTime(parser_info.parser_info_type__), parser_info.parser_info_type__

    if isinstance(parser_info, FuncOrTypeExpressionParserInfo):
        if isinstance(parser_info.value, str):
            return _GetNamespaceType(parser_info, namespace_stack)

        if isinstance(parser_info.value, MiniLanguageType):
            return parser_info.value

    elif isinstance(parser_info, NoneExpressionParserInfo):
        return NoneType()

    elif isinstance(parser_info, TernaryExpressionParserInfo):
        condition_result = EvalExpression(
            parser_info.condition_expression,
            compile_time_infos_items,
            namespace_stack,
        )
        condition_result = condition_result.type.ToBoolValue(condition_result.value)

        return ToType(
            parser_info.true_expression if condition_result else parser_info.false_expression,
            compile_time_infos_items,
            namespace_stack,
        )

    elif isinstance(parser_info, VariantExpressionParserInfo):
        return VariantType(
            [
                ToType(type_expression, compile_time_infos_items, namespace_stack)
                for type_expression in parser_info.types
            ],
        )

    raise ErrorException(
        InvalidParserInfoMiniLanguageTypeError.Create(
            region=parser_info.regions__.self__,
        ),
    )


# ----------------------------------------------------------------------
def ToExpression(
    parser_info: ExpressionParserInfo,
    compile_time_infos_items: List[Dict[str, CompileTimeInfo]],
    namespace_stack: List[NamespaceInfo],
) -> MiniLanguageExpression:
    return _ToExpressionImpl(parser_info, compile_time_infos_items, namespace_stack, set())


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ToExpressionImpl(
    parser_info: ExpressionParserInfo,
    compile_time_infos_items: List[Dict[str, CompileTimeInfo]],
    namespace_stack: List[NamespaceInfo],
    suppress_warnings_set: Set[str],
) -> MiniLanguageExpression:
    assert ParserInfoType.IsCompileTime(parser_info.parser_info_type__), parser_info.parser_info_type__

    if isinstance(parser_info, BinaryExpressionParserInfo):
        operator = parser_info.operator.ToMiniLanguageOperatorType()
        assert operator is not None

        return BinaryExpression(
            _ToExpressionImpl(
                parser_info.left_expression,
                compile_time_infos_items,
                namespace_stack,
                suppress_warnings_set,
            ),
            operator,
            _ToExpressionImpl(
                parser_info.right_expression,
                compile_time_infos_items,
                namespace_stack,
                suppress_warnings_set,
            ),
            parser_info.left_expression.regions__.self__,
        )

    elif isinstance(parser_info, BooleanExpressionParserInfo):
        return LiteralExpression(BooleanType(), parser_info.value)

    elif isinstance(parser_info, CallExpressionParserInfo):
        expression_type = cast(
            TypingType[MiniLanguageExpression],
            EvalExpression(parser_info.expression, compile_time_infos_items, namespace_stack).value,
        )

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
                arg_info = CallHelpers.ArgumentInfo(
                    _ToExpressionImpl(
                        argument.expression,
                        compile_time_infos_items,
                        namespace_stack,
                        suppress_warnings_set,
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

    elif isinstance(parser_info, CharacterExpressionParserInfo):
        return LiteralExpression(CharacterType(), parser_info.value)

    elif isinstance(parser_info, FuncOrTypeExpressionParserInfo):
        if isinstance(parser_info.value, str):
            mini_language_type = _GetNamespaceType(parser_info, namespace_stack)
            value = mini_language_type.namespace_info

        elif isinstance(parser_info.value, MiniLanguageType):
            mini_language_type = parser_info.value
            value = parser_info.value

        else:
            mini_language_type = parser_info.value.EvalType()
            value = parser_info.value

        return LiteralExpression(mini_language_type, value)

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
                compile_time_infos_items,
                namespace_stack,
                suppress_warnings_set,
            ),
            _ToExpressionImpl(
                parser_info.true_expression,
                compile_time_infos_items,
                namespace_stack,
                suppress_warnings_set,
            ),
            _ToExpressionImpl(
                parser_info.false_expression,
                compile_time_infos_items,
                namespace_stack,
                suppress_warnings_set,
            ),
        )

    elif isinstance(parser_info, TypeCheckExpressionParserInfo):
        return TypeCheckExpression(
            parser_info.operator,
            _ToExpressionImpl(
                parser_info.expression,
                compile_time_infos_items,
                namespace_stack,
                suppress_warnings_set,
            ),
            ToType(parser_info.type, compile_time_infos_items, namespace_stack),
        )

    elif isinstance(parser_info, UnaryExpressionParserInfo):
        return UnaryExpression(
            parser_info.operator,
            _ToExpressionImpl(
                parser_info.expression,
                compile_time_infos_items,
                namespace_stack,
                suppress_warnings_set,
            ),
            parser_info.expression.regions__.self__,
        )

    elif isinstance(parser_info, VariableExpressionParserInfo):
        # BugBug: Fix this
        compile_time_value = compile_time_infos_items[-1].get(parser_info.name, None)
        if compile_time_value is None and parser_info.name not in suppress_warnings_set:
            raise ErrorException(
                InvalidVariableNameError.Create(
                    region=parser_info.regions__.name,
                    name=parser_info.name,
                ),
            )

        return VariableExpression(
            compile_time_value.type if compile_time_value is not None else NoneType(),
            parser_info.name,
            parser_info.regions__.name,
        )

    raise ErrorException(
        InvalidParserInfoExpressionError.Create(
            region=parser_info.regions__.self__,
        ),
    )


# ----------------------------------------------------------------------
class _ParserInfoMiniLanguageType(MiniLanguageType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        namespace_info: NamespaceInfo,
    ):
        self._name                          = name
        self.namespace_info                 = namespace_info

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def name(self) -> str:
        return self._name

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsSupportedValue(
        value: Any,
    ) -> bool:
        # ParserInfo types can not be represented in the MiniLanguage
        return False

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ToBoolValue(
        value: Any,
    ) -> bool:
        return False

    # ----------------------------------------------------------------------
    @Interface.override
    def ToStringValue(
        self,
        value: Any,
    ) -> str:
        return self._name

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSupportedValueOfType(
        self,
        value: Any,
        query_type: MiniLanguageType,
    ) -> MiniLanguageType.IsSupportedResult:
        return MiniLanguageType.IsSupportedResult(
            self._IsSupportedValueOfTypeImpl(query_type),
            self,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def IsNotSupportedValueOfType(
        self,
        value: Any,
        query_type: MiniLanguageType,
    ) -> MiniLanguageType.IsSupportedResult:
        return MiniLanguageType.IsSupportedResult(
            not self._IsSupportedValueOfTypeImpl(query_type),
            self,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _IsSupportedValueOfTypeImpl(
        self,
        query_type: MiniLanguageType,
    ) -> bool:
        if not isinstance(self.namespace_info, ParsedNamespaceInfo):
            raise Exception("BugBug: Module")

        if not isinstance(query_type, _ParserInfoMiniLanguageType):
            return False

        # BugBug: Implement
        return False


# ----------------------------------------------------------------------
def _GetNamespaceType(
    parser_info: FuncOrTypeExpressionParserInfo,
    namespace_stack: List[NamespaceInfo],
) -> _ParserInfoMiniLanguageType:
    assert isinstance(parser_info.value, str), parser_info.value

    for namespace_info in reversed(namespace_stack):
        namespace_info = namespace_info.children.get(parser_info.value, None)
        if namespace_info is None:
            continue

        return _ParserInfoMiniLanguageType(parser_info.value, namespace_info)

    raise ErrorException(
        InvalidTypeError.Create(
            region=parser_info.regions__.self__,
            name=parser_info.value,
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
