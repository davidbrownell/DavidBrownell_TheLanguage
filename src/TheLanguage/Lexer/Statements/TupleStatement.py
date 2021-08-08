# ----------------------------------------------------------------------
# |
# |  TupleStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-31 18:42:20
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleStatement object"""

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
    from ..AST import StatementNode


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TupleStatement(StatementNode):
    """\
    TODO: Describe
    """

    Statements: List[StatementNode]
