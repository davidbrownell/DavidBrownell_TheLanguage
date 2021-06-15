# ----------------------------------------------------------------------
# |
# |  TupleExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 14:49:37
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
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import (
        DynamicStatements,
        GrammarStatement,
        Statement,
    )


# ----------------------------------------------------------------------
class TupleExpression(GrammarStatement):
    """\
    Creates a Tuple.

    '(' <content> ')'
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleExpression, self).__init__(
            GrammarStatement.Type.Expression,
            Statement(
                "Tuple Expression",
                [
                    # Multiple elements
                    #   '(' <expr> (',' <expr>)+ ','? ')'
                    Statement(
                        "Multiple",
                        CommonTokens.LParen,
                        CommonTokens.PushIgnoreWhitespaceControl,
                        DynamicStatements.Expressions,
                        (
                            Statement(
                                "Comma and Expression",
                                CommonTokens.Comma,
                                DynamicStatements.Expressions,
                            ),
                            1,
                            None,
                        ),
                        (CommonTokens.Comma, 0, 1),
                        CommonTokens.PopIgnoreWhitespaceControl,
                        CommonTokens.RParen,
                    ),

                    # Single element
                    #   '(' <expr> ',' ')'
                    #
                    #   Note that for single element tuples, the comma is required
                    #   to differentiate it from a grouping construct.
                    Statement(
                        "Single",
                        CommonTokens.LParen,
                        CommonTokens.PushIgnoreWhitespaceControl,
                        DynamicStatements.Expressions,
                        CommonTokens.Comma,
                        CommonTokens.PopIgnoreWhitespaceControl,
                        CommonTokens.RParen,
                    ),
                ],
            ),
        )
