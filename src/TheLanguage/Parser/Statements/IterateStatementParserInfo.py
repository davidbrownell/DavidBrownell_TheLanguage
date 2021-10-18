# ----------------------------------------------------------------------
# |
# |  IterateStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 14:42:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IterateStatementParserInfo object"""

import os

from typing import List

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import StatementParserInfo
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Names.NameParserInfo import NameParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IterateStatementParserInfo(StatementParserInfo):
    """\
    Example syntax:

    for value in GenerateValues(): pass
        -----    ----------------  ----
        |        |                 |
        |        |                 - Statement(s)
        |        - Expression
        - Name
    """

    Name: NameParserInfo
    Expression: ExpressionParserInfo
    Statements: List[StatementParserInfo]
