# ----------------------------------------------------------------------
# |
# |  VariantExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 14:12:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantExpression object"""

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

    from ..Common.Impl import VariantPhraseImpl
    from ..Common import MutabilityModifier

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractOptional,
        ExtractSequence,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.ParserInfos.Expressions.VariantExpressionParserInfo import (
        ExpressionParserInfo,
        VariantExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class VariantExpression(GrammarPhrase):
    PHRASE_NAME                             = "Variant Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariantExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            self.PHRASE_NAME,
            [
                # Variant
                VariantPhraseImpl.Create(DynamicPhrasesType.Expressions),

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

            # Variant
            variant_node = cast(AST.Node, nodes[0])
            variant_info = cast(List[ExpressionParserInfo], VariantPhraseImpl.Extract(variant_node))

            # <mutability_modifier>?
            mutability_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
            if mutability_modifier_node is None:
                mutability_modifier_info = None
            else:
                mutability_modifier_info = MutabilityModifier.Extract(mutability_modifier_node)

            return VariantExpressionParserInfo.Create(
                CreateRegions(node, mutability_modifier_node),
                variant_info,
                mutability_modifier_info,
            )

        # ----------------------------------------------------------------------

        return Callback
