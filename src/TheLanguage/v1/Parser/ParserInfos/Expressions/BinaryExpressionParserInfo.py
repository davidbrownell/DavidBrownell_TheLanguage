# ----------------------------------------------------------------------
# |
# |  BinaryExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 16:22:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryExpressionParserInfo object"""

import os

from contextlib import contextmanager
from enum import auto, Enum
from typing import Callable, Dict, List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import CompileTimeInfo, ExpressionParserInfo, ParserInfo, ParserInfoType, TranslationUnitRegion

    from .FuncOrTypeExpressionParserInfo import InvalidCompileTimeTypeError

    from ...Error import CreateError, Error, ErrorException
    from ...MiniLanguage.Expressions.BinaryExpression import OperatorType as MiniLanguageOperatorType


# ----------------------------------------------------------------------
_initial_num_mini_language_operator_types: Optional[int] = None

class OperatorType(Enum):
    # ----------------------------------------------------------------------
    def _generate_next_value_(name, start, count, last_values):  # type: ignore  # pylint: disable=no-self-argument,unused-argument
        global _initial_num_mini_language_operator_types  # pylint: disable=global-statement

        if _initial_num_mini_language_operator_types is None:
            _initial_num_mini_language_operator_types = count

        return count

    # ----------------------------------------------------------------------

    # Operators valid within the MiniLanguage
    Multiply                                = MiniLanguageOperatorType.Multiply
    Divide                                  = MiniLanguageOperatorType.Divide
    DivideFloor                             = MiniLanguageOperatorType.DivideFloor
    Modulo                                  = MiniLanguageOperatorType.Modulo
    Power                                   = MiniLanguageOperatorType.Power
    Add                                     = MiniLanguageOperatorType.Add
    Subtract                                = MiniLanguageOperatorType.Subtract
    BitShiftLeft                            = MiniLanguageOperatorType.BitShiftLeft
    BitShiftRight                           = MiniLanguageOperatorType.BitShiftRight
    BitwiseAnd                              = MiniLanguageOperatorType.BitwiseAnd
    BitwiseXor                              = MiniLanguageOperatorType.BitwiseXor
    BitwiseOr                               = MiniLanguageOperatorType.BitwiseOr
    Less                                    = MiniLanguageOperatorType.Less
    LessEqual                               = MiniLanguageOperatorType.LessEqual
    Greater                                 = MiniLanguageOperatorType.Greater
    GreaterEqual                            = MiniLanguageOperatorType.GreaterEqual
    Equal                                   = MiniLanguageOperatorType.Equal
    NotEqual                                = MiniLanguageOperatorType.NotEqual
    LogicalAnd                              = MiniLanguageOperatorType.LogicalAnd
    LogicalOr                               = MiniLanguageOperatorType.LogicalOr

    # Operators that are not valid within the MiniLanguage

    # Make sure to update `../../../../Grammar/PrecedenceFunc.py` when values are added.
    Access                                  = auto()
    AccessReturnSelf                        = auto()

    Assign                                  = auto()

    In                                      = auto()
    NotIn                                   = auto()

    # TODO: Need a binary statement type for these
    # BitflipInplace                          = auto()
    # MultiplyInplace                         = auto()
    # DivideInplace                           = auto()
    # DivideFloorInplace                      = auto()
    # ModuloInplace                           = auto()
    # PowerInplace                            = auto()
    # AddInplace                              = auto()
    # SubtractInplace                         = auto()
    # BitShiftLeftInplace                     = auto()
    # BitShiftRightInplace                    = auto()
    # BitwiseAndInplace                       = auto()
    # BitwiseXorInplace                       = auto()
    # BitwiseOrInplace                        = auto()

    # ----------------------------------------------------------------------
    def ToMiniLanguageOperatorType(self) -> Optional[MiniLanguageOperatorType]:
        try:
            return MiniLanguageOperatorType(self.value)
        except ValueError:
            return None


assert _initial_num_mini_language_operator_types == len(MiniLanguageOperatorType)
del _initial_num_mini_language_operator_types


# ----------------------------------------------------------------------
InvalidBinaryOperatorError                  = CreateError(
    "'{operator}' is not a valid binary operator for compile-time expressions",
    operator=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class BinaryExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    left_expression: ExpressionParserInfo
    operator: OperatorType
    right_expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        left_expression: ExpressionParserInfo,
        operator: OperatorType,
        right_expression: ExpressionParserInfo,
        *args,
        **kwargs,
    ):
        return cls(  # pylint: disable=too-many-function-args
            ParserInfoType.GetDominantType(left_expression, right_expression),      # type: ignore
            regions,                                                                # type: ignore
            left_expression,
            operator,
            right_expression,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):  # type: ignore
        super(BinaryExpressionParserInfo, self).__post_init__(
            *args,
            **{
                **kwargs,
                **{
                    "regionless_attributes": [
                        "left_expression",
                        "right_expression",
                    ],
                },
            },
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def IsType(self) -> Optional[bool]:
        return (
            self.operator in [OperatorType.LogicalOr, OperatorType.Access]
            and self.left_expression.IsType() is not False
            and self.right_expression.IsType() is not False
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "left_expression", self.left_expression  # type: ignore
        yield "right_expression", self.right_expression  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def _InitializeAsTypeImpl(
        self,
        parser_info_type: ParserInfoType,
        *,
        is_instantiated_type: bool=True,
    ) -> None:
        errors: List[Error] = []

        if parser_info_type.IsCompileTime():
            errors.append(
                InvalidCompileTimeTypeError.Create(
                    region=self.regions__.self__,
                ),
            )

        elif (
            parser_info_type == ParserInfoType.Standard
            or parser_info_type == ParserInfoType.Unknown
        ):
            if self.operator != OperatorType.Access:
                errors.append(
                    InvalidCompileTimeTypeError.Create(
                        region=self.regions__.self__,
                    ),
                )
            else:
                try:
                    self.left_expression.InitializeAsType(
                        parser_info_type,
                        is_instantiated_type=False,
                    )

                    self.right_expression.InitializeAsType(
                        parser_info_type,
                        is_instantiated_type=is_instantiated_type,
                    )

                except ErrorException as ex:
                    errors += ex.errors

        else:
            assert False, parser_info_type  # type: ignore

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def _InitializeAsExpressionImpl(self) -> None:
        self.left_expression.InitializeAsExpression()
        self.right_expression.InitializeAsExpression()

    # ----------------------------------------------------------------------
    @contextmanager
    @Interface.override
    def _InitConfigurationImpl(self, *args, **kwargs):
        assert self.parser_info_type__ == ParserInfoType.Configuration, self.parser_info_type__

        operator = self.operator.ToMiniLanguageOperatorType()
        if operator is None:
            raise ErrorException(
                InvalidBinaryOperatorError.Create(
                    region=self.regions__.operator,
                    operator=self.operator.name,
                ),
            )

        yield
