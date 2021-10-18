# ----------------------------------------------------------------------
# |
# |  BinaryStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 13:55:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryStatementParserInfo"""

import os

from enum import auto, Enum

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

    from ..Common.VisitorTools import StackHelper, VisitType
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Names.NameParserInfo import NameParserInfo


# ----------------------------------------------------------------------
class OperatorType(Enum):
    # Mathematical
    AddInplace                              = auto()
    SubtractInplace                         = auto()
    MultiplyInplace                         = auto()
    PowerInplace                            = auto()
    DivideInplace                           = auto()
    DivideFloorInplace                      = auto()
    ModuloInplace                           = auto()

    # Bit Manipulation
    BitShiftLeftInplace                     = auto()
    BitShiftRightInplace                    = auto()
    BitXorInplace                           = auto()
    BitAndInplace                           = auto()
    BitOrInplace                            = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class BinaryStatementParserInfo(StatementParserInfo):
    Name: NameParserInfo
    Operator: OperatorType
    Expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        results = []

        results.append(visitor.OnBinaryStatement(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[self] as helper:
            with helper["Name"]:
                results.append(self.Name.Accept(visitor, helper.stack, *args, **kwargs))

            with helper["Expression"]:
                results.append(self.Expression.Accept(visitor, helper.stack, *args, **kwargs))

        results.append(visitor.OnBinaryStatement(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results
