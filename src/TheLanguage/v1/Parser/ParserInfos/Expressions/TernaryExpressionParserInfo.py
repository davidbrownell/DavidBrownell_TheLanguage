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

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfoType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TernaryExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type__: ParserInfoType      = field(init=False)

    condition_expression: ExpressionParserInfo
    true_expression: ExpressionParserInfo
    false_expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):  # type: ignore
        super(TernaryExpressionParserInfo, self).__post_init__(
            ParserInfoType(
                max(
                    self.condition_expression.parser_info_type__.value,  # type: ignore
                    self.true_expression.parser_info_type__.value,  # type: ignore
                    self.false_expression.parser_info_type__.value,  # type: ignore
                ),
            ),
            regions,
            regionless_attributes=[
                "condition_expression",
                "true_expression",
                "false_expression",
            ],
        )
