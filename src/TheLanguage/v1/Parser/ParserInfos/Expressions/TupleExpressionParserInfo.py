# ----------------------------------------------------------------------
# |
# |  TupleExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-01 14:05:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleExpressionParserInfo object"""

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
class TupleExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    types: List[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        types: List[ExpressionParserInfo],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.GetDominantType(*types),     # type: ignore
            regions,                                    # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(TupleExpressionParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=["types", ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("types", self.types),
            ],  # type: ignore
            children=None,
        )
