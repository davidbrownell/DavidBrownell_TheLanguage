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

from typing import cast, List, Optional, Tuple

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens as CommonTokens

    from ..GrammarPhrase import AST
    from ..Statements.DocstringStatement import DocstringStatement

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        PhraseItem,
        OneOrMorePhraseItem,
    )

    from ...Parser.Parser import (
        CreateError,
        CreateRegion,
        Error,
        ErrorException,
        GetParserInfoNoThrow,
        TranslationUnitRegion,
    )

    from ...Parser.ParserInfos.Statements.StatementParserInfo import StatementParserInfo


# ----------------------------------------------------------------------
MultipleDocstringsError                     = CreateError(
    "There may only be one docstring within a scope",
    prev_region=TranslationUnitRegion,
)

MisplacedDocstringError                     = CreateError(
    "Docstrings must be the 1st statement within a scope; this is the '{ordinal}' statement",
    ordinal=int,
)


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
def Extract(
    node: AST.Node,
) -> Tuple[
    List[StatementParserInfo],
    Optional[Tuple[AST.Leaf, str]],
]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 2

    errors: List[Error] = []

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
    phrases: List[StatementParserInfo] = []
    docstring_leaf: Optional[AST.Leaf] = None
    docstring_info: Optional[str] = None

    statement_ctr = 0

    for statement_node in statement_nodes:
        statement_ctr += 1

        if statement_node.type is not None and statement_node.type.name == DocstringStatement.PHRASE_NAME:
            if docstring_leaf is not None:
                errors.append(
                    MultipleDocstringsError.Create(
                        region=CreateRegion(statement_node),
                        prev_region=CreateRegion(docstring_leaf),
                    ),
                )

                if statement_ctr != 1:
                    errors.append(
                        MisplacedDocstringError.Create(
                            region=CreateRegion(statement_node),
                            ordinal=statement_ctr,
                        ),
                    )

            docstring_result = DocstringStatement.GetDocstringInfo(cast(AST.Node, statement_node))
            if docstring_result is not None:
                docstring_leaf, docstring_info = docstring_result

        else:
            statement_phrase = cast(StatementParserInfo, GetParserInfoNoThrow(cast(AST.Node, statement_node)))
            if statement_phrase is not None:
                phrases.append(statement_phrase)

    if errors:
        raise ErrorException(*errors)

    # Note that the phrases may be empty; this is valid in some cases, so it is a condition that needs
    # to be handled by the caller if necessary.

    if docstring_leaf is None:
        assert docstring_info is None
        return (phrases, None)

    return phrases, (docstring_leaf, cast(str, docstring_info))
