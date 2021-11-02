import itertools
import os

from typing import cast, Callable, List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import Tokens as CommonTokens

    from ....Error import Error

    from .....Lexer.Phrases.DSL import (
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        Node,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from .....Parser.ParserInfo import ParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PositionalAfterKeywordError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Positional arguments may not appear after keyword arguments.",
    )


# ----------------------------------------------------------------------
def Create(
    name: str,
    open_token: str,
    close_token: str,
    argument_item: PhraseItem,
    *,
    allow_empty: bool,
) -> PhraseItem:

    # <argument_item> (',' <argument_item>)* ','?
    content_phrase_item = [
        # <argument_item>
        argument_item,

        # (',' <argument_item>)*
        ZeroOrMorePhraseItem.Create(
            name="Comma and Argument",
            item=[
                ",",
                argument_item,
            ],
        ),

        # ','?
        OptionalPhraseItem.Create(
            name="Trailing Comma",
            item=",",
        ),
    ]

    if allow_empty:
        content_phrase_item = OptionalPhraseItem(content_phrase_item)

    return PhraseItem.Create(
        name=name,
        item=[
            open_token,
            CommonTokens.PushIgnoreWhitespaceControl,

            content_phrase_item,

            CommonTokens.PopIgnoreWhitespaceControl,
            close_token,
        ],
    )


# ----------------------------------------------------------------------
def ExtractParserInfo(
    extract_argument_info_func: Callable[
        [Node],
        Tuple[
            ParserInfo,                     # ParserInfo for the parameter
            bool,                           # True if the code contains a keyword, False if not
        ]
    ],
    node: Node,
    *,
    allow_empty: bool,
) -> List[ParserInfo]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 5

    if allow_empty:
        arguments_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))
        if arguments_node is None:
            # We don't want to return None here, as there aren't arguments, but argument information
            # (e.g. '(' and ')' was found). Return a non-null value so that the caller can associate
            # a node with the result.
            return []
    else:
        arguments_node = cast(Node, nodes[2])

    arguments_nodes = ExtractSequence(arguments_node)
    assert len(arguments_nodes) == 3

    # Extract the arguments
    parser_infos: List[ParserInfo] = []
    encountered_keyword = False

    for argument_node in itertools.chain(
        [arguments_nodes[0]],
        (
            ExtractSequence(delimited_node)[1]
            for delimited_node in cast(List[Node], ExtractRepeat(cast(Node, arguments_nodes[1])))
        ),
    ):
        argument_node = cast(Node, argument_node)

        info, is_keyword = extract_argument_info_func(argument_node)

        if is_keyword:
            encountered_keyword = True
        elif encountered_keyword:
            raise PositionalAfterKeywordError.FromNode(argument_node)

        parser_infos.append(info)

    assert parser_infos
    return parser_infos
