# ----------------------------------------------------------------------
# |
# |  TransferExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-01 18:53:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TransferExpression object"""

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
    from ..AST import ExpressionNode, VariableNode


# ----------------------------------------------------------------------
class TransferType(Enum):
    """
    TODO: Document
    """

    Copy                                    = auto()
    Move                                    = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TransferExpression(ExpressionNode):
    """\
    TODO: Document
    """

    Type: TransferType
    Variable: VariableNode

    # ----------------------------------------------------------------------
    @Interface.override
    @property
    def ExpressionResultType(self):
        return None # BugBug