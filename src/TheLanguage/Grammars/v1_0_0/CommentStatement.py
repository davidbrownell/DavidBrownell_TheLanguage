# ----------------------------------------------------------------------
# |
# |  CommentStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-05 17:03:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains a statement that processes and ignores comments"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarStatement import GrammarStatement

    from ...ParserImpl.Statement import Statement


# ----------------------------------------------------------------------
class CommentStatement(GrammarStatement):
    """Eats single-line comments"""

    # ----------------------------------------------------------------------
    def __init__(self):
        super(CommentStatement, self).__init__(
            GrammarStatement.Type.Statement,
            Statement("Comment", Statement.CommentToken),
        )
