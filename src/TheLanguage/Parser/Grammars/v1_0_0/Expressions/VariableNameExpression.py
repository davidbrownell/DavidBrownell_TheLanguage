# ----------------------------------------------------------------------
# |
# |  VariableNameExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 10:16:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableNameExpression object"""

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
    from ....Statements import StatementDSL


# ----------------------------------------------------------------------
class VariableNameExpression(GrammarStatement):
    """A variable name"""

    NODE_NAME                               = "Variable Name"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class VariableInfo(object):
        Node: GrammarDSL.Node
        Name: str
        LeafLookup: Dict[int, GrammarDSL.Leaf]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableNameExpression, self).__init__(
            GrammarStatement.Type.Expression,
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,

                # <name>
                item=CommonTokens.Name,
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: GrammarDSL.Node,
    ):
        node_values = StatementDSL.ExtractValues(node)
        leaf_lookup = {}

        # <name>
        name, name_leaf = node_values[0]  # type: ignore
        leaf_lookup[id(name)] = name_leaf

        if not NamingConventions.Variable.Regex.match(name):
            raise NamingConventions.InvalidVariableNameError.FromNode(name_leaf, name)  # type: ignore

        # Commit the data
        object.__setattr__(node, "Info", cls.VariableInfo(node, name, leaf_lookup))  # type: ignore
