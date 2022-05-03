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

from enum import auto, Enum
from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo, Region

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
    Modulus                                 = MiniLanguageOperatorType.Modulus
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
    Access                                  = auto()
    AccessReturnSelf                        = auto()

    # ----------------------------------------------------------------------
    def ToMiniLanguageOperatorType(self) -> Optional[MiniLanguageOperatorType]:
        try:
            return MiniLanguageOperatorType(self.value)
        except ValueError:
            return None


assert _initial_num_mini_language_operator_types == len(MiniLanguageOperatorType)
del _initial_num_mini_language_operator_types


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
        regions: List[Optional[Region]],
        left_expression: ExpressionParserInfo,
        operator: OperatorType,
        right_expression: ExpressionParserInfo,
        *args,
        **kwargs,
    ):
        return cls(  # pylint: disable=too-many-function-args
            cls._GetDominantExpressionType(left_expression, right_expression),  # type: ignore
            regions,                                                            # type: ignore
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
            **kwargs,
            regionless_attributes=[
                "left_expression",
                "right_expression",
            ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("left_expression", self.left_expression),
                ("right_expression", self.right_expression),
            ],
            children=None,
        )
