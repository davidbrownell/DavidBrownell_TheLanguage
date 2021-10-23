# ----------------------------------------------------------------------
# |
# |  UnaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-11 17:04:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UnaryExpression object"""

import os

from typing import Callable, cast, Dict, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Expressions.UnaryExpressionParserInfo import (
        ExpressionParserInfo,
        OperatorType,
        UnaryExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class UnaryExpression(GrammarPhrase):
    """\
    A prefix to an expression.

    <op> <expression>

    Examples:
        not foo
        ~bar
        await baz
    """

    PHRASE_NAME                             = "Unary Expression"

    # Note that any alphanumeric operators added here must also be added to 'ReservedKeywords'
    # in ../Common/Tokens.py.
    OPERATOR_MAP: Dict[str, OperatorType]   = {
        # Async
        "await": OperatorType.Await,

        # Transfer
        "copy": OperatorType.Copy,
        "move": OperatorType.Move,

        # Logical
        "not": OperatorType.Not,

        # Mathematical
        "+": OperatorType.Positive,
        "-": OperatorType.Negative,

        # Bit Manipulation
        "~": OperatorType.BitCompliment,
    }

    assert len(OPERATOR_MAP) == len(OperatorType)

    # ----------------------------------------------------------------------
    def __init__(self):
        super(UnaryExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <operator>
                    PhraseItem.Create(
                        name="Operator",
                        item=tuple(self.__class__.OPERATOR_MAP.keys()),
                    ),

                    # <expression>
                    DynamicPhrasesType.Expressions,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 2

            # <operator>
            operator_leaf = cast(AST.Leaf, ExtractOr(cast(AST.Node, nodes[0])))

            op_value = cast(
                str,
                ExtractToken(
                    operator_leaf,
                    use_match=True,
                ),
            )

            operator_info = cls.OPERATOR_MAP[op_value]

            # <expression>
            expression_node = ExtractDynamic(cast(AST.Node, nodes[1]))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            return UnaryExpressionParserInfo(
                CreateParserRegions(node, operator_leaf, expression_node),  # type: ignore
                operator_info,
                expression_info,
            )

        # ----------------------------------------------------------------------

        return Impl
