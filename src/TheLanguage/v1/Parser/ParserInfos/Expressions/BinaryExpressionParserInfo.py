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

    from ...Error import ErrorException

    from ...MiniLanguage.Expressions.BinaryExpression import OperatorType


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
        parser_info_type = cls._GetDominantExpressionType(left_expression, right_expression)
        if isinstance(parser_info_type, list):
            raise ErrorException(*parser_info_type)

        return cls(                         # pylint: disable=too-many-function-args
            parser_info_type,               # type: ignore
            regions,                        # type: ignore
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
