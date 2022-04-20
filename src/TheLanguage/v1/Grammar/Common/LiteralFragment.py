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
import re
import textwrap

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
        RegexToken,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.ParserInfos.Literals.BooleanLiteralParserInfo import BooleanLiteralParserInfo
    from ...Parser.ParserInfos.Literals.CharacterLiteralParserInfo import CharacterLiteralParserInfo
    from ...Parser.ParserInfos.Literals.IntegerLiteralParserInfo import IntegerLiteralParserInfo
    from ...Parser.ParserInfos.Literals.LiteralParserInfo import LiteralParserInfo
    from ...Parser.ParserInfos.Literals.NoneLiteralParserInfo import NoneLiteralParserInfo
    from ...Parser.ParserInfos.Literals.NumberLiteralParserInfo import NumberLiteralParserInfo
    from ...Parser.ParserInfos.Literals.StringLiteralParserInfo import StringLiteralParserInfo


# ----------------------------------------------------------------------
def Create(
    phrase_name: str,
) -> PhraseItem:
    return PhraseItem(
        name=phrase_name,
        item=(
            # True|False
            PhraseItem(
                name="Boolean",
                item=(
                    "True",
                    "False",
                ),
            ),

            # <character>
            # TODO: Unicode support doesn't seem to be working: 😀
            PhraseItem(
                RegexToken(
                    "Character",
                    re.compile(
                        textwrap.dedent(
                            r"""(?#
                            Single Quote                )'(?#
                            Content [begin]             )(?P<value>(?#
                                Standard char           ).(?#
                                Unicode 16-bit hex]     )|\\u\d{4}|(?#
                                Unicode 32-bit hex]     )|\\U\d{8}(?#
                            Content [end]               ))(?#
                            Single Quote                )'(?#
                            )""",
                        ),
                        re.UNICODE,
                    ),
                ),
            ),

            # <integer>
            PhraseItem(
                RegexToken(
                    "Integer",
                    re.compile(
                        textwrap.dedent(
                            r"""(?P<value>(?#
                            +/-                         )[+-]?(?#
                            Digits                      )\d+(?#
                            ))""",
                        ),
                    ),
                ),
            ),

            # None
            PhraseItem(
                name="None",
                item="None",
            ),

            # <number>
            PhraseItem(
                RegexToken(
                    "Number",
                    re.compile(
                        textwrap.dedent(
                            r"""(?P<value>(?#
                            +/-                         )[+-]?(?#
                            Leading Digits              )\d*(?#
                            Decimal Point               )\.(?#
                            Trailing Digits             )\d+(?#
                            ))""",
                        ),
                    ),
                ),
            ),

            # <string>
            PhraseItem(
                RegexToken(
                    "String",
                    re.compile(
                        textwrap.dedent(
                            r"""(?#
                            Double Quote                )"(?#
                            Content [begin]             )(?P<value>(?#
                            Non-Quote Chars             )(?:\\\"|[^\n])*(?#
                            Content [end]               ))(?#
                            Double Quote                )"(?#
                            )""",
                        ),
                    ),
                ),
            ),
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

    elif node.type.name == "Character":
        value_node = cast(AST.Leaf, node)
        value_info = ExtractToken(value_node)

        # TODO: How do we want to store these values?

        return CharacterLiteralParserInfo.Create(
            CreateRegions(value_node),
            value_info,
        )

    elif node.type.name == "Integer":
        value_node = cast(AST.Leaf, node)
        value_info = int(ExtractToken(value_node))

        return IntegerLiteralParserInfo.Create(
            CreateRegions(value_node),
            value_info,
        )

    elif node.type.name == "None":
        return NoneLiteralParserInfo.Create(CreateRegions(node))

    elif node.type.name == "Number":
        value_node = cast(AST.Leaf, node)
        value_info = float(ExtractToken(value_node))

        return NumberLiteralParserInfo.Create(
            CreateRegions(value_node),
            value_info,
        )

    elif node.type.name == "String":
        value_node = cast(AST.Leaf, node)
        value_info = ExtractToken(value_node).replace('\\"', '"')

        return StringLiteralParserInfo.Create(
            CreateRegions(value_node),
            value_info,
        )

    assert False, node.type  # pragma: no cover
