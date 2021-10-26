# ----------------------------------------------------------------------
# |
# |  ArgumentsPhraseItem.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 08:03:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality used when parsing arguments"""

import itertools
import os

from typing import cast, List, Optional, Union

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

    from ...Error import Error

    from ....Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Common.ArgumentParserInfo import (
        ArgumentParserInfo,
        ExpressionParserInfo,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PositionalAfterKeywordError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Positional arguments may not appear after keyword arguments.",
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    """\
    '(' <arguments>? ')'
    """

    argument_item = PhraseItem.Create(
        name="Argument",
        item=[
            # (<name> '=')?
            OptionalPhraseItem.Create(
                name="With Keyword",
                item=[
                    CommonTokens.ArgumentName,
                    "=",
                ],
            ),

            # <expression>
            DynamicPhrasesType.Expressions,
        ],
    )

    return PhraseItem.Create(
        name="Arguments",
        item=[
            # '('
            "(",
            CommonTokens.PushIgnoreWhitespaceControl,

            # (<argument_item> (',' <argument_item>)*) ','?)?
            OptionalPhraseItem.Create(
                name="Argument Items",
                item=[
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
                ],
            ),

            # ')'
            CommonTokens.PopIgnoreWhitespaceControl,
            ")",
        ],
    )


# ----------------------------------------------------------------------
def ExtractParserInfo(
    node: Node,
) -> Union[bool, List[ArgumentParserInfo]]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 5

    arguments_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))
    if arguments_node is None:
        # We don't want to return None here, as there aren't arguments, but argument information
        # (e.g. '(' and ')' was found). Return a non-null value so that the caller can associate
        # a node with the result.
        return False

    # Extract the arguments
    arguments_nodes = ExtractSequence(arguments_node)
    assert len(arguments_nodes) == 3

    argument_parser_infos: List[ArgumentParserInfo] = []
    encountered_keyword = False

    for argument_node in itertools.chain(
        [arguments_nodes[0]],
        [
            ExtractSequence(delimited_node)[1]
            for delimited_node in cast(List[Node], ExtractRepeat(cast(Node, arguments_nodes[1])))
        ],
    ):
        argument_node = cast(Node, argument_node)

        argument_nodes = ExtractSequence(argument_node)
        assert len(argument_nodes) == 2

        # (<name> '=')?
        keyword_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], argument_nodes[0])))

        if keyword_node is None:
            # This is a positional argument

            if encountered_keyword:
                raise PositionalAfterKeywordError.FromNode(argument_node)

            keyword_info = None

        else:
            # This is a keyword argument
            encountered_keyword = True

            keyword_nodes = ExtractSequence(keyword_node)
            assert len(keyword_nodes) == 2

            keyword_node = cast(Leaf, keyword_nodes[0])
            keyword_info = cast(str, ExtractToken(keyword_node))

        # <expression>
        expression_node = ExtractDynamic(cast(Node, argument_nodes[1]))
        expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

        argument_parser_infos.append(
            # pylint: disable=too-many-function-args
            ArgumentParserInfo(
                CreateParserRegions(argument_node, expression_node, keyword_node),  # type: ignore
                expression_info,
                keyword_info,
            ),
        )

    assert argument_parser_infos
    return argument_parser_infos
