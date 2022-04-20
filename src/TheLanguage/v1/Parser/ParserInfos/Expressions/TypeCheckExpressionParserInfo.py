# ----------------------------------------------------------------------
# |
# |  TypeCheckExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 14:50:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeCheckExpressionParserInfo object"""

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
    from ..Types.TypeParserInfo import TypeParserInfo
    from ...MiniLanguage.Expressions.TypeCheckExpression import OperatorType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeCheckExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type__: ParserInfoType      = field(init=False)

    operator: OperatorType
    expression: ExpressionParserInfo
    type: TypeParserInfo

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):  # type: ignore
        super(TypeCheckExpressionParserInfo, self).__post_init__(
            self.expression.parser_info_type__,  # type: ignore
            regions,
            regionless_attributes=[
                "expression",
                "type",
            ],
        )
