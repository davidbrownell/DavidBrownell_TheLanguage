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

from typing import cast, Dict

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.GrammarAST import ExtractLeafValue
    from ..Common import GrammarDSL
    from ..Common import NamingConventions
    from ..Common import Tokens as CommonTokens
    from ...GrammarStatement import GrammarStatement
    from ....Statements.StatementDSL import NodeInfo as RawNodeInfo


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
        Node: GrammarDSL.Node
        Name: str
        Expression: RawNodeInfo.AnyType
        ItemsLookup: Dict[int, GrammarDSL.Leaf]

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
        raw_info = RawNodeInfo.Extract(node)
        string_lookup = {}

        # <name>
        name_text, name_leaf = raw_info[0]  # type: ignore
        string_lookup[id(name_text)] = name_leaf

        if not NamingConventions.Variable.Regex.match(name_text):
            raise NamingConventions.InvalidVariableNameError.FromNode(name_leaf, name_text)

        # <expr>
        expr = raw_info[2]  # type: ignore

        # Commit the data
        object.__setattr__(node, "Info", cls.VariableInfo(node, name_text, expr, string_lookup))
