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
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common import Tokens as CommonTokens
    from .Common import NamingConventions
    from .VariableDeclarationStatement import InvalidVariableNameError

    from ..GrammarStatement import (
        DynamicStatements,
        GrammarStatement,
        Node,
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
        *statement_items_suffix: Statement.ItemType,
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
            statement_items += list(statement_items_suffix)

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
    """\
    '(' <name> (',' <name>)* ',' ')' '=' ...
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleVariableDeclarationStatement, self).__init__(
            "Variable Declaration",
            GrammarStatement.Type.Statement,
            CommonTokens.Name,
            CommonTokens.Equal,
            DynamicStatements.Expressions,
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        # Drill into the Or node
        assert isinstance(node.Children[0].Type, list)
        assert len(node.Children[0].Children) == 1
        node = node.Children[0].Children[0]

        if node.Type.Name == "Single":
            assert len(node.Children) > 2
            elements = [node.Children[1]]

        elif node.Type.Name == "Multiple":
            assert len(node.Children) > 3

            elements = [node.Children[1]]

            for child in node.Children[2].Children:
                # First element is the comma, second is the value
                assert len(child.Children) == 2
                elements.append(child.Children[1])

        else:
            assert False, node  # pragma: no cover

        for element in elements:
            element_name = element.Value.Match.group("value")

            if not NamingConventions.Variable.Regex.match(element_name):
                raise InvalidVariableNameError.FromNode(element, element_name)
