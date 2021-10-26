# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 11:31:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType object"""

import itertools
import os

from typing import Callable, cast, List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ..Expressions.NoneLiteralExpression import NoneLiteralExpression

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrase,
        ExtractDynamic,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Types.VariantTypeParserInfo import (
        TypeParserInfo,
        VariantTypeParserInfo,
    )


# ----------------------------------------------------------------------
class VariantType(GrammarPhrase):
    """\
    A type that can be any one of a collection of types.

    '(' <type> '|' (<type> '|')* <type> ')'

    Examples:
        (Int | Float)
        (Int val | Bool | Char view)
    """

    PHRASE_NAME                             = "Variant Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        type_phrase_item = PhraseItem.Create(
            name="Type",
            item=(
                DynamicPhrasesType.Types,
                NoneLiteralExpression.CreatePhraseItem(),
            ),
        )

        super(VariantType, self).__init__(
            DynamicPhrasesType.Types,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <type> '|'
                    type_phrase_item,
                    "|",

                    ZeroOrMorePhraseItem.Create(
                        name="Type and Sep",
                        item=[
                            type_phrase_item,
                            "|",
                        ],
                    ),

                    # <type>
                    type_phrase_item,

                    # ')'
                    CommonTokens.PopIgnoreWhitespaceControl,
                    ")",
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 8

            type_infos: List[Optional[TypeParserInfo]] = []

            for child_node in itertools.chain(
                [nodes[2]],
                [
                    ExtractSequence(delimited_node)[0]
                    for delimited_node in cast(
                        List[AST.Node],
                        ExtractRepeat(cast(AST.Node, nodes[4])),
                    )
                ],
                [nodes[5]],
            ):
                type_node = cast(AST.Node, ExtractOr(cast(AST.Node, child_node)))

                assert type_node.Type is not None

                if isinstance(type_node.Type, DynamicPhrase):
                    type_node = ExtractDynamic(type_node)
                    type_info = cast(TypeParserInfo, GetParserInfo(type_node))
                elif type_node.Type.Name == NoneLiteralExpression.PHRASE_ITEM_NAME:
                    type_info = None
                else:
                    assert False, type_node.Type  # pragma: no cover

                type_infos.append(type_info)

            return VariantTypeParserInfo(
                CreateParserRegions(node),  # type: ignore
                type_infos,
            )

        # ----------------------------------------------------------------------

        return Impl
