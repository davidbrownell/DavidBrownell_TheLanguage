# ----------------------------------------------------------------------
# |
# |  YieldStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 09:24:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the YieldStatementParserInfo object"""

import os

from typing import Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import StatementParserInfo
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class YieldStatementParserInfo(StatementParserInfo):
    Expression: Optional[ExpressionParserInfo]
    IsRecursive: Optional[bool]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(YieldStatementParserInfo, self).__post_init__(regions)

        assert self.IsRecursive is None or self.IsRecursive, "Valid values are True and None"
        assert self.IsRecursive is None or self.Expression is not None, "IsRecursive should never be set without a corresponding Expression"
