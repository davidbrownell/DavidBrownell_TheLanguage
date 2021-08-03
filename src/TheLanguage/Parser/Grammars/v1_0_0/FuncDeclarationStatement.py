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
        ExtractOptionalNode,
        Leaf,
        Node,
    )

    from .Common import GrammarDSL
    from .Common import NamingConventions
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import GrammarStatement


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
    class Info(object):
        Export: bool                        # TODO: Use 'public'|'private'|'protected'
        Type: Node                          # TODO: Rename to 'ReturnType'
        Name: str
        Parameters: FuncParameters.Parameters
        Docstring: Optional[str]
        Statements: List[Node]

        # TODO: Add exceptions flag, remove trailing '?'
        # TODO: Add coroutine flags, remove trailing '...'

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
                    # TODO: Change this to public|protected|private
                    # 'export'?
                    GrammarDSL.StatementItem(
                        CommonTokens.Export,
                        arity="?",
                    ),

                    # <type>
                    GrammarDSL.DynamicStatementsType.Types,

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
                        GrammarDSL.DynamicStatementsType.Statements,
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
        child_index = 0

        # 'export'?
        assert len(node.Children) >= child_index + 1
        if isinstance(ExtractOptionalNode(node, child_index), Leaf):
            export = True
            child_index += 1
        else:
            export = False

        # <type>
        assert len(node.Children) >= child_index + 1
        the_type = ExtractDynamicExpressionNode(cast(Node, node.Children[child_index]))
        child_index += 1

        # <name>
        assert len(node.Children) >= child_index + 1
        name = ExtractLeafValue(cast(Leaf, node.Children[child_index]))

        if not NamingConventions.Function.Regex.match(name):
            raise NamingConventions.InvalidFunctionNameError.FromNode(node.Children[child_index], name)

        child_index += 1

        # '(' <parameters> ')'
        assert len(node.Children) >= child_index + 1
        parameters = FuncParameters.Extract(cast(Node, node.Children[child_index]))
        child_index += 1

        # ':' '\n' <indent>
        assert len(node.Children) >= child_index + 3
        child_index += 3

        # <docstring>?
        docstring_node = ExtractOptionalNode(node, child_index, "Docstring")
        if docstring_node is not None:
            child_index += 1

            docstring_node = cast(Node, docstring_node)
            assert len(docstring_node.Children) == 2
            docstring_node = cast(Leaf, docstring_node.Children[0])

            docstring = ExtractLeafValue(docstring_node)
        else:
            docstring = None

        # <statement>+
        assert len(node.Children) >= child_index + 1
        statements = [
            ExtractDynamicExpressionNode(cast(Node, child))
            for child in cast(Node, node.Children[child_index]).Children
        ]
        child_index += 1

        # <dedent>
        child_index += 1

        assert len(node.Children) == child_index

        # Persist the info
        object.__setattr__(
            node,
            "Info",
            cls.Info(
                export,
                the_type,
                name,
                parameters,
                docstring,
                statements,
            ),
        )
