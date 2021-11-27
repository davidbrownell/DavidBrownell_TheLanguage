# ----------------------------------------------------------------------
# |
# |  SliceExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-11-26 16:53:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
import os

from typing import Callable, cast, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        OptionalPhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Expressions.SliceExpressionParserInfo import (
        ExpressionParserInfo,
        SliceExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class SliceExpression(GrammarPhrase):
    PHRASE_NAME                             = "Slice Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(SliceExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    DynamicPhrasesType.Expressions, # OptionalPhraseItem.Create(DynamicPhrasesType.Expressions),
                    "..",
                    DynamicPhrasesType.Expressions, # OptionalPhraseItem.Create(DynamicPhrasesType.Expressions),
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
            assert len(nodes) == 3

            # <expression>
            # TODO: Needs to be optional, but left-recursive detection needs some work
            start_node = cast(AST.Node, nodes[0]) # cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[0])))
            if start_node is None:
                start_info = None
            else:
                start_node = ExtractDynamic(start_node)
                start_info = cast(ExpressionParserInfo, GetParserInfo(start_node))

            # <expression>
            # TODO: Needs to be optional, but conflicts with scoped statements when not (as it eats the colon that should belong to the scoped statement)
            end_node = cast(AST.Node, nodes[2]) # cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
            if end_node is None:
                end_info = None
            else:
                end_node = ExtractDynamic(end_node)
                end_info = cast(ExpressionParserInfo, GetParserInfo(end_node))

            return SliceExpressionParserInfo(
                CreateParserRegions(node, start_node, end_node),  # type: ignore
                start_info,
                end_info,
            )

        # ----------------------------------------------------------------------

        return Impl
