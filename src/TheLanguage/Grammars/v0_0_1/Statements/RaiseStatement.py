# ----------------------------------------------------------------------
# |
# |  RaiseStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 23:41:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RaiseStatement object"""

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
    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo
    from ....Lexer.Statements.RaiseStatementLexerInfo import (
        ExpressionLexerInfo,
        RaiseStatementLexerInfo,
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
class RaiseStatement(GrammarPhrase):
    """\
    Raises an exception.

    'raise' <expr>?

    Examples:
        raise
        raise foo
        raise (a, b, c)
    """

    PHRASE_NAME                             = "Raise Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(RaiseStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "raise",
                    PhraseItem(
                        item=DynamicPhrasesType.Expressions,
                        arity="?",
                    ),
                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractLexerInfo(
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # <expr>?
            expression_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[1])))
            if expression_node is not None:
                expression_info = cast(ExpressionLexerInfo, GetLexerInfo(ExtractDynamic(cast(Node, expression_node))))
            else:
                expression_info = None

            SetLexerInfo(
                node,
                RaiseStatementLexerInfo(
                    CreateLexerRegions(node, expression_node),  # type: ignore
                    expression_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
