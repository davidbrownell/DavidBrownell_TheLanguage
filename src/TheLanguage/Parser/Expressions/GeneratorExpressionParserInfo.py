# ----------------------------------------------------------------------
# |
# |  GeneratorExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-13 09:02:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GeneratorExpressionParserData, GeneratorExpressionParserInfo, and GeneratorExpressionParserRegions objects"""

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
    from .ExpressionParserInfo import ExpressionParserInfo
    from ..Names.NameParserInfo import NameParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class GeneratorExpressionParserInfo(ExpressionParserInfo):
    """\
    Example syntax:

        DisplayOdd(a) for variable in [1, 2, 3] if a & 1
        -------------     --------    ---------    -----
        |                 |           |            |
        |                 |           |            - Condition Expression
        |                 |           - SourceExpression
        |                 - Name
        - DisplayExpression
    """

    DisplayExpression: ExpressionParserInfo
    Name: NameParserInfo
    SourceExpression: ExpressionParserInfo
    ConditionExpression: Optional[ExpressionParserInfo]
