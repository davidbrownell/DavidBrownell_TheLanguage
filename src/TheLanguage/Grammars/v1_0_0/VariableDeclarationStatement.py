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

from typing import cast

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common.GrammarAST import GetRegexMatch
    from .Common import GrammarDSL
    from .Common import NamingConventions
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import GrammarStatement


# ----------------------------------------------------------------------
class VariableDeclarationStatement(GrammarStatement):
    """\
    Declares a variable.

    <name> = <expression>
    """

    NODE_NAME                               = "Variable Declaration"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
                item=[
                    CommonTokens.Name,
                    CommonTokens.Equal,
                    GrammarDSL.DynamicStatements.Expressions,
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
        assert len(node.Children) > 1, node
        name_leaf = cast(GrammarDSL.Leaf, node.Children[0])

        variable_name = GetRegexMatch(name_leaf)

        if not NamingConventions.Variable.Regex.match(variable_name):
            raise NamingConventions.InvalidVariableNameError.FromNode(name_leaf, variable_name)
