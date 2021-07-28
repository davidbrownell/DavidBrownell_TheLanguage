# ----------------------------------------------------------------------
# |
# |  FuncDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-27 00:47:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncDeclarationStatement object"""

import os
import textwrap

from typing import cast, List, Optional

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
    from .Common import FuncParameters

    from .Common.GrammarAST import (
        ExtractDynamicExpressionNode,
        ExtractLeafValue,
        Leaf,
        Node,
    )

    from .Common import GrammarDSL
    from .Common import NamingConventions
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import GrammarStatement

    from ...ParserImpl.Statements.RepeatStatement import RepeatStatement
    from ...ParserImpl.Statements.Statement import Statement


# ----------------------------------------------------------------------
class FuncDeclarationStatement(GrammarStatement):
    """\
    Declares a function.

    'export'? <type> <name> '(' <parameters> ')' ':'
        <docstring>?
        <statement>+
    """

    NODE_NAME                               = "Function Declaration"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class NodeInfo(object):
        Export: bool
        Type: Node
        Name: str
        Parameters: FuncParameters.Parameters
        Docstring: Optional[str]
        Statements: List[Node]

        # ----------------------------------------------------------------------
        def __str__(self):
            return self.ToString()

        # ----------------------------------------------------------------------
        def ToString(
            self,
            verbose=False,
        ) -> str:
            return textwrap.dedent(
                """\
                {name}
                    Export: {export}
                    Statements: {num_statements}
                    Type:
                        {the_type}
                    Parameters:
                        {parameters}
                    Docstring:
                        {docstring}
                """,
            ).format(
                name=self.Name,
                export=self.Export,
                num_statements=len(self.Statements),
                the_type=StringHelpers.LeftJustify(
                    self.Type.ToString(
                        verbose=verbose,
                    ).rstrip(),
                    8,
                ),
                parameters=StringHelpers.LeftJustify(
                    self.Parameters.ToString(
                        verbose=verbose,
                    ).rstrip(),
                    8,
                ),
                docstring=StringHelpers.LeftJustify(
                    (self.Docstring or "<No Data>").rstrip(),
                    8,
                ),
            )

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
                item=[
                    # 'export'?
                    GrammarDSL.StatementItem(
                        CommonTokens.Export,
                        arity="?",
                    ),

                    # <type>
                    GrammarDSL.DynamicStatements.Types,

                    # <name>
                    CommonTokens.Name,

                    # '(' <parameters> ')'
                    FuncParameters.CreateStatement(),

                    # ':'
                    CommonTokens.Colon,
                    CommonTokens.Newline,
                    CommonTokens.Indent,

                    # <docstring>?
                    # TODO: Move this to a common location
                    GrammarDSL.StatementItem(
                        name="Docstring",
                        item=[
                            CommonTokens.DocString,
                            CommonTokens.Newline,
                        ],
                        arity="?",
                    ),

                    # <statement>+
                    GrammarDSL.StatementItem(
                        GrammarDSL.DynamicStatements.Statements,
                        arity="+",
                    ),

                    CommonTokens.Dedent,
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
        # export
        assert node.Children

        if (
            isinstance(node.Children[0].Type, RepeatStatement)
            and len(cast(Node, node.Children[0]).Children) == 1
            and isinstance(cast(Node, node.Children[0]).Children[0], Leaf)
        ):
            export = True
            child_offset = 1
        else:
            export = False
            child_offset = 0

        # type
        assert len(node.Children) > child_offset + 1
        the_type = ExtractDynamicExpressionNode(cast(Node, node.Children[child_offset]))

        # name
        assert len(node.Children) > child_offset + 2
        name = cast(str, ExtractLeafValue(cast(Leaf, node.Children[child_offset + 1])))

        if not NamingConventions.Function.Regex.match(name):
            raise NamingConventions.InvalidFunctionNameError.FromNode(node.Children[child_offset + 2], name)

        # parameters
        assert len(node.Children) > child_offset + 3
        parameters = FuncParameters.Extract(cast(Node, node.Children[child_offset + 2]))

        # Move past the colon, newline, and indent
        child_offset += 3

        # docstring
        assert len(node.Children) > child_offset + 4
        if (
            isinstance(node.Children[child_offset + 3].Type, RepeatStatement)
            and len(cast(Node, node.Children[child_offset + 3]).Children) == 1
            and cast(Statement, cast(Node, node.Children[child_offset + 3]).Children[0].Type).Name == "Docstring"
        ):
            # Drill into the optional node
            docstring_node = cast(Node, cast(Node, node.Children[child_offset + 3]).Children[0])

            assert len(docstring_node.Children) == 2
            docstring_node = cast(Leaf, docstring_node.Children[0])

            docstring = cast(str, ExtractLeafValue(docstring_node))
            child_offset += 1
        else:
            docstring = None

        # statements
        assert len(node.Children) > child_offset + 4
        statements = [
            ExtractDynamicExpressionNode(cast(Node, child))
            for child in cast(Node, node.Children[child_offset + 3]).Children
        ]

        # Persist the info
        object.__setattr__(
            node,
            "Info",
            cls.NodeInfo(
                export,
                the_type,
                name,
                parameters,
                docstring,
                statements,
            ),
        )
