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

    from ...Parser.Parser import (
        CreateError,
        CreateRegion,
        CreateRegions,
    )

    from ...Parser.ParserInfos.CompileTypes.BooleanCompileTypeParserInfo import BooleanCompileTypeParserInfo
    from ...Parser.ParserInfos.CompileTypes.CharacterCompileTypeParserInfo import CharacterCompileTypeParserInfo
    from ...Parser.ParserInfos.CompileTypes.IntegerCompileTypeParserInfo import IntegerCompileTypeParserInfo
    from ...Parser.ParserInfos.CompileTypes.NoneCompileTypeParserInfo import NoneCompileTypeParserInfo
    from ...Parser.ParserInfos.CompileTypes.NumberCompileTypeParserInfo import NumberCompileTypeParserInfo
    from ...Parser.ParserInfos.CompileTypes.StringCompileTypeParserInfo import StringCompileTypeParserInfo


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

                    # <compile_type>
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

        # <compile_type>
        name_leaf = cast(AST.Leaf, nodes[0])
        name_info = ExtractToken(name_leaf)

        if name_info == "Bool":
            parser_info_type = BooleanCompileTypeParserInfo
        elif name_info == "Char":
            parser_info_type = CharacterCompileTypeParserInfo
        elif name_info == "Int":
            parser_info_type = IntegerCompileTypeParserInfo
        elif name_info == "None":
            parser_info_type = NoneCompileTypeParserInfo
        elif name_info == "Num":
            parser_info_type = NumberCompileTypeParserInfo
        elif name_info == "Str":
            parser_info_type = StringCompileTypeParserInfo
        else:
            return [
                InvalidTypeError.Create(
                    region=CreateRegion(name_leaf),
                    type=name_info,
                ),
            ]

        return parser_info_type.Create(
            CreateRegions(node),
        )
