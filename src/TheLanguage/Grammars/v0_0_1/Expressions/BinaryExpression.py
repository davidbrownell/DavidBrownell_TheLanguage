# ----------------------------------------------------------------------
# |
# |  BinaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 18:48:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryExpression object"""

import os

from typing import Callable, cast, Dict, Union

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
    from ....Parser.Expressions.BinaryExpressionParserInfo import (
        BinaryExpressionParserInfo,
        ExpressionParserInfo,
        OperatorType,
    )


# ----------------------------------------------------------------------
class BinaryExpression(GrammarPhrase):
    """\
    Expression in the form:

    <expr> <op> <expr>

    Examples:
        one + two
        foo / bar
        biz and baz
        instance.Method
    """

    PHRASE_NAME                             = "Binary Expression"

    OPERATOR_MAP: Dict[str, OperatorType]   = {
        # Logical
        "and": OperatorType.LogicalAnd,
        "or": OperatorType.LogicalOr,
        "in": OperatorType.LogicalIn,
        "is": OperatorType.LogicalIs,

        # Function Invocation
        ".": OperatorType.ChainedFunc,
        "->": OperatorType.ChainedFuncReturnSelf,

        # Comparison
        "<": OperatorType.Less,
        "<=": OperatorType.LessEqual,
        ">": OperatorType.Greater,
        ">=": OperatorType.GreaterEqual,
        "==": OperatorType.Equal,
        "!=": OperatorType.NotEqual,

        # Mathematical
        "+": OperatorType.Add,
        "-": OperatorType.Subtract,
        "*": OperatorType.Multiply,
        "**": OperatorType.Power,
        "/": OperatorType.Divide,
        "//": OperatorType.DivideFloor,
        "%": OperatorType.Modulo,

        # Bit Manipulation
        "<<": OperatorType.BitShiftLeft,
        ">>": OperatorType.BitShiftRight,
        "^": OperatorType.BitXor,
        "&": OperatorType.BitAnd,
        "|": OperatorType.BitOr,
    }

    assert len(OPERATOR_MAP) == len(OperatorType)

    # ----------------------------------------------------------------------
    def __init__(self):
        super(BinaryExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # <op>
                    PhraseItem.Create(
                        name="Operator",
                        item=tuple(self.__class__.OPERATOR_MAP.keys()),
                    ),

                    # <expr>
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
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # <expr>
            left_node = ExtractDynamic(cast(AST.Node, nodes[0]))
            left_info = cast(ExpressionParserInfo, GetParserInfo(left_node))

            # <op>
            operator_leaf = cast(AST.Leaf, ExtractOr(cast(AST.Node, nodes[1])))

            op_value = cast(
                str,
                ExtractToken(
                    operator_leaf,
                    use_match=True,
                ),
            )

            operator_info = cls.OPERATOR_MAP[op_value]

            # <expr>
            right_node = ExtractDynamic(cast(AST.Node, nodes[2]))
            right_info = cast(ExpressionParserInfo, GetParserInfo(right_node))

            return BinaryExpressionParserInfo(
                CreateParserRegions(node, left_node, operator_leaf, right_node),  # type: ignore
                left_info,
                operator_info,
                right_info,
            )

        # ----------------------------------------------------------------------

        return Impl
