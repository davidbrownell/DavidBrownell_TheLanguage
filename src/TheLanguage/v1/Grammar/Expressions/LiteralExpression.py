# ----------------------------------------------------------------------
# |
# |  LiteralExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 15:14:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LiteralExpression object"""

import os
import re
import textwrap

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

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractOr,
        ExtractToken,
        PhraseItem,
        RegexToken,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.ParserInfos.ParserInfo import ParserInfoType

    from ...Parser.ParserInfos.Expressions.BooleanExpressionParserInfo import BooleanExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.CharacterExpressionParserInfo import CharacterExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.IntegerExpressionParserInfo import IntegerExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.NumberExpressionParserInfo import NumberExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.StringExpressionParserInfo import StringExpressionParserInfo


# ----------------------------------------------------------------------
class LiteralExpression(GrammarPhrase):
    PHRASE_NAME                             = "Literal Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(LiteralExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            self.PHRASE_NAME,
            (
                # <Boolean>
                PhraseItem(
                    name="Boolean",
                    item=(
                        "__True!",
                        "__False!",
                        "True!",
                        "False!",
                        "True",
                        "False",
                    ),
                ),

                # <Character>
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

                # <Integer>
                PhraseItem(
                    RegexToken(
                        "Integer",
                        re.compile(
                            textwrap.dedent(
                                r"""(?P<value>(?#
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

                # <Number>
                PhraseItem(
                    RegexToken(
                        "Number",
                        re.compile(
                            textwrap.dedent(
                                r"""(?P<value>(?#
                                Leading Digits              )\d*(?#
                                Decimal Point               )\.(?#
                                Trailing Digits             )\d+(?#
                                ))""",
                            ),
                        ),
                    ),
                ),

                # <String>
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
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        node = cast(AST.Node, ExtractOr(node))

        assert node.type is not None

        if node.type.name == "Boolean":
            value_node = cast(AST.Leaf, ExtractOr(node))

            value_info = ExtractToken(
                value_node,
                return_match_contents=True,
            )

            if "True" in value_info:
                value = True
            elif "False" in value_info:
                value = False
            else:
                assert False, value_info  # pragma: no cover

            if value_info.startswith("__"):
                parser_info_type = ParserInfoType.Configuration
            elif value_info.endswith("!"):
                parser_info_type = ParserInfoType.TypeCustomization
            else:
                parser_info_type = ParserInfoType.Unknown

            return BooleanExpressionParserInfo.Create(
                parser_info_type,
                CreateRegions(value_node),
                value,
            )

        elif node.type.name == "Character":
            value_node = cast(AST.Leaf, node)
            value_info = ExtractToken(value_node)

            # TODO: How do we want to store these values?

            return CharacterExpressionParserInfo.Create(
                CreateRegions(value_node),
                value_info,
            )

        elif node.type.name == "Integer":
            value_node = cast(AST.Leaf, node)
            value_info = int(ExtractToken(value_node))

            return IntegerExpressionParserInfo.Create(
                CreateRegions(value_node),
                value_info,
            )

        elif node.type.name == "None":
            return NoneExpressionParserInfo.Create(CreateRegions(node))

        elif node.type.name == "Number":
            value_node = cast(AST.Leaf, node)
            value_info = float(ExtractToken(value_node))

            return NumberExpressionParserInfo.Create(
                CreateRegions(value_node),
                value_info,
            )

        elif node.type.name == "String":
            value_node = cast(AST.Leaf, node)
            value_info = ExtractToken(value_node).replace('\\"', '"')

            return StringExpressionParserInfo.Create(
                CreateRegions(value_node),
                value_info,
            )

        assert False, node.type  # pragma: no cover
