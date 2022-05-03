# ----------------------------------------------------------------------
# |
# |  VariableExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 15:06:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableExpressionParserInfo object"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import (  # pylint: disable=unused-import
        ExpressionParserInfo,
        ParserInfoType,                     # convenience import
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    name: str
