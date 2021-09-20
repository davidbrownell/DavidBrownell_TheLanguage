# ----------------------------------------------------------------------
# |
# |  ReturnStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 23:00:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ReturnStatement object"""

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
    from ....Parser.Statements.ReturnStatementParserInfo import (
        ExpressionParserInfo,
        ReturnStatementParserInfo,
    )

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class ReturnStatement(GrammarPhrase):
    """\
    Returns from a function.

    'return' <expr>?

    Example:
        return
        return var
    """

    PHRASE_NAME                               = "Return Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ReturnStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "return",
                    PhraseItem(
                        name="Value",
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
    def ExtractParserInfo(
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractParserInfoResult]:
        # ----------------------------------------------------------------------
        def CreateParserInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # <expr>?
            expression_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[1])))
            if expression_node is not None:
                expression_info = cast(ExpressionParserInfo, GetParserInfo(ExtractDynamic(cast(Node, expression_node))))
            else:
                expression_info = None

            SetParserInfo(
                node,
                ReturnStatementParserInfo(
                    CreateParserRegions(node, expression_node),  # type: ignore
                    expression_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)
