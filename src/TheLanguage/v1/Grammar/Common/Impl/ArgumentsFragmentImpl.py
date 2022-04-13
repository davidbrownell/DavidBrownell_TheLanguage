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

from typing import Callable, cast, List, Optional, Union, Tuple

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
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Error import CreateError, Error, Region
    from ....Parser.Parser import CreateRegion, Phrase


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
    argument_element: PhraseItem,
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
def Extract(
    extract_element_func: Callable[[AST.Node], Tuple[Phrase, bool]],
    node: AST.Node,
    *,
    allow_empty: bool,
) -> Union[
    List[Error],
    bool,
    List[Phrase],
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

    phrases: List[Phrase] = []
    errors: List[Error] = []

    for element_node in itertools.chain(
        [cast(AST.Node, all_arguments_nodes[0]), ],
        (
            cast(AST.Node, ExtractSequence(delimited_node)[1])
            for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, all_arguments_nodes[1])))
        ),
    ):
        this_phrase, is_keyword = extract_element_func(element_node)

        if is_keyword:
            if first_keyword_node is not None:
                errors.append(
                    KeywordRequiredError.Create(
                        region=CreateRegion(element_node),
                        prev_region=CreateRegion(first_keyword_node),
                    ),
                )
            elif first_keyword_node is None:
                first_keyword_node = element_node

        phrases.append(this_phrase)

    return errors or phrases
