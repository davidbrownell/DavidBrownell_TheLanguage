# ----------------------------------------------------------------------
# |
# |  TryCatchExceptionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-31 14:11:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TryCatchExceptionStatement object"""

import os

from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..AST import StatementNode
    from ..Types.StandardType import StandardType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TryCatchExceptionStatement(StatementNode):
    """\
    TODO: Describe
    """

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class CatchStatement(StatementNode):
        """\
        TODO: Describe
        """

        Exception: StandardType
        Statements: List[StatementNode]

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    TryStatements: List[StatementNode]
    CatchStatements: List[CatchStatement]
    FinallyStatements: Optional[List[StatementNode]]
