# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-11 07:08:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Statement to invoke functions"""

import os

from typing import cast, Generator, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import CommonTokens

    from ..GrammarStatement import (
        DynamicStatements,
        GrammarStatement,
        Leaf,
        Node,
        Statement,
        ValidationError,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PositionalParamAfterKeywordParamError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Positional arguments may not appear after keyword arguments")


# ----------------------------------------------------------------------
class FuncInvocationStatement(GrammarStatement):
    """\
    Invokes functions.

        <name> '(' <args> ')'

    """

    # ----------------------------------------------------------------------
    def __init__(self):
        # <name> = <expression|name>
        parameter_statement = [
            self._NamedStatement,
            DynamicStatements.Expressions,
            CommonTokens.NameToken,
        ]

        super(FuncInvocationStatement, self).__init__(
            GrammarStatement.Type.Hybrid,
            Statement(
                "Function Invocation",
                CommonTokens.NameToken,
                CommonTokens.LParenToken,
                CommonTokens.PushIgnoreWhitespaceControlToken(),

                (
                    Statement(
                        "Parameters",
                        parameter_statement,
                        (
                            Statement(
                                "Comma and Statement",
                                CommonTokens.CommaToken,
                                parameter_statement,
                            ),
                            0,
                            None,
                        ),
                        (CommonTokens.CommaToken, 0, 1),
                    ),
                    0,
                    1,
                ),

                CommonTokens.PopIgnoreWhitespaceControlToken(),
                CommonTokens.RParenToken,
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        # Keyword arguments must come after positional arguments
        encountered_keyword = False

        for parameter_info in cls._GenerateParameterInfo(node):
            if isinstance(parameter_info, tuple) and len(parameter_info) == 3:
                encountered_keyword = True
            elif encountered_keyword:
                reference_node = parameter_info[0] if isinstance(parameter_info, tuple) else parameter_info

                raise PositionalParamAfterKeywordParamError(
                    reference_node.IterBefore.Line,
                    reference_node.IterBefore.Column,
                    reference_node.IterAfter.Line,
                    reference_node.IterAfter.Column,
                )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    _NamedStatement                         = Statement(
        "Named",
        CommonTokens.NameToken,
        CommonTokens.EqualToken,
        [
            DynamicStatements.Expressions,
            CommonTokens.NameToken,
        ],
    )

    _ParameterInfo                          = Union[
        Tuple[Node, str, "_ParameterInfo"],             # Named Statement
        Node,                                           # Dynamic Statement
        Tuple[Leaf, str],                               # Name
    ]

    # ----------------------------------------------------------------------
    @classmethod
    def _GenerateParameterInfo(
        cls,
        node: Node,
    ) -> Generator["_ParameterInfo", None, None]:

        if len(node.Children) == 3:
            return

        # Function Invocation
        assert len(node.Children) == 4
        node = node.Children[2]

        # Repeat Parameters
        assert len(node.Children) == 1
        node = node.Children[0]

        # Parameters
        assert node.Children

        yield cls._ExtractParameterInfo(node.Children[0])

        if (
            len(node.Children) > 1
            and isinstance(node.Children[1].Type, tuple)
            and isinstance(node.Children[1].Type[0], Statement)
        ):
            node = node.Children[1]

            for child in node.Children:
                # First value is the comma, second value is the parameter information
                assert len(child.Children) == 2
                yield cls._ExtractParameterInfo(child.Children[1])

    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractParameterInfo(
        cls,
        node: Node,
    ) -> "_ParameterInfo":

        assert len(node.Children) == 1
        node = node.Children[0]

        # Named Statement
        if node.Type == cls._NamedStatement:
            assert len(node.Children) == 3
            key = node.Children[0].Value.Match.group("value")
            value = cls._ExtractParameterInfo(node.Children[2])

            return node, key, value

        # Dynamic Expression
        elif isinstance(node, Node):
            return node

        # Name
        elif isinstance(node, Leaf):
            leaf = cast(Leaf, node)

            return leaf, leaf.Value.Match.group("value")

        else:
            assert False, node  # pragma: no cover
