# ----------------------------------------------------------------------
# |
# |  TernaryExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 15:47:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TernaryExpressionParserInfo object"""

import os

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
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfoType, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TernaryExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    condition_expression: ExpressionParserInfo
    true_expression: ExpressionParserInfo
    false_expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        condition_expression: ExpressionParserInfo,
        true_expression: ExpressionParserInfo,
        false_expression: ExpressionParserInfo,
        *args,
        **kwargs,
    ):
        return cls(                         # pylint: disable=too-many-function-args
            ParserInfoType.GetDominantType(
                condition_expression,
                true_expression,
                false_expression,
            ),                              # type: ignore
            regions,                        # type: ignore
            condition_expression,
            true_expression,
            false_expression,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(TernaryExpressionParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=[
                "condition_expression",
                "true_expression",
                "false_expression",
            ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def IsType(self) -> Optional[bool]:
        return (
            self.condition_expression.IsType() is False
            and self.true_expression.IsType() is not False
            and self.false_expression.IsType() is not False
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateAsType(
        self,
        parser_info_type: ParserInfoType,
        *,
        is_instantiated_type: Optional[bool]=True,
    ) -> None:
        self.condition_expression.ValidateAsExpression()

        self.true_expression.ValidateAsType(
            parser_info_type,
            is_instantiated_type=is_instantiated_type,
        )

        self.false_expression.ValidateAsType(
            parser_info_type,
            is_instantiated_type=is_instantiated_type,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateAsExpression(self) -> None:
        self.condition_expression.ValidateAsExpression()
        self.true_expression.ValidateAsExpression()
        self.false_expression.ValidateAsExpression()

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("conditional_expression", self.condition_expression),
                ("true_expression", self.true_expression),
                ("false_expression", self.false_expression),
            ],
            children=None,
        )
