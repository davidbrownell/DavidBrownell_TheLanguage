# ----------------------------------------------------------------------
# |
# |  VariableDeclarationStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 13:27:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableDeclarationStatementParserInfo object"""

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
    from .StatementParserInfo import StatementParserInfo

    from ..Common.TypeModifier import TypeModifier
    from ..Common.VisitorTools import StackHelper, VisitType

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Names.NameParserInfo import NameParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableDeclarationStatementParserInfo(StatementParserInfo):
    Modifier: Optional[TypeModifier]
    Name: NameParserInfo
    Expression: ExpressionParserInfo

    # TODO: Not all type modifiers are valid in this context

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        results = []

        results.append(visitor.OnVariableDeclarationStatement(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[self] as helper:
            with helper["Name"]:
                results.append(self.Name.Accept(visitor, helper.stack, *args, **kwargs))

            with helper["Expression"]:
                results.append(self.Expression.Accept(visitor, helper.stack, *args, **kwargs))

        results.append(visitor.OnVariableDeclarationStatement(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results
