# ----------------------------------------------------------------------
# |
# |  GeneratorExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 09:49:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GeneratorExpressionParserInfo object"""

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

        DecorateValue(value) for value in [1, 2, 3] if value & 1
        --------------------     -----    ---------    ---------
        |                        |        |            |
        |                        |        |            - Condition Expression
        |                        |        - Source Expression
        |                        - Name
        - Result Expression
    """

    ResultExpression: ExpressionParserInfo
    Name: NameParserInfo
    SourceExpression: ExpressionParserInfo
    ConditionExpression: Optional[ExpressionParserInfo]
