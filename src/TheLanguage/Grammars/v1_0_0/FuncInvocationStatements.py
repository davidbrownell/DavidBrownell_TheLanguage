# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatements.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 00:17:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationStatement and FuncInvocationExpression objects"""

import os

from typing import List, Optional, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common import Tokens as CommonTokens
    from .Common import Statements as CommonStatements

    from ..GrammarStatement import (
        DynamicStatements,
        GrammarStatement,
        Leaf,
        Node,
        StatementEx,
        ValidationError,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PositionalArgumentAfterKeywordArgumentError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Positional arguments may not appear after keyword arguments")


# ----------------------------------------------------------------------
class _FuncInvocationBase(GrammarStatement):
    """\
    Invokes a function.

    <name> '(' <args> ')'
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        grammar_statement_type: GrammarStatement.Type,
    ):
        argument_statement = [
            # <name> = <rhs>
            StatementEx(
                "Keyword",
                CommonTokens.Name,
                CommonTokens.Equal,
                DynamicStatements.Expressions,
            ),

            DynamicStatements.Expressions,
        ]

        super(_FuncInvocationBase, self).__init__(
            grammar_statement_type,
            StatementEx(
                "Function Invocation",
                CommonTokens.Name,
                CommonTokens.LParen,
                CommonTokens.PushIgnoreWhitespaceControl,

                (
                    StatementEx(
                        "Arguments",
                        argument_statement,
                        (
                            StatementEx(
                                "Comma and Argument",
                                CommonTokens.Comma,
                                argument_statement,
                            ),
                            0,
                            None,
                        ),
                        (CommonTokens.Comma, 0, 1),
                    ),
                    0,
                    1,
                ),

                CommonTokens.PopIgnoreWhitespaceControl,
                CommonTokens.RParen,
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        assert len(node.Children) >= 3
        node.arguments = cls._GetArguments(node.Children[2])

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _ArgumentInfo(object):
        Argument: Node

        # The following values are only valid for keyword arguments
        Keyword: Optional[str]
        DefaultValue: Optional[Node]

    # ----------------------------------------------------------------------
    @classmethod
    def _GetArguments(
        cls,
        node: Union[Node, Leaf],
    ) -> List["FuncInvocationHybrid._ArgumentInfo"]:

        if isinstance(node, Leaf):
            # The leaf is the closing ')' token; this indicates that there aren't any
            # arguments.
            return []

        # Drill into the Optional node
        assert isinstance(node.Type, tuple)
        assert len(node.Children) == 1
        node = node.Children[0]

        # Get the arguments
        arguments = []

        arguments.append(cls._CreateArgumentInfo(node.Children[0]))

        if (
            len(node.Children) >= 2
            and isinstance(node.Children[1].Type, tuple)
            and isinstance(node.Children[1].Type[0], Statement)
        ):
            for argument_node in node.Children[1].Children:
                # First value is the comma, second is the argument
                assert len(argument_node.Children) == 2
                argument_node = argument_node.Children[1]

                arguments.append(cls._CreateArgumentInfo(argument_node))

        # Ensure that all arguments after the first keyword argument
        # are also keyword arguments.
        encountered_keyword = False

        for argument in arguments:
            if argument.DefaultValue:
                encountered_keyword = True
            elif encountered_keyword:
                raise PositionalArgumentAfterKeywordArgumentError.FromNode(argument.Argument)

        return arguments

    # ----------------------------------------------------------------------
    @classmethod
    def _CreateArgumentInfo(
        cls,
        node: Node,
    ) -> "FuncInvocationHybrid._ArgumentInfo":
        # Drill into the Or node
        assert isinstance(node.Type, list)
        assert len(node.Children) == 1
        node = node.Children[0]

        if isinstance(node.Type, Statement):
            # Keyword Argument
            assert len(node.Children) == 3

            return cls._ArgumentInfo(
                node,
                node.Children[0].Value.Match.group("value"),
                CommonStatements.ExtractDynamicExpressionsNode(node.Children[2]),
            )

        return cls._ArgumentInfo(
            CommonStatements.ExtractDynamicExpressionsNode(node),
            None,
            None,
        )


# ----------------------------------------------------------------------
class FuncInvocationStatement(_FuncInvocationBase):
    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncInvocationStatement, self).__init__(GrammarStatement.Type.Statement)


# ----------------------------------------------------------------------
class FuncInvocationExpression(_FuncInvocationBase):
    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncInvocationExpression, self).__init__(GrammarStatement.Type.Expression)
