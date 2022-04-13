# ----------------------------------------------------------------------
# |
# |  StatementsFragment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 11:01:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when processing statements"""

import os

from typing import cast, List, Optional, Tuple, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens as CommonTokens

    from ..GrammarPhrase import AST

    from ...Common.Diagnostics import CreateError, Diagnostics, Error

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        PhraseItem,
        OneOrMorePhraseItem,
    )

    from ...Parser.Parser import GetPhraseNoThrow, Phrase


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    return PhraseItem(
        name="Statements",
        item=[
            # ':'
            ":",

            # Multi- or Single-line
            (
                PhraseItem(
                    name="Multi-line",
                    item=[
                        CommonTokens.Newline,
                        CommonTokens.Indent,

                        # <statement>+
                        OneOrMorePhraseItem(
                            item=DynamicPhrasesType.Statements,
                        ),

                        CommonTokens.Dedent,
                    ],
                ),

                # Single-line
                DynamicPhrasesType.Statements,
            ),
        ],
    )


# ----------------------------------------------------------------------
# TODO: Fix this return value as it is wonky!
def Extract(
    node: AST.Node,
    diagnostics: Diagnostics,
) -> Optional[
    Tuple[
        List[Phrase],
        Optional[Tuple[AST.Leaf, str]],
    ]
]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 2

    statements_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[1])))

    assert statements_node.type is not None
    if statements_node.type.name == "Multi-line":
        multiline_nodes = ExtractSequence(statements_node)
        assert len(multiline_nodes) == 4

        statement_nodes = [
            ExtractDynamic(multiline_node)
            for multiline_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, multiline_nodes[2])))
        ]

    else:
        statement_nodes = [ExtractDynamic(statements_node)]

    # Extract phrases and process docstrings (if any)
    phrases: List[Phrase] = []
    docstring_leaf: Optional[AST.Leaf] = None
    docstring_info: Optional[Phrase] = None

    is_first_statement = True

    for statement_node in statement_nodes:
        statement_phrase = GetPhraseNoThrow(cast(AST.Node, statement_node))
        if statement_phrase is None:
            continue

        if False: # TODO: Remove this and uncomment the code below once DocstringStatement is implemented
            pass
        # if statement_node.type is not None and statement_node.type.name == DocstringStatement.PHRASE_NAME:
        #     if validate_docstrings:
        #         if docstring_leaf is not None:
        #            errors.append(
        #                MultipleDocstringsError.Create(
        #                    CreateRegion(statement_node),
        #                    prev_region=CreateRegion(docstring_leaf),
        #                ),
        #            )
        #
        #        if not is_first_statement:
        #            errors.append(
        #                MisplacedDocstringError.Create(
        #                    CreateRegion(statement_node),
        #                ),
        #            )
        #
        #     docstring_leaf = cast(AST.Leaf, statement_node)
        #     docstring_info = statement_phrase

        else:
            phrases.append(statement_phrase)

        is_first_statement = False

    # Note that the phrases may be empty; this is valid in some cases, so it is a condition that needs
    # to be handled by the caller if necessary.

    if docstring_leaf is None:
        assert docstring_info is None
        return (phrases, None)

    assert docstring_info is not None
    return (phrases, (docstring_leaf, "TODO")) # TODO: Finish this once DocstringStatement objects are available
