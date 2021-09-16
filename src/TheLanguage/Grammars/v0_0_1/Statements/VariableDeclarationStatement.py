# ----------------------------------------------------------------------
# |
# |  VariableDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 15:25:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableDeclarationStatement object"""

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
    from ..Common import TypeModifier
    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo
    from ....Lexer.Statements.VariableDeclarationStatementLexerInfo import (
        ExpressionLexerInfo,
        NameLexerInfo,
        VariableDeclarationStatementLexerInfo,
    )

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class VariableDeclarationStatement(GrammarPhrase):
    """\
    Declares a variable.

    <modifier>? <name> '=' <expr>

    Examples:
        foo = bar
        (a, b,) = Func()
    """

    PHRASE_NAME                             = "Variable Declaration Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableDeclarationStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <modifier>?
                    PhraseItem(
                        name="Modifier",
                        item=TypeModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # <name>
                    DynamicPhrasesType.Names,

                    "=",

                    # <expr>
                    DynamicPhrasesType.Expressions,
                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractLexerInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 5

            # <modifier>?
            modifier_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[0])))
            if modifier_node is not None:
                modifier_info = TypeModifier.Extract(modifier_node)
            else:
                modifier_info = None

            # <name>
            name_node = cast(Node, ExtractDynamic(cast(Node, nodes[1])))
            name_info = cast(NameLexerInfo, GetLexerInfo(name_node))

            # <expr>
            expr_node = cast(Node, ExtractDynamic(cast(Node, nodes[3])))
            expr_info = cast(ExpressionLexerInfo, GetLexerInfo(expr_node))

            SetLexerInfo(
                node,
                VariableDeclarationStatementLexerInfo(
                    CreateLexerRegions(node, modifier_node, name_node, expr_node),  # type: ignore
                    modifier_info,  # type: ignore
                    name_info,
                    expr_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
