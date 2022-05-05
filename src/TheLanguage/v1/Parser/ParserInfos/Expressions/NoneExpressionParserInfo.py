# ----------------------------------------------------------------------
# |
# |  NoneExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 12:00:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NoneExpressionParserInfo object"""

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


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NoneExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.Unknown,         # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsType() -> Optional[bool]:
        return None

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateAsType(
        self,
        parser_info_type: ParserInfoType,               # pylint: disable=unused-argument
        *,
        is_instantiated_type: Optional[bool]=True,      # pylint: disable=unused-argument
    ) -> None:
        # This can be an expression or a type
        pass

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ValidateAsExpression() -> None:
        # This can be an expression or a type
        pass
