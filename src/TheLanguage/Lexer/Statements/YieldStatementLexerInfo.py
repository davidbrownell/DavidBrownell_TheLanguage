# ----------------------------------------------------------------------
# |
# |  YieldStatementLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-16 12:34:42
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the YieldStatementLexerInfo object"""

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
    from .StatementLexerInfo import StatementLexerInfo
    from ..Expressions.ExpressionLexerInfo import ExpressionLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class YieldStatementLexerInfo(StatementLexerInfo):
    Expression: Optional[ExpressionLexerInfo]
    IsRecursive: Optional[bool]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(YieldStatementLexerInfo, self).__post_init__(regions)

        assert self.IsRecursive is None or self.IsRecursive, "Valid values are True and None"
        assert self.IsRecursive is None or self.Expression is not None, "IsRecursive should never be set without a corresponding Expression"
