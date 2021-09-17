# ----------------------------------------------------------------------
# |
# |  BinaryStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-17 13:07:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryStatement object"""

import os

from typing import cast, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import CreateParserRegions, GrammarPhrase

    from ....Parser.ParserInfo import GetParserInfo, SetParserInfo

    from ....Parser.Statements.BinaryStatementParserInfo import (
        BinaryStatementParserInfo,
        ExpressionParserInfo,
        NameParserInfo,
        OperatorType,
    )

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
    )


# ----------------------------------------------------------------------
class BinaryStatement(GrammarPhrase):
    """\
    Statement that follows the form:

    <name> <op> <expr>

    Examples:
        value += one
        value <<= two
    """

    PHRASE_NAME                             = "Binary Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(BinaryStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <name>
                    DynamicPhrasesType.Names,

                    # <op>
                    CreatePhrase(
                        name="Operator",
                        item=(
                            # Mathematical
                            "+=",           # Addition
                            "-=",           # Subtraction
                            "*=",           # Multiplication
                            "**=",          # Power
                            "/=",           # Decimal Division
                            "//=",          # Integer Division
                            "%=",           # Modulo

                            # Bit Manipulation
                            "<<=",          # Left Shift
                            ">>=",          # Right Shift
                            "^=",           # Xor
                            "&=",           # Bitwise and
                            "|=",           # Bitwise or
                        ),
                    ),

                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # End
                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractParserInfoResult]:
        # ----------------------------------------------------------------------
        def CreateParserInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 4

            # <name>
            name_node = cast(Node, ExtractDynamic(cast(Node, nodes[0])))
            name_info = cast(NameParserInfo, GetParserInfo(name_node))

            # <op>
            operator_leaf = cast(Leaf, ExtractOr(cast(Node, nodes[1])))
            operator_value = cast(
                str,
                ExtractToken(
                    operator_leaf,
                    use_match=True,
                ),
            )

            if operator_value == "+=":
                operator_info = OperatorType.AddInplace
            elif operator_value == "-=":
                operator_info = OperatorType.SubtractInplace
            elif operator_value == "*=":
                operator_info = OperatorType.MultiplyInplace
            elif operator_value == "**=":
                operator_info = OperatorType.PowerInplace
            elif operator_value == "/=":
                operator_info = OperatorType.DivideInplace
            elif operator_value == "//=":
                operator_info = OperatorType.DivideFloorInplace
            elif operator_value == "%=":
                operator_info = OperatorType.ModuloInplace
            elif operator_value == "<<=":
                operator_info = OperatorType.BitShiftLeftInplace
            elif operator_value == ">>=":
                operator_info = OperatorType.BitShiftRightInplace
            elif operator_value == "^=":
                operator_info = OperatorType.BitXorInplace
            elif operator_value == "&=":
                operator_info = OperatorType.BitAndInplace
            elif operator_value == "|=":
                operator_info = OperatorType.BitOrInplace
            else:
                assert False, operator_value

            # <expr>
            expr_node = ExtractDynamic(cast(Node, nodes[2]))
            expr_info = cast(ExpressionParserInfo, GetParserInfo(expr_node))

            SetParserInfo(
                node,
                BinaryStatementParserInfo(
                    CreateParserRegions(node, name_node, operator_leaf, expr_node),  # type: ignore
                    name_info,
                    operator_info,
                    expr_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)
