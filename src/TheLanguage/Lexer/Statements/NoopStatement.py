# ----------------------------------------------------------------------
# |
# |  NoopStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 16:50:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NoopStatement object"""

import os

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
class NoopStatement(StatementNode):
    """\
    TODO: Comment
    """

    pass
