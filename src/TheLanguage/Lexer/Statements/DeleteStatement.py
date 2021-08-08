# ----------------------------------------------------------------------
# |
# |  DeleteStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-31 12:57:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DeleteStatement object"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .VariableStatement import VariableStatement
    from ..AST import StatementNode


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DeleteStatement(StatementNode):
    """\
    TODO: Comment
    """

    Variable: VariableStatement
