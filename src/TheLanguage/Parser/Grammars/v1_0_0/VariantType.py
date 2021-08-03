# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-28 00:55:22
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType object"""

import os

from typing import cast, List

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common.GrammarAST import (
        ExtractDynamicExpressionNode,
        ExtractRepeatedNodes,
        Node,
    )

    from .Common import GrammarDSL
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import GrammarStatement


# ----------------------------------------------------------------------
class VariantType(GrammarStatement):
    """'(' <type> '|' (<type> '|')* <type> ')'"""

    NODE_NAME                               = "Variant"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class TypeInfo(object):
        Types: List[Node]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariantType, self).__init__(
            GrammarStatement.Type.Type,
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
                item=[
                    # '('
                    CommonTokens.LParen,
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <type>
                    GrammarDSL.DynamicStatementsType.Types,

                    # '|'
                    CommonTokens.VariantSep,

                    # (<type> '|')*
                    GrammarDSL.StatementItem(
                        name="Sep and Type",
                        item=[
                            GrammarDSL.DynamicStatementsType.Types,
                            CommonTokens.VariantSep,
                        ],
                        arity="*",
                    ),

                    # <type>
                    GrammarDSL.DynamicStatementsType.Types,

                    # ')'
                    CommonTokens.PopIgnoreWhitespaceControl,
                    CommonTokens.RParen,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        child_index = 0

        types = []

        # '('
        assert len(node.Children) >= child_index + 1
        child_index += 1

        # <type>
        assert len(node.Children) >= child_index + 1
        types.append(ExtractDynamicExpressionNode(cast(Node, node.Children[child_index])))
        child_index += 1

        # '|'
        assert len(node.Children) >= child_index + 1
        child_index += 1

        # (<type> '|')*
        potential_types = ExtractRepeatedNodes(node, child_index, "Sep and Type")
        if potential_types is not None:
            child_index += 1

            for child in potential_types:
                child = cast(Node, child)

                assert len(child.Children) == 2
                types.append(ExtractDynamicExpressionNode(cast(Node, child.Children[0])))

        # <type>
        assert len(node.Children) >= child_index + 1
        types.append(ExtractDynamicExpressionNode(cast(Node, node.Children[child_index])))
        child_index += 1

        # ')'
        assert len(node.Children) >= child_index + 1
        child_index += 1

        assert len(node.Children) == child_index

        # Commit the results
        object.__setattr__(node, "Info", cls.TypeInfo(types))
