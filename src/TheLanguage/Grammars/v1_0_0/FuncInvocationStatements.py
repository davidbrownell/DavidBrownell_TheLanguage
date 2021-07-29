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
    from .Common.GrammarAST import (
        ExtractDynamicExpressionNode,
        ExtractLeafValue,
        ExtractOptionalNode,
        ExtractOrNode,
        Leaf,
        Node,
    )

    from .Common import GrammarDSL
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import GrammarStatement, ValidationError

    from ...ParserImpl.Statements.DynamicStatement import DynamicStatement
    from ...ParserImpl.Statements.SequenceStatement import SequenceStatement
    from ...ParserImpl.Statements.TokenStatement import NewlineToken


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
                Argument:
                    {arg}
                Keyword: {keyword}
                DefaultValue:{default}
                """,
            ).format(
                arg=StringHelpers.LeftJustify(
                    self.Argument.ToString(
                        verbose=verbose,
                    ).rstrip(),
                    4,
                ),
                keyword=self.Keyword or "<No Keyword>",
                default=" <No Default>" if self.DefaultValue is None else "\n    {}\n".format(
                    StringHelpers.LeftJustify(
                        self.DefaultValue.ToString(
                            verbose=verbose,
                        ).rstrip(),
                        4,
                    ),
                )
            )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class NodeInfo(object):
        Name: str
        Arguments: List["_FuncInvocationBase.ArgumentInfo"]

        # ----------------------------------------------------------------------
        def __str__(self):
            return self.ToString()

        # ----------------------------------------------------------------------
        def ToString(
            self,
            verbose=False,
        ):
            return textwrap.dedent(
                """\
                {name}
                    {arguments}
                """,
            ).format(
                name=self.Name,
                arguments="<No Arguments>" if not self.Arguments else StringHelpers.LeftJustify(
                    "".join(
                        [
                            textwrap.dedent(
                                """\
                                {}
                                {}
                                """,
                            ).format(
                                arg_index,
                                arg.ToString(
                                    verbose=verbose,
                                ),
                            )
                            for arg_index, arg in enumerate(self.Arguments)
                        ],
                    ).rstrip(),
                    4,
                ),
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
        statement_items = []

        # <name>
        statement_items += [
            CommonTokens.Name,
        ]

        # '(' <args> ')'
        #
        # Note that this statement is declared separately, as it is
        # recursive outside of the function name.
        statement_items += [
            GrammarDSL.StatementItem(
                name="Arguments",
                item=[
                    CommonTokens.LParen,
                    CommonTokens.PushIgnoreWhitespaceControl,

                    GrammarDSL.StatementItem(
                        name="Optional Arguments",
                        item=GrammarDSL.CreateDelimitedStatementItem(
                            GrammarDSL.StatementItem(
                                name="Argument",
                                item=(
                                    # <name> '=' <expr>
                                    GrammarDSL.StatementItem(
                                        name="Keyword Arg",
                                        item=[
                                            CommonTokens.Name,
                                            CommonTokens.Equal,
                                            GrammarDSL.DynamicStatements.Expressions,
                                        ],
                                    ),

                                    # <expr>
                                    GrammarDSL.DynamicStatements.Expressions,
                                ),
                            ),
                        ),
                        arity="?",
                    ),

                    CommonTokens.PopIgnoreWhitespaceControl,
                    CommonTokens.RParen,

                    # TODO: Chained Call
                    #    Note: May need to implement this by parsing the trailing content
                    #          as a block based on indentation.
                    #
                    # GrammarDSL.StatementItem(
                    #     name="Chained Call",
                    #     item=[
                    #         CommonTokens.PushIgnoreWhitespaceControl,
                    #         (
                    #             CommonTokens.DottedName,
                    #             CommonTokens.ArrowedName,
                    #         ),
                    #         None,
                    #         CommonTokens.PopIgnoreWhitespaceControl,
                    #     ],
                    #     arity="?",
                    # ),
                ],
            ),
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
        child_index = 0

        # <name>
        assert len(node.Children) >= child_index + 1
        func_name = ExtractLeafValue(cast(Leaf, node.Children[child_index]))
        child_index += 1

        # Do not validate the function name here, as we may be looking at a
        # dot-delimited name. The name will be validated when we attempt to
        # find the referenced value.

        # Arguments sub-statement

        # ----------------------------------------------------------------------
        def ExtractArguments(
            node: Node,
        ) -> List["_FuncInvocationBase.ArgumentInfo"]:
            child_index = 0

            # '('
            assert len(node.Children) >= child_index + 1
            child_index += 1

            # <args>
            arguments = []

            potential_arguments_node = ExtractOptionalNode(node, 1)
            if potential_arguments_node:
                child_index += 1

                # Get the arguments
                for argument_node in GrammarDSL.ExtractDelimitedNodes(
                    cast(Node, potential_arguments_node),
                ):
                    argument_node = cast(Node, ExtractOrNode(argument_node))

                    if isinstance(argument_node.Type, DynamicStatement):
                        argument_info = _FuncInvocationBase.ArgumentInfo(
                            ExtractDynamicExpressionNode(argument_node),
                            None,
                            None,
                        )
                    else:
                        assert len(argument_node.Children) == 3

                        argument_info = _FuncInvocationBase.ArgumentInfo(
                            argument_node,
                            ExtractLeafValue(cast(Leaf, argument_node.Children[0])),
                            ExtractDynamicExpressionNode(cast(Node, argument_node.Children[2])),
                        )

                    arguments.append(argument_info)

            # ')'
            assert len(node.Children) >= child_index + 1
            child_index += 1

            assert len(node.Children) == child_index
            return arguments

        # ----------------------------------------------------------------------

        assert len(node.Children) >= child_index + 1
        assert isinstance(node.Children[child_index].Type, SequenceStatement)
        arguments = ExtractArguments(cast(Node, node.Children[child_index]))
        child_index += 1

        # TODO: Extract the chain info

        # Statements will have a trailing newline
        if len(node.Children) > child_index:
            assert isinstance(node.Children[child_index].Type, NewlineToken)
            child_index += 1

        assert len(node.Children) == child_index

        # Ensure that all arguments after the first keyword argument
        # are also keyword arguments.
        encountered_keyword = False

        for argument in arguments:
            if argument.DefaultValue:
                encountered_keyword = True
            elif encountered_keyword:
                raise PositionalArgumentAfterKeywordArgumentError.FromNode(argument.Argument)

        # Persist the info
        object.__setattr__(node, "Info", cls.NodeInfo(func_name, arguments))


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
