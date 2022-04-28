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
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfoType, Region
    from ..Common.FuncArgumentsParserInfo import FuncArgumentsParserInfo
    from ...Error import ErrorException


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
        regions: List[Optional[Region]],
        expression: ExpressionParserInfo,
        arguments: Union[bool, FuncArgumentsParserInfo],
        *args,
        **kwargs,
    ):
        if isinstance(arguments, bool):
            parser_info_type = ParserInfoType.Unknown
        else:
            parser_info_type = cls._GetDominantExpressionType(expression, *arguments.arguments)
            if isinstance(parser_info_type, list):
                raise ErrorException(*parser_info_type)

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
            **kwargs,
            regionless_attributes=["expression", ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        details = []

        if not isinstance(self.arguments, bool):
            details.append(("arguments", self.arguments))

        return self._AcceptImpl(
            visitor,
            details=[
                ("expression", self.expression),
            ] + details,  # type: ignore
            children=None,
        )
