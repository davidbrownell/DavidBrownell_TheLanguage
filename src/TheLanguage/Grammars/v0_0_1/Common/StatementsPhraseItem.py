# ----------------------------------------------------------------------
# |
# |  StatementsPhraseItem.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-08 13:45:36
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

from dataclasses import dataclass
import inflect

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens as CommonTokens
    from ..Statements.DocstringStatement import DocstringStatement
    from ...Error import Error

    from ....Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        Leaf,
        Node,
        OneOrMorePhraseItem,
        PhraseItem,
    )

    from ....Parser.Parser import GetParserInfo
    from ....Parser.Statements.StatementParserInfo import StatementParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidDocstringError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Docstrings are not supported in this context.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MultipleDocstringsError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "There may only be one docstring within a scope.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MisplacedDocstringError(Error):
    StatementOrdinal: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Docstrings must be the 1st statement within a scope; this is the '{StatementOrdinal}' statement.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StatementsRequiredError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Statements are required.",
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    return PhraseItem.Create(
        name="Statements",
        item=[
            # ':'
            ":",

            # - Multi-line statements
            # - Single-line statement
            (
                # <newline> <indent> <statement>+ <dedent>
                PhraseItem.Create(
                    name="Multi-line",
                    item=[
                        CommonTokens.Newline,
                        CommonTokens.Indent,

                        # <statement>+
                        OneOrMorePhraseItem.Create(
                            name="Statements",
                            item=DynamicPhrasesType.Statements,
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
def ExtractParserInfoWithDocstrings(
    node: Node,
) -> Tuple[
    List[StatementParserInfo],
    Optional[Tuple[str, Leaf]],
]:
    return _ExtractParserInfoImpl(
        node,
        validate_docstrings=True,
    )


# ----------------------------------------------------------------------
def ExtractParserInfo(
    node: Node,
) -> List[StatementParserInfo]:
    # Don't validate docstrings, as we don't want to generate nitpicky errors about the usage of the
    # docstrings when they aren't even valid in this context. So, suppress errors and then generate
    # an error here if a docstring was encountered.
    statement_infos, docstring_info = _ExtractParserInfoImpl(
        node,
        validate_docstrings=False,
    )

    if docstring_info is not None:
        raise InvalidDocstringError.FromNode(docstring_info[1])

    if not statement_infos:
        raise StatementsRequiredError.FromNode(node)

    return statement_infos


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractParserInfoImpl(
    node: Node,
    *,
    validate_docstrings: bool,
) -> Tuple[
    List[StatementParserInfo],
    Optional[Tuple[str, Leaf]],
]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 2

    statements_node = cast(Node, ExtractOr(cast(Node, nodes[1])))

    assert statements_node.Type is not None
    if statements_node.Type.Name == "Multi-line":
        multiline_nodes = ExtractSequence(statements_node)
        assert len(multiline_nodes) == 4

        statement_nodes = [
            ExtractDynamic(multiline_node)
            for multiline_node in cast(List[Node], ExtractRepeat(cast(Node, multiline_nodes[2])))
        ]

    else:
        statement_nodes = [ExtractDynamic(statements_node)]

    assert statement_nodes

    # Extract statements infos and process docstrings (if any)
    statement_infos: List[StatementParserInfo] = []
    docstring_leaf: Optional[Leaf] = None
    docstring_info: Optional[str] = None

    for statement_node_index, statement_node in enumerate(statement_nodes):
        statement_info = cast(Optional[StatementParserInfo], GetParserInfo(statement_node, allow_none=True))

        if statement_node.Type is not None and statement_node.Type.Name == DocstringStatement.PHRASE_NAME:
            if validate_docstrings:
                if docstring_leaf is not None:
                    raise MultipleDocstringsError.FromNode(statement_node)

                if statement_node_index != 0:
                    raise MisplacedDocstringError.FromNode(
                        statement_node,
                        inflect.engine().ordinal(statement_node_index + 1),
                    )

            docstring_leaf, docstring_info = DocstringStatement.GetMultilineContent(cast(Node, statement_node))

        elif statement_info is not None:
            statement_infos.append(statement_info)

    # Note that statement_infos may be empty; this is valid in some cases, so it is a condition that
    # needs to be handled by the caller if necessary.

    if docstring_leaf is None:
        assert docstring_info is None
        return statement_infos, None

    assert docstring_info is not None
    return statement_infos, (docstring_info, docstring_leaf)
