# ----------------------------------------------------------------------
# |
# |  BooleanExpressionParserInfo.py
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
"""Contains the BooleanExpressionParserInfo object"""

import os

from contextlib import contextmanager

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


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class BooleanExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    value: bool

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(BooleanExpressionParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=["value", ],
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    @Interface.override
    def _InitConfigurationImpl(*args, **kwargs):
        # Nothing to do here
        yield
