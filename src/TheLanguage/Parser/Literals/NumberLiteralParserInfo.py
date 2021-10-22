# ----------------------------------------------------------------------
# |
# |  NumberLiteralParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-22 10:14:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NumberLiteralParserInfo object"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .LiteralParserInfo import LiteralParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NumberLiteralParserInfo(LiteralParserInfo):
    """An integer or float value; context is necessary to determine if the literal is used correctly"""
    Value: float
