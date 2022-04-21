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

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfoType
    from ...MiniLanguage.Expressions.UnaryExpression import OperatorType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class UnaryExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type__: ParserInfoType      = field(init=False)

    operator: OperatorType
    expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):  # type: ignore
        # At the moment, all unary operations are valid at compile time, so no need to check.

        super(UnaryExpressionParserInfo, self).__post_init__(
            self.expression.parser_info_type__,  # type: ignore
            regions,
            regionless_attributes=["expression", ],
        )
