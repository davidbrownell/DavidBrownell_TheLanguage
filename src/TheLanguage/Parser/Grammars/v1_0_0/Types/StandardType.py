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

from typing import Dict, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import GrammarDSL
    from ..Common import NamingConventions
    from ..Common import Tokens as CommonTokens
    from ...GrammarStatement import GrammarStatement


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
        Name: str
        Modifier: Optional[CommonTokens.Token]
        LeafLookup: Dict[int, GrammarDSL.Leaf]

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
                    # <name>
                    CommonTokens.Name,

                    # <template>?
                    # TODO: Templates

                    # <modifier>?
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
        node: GrammarDSL.Node,
    ):
        node_values = GrammarDSL.ExtractValues(node)
        leaf_lookup = {}

        # <name>
        name, name_leaf = node_values[0]  # type: ignore
        leaf_lookup[id(name)] = name_leaf

        if not NamingConventions.Type.Regex.match(name):
            raise NamingConventions.InvalidTypeNameError.FromNode(name_leaf, name)  # type: ignore

        # <templates>?
        # TODO: Extract templates

        # <modifier>?
        if node_values[1]:  # type: ignore
            modifier = node_values[1][1].Type  # type: ignore
        else:
            modifier = None

        # Commit the data
        object.__setattr__(node, "Info", cls.TypeInfo(name, modifier, leaf_lookup))  # type: ignore
