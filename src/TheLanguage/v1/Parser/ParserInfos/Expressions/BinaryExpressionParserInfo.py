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
    from .CallExpressionParserInfo import CallExpressionParserInfo
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfo, ParserInfoType, TranslationUnitRegion

    from .FuncOrTypeExpressionParserInfo import InvalidCompileTimeTypeError

    from ..Statements.FuncDefinitionStatementParserInfo import OperatorType as FuncOperatorType

    from ...Error import Error, ErrorException
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
    Access                                  = auto()
    AccessReturnSelf                        = auto()

    MultiplyInplace                         = auto()
    DivideInplace                           = auto()
    DivideFloorInplace                      = auto()
    ModuloInplace                           = auto()
    PowerInplace                            = auto()
    AddInplace                              = auto()
    SubtractInplace                         = auto()
    BitShiftLeftInplace                     = auto()
    BitShiftRightInplace                    = auto()
    BitwiseAndInplace                       = auto()
    BitwiseXorInplace                       = auto()
    BitwiseOrInplace                        = auto()

    # ----------------------------------------------------------------------
    def ToMiniLanguageOperatorType(self) -> Optional[MiniLanguageOperatorType]:
        try:
            return MiniLanguageOperatorType(self.value)
        except ValueError:
            return None


assert _initial_num_mini_language_operator_types == len(MiniLanguageOperatorType)
del _initial_num_mini_language_operator_types


# ----------------------------------------------------------------------
_expression_to_func_map                     = {
    OperatorType.Multiply:                  FuncOperatorType.Multiply,
    OperatorType.Divide:                    FuncOperatorType.Divide,
    OperatorType.DivideFloor:               FuncOperatorType.DivideFloor,
    OperatorType.Modulo:                    FuncOperatorType.Modulo,
    OperatorType.Power:                     FuncOperatorType.Power,
    OperatorType.Add:                       FuncOperatorType.Add,
    OperatorType.Subtract:                  FuncOperatorType.Subtract,
    OperatorType.BitShiftLeft:              FuncOperatorType.BitShiftLeft,
    OperatorType.BitShiftRight:             FuncOperatorType.BitShiftRight,
    OperatorType.BitwiseAnd:                FuncOperatorType.BitwiseAnd,
    OperatorType.BitwiseXor:                FuncOperatorType.BitwiseXor,
    OperatorType.BitwiseOr:                 FuncOperatorType.BitwiseOr,
    OperatorType.Less:                      FuncOperatorType.Less,
    OperatorType.LessEqual:                 FuncOperatorType.LessEqual,
    OperatorType.Greater:                   FuncOperatorType.Greater,
    OperatorType.GreaterEqual:              FuncOperatorType.GreaterEqual,
    OperatorType.Equal:                     FuncOperatorType.Equal,
    OperatorType.NotEqual:                  FuncOperatorType.NotEqual,
    OperatorType.LogicalAnd:                FuncOperatorType.LogicalAnd,
    OperatorType.LogicalOr:                 FuncOperatorType.LogicalOr,
    OperatorType.Access:                    FuncOperatorType.GetAttribute,
    OperatorType.AccessReturnSelf:          None,
    OperatorType.MultiplyInplace:           FuncOperatorType.MultiplyInplace,
    OperatorType.DivideInplace:             FuncOperatorType.DivideInplace,
    OperatorType.DivideFloorInplace:        FuncOperatorType.DivideFloorInplace,
    OperatorType.ModuloInplace:             FuncOperatorType.ModuloInplace,
    OperatorType.PowerInplace:              FuncOperatorType.PowerInplace,
    OperatorType.AddInplace:                FuncOperatorType.AddInplace,
    OperatorType.SubtractInplace:           FuncOperatorType.SubtractInplace,
    OperatorType.BitShiftLeftInplace:       FuncOperatorType.BitShiftLeftInplace,
    OperatorType.BitShiftRightInplace:      FuncOperatorType.BitShiftRightInplace,
    OperatorType.BitwiseAndInplace:         FuncOperatorType.BitwiseAndInplace,
    OperatorType.BitwiseXorInplace:         FuncOperatorType.BitwiseXorInplace,
    OperatorType.BitwiseOrInplace:          FuncOperatorType.BitwiseOrInplace,
}

assert len(_expression_to_func_map) == len(OperatorType)

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
            ParserInfoType.GetDominantType(left_expression, right_expression),  # type: ignore
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
    def IsType(self) -> Optional[bool]:
        return (
            self.operator == OperatorType.Access
            and self.left_expression.IsType() is not False
            and self.right_expression.IsType() is not False
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def InitializeAsType(
        self,
        parser_info_type: ParserInfoType,
        *,
        is_instantiated_type: Optional[bool]=True,
    ) -> None:
        errors: List[Error] = []

        if ParserInfoType.IsCompileTime(parser_info_type):
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
    def InitializeAsExpression(self) -> None:
        self.left_expression.InitializeAsExpression()
        self.right_expression.InitializeAsExpression()

    # ----------------------------------------------------------------------
    @Interface.override
    def Lower(self) -> Optional[ParserInfo]:
        assert not ParserInfoType.IsCompileTimeStrict(self.parser_info_type__), self.parser_info_type__

        if self.IsType():
            return None

        func_operator = _expression_to_func_map[self.operator]
        if func_operator is None:
            return None

        # BugBug

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "left_expression", self.left_expression  # type: ignore
        yield "right_expression", self.right_expression  # type: ignore
