# ----------------------------------------------------------------------
# |
# |  CharacterExpressionParserInfo.py
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
"""Contains the CharacterExpressionParserInfo object"""

import os

from typing import Any, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfoType
    from .Traits.SimpleExpressionTrait import SimpleExpressionTrait


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class CharacterExpressionParserInfo(
    SimpleExpressionTrait,
    ExpressionParserInfo,
):
    # ----------------------------------------------------------------------
    value: int

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.Unknown,         # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        ExpressionParserInfo.__post_init__(
            self,
            *args,
            **{
                **kwargs,
                **{
                    "regionless_attributes": [
                        "value",
                    ],
                },
            },
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GetUniqueId(self) -> Tuple[Any, ...]:
        return (self.value, )
