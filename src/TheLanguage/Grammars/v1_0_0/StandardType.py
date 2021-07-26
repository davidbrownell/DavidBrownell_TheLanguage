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
        Leaf,
        Node,
    )

    from .Common import GrammarDSL
    from .Common import NamingConventions
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import GrammarStatement

    from ...ParserImpl.Token import Token
    from ...ParserImpl.Statements.OrStatement import OrStatement
    from ...ParserImpl.Statements.RepeatStatement import RepeatStatement


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
        assert len(node.Children) >= 1
        name = cast(str, ExtractLeafValue(cast(Leaf, node.Children[0])))

        if not NamingConventions.Type.Regex.match(name):
            raise NamingConventions.InvalidTypeNameError.FromNode(node.Children[0], name)

        if len(node.Children) >= 2:
            modifier_node = cast(Node, node.Children[1])

            # Drill into the Repeat node
            assert isinstance(modifier_node.Type, RepeatStatement)
            assert len(modifier_node.Children) == 1
            modifier_node = cast(Node, modifier_node.Children[0])

            # Drill into the Or node
            assert isinstance(modifier_node.Type, OrStatement)
            assert len(modifier_node.Children) == 1
            modifier_node = cast(Leaf, modifier_node.Children[0])

            modifier = cast(Token, modifier_node.Type)
        else:
            modifier = None

        return cls.TypeInfo(
            node,
            name,
            modifier,
        )
