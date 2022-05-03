# ----------------------------------------------------------------------
# |
# |  IndexExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-01 15:04:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IndexExpressionParserInfo object"""

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
class IndexExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    lhs_expression: ExpressionParserInfo
    index_expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        lhs_expression: ExpressionParserInfo,
        index_expression: ExpressionParserInfo,
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.GetDominantType(lhs_expression, index_expression),   # type: ignore
            regions,                                                            # type: ignore
            lhs_expression,
            index_expression,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(IndexExpressionParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=[
                "lhs_expression",
                "index_expression",
            ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("lhs_expression", self.lhs_expression),
                ("index_expression", self.index_expression),
            ],
            children=None,
        )
