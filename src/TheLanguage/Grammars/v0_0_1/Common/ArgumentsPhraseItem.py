# ----------------------------------------------------------------------
# |
# |  ArgumentsPhraseItem.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-05 13:45:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when processing arguments (such as when calling functions or methods)"""

import itertools
import os

from typing import cast, List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens as CommonTokens

    from ...GrammarError import GrammarError
    from ...GrammarPhrase import CreateLexerRegions

    from ....Lexer.Common.ArgumentLexerInfo import (
        ArgumentLexerInfo,
        ExpressionLexerInfo,
    )

    from ....Lexer.LexerInfo import GetLexerInfo

    from ....Parser.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PositionalAfterKeywordError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty("Positional arguments may not appear after keyword arguments.")  # type: ignore


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    """\
    '(' <arguments>? ')'
    """

    argument_item = PhraseItem(
        name="Argument",
        item=[
            # (<name> '=')?
            PhraseItem(
                name="With Keyword",
                item=[
                    CommonTokens.GenericName,
                    "=",
                ],
                arity="?",
            ),

            # <expr>
            DynamicPhrasesType.Expressions,
        ]
    )

    return PhraseItem(
        name="Arguments",
        item=[
            # '('
            "(",
            CommonTokens.PushIgnoreWhitespaceControl,

            # (<argument_item> (',' <argument_item>)* ','?)?
            PhraseItem(
                name="Argument Items",
                item=[
                    # <argument_item>
                    argument_item,

                    # (',' <argument_item>)*
                    PhraseItem(
                        name="Comma and Argument",
                        item=[
                            ",",
                            argument_item,
                        ],
                        arity="*",
                    ),

                    # ','?
                    PhraseItem(
                        name="Trailing Comma",
                        item=",",
                        arity="?",
                    ),
                ],
                arity="?",
            ),

            # ')'
            CommonTokens.PopIgnoreWhitespaceControl,
            ")",
        ],
    )


# ----------------------------------------------------------------------
def ExtractLexerInfo(
    node: Node,
) -> Optional[List[ArgumentLexerInfo]]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 5

    arguments_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))
    if arguments_node is None:
        return None

    # Extract the arguments
    arguments_nodes = ExtractSequence(arguments_node)
    assert len(arguments_nodes) == 3

    argument_infos: List[ArgumentLexerInfo] = []
    encountered_keyword = False

    for argument_node in itertools.chain(
        [arguments_nodes[0]],
        [
            ExtractSequence(node)[1] for node in cast(
                List[Node],
                ExtractRepeat(cast(Node, arguments_nodes[1])),
            )
        ],
    ):
        argument_node = cast(Node, argument_node)

        argument_nodes = ExtractSequence(argument_node)
        assert len(argument_nodes) == 2

        # Keyword
        keyword_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], argument_nodes[0])))

        if keyword_node is not None:
            encountered_keyword = True

            keyword_nodes = ExtractSequence(keyword_node)
            assert len(keyword_nodes) == 2

            keyword_node = cast(Leaf, keyword_nodes[0])
            keyword_info = cast(str, ExtractToken(keyword_node))

        else:
            if encountered_keyword:
                raise PositionalAfterKeywordError.FromNode(argument_node)

            keyword_info = None

        # Expression
        expression_node = ExtractDynamic(cast(Node, argument_nodes[1]))
        expression_info = cast(ExpressionLexerInfo, GetLexerInfo(expression_node))

        # pylint: disable=too-many-function-args
        argument_infos.append(
            ArgumentLexerInfo(
                CreateLexerRegions(
                    argument_node,
                    expression_node,
                    keyword_node,
                ),  # type: ignore
                expression_info,
                keyword_info,
            ),
        )

    assert argument_infos
    return argument_infos
