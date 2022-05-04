# ----------------------------------------------------------------------
# |
# |  ArgumentsFragmentImpl.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 12:58:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that helps when implementing arguments"""

import itertools
import os

from typing import Callable, cast, List, Optional, Union, Type, TypeVar, Tuple

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import Tokens as CommonTokens

    from ...GrammarPhrase import AST

    from ....Lexer.Phrases.DSL import (
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        OptionalPhraseItem,
        PhraseItem,
        PhraseItemItemType,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import (
        CreateError,
        CreateRegion,
        CreateRegions,
        Error,
        ErrorException,
        ParserInfo,
        Region,
    )


# TODO: Add perfect forwarding

# ----------------------------------------------------------------------
KeywordRequiredError                        = CreateError(
    "Positional arguments may not appear after keyword arguments",
    prev_region=Region,
)


# ----------------------------------------------------------------------
def Create(
    name: str,
    open_token: str,
    close_token: str,
    argument_element: PhraseItemItemType,
    *,
    allow_empty: bool,
) -> PhraseItem:
    # <argument_element> (',' <argument_element>)* ','?
    arguments = [
        # <argument_element>
        argument_element,

        # (',' <argument_element>)*
        ZeroOrMorePhraseItem(
            name="Comma and Element",
            item=[
                ",",
                argument_element,
            ],
        ),

        # ','?
        OptionalPhraseItem(
            name="Trailing Comma",
            item=",",
        ),
    ]

    if allow_empty:
        arguments = OptionalPhraseItem(arguments)

    return PhraseItem(
        name=name,
        item=[
            open_token,
            CommonTokens.PushIgnoreWhitespaceControl,

            arguments,

            CommonTokens.PopIgnoreWhitespaceControl,
            close_token,
        ],
    )


# ----------------------------------------------------------------------
ExtractReturnType                           = TypeVar("ExtractReturnType", bound=ParserInfo)

def Extract(
    parser_info_type: Type[ExtractReturnType],
    extract_element_func: Callable[[AST.Node], Tuple[ParserInfo, bool]],
    node: AST.Node,
    *,
    allow_empty: bool,
) -> Union[
    bool,
    ExtractReturnType,
]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 5

    if allow_empty:
        all_arguments_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
        if all_arguments_node is None:
            return False
    else:
        all_arguments_node = cast(AST.Node, nodes[2])

    all_arguments_nodes = ExtractSequence(all_arguments_node)
    assert len(all_arguments_nodes) == 3

    first_keyword_node: Optional[AST.Node] = None

    parser_infos: List[ParserInfo] = []
    errors: List[Error] = []

    for element_node in itertools.chain(
        [cast(AST.Node, all_arguments_nodes[0]), ],
        (
            cast(AST.Node, ExtractSequence(delimited_node)[1])
            for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, all_arguments_nodes[1])))
        ),
    ):
        try:
            this_parser_info, is_keyword = extract_element_func(element_node)

        except ErrorException as ex:
            errors += ex.errors
            continue

        if is_keyword:
            if first_keyword_node is None:
                first_keyword_node = element_node
        elif first_keyword_node is not None:
            errors.append(
                KeywordRequiredError.Create(
                    region=CreateRegion(element_node),
                    prev_region=CreateRegion(first_keyword_node),
                ),
            )

        parser_infos.append(this_parser_info)

    if errors:
        raise ErrorException(*errors)

    return parser_info_type.Create(  # type: ignore
        CreateRegions(node, node),
        parser_infos,
    )
