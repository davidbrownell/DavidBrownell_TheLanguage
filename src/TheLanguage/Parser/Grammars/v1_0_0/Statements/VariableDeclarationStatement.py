# ----------------------------------------------------------------------
# |
# |  VariableDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 10:03:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableDeclarationStatement object"""

import os

from typing import Dict

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
class VariableDeclarationStatement(GrammarStatement):
    """\
    Declares a variable.

    <name> = <expression>
    """

    NODE_NAME                               = "Variable Declaration"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class VariableInfo(object):
        Name: str
        Expression: GrammarDSL.Node
        LeafLookup: Dict[int, GrammarDSL.Leaf]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
                item=[
                    # <name>
                    CommonTokens.Name,

                    # '='
                    CommonTokens.Equal,

                    # <expr>
                    GrammarDSL.DynamicStatementsType.Expressions,
                    CommonTokens.Newline,
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

        if not NamingConventions.Variable.Regex.match(name):
            raise NamingConventions.InvalidVariableNameError.FromNode(name_leaf, name)  # type: ignore

        # <expr>
        expr = node_values[2]  # type: ignore

        # Commit the data
        object.__setattr__(node, "Info", cls.VariableInfo(name, expr, leaf_lookup))  # type: ignore
