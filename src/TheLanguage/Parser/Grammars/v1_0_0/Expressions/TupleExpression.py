# ----------------------------------------------------------------------
# |
# |  TupleExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-06 18:35:19
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
    from ..Common import GrammarDSL
    from ..Common.TupleBase import TupleBase
    from ...GrammarStatement import GrammarStatement


# ----------------------------------------------------------------------
class TupleExpression(TupleBase):
    """\
    Creates a tuple that can be used as an expression.

    '(' <content> ')'

    Examples:
        var = (a, b)
        Func((a, b, c), (a,))
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleExpression, self).__init__(
            GrammarStatement.Type.Expression,
            "Tuple Expression",
            GrammarDSL.DynamicStatementsType.Expressions,
            additional_sequence_suffix_items=[],
        )
