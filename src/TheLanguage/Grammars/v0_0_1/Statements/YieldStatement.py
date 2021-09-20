# ----------------------------------------------------------------------
# |
# |  YieldStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 23:18:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the YieldStatement object"""

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
    from ....Parser.Statements.YieldStatementParserInfo import (
        ExpressionParserInfo,
        YieldStatementParserInfo,
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
class YieldStatement(GrammarPhrase):
    """\
    Yields a value to the caller.

    'yield' ('from'? <expr>)?

    Examples:
        yield
        yield foo
        yield from Func()
    """

    PHRASE_NAME                             = "Yield Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(YieldStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "yield",
                    PhraseItem(
                        name="Suffix",
                        item=[
                            PhraseItem(
                                item="from",
                                arity="?",
                            ),
                            DynamicPhrasesType.Expressions,
                        ],
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

            # Suffix?
            suffix_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[1])))
            if suffix_node is not None:
                suffix_nodes = ExtractSequence(suffix_node)
                assert len(suffix_nodes) == 2

                # 'from'?
                is_recursive_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], suffix_nodes[0])))

                # <expr>
                expr_node = ExtractDynamic(cast(Node, suffix_nodes[1]))
                expr_info = cast(ExpressionParserInfo, GetParserInfo(expr_node))
            else:
                is_recursive_node = None

                expr_node = None
                expr_info = None

            SetParserInfo(
                node,
                YieldStatementParserInfo(
                    CreateParserRegions(node, expr_node, is_recursive_node),  # type: ignore
                    expr_info,
                    True if is_recursive_node is not None else None,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)
