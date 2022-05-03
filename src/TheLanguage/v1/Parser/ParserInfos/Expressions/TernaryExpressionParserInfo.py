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
    from .ExpressionParserInfo import ExpressionParserInfo, Region


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
            cls._GetDominantExpressionType(
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
