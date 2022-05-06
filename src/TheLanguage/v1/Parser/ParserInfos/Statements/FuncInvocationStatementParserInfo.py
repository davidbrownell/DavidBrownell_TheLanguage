# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-29 17:02:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationStatementParserInfo object"""

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
    from .StatementParserInfo import Region, ScopeFlag, StatementParserInfo
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncInvocationStatementParserInfo(StatementParserInfo):
    # ----------------------------------------------------------------------
    expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        expression: ExpressionParserInfo,
        *args,
        **kwargs,
    ):
        return cls(
            ScopeFlag.Function,
            expression.parser_info_type__,  # type: ignore
            regions,                        # type: ignore
            expression,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(FuncInvocationStatementParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=["expression", ],
        )

        # Validate
        self.expression.ValidateAsExpression()

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
