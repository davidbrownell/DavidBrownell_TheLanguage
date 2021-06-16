# ----------------------------------------------------------------------
# |
# |  TupleStatements.py
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

from typing import List, Optional, Union

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
class _TupleBase(GrammarStatement):
    """\
    Creates a Tuple.

    '(' <content> ')'
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        desc: str,
        grammar_statement_type: GrammarStatement.Type,
        content: Union[DynamicStatements, CommonTokens.RegexToken],
        statement_items_suffix: Optional[List[Statement.ItemType]] =None,
    ):
        statement_items = [
            [
                # Multiple elements
                #   '(' <expr> (',' <expr>)+ ','? ')'
                Statement(
                    "Multiple",
                    CommonTokens.LParen,
                    CommonTokens.PushIgnoreWhitespaceControl,
                    content,
                    (
                        Statement(
                            "Comma and {}".format(desc),
                            CommonTokens.Comma,
                            content,
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
                    content,
                    CommonTokens.Comma,
                    CommonTokens.PopIgnoreWhitespaceControl,
                    CommonTokens.RParen,
                ),
            ],
        ]

        if statement_items_suffix:
            statement_items += statement_items_suffix

        super(_TupleBase, self).__init__(
            grammar_statement_type,
            Statement("Tuple {}".format(desc), *statement_items),
        )


# ----------------------------------------------------------------------
class TupleExpression(_TupleBase):
    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleExpression, self).__init__(
            "Expression",
            GrammarStatement.Type.Expression,
            DynamicStatements.Expressions,
        )


# ----------------------------------------------------------------------
class TupleVariableDeclarationStatement(_TupleBase):
    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleVariableDeclarationStatement, self).__init__(
            "Variable Declaration",
            GrammarStatement.Type.Statement,
            CommonTokens.Name,
            [
                CommonTokens.Equal,
                DynamicStatements.Expressions,
            ],
        )
