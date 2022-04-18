# ----------------------------------------------------------------------
# |
# |  VariantCompileType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-15 10:10:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantCompileType object"""

import os

from typing import cast, List

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

    from ...Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
    )

    from ...Parser.Phrases.CompileTypes import VariantCompileType as VariantCompileTypeModule
    from ...Parser.Parser import CreateRegions


# ----------------------------------------------------------------------
class VariantCompileType(GrammarPhrase):
    PHRASE_NAME                             = "Variant CompileType"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariantCompileType, self).__init__(
            DynamicPhrasesType.CompileTypes,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=VariantPhraseImpl.Create(DynamicPhrasesType.CompileTypes),
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
            return VariantCompileTypeModule.VariantCompileType.Create(
                CreateRegions(node, node),
                cast(List[VariantCompileTypeModule.CompileTypePhrase], VariantPhraseImpl.Extract(node)),
            )

        # ----------------------------------------------------------------------

        return Callback
