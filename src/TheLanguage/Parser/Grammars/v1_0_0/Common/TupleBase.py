# ----------------------------------------------------------------------
# |
# |  TupleBase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-06 18:22:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleBase object"""

import os

from typing import cast, Generator, List, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .GrammarAST import (
        ExtractLeafValue,
        ExtractOrNode,
    )

    from . import GrammarDSL
    from . import NamingConventions
    from . import Tokens as CommonTokens

    from ...GrammarStatement import GrammarStatement

    from ....Statements.SequenceStatement import SequenceStatement


# ----------------------------------------------------------------------
class TupleBase(GrammarStatement):
    """Base class for Tuple expressions, statements, and types"""

    MULTIPLE_NODE_NAME                      = "Multiple"
    SINGLE_NODE_NAME                        = "Single"

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
                        # '('
                        CommonTokens.LParen,
                        CommonTokens.PushIgnoreWhitespaceControl,

                        # <tuple_element> (',' <tuple_element>)+ ','?
                        GrammarDSL.CreateDelimitedStatementItem(
                            tuple_element_item,
                            are_multiple_items_required=True,
                        ),

                        # ')'
                        CommonTokens.PopIgnoreWhitespaceControl,
                        CommonTokens.RParen,
                    ],
                ),

                # Single Element
                #   '(' <tuple_element> ',' ')'
                GrammarDSL.StatementItem(
                    name=self.SINGLE_NODE_NAME,
                    item=[
                        # '('
                        CommonTokens.LParen,
                        CommonTokens.PushIgnoreWhitespaceControl,

                        # <tuple_element>
                        tuple_element_item,

                        # ','
                        CommonTokens.Comma,

                        # ')'
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

        super(TupleBase, self).__init__(grammar_statement_type, tuple_statement)

    # ----------------------------------------------------------------------
    @classmethod
    def EnumElements(
        cls,
        node: GrammarDSL.Node,
    ) -> Generator[
        Union[GrammarDSL.Leaf, GrammarDSL.Node],
        None,
        None,
    ]:
        if isinstance(node.Type, SequenceStatement):
            assert node.Children
            node = cast(GrammarDSL.Node, node.Children[0])

        node = cast(GrammarDSL.Node, ExtractOrNode(node))
        assert node.Type

        if node.Type.Name == cls.SINGLE_NODE_NAME:
            assert len(node.Children) == 4
            yield node.Children[1]

        elif node.Type.Name == cls.MULTIPLE_NODE_NAME:
            assert len(node.Children) == 3
            yield from GrammarDSL.ExtractDelimitedNodes(cast(GrammarDSL.Node, node.Children[1]))

        else:
            assert False, node.Type.Name
