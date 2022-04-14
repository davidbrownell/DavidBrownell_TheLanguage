# ----------------------------------------------------------------------
# |
# |  TupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 09:06:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleType object"""

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
    from ..Common.Impl import TuplePhraseImpl

    from ..GrammarPhrase import AST, GrammarPhrase

    from ...Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractOptional,
        ExtractSequence,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.Types.TupleType import (
        TupleType as ParserTupleType,
        TypePhrase as ParserTypePhrase,
    )


# ----------------------------------------------------------------------
class TupleType(GrammarPhrase):
    PHRASE_NAME                             = "Tuple Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleType, self).__init__(
            DynamicPhrasesType.Types,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # Elements
                    TuplePhraseImpl.Create(DynamicPhrasesType.Types),

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
        # ----------------------------------------------------------------------
        def Callback():
            nodes = ExtractSequence(node)
            assert len(nodes) == 2

            # Elements
            elements_node = cast(AST.Node, nodes[0])
            elements_info = cast(List[ParserTypePhrase], TuplePhraseImpl.Extract(elements_node))

            # <mutability_modifier>?
            mutability_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
            if mutability_modifier_node is None:
                mutability_modifier_info = None
            else:
                mutability_modifier_info = MutabilityModifier.Extract(mutability_modifier_node)

            return ParserTupleType(
                CreateRegions(node, mutability_modifier_node, elements_node),  # type: ignore
                mutability_modifier_info,
                elements_info,
            )

        # ----------------------------------------------------------------------

        return Callback  # type: ignore
