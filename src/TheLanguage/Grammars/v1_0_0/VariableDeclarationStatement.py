# ----------------------------------------------------------------------
# |
# |  VariableDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 14:27:21
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
import textwrap

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import StringHelpers

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common import Tokens as CommonTokens
    from .Common import NamingConventions

    from ..GrammarStatement import (
        DynamicStatements,
        GrammarStatement,
        Node,
        Statement,
        ValidationError,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidVariableNameError(ValidationError):
    VariableName: str

    MessageTemplate                         = Interface.DerivedProperty(
        textwrap.dedent(
            """\
            '{{VariableName}}' is not a valid variable name.

            Variable names must:
                {}
            """,
        ).format(
            StringHelpers.LeftJustify("\n".join(NamingConventions.Variable.Constraints).rstrip(), 4),
        ),
    )


# ----------------------------------------------------------------------
class VariableDeclarationStatement(GrammarStatement):
    """\
    Declares a variable.

    <name> = <expression>>
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            Statement(
                "Variable Declaration",
                CommonTokens.Name,
                CommonTokens.Equal,
                DynamicStatements.Expressions,
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        # Validate the variable name
        assert len(node.Children) > 1
        name_node = node.Children[0]

        variable_name = name_node.Value.Match.group("value")

        if not NamingConventions.Variable.Regex.match(variable_name):
            raise InvalidVariableNameError.FromNode(name_node, variable_name)
