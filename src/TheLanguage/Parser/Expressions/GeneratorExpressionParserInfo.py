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
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo

    from ..Common.VisitorTools import StackHelper, VisitType
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

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        results = []

        results.append(visitor.OnGeneratorExpression(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[self] as helper:
            with helper["ResultExpression"]:
                results.append(self.ResultExpression.Accept(visitor, helper.stack, *args, **kwargs))

            with helper["Name"]:
                results.append(self.Name.Accept(visitor, helper.stack, *args, **kwargs))

            with helper["SourceExpression"]:
                results.append(self.SourceExpression.Accept(visitor, helper.stack, *args, **kwargs))

            if self.ConditionExpression is not None:
                with helper["ConditionExpression"]:
                    results.append(self.ConditionExpression.Accept(visitor, helper.stack, *args, **kwargs))

        results.append(visitor.OnGeneratorExpression(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results
