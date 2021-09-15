# ----------------------------------------------------------------------
# |
# |  StatementsPhraseItem.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-05 18:29:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when processing statements"""

import os

from typing import cast, List, Optional, Tuple

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens

    from ....Lexer.LexerInfo import GetLexerInfo
    from ....Lexer.Statements.StatementLexerInfo import StatementLexerInfo

    from ....Parser.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    return PhraseItem(
        name="Statements",
        item=[
            # ':'
            ":",

            # - Multi-line statements
            # - Single-line statement
            (
                # <newline> <indent> <statement>+ <dedent>
                PhraseItem(
                    name="Multi-line",
                    item=[
                        CommonTokens.Newline,
                        CommonTokens.Indent,

                        # <statement>+
                        PhraseItem(
                            name="Statements",
                            item=DynamicPhrasesType.Statements,
                            arity="+",
                        ),

                        CommonTokens.Dedent,
                    ],
                ),

                # <statement>
                DynamicPhrasesType.Statements,
            ),
        ],
    )


# ----------------------------------------------------------------------
def ExtractLexerInfo(
    node: Node,
) -> List[StatementLexerInfo]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 2

    statements_node = cast(Node, ExtractOr(cast(Node, nodes[1])))
    assert statements_node.Type

    if statements_node.Type.Name == "Multi-line":
        multiline_nodes = ExtractSequence(statements_node)
        assert len(multiline_nodes) == 4

        statements = [
            ExtractDynamic(multiline_node)
            for multiline_node in cast(List[Node], ExtractRepeat(cast(Node, multiline_nodes[2])))
        ]

    else:
        statements = [ExtractDynamic(statements_node)]

    assert statements
    return [cast(StatementLexerInfo, GetLexerInfo(statement)) for statement in statements]
