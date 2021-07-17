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

from typing import Generator, Tuple, Union

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
    from .Common import NamingConventions
    from .Common import Tokens as CommonTokens
    from ..GrammarStatement import GrammarStatement

    from ...ParserImpl.Statements.OrStatement import OrStatement
    from ...ParserImpl.Statements.SequenceStatement import SequenceStatement


# ----------------------------------------------------------------------
class _TupleBase(GrammarStatement):

    MULTIPLE_NODE_NAME                     = "Multiple"
    SINGLE_NODE_NAME                       = "Single"

    # ----------------------------------------------------------------------
    @classmethod
    def EnumElements(
        cls,
        node: GrammarAST.Node,
    ) -> Generator[
        Union[
            GrammarAST.Leaf,
            GrammarAST.Node,
        ],
        None,
        None,
    ]:
        if isinstance(node.Type, SequenceStatement):
            assert node.Children
            node = node.Children[0]

        assert isinstance(node.Type, OrStatement)
        assert len(node.Children) == 1
        node = node.Children[0]

        if node.Type.Name == cls.SINGLE_NODE_NAME:
            assert len(node.Children) == 4
            yield node.Children[1]

        elif node.Type.Name == cls.MULTIPLE_NODE_NAME:
            assert len(node.Children) > 3
            yield node.Children[1]

            for child in node.Children[2].Children:
                assert len(child.Children) == 2
                yield child.Children[1]

        else:
            assert False, node.Type.Name  # pragma: no cover


# ----------------------------------------------------------------------
class TupleExpression(_TupleBase):
    """\
    Creates a tuple.

    '(' <content> ')'
    """

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
class TupleVariableDeclarationStatement(_TupleBase):
    """\
    Creates a tuple variable declaration.

    '(' <content> ')' '=' <expr>
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        tuple_element = (CommonTokens.Name, None)

        tuple_definition = GrammarDSL.CreateStatement(
            name="Tuple",
            item=(
                # Multiple Elements
                #   '(' <tuple|name> (',' <tuple|name>)+ ','? ')'
                GrammarDSL.StatementItem(
                    Name=self.MULTIPLE_NODE_NAME,
                    Item=[
                        CommonTokens.LParen,
                        CommonTokens.PushIgnoreWhitespaceControl,
                        tuple_element,
                        GrammarDSL.StatementItem(
                            Name="Comma and Element",
                            Item=[
                                CommonTokens.Comma,
                                tuple_element,
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
    def EnumElements(
        cls,
        node: GrammarAST.Node,
    ) -> Generator[
        Tuple[
            GrammarAST.Node,                # Tuple Element
            Union[
                str,                        # <name>
                GrammarAST.Node,            # Tuple
            ],
        ],
        None,
        None,
    ]:
        for node in super(TupleVariableDeclarationStatement, cls).EnumElements(node):
            assert isinstance(node.Type, OrStatement)
            assert len(node.Children) == 1
            node = node.Children[0]

            if isinstance(node, GrammarAST.Leaf):
                yield node, node.Value.Match.group("value")
            else:
                yield node, node

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: GrammarAST.Node,
    ):
        for element_node, value in cls.EnumElements(node):
            if isinstance(value, str):
                if not NamingConventions.Variable.Regex.match(value):
                    raise NamingConventions.InvalidVariableNameError.FromNode(element_node, value)

                continue

            # If here, we are looking at a nested tuple
            cls.ValidateNodeSyntax(element_node)
