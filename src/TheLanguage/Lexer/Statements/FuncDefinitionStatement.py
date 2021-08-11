# ----------------------------------------------------------------------
# |
# |  FuncDefinitionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-31 18:16:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncDefinitionStatement object"""

import os

from typing import List

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Interfaces.IDocstring import IDocstring

    from ..AST import StatementNode

    from ..Common import Flags
    from ..Common.FuncDefinitionNode import FuncDefinitionNode as _FuncDefinitionNode


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FuncDefinitionStatement(
    StatementNode,
    _FuncDefinitionNode,
    IDocstring,
):
    """\
    TODO: Comment
    """

    Visibility: Flags.VisibilityType
    Statements: List[StatementNode]

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetTypeDescriptions() -> List[str]:
        return ["function"]
