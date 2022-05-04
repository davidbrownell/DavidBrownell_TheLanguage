# ----------------------------------------------------------------------
# |
# |  TupleExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 14:12:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleExpression object"""

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

    from ..Common.Impl import TuplePhraseImpl

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractSequence,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.ParserInfos.Expressions.TupleExpressionParserInfo import (
        ExpressionParserInfo,
        TupleExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class TupleExpression(GrammarPhrase):
    PHRASE_NAME                             = "Tuple Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            self.PHRASE_NAME,
            [
                TuplePhraseImpl.Create(DynamicPhrasesType.Expressions),
            ],
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        # ----------------------------------------------------------------------
        def Callback():
            nodes = ExtractSequence(node)
            assert len(nodes) == 1

            tuple_node = cast(AST.Node, nodes[0])
            tuple_info = cast(List[ExpressionParserInfo], TuplePhraseImpl.Extract(tuple_node))

            return TupleExpressionParserInfo.Create(
                CreateRegions(node),
                tuple_info,
            )

        # ----------------------------------------------------------------------

        return Callback
