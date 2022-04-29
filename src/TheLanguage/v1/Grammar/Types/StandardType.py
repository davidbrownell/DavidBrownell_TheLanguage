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

from typing import cast, List, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import ConstraintArgumentsFragment
    from ..Common import MutabilityModifier
    from ..Common import TemplateArgumentsFragment
    from ..Common import Tokens as CommonTokens

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.ParserInfos.Types.StandardTypeParserInfo import (
        StandardTypeItemParserInfo,
        StandardTypeParserInfo,
    )


# ----------------------------------------------------------------------
class StandardType(GrammarPhrase):
    PHRASE_NAME                             = "Standard Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        element_phrase_item = PhraseItem(
            name="Element",
            item=[
                # <name>
                CommonTokens.TypeName,

                # <template_arguments>?
                OptionalPhraseItem(
                    TemplateArgumentsFragment.Create(),
                ),

                # <constraint_arguments>?
                OptionalPhraseItem(
                    ConstraintArgumentsFragment.Create(),
                ),
            ],
        )

        # TODO: This should not include dots; that should be handled by a different operator.

        super(StandardType, self).__init__(
            DynamicPhrasesType.Types,
            self.PHRASE_NAME,
            [
                # Elements
                PhraseItem(
                    name="Elements",
                    item=[
                        # <element_phrase_item>
                        element_phrase_item,

                        ZeroOrMorePhraseItem(
                            [".", element_phrase_item],
                        ),
                    ],
                ),

                # <mutability_modifier>?
                OptionalPhraseItem(
                    name="Mutability Modifier",
                    item=MutabilityModifier.CreatePhraseItem(),
                ),
            ],
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        # ----------------------------------------------------------------------
        def Callback():
            nodes = ExtractSequence(node)
            assert len(nodes) == 2

            # <element_phrase_item>
            elements_node = cast(AST.Node, nodes[0])

            elements_nodes = ExtractSequence(elements_node)
            assert len(elements_nodes) == 2

            items: List[StandardTypeItemParserInfo] = []

            for element_node in itertools.chain(
                [cast(AST.Node, elements_nodes[0]), ],
                (
                    cast(AST.Node, ExtractSequence(delimited_node)[1])
                    for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, elements_nodes[1])))
                )
            ):
                element_nodes = ExtractSequence(element_node)
                assert len(element_nodes) == 3

                # <name>
                name_leaf = cast(AST.Leaf, element_nodes[0])
                name_info = CommonTokens.TypeName.Extract(name_leaf)  # type: ignore

                # <template_arguments>?
                template_info = None

                template_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], element_nodes[1])))
                if template_node is not None:
                    result = TemplateArgumentsFragment.Extract(template_node)

                    if isinstance(result, bool):
                        template_node = None
                    else:
                        template_info = result

                # <constraint_arguments>?
                constraint_info = None

                constraint_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], element_nodes[2])))
                if constraint_node is not None:
                    result = ConstraintArgumentsFragment.Extract(constraint_node)

                    if isinstance(result, bool):
                        constraint_node = None
                    else:
                        constraint_info = result

                items.append(
                    StandardTypeItemParserInfo.Create(
                        CreateRegions(element_node, name_leaf),
                        name_info,
                        template_info,
                        constraint_info,
                    ),
                )

            # <mutability_modifier>?
            mutability_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
            if mutability_modifier_node is None:
                mutability_modifier_info = None
            else:
                mutability_modifier_info = MutabilityModifier.Extract(mutability_modifier_node)

            return StandardTypeParserInfo.Create(
                CreateRegions(node, mutability_modifier_node, elements_node),
                mutability_modifier_info,
                items,
            )

        # ----------------------------------------------------------------------

        return Callback
