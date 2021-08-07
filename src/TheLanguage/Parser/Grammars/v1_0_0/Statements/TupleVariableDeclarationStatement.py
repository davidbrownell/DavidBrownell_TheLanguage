# ----------------------------------------------------------------------
# |
# |  TupleVariableDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-06 18:48:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleVariableDeclarationStatement object"""

import os

from typing import cast, Generator, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.GrammarAST import (
        ExtractOrNode,
        ExtractLeafValue,
    )

    from ..Common import GrammarDSL
    from ..Common import NamingConventions
    from ..Common import Tokens as CommonTokens
    from ..Common.TupleBase import TupleBase
    from ...GrammarStatement import GrammarStatement


# ----------------------------------------------------------------------
class TupleVariableDeclarationStatement(TupleBase):
    """\
    Creates a tuple variable declaration.

    '(' <content> ')' '=' <expr>

    Examples:
        (a, b) = Func()
        (a,) = value
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleVariableDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            "Tuple Variable Declaration",
            (CommonTokens.Name, None),
            additional_sequence_suffix_items=[
                CommonTokens.Equal,
                GrammarDSL.DynamicStatementsType.Expressions,
                CommonTokens.Newline,
            ],
        )

    # ----------------------------------------------------------------------
    @classmethod
    def EnumElements(
        cls,
        node: GrammarDSL.Node,
    ) -> Generator[
        Union[
            Tuple[GrammarDSL.Leaf, str],
            Tuple[GrammarDSL.Node, GrammarDSL.Node],
        ],
        None,
        None,
    ]:
        for child_node in super(TupleVariableDeclarationStatement, cls).EnumElements(node):
            child_node = ExtractOrNode(cast(GrammarDSL.Node, child_node))

            if isinstance(child_node, GrammarDSL.Leaf):
                yield child_node, ExtractLeafValue(child_node)
            else:
                yield child_node, child_node

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: GrammarDSL.Node,
    ):
        for element_node, value in cls.EnumElements(node):
            if isinstance(value, str):
                if not NamingConventions.Variable.Regex.match(value):
                    raise NamingConventions.InvalidVariableNameError.FromNode(element_node, value)

                continue

            # If here, we are looking at a nested tuple
            cls.ValidateNodeSyntax(cast(GrammarDSL.Node, element_node))
