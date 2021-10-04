# ----------------------------------------------------------------------
# |
# |  ArgumentParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 08:01:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ArgumentParserInfo object"""

import os

from typing import Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo, ParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ArgumentParserInfo(ParserInfo):
    Expression: ExpressionParserInfo
    Keyword: Optional[str]
