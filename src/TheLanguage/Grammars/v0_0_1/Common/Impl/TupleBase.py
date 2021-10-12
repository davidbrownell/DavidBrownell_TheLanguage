# ----------------------------------------------------------------------
# |
# |  TupleBase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 08:07:06
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

    from ....GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase

    from .....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        OneOrMorePhraseItem,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )


# ----------------------------------------------------------------------
class TupleBase(GrammarPhrase):
    """Base class for tuple expressions, names, statements, and types"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        dynamic_phrases_type: DynamicPhrasesType,
        phrase_name: str,
    ):
        tuple_elemement_item = dynamic_phrases_type

        super(TupleBase, self).__init__(
            dynamic_phrases_type,
            CreatePhrase(
                name=phrase_name,
                item=(
                    # Multiple Elements:
                    #   '(' <tuple_element_item> (',' <tuple_element_item>)+ ','? ')'
                    PhraseItem.Create(
                        name="Multiple Elements",
                        item=[
                            # '('
                            "(",
                            CommonTokens.PushIgnoreWhitespaceControl,

                            # <tuple_element_item>
                            tuple_elemement_item,

                            # (',' <tuple_element_item>)+
                            OneOrMorePhraseItem.Create(
                                name="Comma and Element",
                                item=[
                                    ",",
                                    tuple_elemement_item,
                                ],
                            ),

                            OptionalPhraseItem.Create(
                                name="Trailing Comma",
                                item=",",
                            ),

                            # ')'
                            CommonTokens.PopIgnoreWhitespaceControl,
                            ")",
                        ],
                    ),


                    # Single Element:
                    #   '(' <tuple_element_item> ',' ')'
                    PhraseItem.Create(
                        name="Single Element",
                        item=[
                            # '('
                            "(",
                            CommonTokens.PushIgnoreWhitespaceControl,

                            # <tuple_element_item> ','
                            tuple_elemement_item,
                            ",",

                            # ')'
                            CommonTokens.PopIgnoreWhitespaceControl,
                            ")",
                        ],
                    ),
                ),
            ),
        )

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def _EnumNodes(
        self,
        node: AST.Node,
    ) -> Generator[
        Union[AST.Leaf, AST.Node],
        None,
        None,
    ]:
        node = cast(AST.Node, ExtractOr(node))

        nodes = ExtractSequence(node)
        assert len(nodes) >= 2

        enumeration_items: List[List[AST.Node]] = [
            [cast(AST.Node, nodes[2])],
        ]

        assert node.Type is not None
        if node.Type.Name == "Multiple Elements":
            assert len(nodes) == 7

            enumeration_items.append(
                [
                    cast(AST.Node, ExtractSequence(delimited_node)[1])
                    for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, nodes[3])))
                ],
            )

        elif node.Type.Name == "Single Element":
            assert len(nodes) == 6

        else:
            assert False, node.Type  # pragma: no cover

        for item in itertools.chain(*enumeration_items):
            yield ExtractDynamic(item)
