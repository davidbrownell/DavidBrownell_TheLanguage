# ----------------------------------------------------------------------
# |
# |  UnaryExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 16:19:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UnaryExpressionParserInfo object"""

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
    from ...MiniLanguage.Expressions.UnaryExpression import OperatorType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class UnaryExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    operator: OperatorType
    expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        operator: OperatorType,
        expression: ExpressionParserInfo,
        *args,
        **kwargs,
    ):
        return cls(
            expression.parser_info_type__,  # type: ignore
            regions,                        # type: ignore
            operator,
            expression,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(UnaryExpressionParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=["expression", ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("expression", self.expression),
            ],
            children=None,
        )
