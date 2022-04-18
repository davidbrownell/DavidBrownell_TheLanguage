# ----------------------------------------------------------------------
# |
# |  StandardCompileType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-15 10:10:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardCompileType object"""

import os

from typing import cast

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import Tokens as CommonTokens

    from ...Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractToken,
    )

    from ...Parser.Parser import CreateRegion, CreateRegions

    from ...Parser.MiniLanguage.Types.BooleanType import BooleanType
    from ...Parser.MiniLanguage.Types.CharacterType import CharacterType
    from ...Parser.MiniLanguage.Types.IntegerType import IntegerType
    from ...Parser.MiniLanguage.Types.NoneType import NoneType
    from ...Parser.MiniLanguage.Types.NumberType import NumberType
    from ...Parser.MiniLanguage.Types.StringType import StringType

    from ...Parser.Phrases.CompileTypes.CompileTypePhrase import CompileTypePhrase
    from ...Parser.Phrases.Error import CreateError


# ----------------------------------------------------------------------
InvalidTypeError                            = CreateError(
    "'{type}' is not a valid compile time type",
    type=str,
)


# ----------------------------------------------------------------------
class StandardCompileType(GrammarPhrase):
    PHRASE_NAME                             = "Standard CompileType"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(StandardCompileType, self).__init__(
            DynamicPhrasesType.CompileTypes,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=CommonTokens.CompileTypeName,
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserPhrase(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserPhraseReturnType:
        value = ExtractToken(cast(AST.Leaf, node))

        if value == "Bool!":
            the_type = BooleanType()
        elif value == "Char!":
            the_type = CharacterType()
        elif value == "Int!":
            the_type = IntegerType()
        elif value == "None!":
            the_type = NoneType()
        elif value == "Num!":
            the_type = NumberType()
        elif value == "Str!":
            the_type = StringType()
        else:
            return [
                InvalidTypeError.Create(
                    region=CreateRegion(node),
                    type=value,
                ),
            ]

        return CompileTypePhrase.Create(
            CreateRegions(node, node),
            the_type,
        )
