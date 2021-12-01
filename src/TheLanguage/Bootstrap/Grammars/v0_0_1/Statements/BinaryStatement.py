# ----------------------------------------------------------------------
# |
# |  BinaryStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 13:59:34
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

from typing import Callable, cast, Dict, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens

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

    from ....Parser.Statements.BinaryStatementParserInfo import (
        BinaryStatementParserInfo,
        ExpressionParserInfo,
        NameParserInfo,
        OperatorType,
    )


# ----------------------------------------------------------------------
class BinaryStatement(GrammarPhrase):
    """\
    Statement that follows the form:

    <name> <operator> <expression>

    Examples:
        value += one
        value <<= two
    """

    PHRASE_NAME                             = "Binary Statement"

    OPERATOR_MAP: Dict[str, OperatorType]   = {
        # Mathematical
        "+=": OperatorType.AddInplace,
        "-=": OperatorType.SubtractInplace,
        "*=": OperatorType.MultiplyInplace,
        "**=": OperatorType.PowerInplace,
        "/=": OperatorType.DivideInplace,
        "//=": OperatorType.DivideFloorInplace,
        "%=": OperatorType.ModuloInplace,

        # Bit Manipulation
        "<<=": OperatorType.BitShiftLeftInplace,
        ">>=": OperatorType.BitShiftRightInplace,
        "^=": OperatorType.BitXorInplace,
        "&=": OperatorType.BitAndInplace,
        "|=": OperatorType.BitOrInplace,

        # Assignment
        "=": OperatorType.Assignment,
    }

    assert len(OPERATOR_MAP) == len(OperatorType)

    # ----------------------------------------------------------------------
    def __init__(self):
        super(BinaryStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <name>
                    DynamicPhrasesType.Expressions,

                    # <operator>
                    PhraseItem.Create(
                        name="Operator",
                        item=tuple(self.__class__.OPERATOR_MAP.keys()),
                    ),

                    # <expression>
                    DynamicPhrasesType.Expressions,
                    CommonTokens.Newline,
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
            assert len(nodes) == 4

            # <name>
            name_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
            name_info = cast(ExpressionParserInfo, GetParserInfo(name_node))

            # <operator>
            operator_leaf = cast(AST.Leaf, ExtractOr(cast(AST.Node, nodes[1])))

            operator_value = cast(
                str,
                ExtractToken(
                    operator_leaf,
                    use_match=True,
                ),
            )

            operator_info = cls.OPERATOR_MAP[operator_value]

            # <expression>
            expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[2])))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            return BinaryStatementParserInfo(
                CreateParserRegions(node, name_node, operator_leaf, expression_node),  # type: ignore
                name_info,
                operator_info,
                expression_info,
            )

        # ----------------------------------------------------------------------

        return Impl
