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
"""Contains the TupleExpression, TupleType, and TupleVariableDeclarationStatement objects"""

import os

from typing import cast, Generator, List, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common.GrammarAST import (
        ExtractLeafValue,
        ExtractOrNode,
        Leaf,
        Node,
    )

    from .Common import GrammarDSL
    from .Common import NamingConventions
    from .Common import Tokens as CommonTokens
    from ..GrammarStatement import GrammarStatement

    from ...ParserImpl.Statements.SequenceStatement import SequenceStatement


# ----------------------------------------------------------------------
class _TupleBase(GrammarStatement):

    MULTIPLE_NODE_NAME                     = "Multiple"
    SINGLE_NODE_NAME                       = "Single"

    # ----------------------------------------------------------------------
    def __init__(
        self,
        grammar_statement_type: GrammarStatement.Type,
        tuple_statement_name: str,
        tuple_element_item: GrammarDSL.StatementItem.ItemType,
        additional_sequence_suffix_items: List[GrammarDSL.StatementItem.ItemType],
    ):
        tuple_statement = GrammarDSL.CreateStatement(
            name="Tuple Element" if additional_sequence_suffix_items else tuple_statement_name,
            item=(
                # Multiple Elements
                #   '(' <tuple_element> (',' <tuple_element>)+ ','? ')'
                GrammarDSL.StatementItem(
                    name=self.MULTIPLE_NODE_NAME,
                    item=[
                        CommonTokens.LParen,
                        CommonTokens.PushIgnoreWhitespaceControl,
                        GrammarDSL.CreateDelimitedStatementItem(
                            tuple_element_item,
                            are_multiple_items_required=True,
                        ),
                        CommonTokens.PopIgnoreWhitespaceControl,
                        CommonTokens.RParen,
                    ],
                ),

                # Single Element
                #   '(' <tuple_element> ',' ')'
                GrammarDSL.StatementItem(
                    name=self.SINGLE_NODE_NAME,
                    item=[
                        CommonTokens.LParen,
                        CommonTokens.PushIgnoreWhitespaceControl,
                        tuple_element_item,
                        CommonTokens.Comma,
                        CommonTokens.PopIgnoreWhitespaceControl,
                        CommonTokens.RParen,
                    ],
                ),
            ),
        )

        if additional_sequence_suffix_items:
            tuple_statement = GrammarDSL.CreateStatement(
                name=tuple_statement_name,
                item=
                    cast(List[GrammarDSL.StatementItem.ItemType], [tuple_statement])
                    + additional_sequence_suffix_items,
            )

        super(_TupleBase, self).__init__(grammar_statement_type, tuple_statement)

    # ----------------------------------------------------------------------
    @classmethod
    def EnumElements(
        cls,
        node: Node,
    ) -> Generator[
        Union[Leaf, Node],
        None,
        None,
    ]:
        if isinstance(node.Type, SequenceStatement):
            assert node.Children
            node = cast(Node, node.Children[0])

        node = cast(Node, ExtractOrNode(node))
        assert node.Type

        if node.Type.Name == cls.SINGLE_NODE_NAME:
            assert len(node.Children) == 4
            yield node.Children[1]

        elif node.Type.Name == cls.MULTIPLE_NODE_NAME:
            assert len(node.Children) == 3
            yield from GrammarDSL.ExtractDelimitedNodes(cast(Node, node.Children[1]))

        else:
            assert False, node.Type.Name  # pragma: no cover


# ----------------------------------------------------------------------
class TupleExpression(_TupleBase):
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
            GrammarDSL.DynamicStatements.Expressions,
            additional_sequence_suffix_items=[],
        )


# ----------------------------------------------------------------------
class TupleType(_TupleBase):
    """\
    Creates a tuple that can be used as a type.

    '(' <content> ')'

    Examples:
        var = value as (Foo, Bar)
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleType, self).__init__(
            GrammarStatement.Type.Type,
            "Tuple Type",
            GrammarDSL.DynamicStatements.Types,
            additional_sequence_suffix_items=[],
        )


# ----------------------------------------------------------------------
class TupleVariableDeclarationStatement(_TupleBase):
    """\
    Creates a tuple variable declaration.

    '(' <content> ')' '=' <expr>

    Examples:
        (a, b) = Func()
        (a,) = value
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleVariableDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            "Tuple Variable Declaration",
            (CommonTokens.Name, None),
            additional_sequence_suffix_items=[
                CommonTokens.Equal,
                GrammarDSL.DynamicStatements.Expressions,
                CommonTokens.Newline,
            ],
        )

    # ----------------------------------------------------------------------
    @classmethod
    def EnumElements(
        cls,
        node: Node,
    ) -> Generator[
        Union[
            Tuple[Leaf, str],
            Tuple[Node, Node],
        ],
        None,
        None,
    ]:
        for child_node in super(TupleVariableDeclarationStatement, cls).EnumElements(node):
            child_node = ExtractOrNode(cast(Node, child_node))

            if isinstance(child_node, Leaf):
                yield child_node, ExtractLeafValue(child_node)
            else:
                yield child_node, child_node

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        for element_node, value in cls.EnumElements(node):
            if isinstance(value, str):
                if not NamingConventions.Variable.Regex.match(value):
                    raise NamingConventions.InvalidVariableNameError.FromNode(element_node, value)

                continue

            # If here, we are looking at a nested tuple
            cls.ValidateNodeSyntax(cast(Node, element_node))