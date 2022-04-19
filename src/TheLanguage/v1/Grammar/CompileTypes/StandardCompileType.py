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
        ExtractSequence,
        ExtractToken,
    )

    from ...Parser.Parser import CreateError, CreateRegion, CreateRegions

    from ...Parser.MiniLanguage.Types.BooleanType import BooleanType
    from ...Parser.MiniLanguage.Types.CharacterType import CharacterType
    from ...Parser.MiniLanguage.Types.IntegerType import IntegerType
    from ...Parser.MiniLanguage.Types.NoneType import NoneType
    from ...Parser.MiniLanguage.Types.NumberType import NumberType
    from ...Parser.MiniLanguage.Types.StringType import StringType

    from ...Parser.ParserInfos.CompileTypes.CompileTypeParserInfo import CompileTypeParserInfo


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
                item=[
                    # Note that needs to be a sequence so that we can properly extract the value
                    CommonTokens.CompileTypeName,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        nodes = ExtractSequence(node)
        assert len(nodes) == 1

        name_leaf = cast(AST.Leaf, nodes[0])
        name_info = ExtractToken(name_leaf)

        if name_info == "Bool":
            the_type = BooleanType()
        elif name_info == "Char":
            the_type = CharacterType()
        elif name_info == "Int":
            the_type = IntegerType()
        elif name_info == "None":
            the_type = NoneType()
        elif name_info == "Num":
            the_type = NumberType()
        elif name_info == "Str":
            the_type = StringType()
        else:
            return [
                InvalidTypeError.Create(
                    region=CreateRegion(name_leaf),
                    type=name_info,
                ),
            ]

        return CompileTypeParserInfo.Create(
            CreateRegions(node, name_leaf),
            the_type,
        )
