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

from typing import List, Optional, Union
from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfo, ParserInfoType, TranslationUnitRegion
    from ...MiniLanguage.Expressions.TypeCheckExpression import OperatorType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeCheckExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    operator: OperatorType
    expression: ExpressionParserInfo
    type: ExpressionParserInfo

    # Values set during validation
    _type_parser_info__: Optional[ParserInfo]           = field(init=False, default=None)

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        operator: OperatorType,
        expression: ExpressionParserInfo,
        the_type: ExpressionParserInfo,
    ):
        return cls(  # pylint: disable=too-many-function-args
            ParserInfoType.TypeCustomization,           # type: ignore
            regions,                                    # type: ignore
            operator,
            expression,
            the_type,
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
    # The following values are set during validation
    def InitType(
        self,
        type_parser_info: ParserInfo
    ) -> None:
        assert self._type_parser_info__ is None, self._type_parser_info__
        object.__setattr__(self, "_type_parser_info__", type_parser_info)

    # ----------------------------------------------------------------------
    @property
    def type_parser_info__(self) -> ParserInfo:
        assert self._type_parser_info__ is not None
        return self._type_parser_info__

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "expression", self.expression  # type: ignore
        yield "type", self.type  # type: ignore
