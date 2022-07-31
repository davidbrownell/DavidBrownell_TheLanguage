# ----------------------------------------------------------------------
# |
# |  CallExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-22 08:11:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CallExpressionParserInfo object"""

import os

from typing import List, Optional, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfo, ParserInfoType, TranslationUnitRegion
    from ..Common.FuncArgumentsParserInfo import FuncArgumentsParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class CallExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    expression: ExpressionParserInfo
    arguments: Union[bool, FuncArgumentsParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        expression: ExpressionParserInfo,
        arguments: Union[bool, FuncArgumentsParserInfo],
        *args,
        **kwargs,
    ):
        if isinstance(arguments, bool):
            parser_info_type = expression.parser_info_type__
        else:
            parser_info_type = ParserInfoType.GetDominantType(expression, arguments)

        if parser_info_type.IsCompileTime():
            expression.OverrideParserInfoType(parser_info_type)

        return cls(
            parser_info_type,               # type: ignore
            regions,                        # type: ignore
            expression,
            arguments,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(CallExpressionParserInfo, self).__post_init__(
            *args,
            **{
                **kwargs,
                **{
                    "regionless_attributes": ["expression", ],
                },
            },
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "expression", self.expression  # type: ignore

        if not isinstance(self.arguments, bool):
            yield "arguments", self.arguments  # type: ignore
