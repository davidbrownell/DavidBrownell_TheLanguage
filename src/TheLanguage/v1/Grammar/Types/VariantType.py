# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 09:35:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType object"""

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
    from ..Common import MutabilityModifier
    from ..Common.Impl import VariantPhraseImpl

    from ..GrammarPhrase import AST, GrammarPhrase

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractOptional,
        ExtractSequence,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.ParserInfos.Types.VariantTypeParserInfo import (
        ParserInfoType,
        TypeParserInfo,
        VariantTypeParserInfo,
    )


# ----------------------------------------------------------------------
class VariantType(GrammarPhrase):
    PHRASE_NAME                             = "Variant Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariantType, self).__init__(
            DynamicPhrasesType.Types,
            self.PHRASE_NAME,
            [
                # Elements
                VariantPhraseImpl.Create(DynamicPhrasesType.Types),

                # <mutability_modifier>?
                OptionalPhraseItem(
                    name="Mutability Modifier",
                    item=MutabilityModifier.CreatePhraseItem(),
                ),
            ],
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        # ----------------------------------------------------------------------
        def Callback():
            nodes = ExtractSequence(node)
            assert len(nodes) == 2

            # Elements
            elements_node = cast(AST.Node, nodes[0])
            elements_info = cast(List[TypeParserInfo], VariantPhraseImpl.Extract(elements_node))

            # <mutability_modifier>?
            mutability_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
            if mutability_modifier_node is None:
                mutability_modifier_info = None
            else:
                mutability_modifier_info = MutabilityModifier.Extract(mutability_modifier_node)

            return VariantTypeParserInfo.Create(
                ParserInfoType.Standard,
                CreateRegions(node, mutability_modifier_node, elements_node),  # type: ignore
                mutability_modifier_info,
                elements_info,
            )

        # ----------------------------------------------------------------------

        return Callback
