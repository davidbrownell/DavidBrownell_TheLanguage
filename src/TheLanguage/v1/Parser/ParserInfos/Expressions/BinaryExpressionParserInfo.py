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

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfoType

    from ...Error import ErrorException

    from ...MiniLanguage.Expressions.BinaryExpression import OperatorType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class BinaryExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type__: ParserInfoType      = field(init=False)

    left_expression: ExpressionParserInfo
    operator: OperatorType
    right_expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):  # type: ignore
        result = self.__class__._GetDominantExpressionType(self.left_expression, self.right_expression)  # pylint: disable=protected-access
        if isinstance(result, list):
            raise ErrorException(*result)

        parser_info_type = result

        super(BinaryExpressionParserInfo, self).__post_init__(
            parser_info_type,
            regions,
            regionless_attributes=[
                "left_expression",
                "right_expression",
            ],
        )
