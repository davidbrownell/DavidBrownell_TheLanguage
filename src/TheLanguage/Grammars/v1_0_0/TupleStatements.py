# ----------------------------------------------------------------------
# |
# |  TupleStatements.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 16:50:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleDeclarationStatement and the TupleExpression objects"""

import os

from typing import List, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common import GrammarAST
    from .Common import GrammarDSL
    from .Common import Tokens as CommonTokens
    from ..GrammarStatement import GrammarStatement


# ----------------------------------------------------------------------
class TupleExpression(GrammarStatement):
    """\
    Creates a tuple.

    '(' <content> ')'
    """

    MULTIPLE_NODE_NAME                      = "Multiple"
    SINGLE_NODE_NAME                        = "Single"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleExpression, self).__init__(
            GrammarStatement.Type.Expression,
            GrammarDSL.CreateStatement(
                name="Tuple Expression",
                item=(
                    # Multiple Elements
                    #   '(' <expr> (',' <expr>)+ '?' ','? ')'
                    GrammarDSL.StatementItem(
                        Name=self.MULTIPLE_NODE_NAME,
                        Item=[
                            CommonTokens.LParen,
                            CommonTokens.PushIgnoreWhitespaceControl,
                            GrammarDSL.DynamicStatements.Expressions,
                            GrammarDSL.StatementItem(
                                Name="Comma and Expression",
                                Item=[
                                    CommonTokens.Comma,
                                    GrammarDSL.DynamicStatements.Expressions,
                                ],
                                Arity="+",
                            ),
                            GrammarDSL.StatementItem(
                                Item=CommonTokens.Comma,
                                Arity="?",
                            ),
                            CommonTokens.PopIgnoreWhitespaceControl,
                            CommonTokens.RParen,
                        ],
                    ),

                    # Single Element
                    #   '(' <expr> ',' ')'
                    GrammarDSL.StatementItem(
                        Name=self.SINGLE_NODE_NAME,
                        Item=[
                            CommonTokens.LParen,
                            CommonTokens.PushIgnoreWhitespaceControl,
                            GrammarDSL.DynamicStatements.Expressions,
                            CommonTokens.Comma,
                            CommonTokens.PopIgnoreWhitespaceControl,
                            CommonTokens.RParen,
                        ],
                    ),
                ),
            ),
        )


# ----------------------------------------------------------------------
class TupleVariableDeclarationStatement(GrammarStatement):
    """\
    Creates a tuple variable declaration.

    '(' <content> ')' '=' <expr>
    """

    MULTIPLE_NODE_NAME                     = "Multiple"
    SINGLE_NODE_NAME                       = "Single"

    # ----------------------------------------------------------------------
    def __init__(self):
        tuple_element = (CommonTokens.Name, None)

        tuple_definition = GrammarDSL.CreateStatement(
            name="Tuple",
            item=(
                # Multiple Elements
                #   '(' <tuple|name> (',' <tuple|name>)+ ','? ')'
                # BugBug GrammarDSL.StatementItem(
                # BugBug     Name=self.MULTIPLE_NODE_NAME,
                # BugBug     Item=[
                # BugBug         CommonTokens.LParen,
                # BugBug         CommonTokens.PushIgnoreWhitespaceControl,
                # BugBug         tuple_element,
                # BugBug         GrammarDSL.StatementItem(
                # BugBug             Name="Comma and Element",
                # BugBug             Item=[
                # BugBug                 CommonTokens.Comma,
                # BugBug                 tuple_element,
                # BugBug             ],
                # BugBug             Arity="+",
                # BugBug         ),
                # BugBug         GrammarDSL.StatementItem(
                # BugBug             Item=CommonTokens.Comma,
                # BugBug             Arity="?",
                # BugBug         ),
                # BugBug         CommonTokens.PopIgnoreWhitespaceControl,
                # BugBug         CommonTokens.RParen,
                # BugBug     ],
                # BugBug ),

                # Single Element
                #   '(' <tuple|name> ',' ')'
                GrammarDSL.StatementItem(
                    Name=self.SINGLE_NODE_NAME,
                    Item=[
                        CommonTokens.LParen,
                        CommonTokens.PushIgnoreWhitespaceControl,
                        tuple_element,
                        CommonTokens.Comma,
                        CommonTokens.PopIgnoreWhitespaceControl,
                        CommonTokens.RParen,
                    ],
                ),
            ),
        )

        super(TupleVariableDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            GrammarDSL.CreateStatement(
                name="Tuple Variable Declaration",
                item=[
                    tuple_definition,
                    CommonTokens.Equal,
                    GrammarDSL.DynamicStatements.Expressions,
                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: GrammarAST.Node,
    ):
        pass # BugBug
