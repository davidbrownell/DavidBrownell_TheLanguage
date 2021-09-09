# ----------------------------------------------------------------------
# |
# |  TupleBase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 16:34:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleBase object"""

import itertools
import os

from typing import cast, Generator, List, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import Tokens as CommonTokens
    from ....GrammarPhrase import GrammarPhrase, Leaf, Node

    from .....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class TupleBase(GrammarPhrase):
    """Base class for Tuple expressions, names, statements, and types"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        grammar_phrase_type: GrammarPhrase.Type,
        phrase_name: str,
    ):
        if grammar_phrase_type == GrammarPhrase.Type.Expression:
            tuple_element_item = DynamicPhrasesType.Expressions

        elif grammar_phrase_type == GrammarPhrase.Type.Name:
            tuple_element_item = DynamicPhrasesType.Names

        elif grammar_phrase_type == GrammarPhrase.Type.Type:
            tuple_element_item = DynamicPhrasesType.Types

        else:
            assert False, grammar_phrase_type  # pragma: no cover

        super(TupleBase, self).__init__(
            grammar_phrase_type,
            CreatePhrase(
                item=PhraseItem(
                    name=phrase_name,
                    item=(
                        # Multiple Elements
                        #   '(' <tuple_element> (',' <tuple_element>)+ ','? ')'
                        PhraseItem(
                            name="Multiple",
                            item=[
                                # '('
                                "(",
                                CommonTokens.PushIgnoreWhitespaceControl,

                                # <tuple_element> (',' <tuple_element>)+ ','?
                                tuple_element_item,

                                PhraseItem(
                                    name="Comma and Element",
                                    item=[
                                        ",",
                                        tuple_element_item,
                                    ],
                                    arity="+",
                                ),

                                PhraseItem(
                                    name="Trailing Comma",
                                    item=",",
                                    arity="?",
                                ),

                                # ')'
                                CommonTokens.PopIgnoreWhitespaceControl,
                                ")",
                            ],
                        ),

                        # Single Element
                        #   '(' <tuple_element> ',' ')'
                        PhraseItem(
                            name="Single",
                            item=[
                                # '('
                                "(",
                                CommonTokens.PushIgnoreWhitespaceControl,

                                # <tuple_element> ','
                                tuple_element_item,
                                ",",

                                # ')'
                                CommonTokens.PopIgnoreWhitespaceControl,
                                ")",
                            ],
                        ),
                    ),

                    # Use the order to disambiguate between group clauses and tuples.
                    ordered_by_priority=True,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    def EnumNodeValues(
        cls,
        node: Node,
    ) -> Generator[
        Union[Leaf, Node],
        None,
        None,
    ]:
        node = cast(Node, ExtractOr(node))
        assert node.Type

        nodes = ExtractSequence(node)
        assert len(nodes) >= 2

        enumeration_items = [
            [nodes[2]],
        ]

        if node.Type.Name == "Multiple":
            assert len(nodes) == 7

            enumeration_items.append(
                [
                    ExtractSequence(child_node)[1] for child_node in cast(List[Node], ExtractRepeat(cast(Node, nodes[3])))
                ],
            )

        elif node.Type.Name == "Single":
            assert len(nodes) == 6

        else:
            assert False, node.Type  # pragma: no cover

        for item in itertools.chain(*enumeration_items):
            yield ExtractDynamic(cast(Node, item))
