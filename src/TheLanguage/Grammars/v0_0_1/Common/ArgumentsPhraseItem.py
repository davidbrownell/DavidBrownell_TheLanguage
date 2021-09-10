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
    from ...GrammarPhrase import ValidationError
    from ....Parser.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PositionalAfterKeywordError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Positional arguments may not appear after keyword arguments.")  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Argument(object):
    Expression: Union[Leaf, Node]
    Keyword: Optional[Union[Leaf, Node]]


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
                    DynamicPhrasesType.Names,
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
def Extract(
    node: Node,
) -> List[Argument]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 5

    # Extract the arguments
    arguments: List[Argument] = []

    if nodes[2] is not None:
        arguments_nodes = ExtractSequence(
            cast(
                Node,
                ExtractOptional(cast(Node, nodes[2])),
            ),
        )
        assert len(arguments_nodes) == 3

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
            if argument_nodes[0] is not None:
                encountered_keyword = True

                keyword_nodes = ExtractSequence(
                    cast(Node, ExtractOptional(cast(Node, argument_nodes[0]))),
                )
                assert len(keyword_nodes) == 2

                keyword_node = ExtractDynamic(cast(Node, keyword_nodes[0]))

            else:
                if encountered_keyword:
                    raise PositionalAfterKeywordError.FromNode(argument_node)

                keyword_node = None

            # Expression
            expression_node = ExtractDynamic(cast(Node, argument_nodes[1]))

            # Commit the value
            arguments.append(Argument(expression_node, keyword_node))

    return arguments
