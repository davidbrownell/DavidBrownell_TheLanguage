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
    from ....Statements.StatementDSL import NodeInfo as RawNodeInfo


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
        Node: GrammarDSL.Node
        Name: str
        Modifier: Optional[CommonTokens.Token]
        ItemsLookup: Dict[int, GrammarDSL.Leaf]

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
        raw_info = RawNodeInfo.Extract(node)
        string_lookup = {}

        # <name>
        name_text, name_leaf = raw_info[0]  # type: ignore
        string_lookup[id(name_text)] = name_leaf

        if not NamingConventions.Type.Regex.match(name_text):
            raise NamingConventions.InvalidTypeNameError.FromNode(name_leaf, name_text)  # type: ignore

        # <template>?
        # TODO: Extract templates

        # <modifier>?
        if RawNodeInfo.IsMissing(raw_info[1]):  # type: ignore
            modifier = None
        else:
            modifier = raw_info[1].Leaf.Type  # type: ignore

        # Commit the data
        object.__setattr__(node, "Info", cls.TypeInfo(node, name_text, modifier, string_lookup))  # type: ignore
