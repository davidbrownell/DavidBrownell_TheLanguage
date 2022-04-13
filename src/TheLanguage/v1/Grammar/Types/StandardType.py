# ----------------------------------------------------------------------
# |
# |  StandardType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 08:49:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardType object"""

import itertools
import os

from typing import cast, Generator, List, Optional, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import MutabilityModifier
    from ..Common import Tokens as CommonTokens

    from ...Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        OneOrMorePhraseItem,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.Types.StandardType import (
        StandardType as ParserStandardType,
        StandardTypeItemPhrase as ParserStandardTypeItemPhrase,
    )


# ----------------------------------------------------------------------
class StandardType(GrammarPhrase):
    PHRASE_NAME                             = "Standard Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        element_phrase_item = CreatePhrase(
            name="Element",
            item=[
                # <name>
                CommonTokens.RuntimeTypeName,

                # TODO: <template_arguments>?
                # TODO: <constraint_arguments>?
            ],
        )

        super(StandardType, self).__init__(
            DynamicPhrasesType.Types,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # Elements
                    CreatePhrase(
                        name="Elements",
                        item=[
                            # <element_phrase_item>
                            element_phrase_item,

                            # ('.' <element_phrase_item>)*
                            OptionalPhraseItem(
                                item=[
                                    CommonTokens.PushIgnoreWhitespaceControl,

                                    OneOrMorePhraseItem(
                                        name="Dot and Element",
                                        item=[
                                            ".",
                                            element_phrase_item,
                                        ],
                                    ),

                                    CommonTokens.PopIgnoreWhitespaceControl,
                                ],
                            ),
                        ],
                    ),

                    # <mutability_modifier>?
                    OptionalPhraseItem(
                        name="Mutability Modifier",
                        item=MutabilityModifier.CreatePhraseItem(),
                    ),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserPhrase(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserPhraseReturnType:
        nodes = ExtractSequence(node)
        assert len(nodes) == 2

        # Elements
        elements_node = cast(AST.Node, nodes[0])
        elements_nodes = ExtractSequence(elements_node)
        assert len(elements_nodes) == 2

        # <element_phrase_item>
        all_element_nodes: List[
            Union[
                List[AST.Node],
                Generator[AST.Node, None, None],
            ]
        ] = [
            [cast(AST.Node, elements_nodes[0]), ],
        ]

        # ('.' <element_phrase_item>)*
        trailing_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], elements_nodes[1])))
        if trailing_node is not None:
            trailing_nodes = ExtractSequence(trailing_node)
            assert len(trailing_nodes) == 3

            all_element_nodes.append(
                (
                    cast(AST.Node, ExtractSequence(delimited_node)[1])
                    for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, trailing_nodes[1])))
                ),
            )

        items: List[ParserStandardTypeItemPhrase] = []

        for this_element_node in itertools.chain(*all_element_nodes):
            these_element_nodes = ExtractSequence(this_element_node)
            assert len(these_element_nodes) == 1 # TODO: 3

            # <name>
            name_leaf = cast(AST.Leaf, these_element_nodes[0])
            name_info = ExtractToken(name_leaf)

            # TODO: <template_arguments>?
            # TODO: <constraint_arguments>?

            items.append(
                ParserStandardTypeItemPhrase.Create(
                    CreateRegions(this_element_node, name_leaf),
                    name_info,
                ),
            )

        # <mutability_modifier>?
        mutability_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
        if mutability_modifier_node is None:
            mutability_modifier_info = None
        else:
            mutability_modifier_info = MutabilityModifier.Extract(mutability_modifier_node)

        return ParserStandardType.Create(
            CreateRegions(node, mutability_modifier_node, elements_node),
            mutability_modifier_info,
            items,
        )
