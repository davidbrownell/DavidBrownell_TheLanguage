# ----------------------------------------------------------------------
# |
# |  CapturedVariablesParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-15 08:35:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CapturedVariablesParserInfo object"""

import os

from typing import List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo, ParserInfo, ParserInfoType, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class CapturedVariablesParserInfo(ParserInfo):
    regions: InitVar[List[Optional[Region]]]
    variables: List[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(CapturedVariablesParserInfo, self).__init__(ParserInfoType.Standard, *args, **kwargs)

        # TODO: Validate that all variables are ultimately variable expressions (dotted notation is OK)
        # TODO: Is dotted notation OK? Capturing variables is a bit like adding a ref; need to think about this more

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("variables", self.variables),
            ],  # type: ignore
            children=None,
        )
