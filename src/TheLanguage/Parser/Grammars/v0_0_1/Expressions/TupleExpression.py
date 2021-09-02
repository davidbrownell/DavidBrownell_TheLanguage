# ----------------------------------------------------------------------
# |
# |  TupleExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 16:59:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleExpression object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.TupleBase import TupleBase
    from ...GrammarPhrase import GrammarPhrase


# ----------------------------------------------------------------------
class TupleExpression(TupleBase):
    """\
    Creates a tuple that can be used as an expression.

    '(' <expr> ',' ')'
    '(' <expr> (',' <expr>)+ ','? ')'

    Example:
        var = (a, b)
        Func((a, b, c), (d,))
    """

    PHRASE_NAME                             = "Tuple Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleExpression, self).__init__(GrammarPhrase.Type.Expression, self.PHRASE_NAME)
