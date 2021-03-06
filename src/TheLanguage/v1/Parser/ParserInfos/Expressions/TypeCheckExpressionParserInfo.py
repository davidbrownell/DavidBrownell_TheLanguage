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
    from ...MiniLanguage.Expressions.TypeCheckExpression import OperatorType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeCheckExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    operator: OperatorType
    expression: ExpressionParserInfo
    type: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        operator: OperatorType,
        expression: ExpressionParserInfo,
        the_type: ExpressionParserInfo,
        *args,
        **kwargs,
    ):
        return cls(  # pylint: disable=too-many-function-args
            ParserInfoType.GetDominantType(expression, the_type),           # type: ignore
            regions,                                                        # type: ignore
            operator,
            expression,
            the_type,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(TypeCheckExpressionParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=[
                "expression",
                "type",
            ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("expression", self.expression),
                ("type", self.type),
            ],
            children=None,
        )
