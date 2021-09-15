# ----------------------------------------------------------------------
# |
# |  GeneratorExpressionLexerInfo.py
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
"""Contains the GeneratorExpressionLexerData, GeneratorExpressionLexerInfo, and GeneratorExpressionLexerRegions objects"""

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
    from .ExpressionLexerInfo import ExpressionLexerInfo
    from ..Names.NameLexerInfo import NameLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class GeneratorExpressionLexerInfo(ExpressionLexerInfo):
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

    DisplayExpression: ExpressionLexerInfo
    Name: NameLexerInfo
    SourceExpression: ExpressionLexerInfo
    ConditionExpression: Optional[ExpressionLexerInfo]
