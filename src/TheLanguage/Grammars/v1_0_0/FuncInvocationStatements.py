# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatements.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-17 13:43:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FunctionInvocationStatement and FunctionInvocationExpression objects"""

import os
import textwrap

from typing import cast, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common.GrammarAST import (
        ExtractDynamicExpressionNode,
        GetRegexMatch,
        Leaf,
        Node,
    )

    from .Common import GrammarDSL
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import GrammarStatement, ValidationError

    from ...ParserImpl.Statements.DynamicStatement import DynamicStatement
    from ...ParserImpl.Statements.OrStatement import OrStatement
    from ...ParserImpl.Statements.RepeatStatement import RepeatStatement
    from ...ParserImpl.Statements.SequenceStatement import SequenceStatement
    from ...ParserImpl.Statements.TokenStatement import TokenStatement


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

    NODE_NAME                               = "Function Invocation"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ArgumentInfo(object):
        Argument: Node

        # The following values are only valid for keyword arguments
        Keyword: Optional[str]
        DefaultValue: Optional[Node]

        # ----------------------------------------------------------------------
        def __str__(self):
            return self.ToString()

        # ----------------------------------------------------------------------
        def ToString(
            self,
            verbose=False,
        ) -> str:
            return self.Argument.ToString(
                verbose=verbose,
            )

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        grammar_statement_type: GrammarStatement.Type,
    ):
        argument_statement = (
            GrammarDSL.StatementItem(
                Name="Keyword",
                Item=[
                    CommonTokens.Name,
                    CommonTokens.Equal,
                    GrammarDSL.DynamicStatements.Expressions,
                ],
            ),

            GrammarDSL.DynamicStatements.Expressions,
        )

        suffix_statement = GrammarDSL.CreateStatement(
            name="Arguments",
            item=[
                # '(' ... ')'
                CommonTokens.LParen,
                CommonTokens.PushIgnoreWhitespaceControl,

                GrammarDSL.StatementItem(
                    Name="Optional Arguments",
                    Item=[
                        argument_statement,
                        GrammarDSL.StatementItem(
                            Item=[
                                CommonTokens.Comma,
                                argument_statement,
                            ],
                            Arity="*",
                        ),
                        GrammarDSL.StatementItem(
                            Item=CommonTokens.Comma,
                            Arity="?",
                        ),
                    ],
                    Arity="?",
                ),

                CommonTokens.PopIgnoreWhitespaceControl,
                CommonTokens.RParen,

                # TODO: Block statement?
                # GrammarDSL.StatementItem(
                #     Name="Suffix Call",
                #     Item=[
                #         CommonTokens.PushIgnoreWhitespaceControl,
                #         (
                #             CommonTokens.DottedName,
                #             CommonTokens.ArrowedName,
                #         ),
                #         None,
                #         CommonTokens.PopIgnoreWhitespaceControl,
                #     ],
                #     Arity="?",
                # ),
            ],
        )

        statement_items = [
            CommonTokens.Name,
            suffix_statement,
        ]

        if grammar_statement_type == GrammarStatement.Type.Statement:
            statement_items.append(CommonTokens.Newline)

        super(_FuncInvocationBase, self).__init__(
            grammar_statement_type,
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
                item=statement_items,
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        assert len(node.Children) >= 2, node.Children

        func_name = GetRegexMatch(cast(Leaf, node.Children[0]))

        # Drill into the arguments node
        assert isinstance(node.Children[1].Type, SequenceStatement)
        arguments_node = cast(Node, node.Children[1])

        assert len(node.Children) >= 2, arguments_node.Children
        potential_arguments_node = arguments_node.Children[1]

        if isinstance(potential_arguments_node, Leaf):
            # This leaf is the closing ')' token; this indicates that there aren't
            # and arguments
            arguments = []

        else:
            # Drill into the optional node
            assert isinstance(potential_arguments_node.Type, RepeatStatement)
            assert len(potential_arguments_node.Children) == 1
            arguments_node = cast(Node, potential_arguments_node.Children[0])

            # Get the arguments
            arguments = []

            arguments.append(cls._ExtractArgumentInfo(cast(Node, arguments_node.Children[0])))

            if (
                len(arguments_node.Children) >= 2
                and isinstance(arguments_node.Children[1].Type, RepeatStatement)
                and not isinstance(arguments_node.Children[1].Type.Statement, TokenStatement)
            ):
                for argument_node in cast(Node, arguments_node.Children[1]).Children:
                    argument_node = cast(Node, argument_node)

                    assert len(argument_node.Children) == 2
                    argument_node = cast(Node, argument_node.Children[1])

                    arguments.append(cls._ExtractArgumentInfo(argument_node))

        # Ensure that all arguments after the first keyword argument
        # are also keyword arguments.
        encountered_keyword = False

        for argument in arguments:
            if argument.DefaultValue:
                encountered_keyword = True
            elif encountered_keyword:
                raise PositionalArgumentAfterKeywordArgumentError.FromNode(argument.Argument)

        # TODO: Persist suffix

        # Persist the info
        object.__setattr__(node, "func_name", func_name)
        object.__setattr__(node, "arguments", arguments)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractArgumentInfo(
        cls,
        node: Node,
    ) -> "ArgumentInfo":
        # Drill into the Or node
        assert isinstance(node.Type, OrStatement)
        assert len(node.Children) == 1
        node = cast(Node, node.Children[0])

        if isinstance(node.Type, DynamicStatement):
            return cls.ArgumentInfo(ExtractDynamicExpressionNode(node), None, None)

        assert len(node.Children) == 3

        return cls.ArgumentInfo(
            node,
            cast(str, GetRegexMatch(cast(Leaf, node.Children[0]))),
            ExtractDynamicExpressionNode(cast(Node, node.Children[2])),
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
