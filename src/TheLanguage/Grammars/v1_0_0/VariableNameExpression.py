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

from typing import cast

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common.GrammarAST import ExtractLeafValue
    from .Common import GrammarDSL
    from .Common import NamingConventions
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import GrammarStatement


# ----------------------------------------------------------------------
class VariableNameExpression(GrammarStatement):
    """A variable name"""

    NODE_NAME                               = "Variable Name"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableNameExpression, self).__init__(
            GrammarStatement.Type.Expression,
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
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
        assert len(node.Children) == 1, node
        name_leaf = cast(GrammarDSL.Leaf, node.Children[0])

        variable_name = ExtractLeafValue(name_leaf)

        if not NamingConventions.Variable.Regex.match(variable_name):
            raise NamingConventions.InvalidVariableNameError.FromNode(name_leaf, variable_name)
