# ----------------------------------------------------------------------
# |
# |  LiteralFragment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-18 12:50:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when working with literal values"""

import os

from typing import cast

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST

    from ...Lexer.Phrases.DSL import (
        ExtractOr,
        ExtractToken,
        PhraseItem,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.ParserInfos.Literals.BooleanLiteralParserInfo import BooleanLiteralParserInfo
    from ...Parser.ParserInfos.Literals.LiteralParserInfo import LiteralParserInfo
    from ...Parser.ParserInfos.Literals.NoneLiteralParserInfo import NoneLiteralParserInfo


# ----------------------------------------------------------------------
def Create(
    phrase_name: str,
) -> PhraseItem:
    return PhraseItem(
        name=phrase_name,
        item=(
            PhraseItem(
                name="Boolean",
                item=(
                    "True",
                    "False",
                ),
            ),
            # TODO: Character
            # TODO: Integer
            PhraseItem(
                name="None",
                item="None",
            ),
            # TODO: Number
            # TODO: String
        ),
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> LiteralParserInfo:
    node = cast(AST.Node, ExtractOr(node))

    assert node.type is not None

    if node.type.name == "Boolean":
        value_node = cast(AST.Leaf, ExtractOr(node))

        value_info = ExtractToken(value_node)
        assert value_info == "True" or value_info == "False", value_info

        return BooleanLiteralParserInfo.Create(
            CreateRegions(value_node),
            value_info == "True",
        )

    elif node.type.name == "None":
        return NoneLiteralParserInfo.Create(CreateRegions(node))

    assert False, node.type  # pragma: no cover
