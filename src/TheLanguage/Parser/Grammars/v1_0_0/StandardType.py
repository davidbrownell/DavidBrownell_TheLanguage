# ----------------------------------------------------------------------
# |
# |  StandardType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-18 13:55:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardType object"""

import os

from typing import cast, Optional

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
        ExtractLeafValue,
        ExtractOptionalNode,
        ExtractOrNode,
        Leaf,
        Node,
    )

    from .Common import GrammarDSL
    from .Common import NamingConventions
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import GrammarStatement

    from ...Components.Token import Token


# ----------------------------------------------------------------------
class StandardType(GrammarStatement):
    """<name> <template>? <modifier>?"""

    NODE_NAME                               = "Standard"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class TypeInfo(object) :
        Node: Node
        Name: str
        Modifier: Optional[CommonTokens.Token]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(StandardType, self).__init__(
            GrammarStatement.Type.Type,
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
                item=[
                    CommonTokens.Name,
                    # TODO: Templates

                    GrammarDSL.StatementItem(
                        name="Modifier",
                        item=(
                            CommonTokens.Var,
                            CommonTokens.Ref,
                            CommonTokens.Val,
                            CommonTokens.View,
                            CommonTokens.Isolated,
                            CommonTokens.Shared,
                            CommonTokens.Immutable,
                            CommonTokens.Mutable,
                        ),
                        arity="?",
                    ),
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

        # <name>
        assert len(node.Children) >= child_index + 1
        name = ExtractLeafValue(cast(Leaf, node.Children[child_index]))
        child_index += 1

        if not NamingConventions.Type.Regex.match(name):
            raise NamingConventions.InvalidTypeNameError.FromNode(node.Children[0], name)

        # TODO: <template>?

        # <modifier>?
        potential_modifier_node = ExtractOptionalNode(node, child_index, "Modifier")
        if potential_modifier_node is not None:
            child_index += 1

            modifier_node = cast(Node, ExtractOrNode(cast(Node, potential_modifier_node)))
            modifier = cast(Token, modifier_node.Type)
        else:
            modifier = None

        assert len(node.Children) == child_index

        return cls.TypeInfo(
            node,
            name,
            modifier,
        )
