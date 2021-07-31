# ----------------------------------------------------------------------
# |
# |  YieldStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 20:20:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the YieldStatement object"""

import os

from enum import auto, Enum
from typing import Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.AST import ExpressionNode, StatementNode


# ----------------------------------------------------------------------
class YieldType(Enum):
    """\
    TODO: Comment
    """

    Standard                                = auto()
    From                                    = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class YieldStatement(StatementNode):
    """\
    TODO: Comment
    """

    Yield: YieldType
    Expression: Optional[ExpressionNode]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(YieldStatement, self).__post_init__()

        assert self.Yield != YieldType.From or self.Expression, (self.Yield, self.Expression)
