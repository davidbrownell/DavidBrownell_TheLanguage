# ----------------------------------------------------------------------
# |
# |  FuncOrTypeExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-22 08:05:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncOrTypeExpression object"""

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
        DynamicPhrasesType,
        ExtractSequence,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import (
        FuncOrTypeExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class FuncOrTypeExpression(GrammarPhrase):
    PHRASE_NAME                             = "Func or Type Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncOrTypeExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            self.PHRASE_NAME,
            [
                # Note that needs to be a sequence so that we can properly extract the value

                # Note that the definition of a type is a subset of the definition of a function,
                # so using function here.

                # <name>
                CommonTokens.FuncName,
            ],
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        nodes = ExtractSequence(node)
        assert len(nodes) == 1

        # <name>
        name_leaf = cast(AST.Leaf, nodes[0])
        name_info = CommonTokens.FuncName.Extract(name_leaf)  # type: ignore

        is_compile_time_region = CommonTokens.FuncName.GetIsCompileTimeRegion(name_leaf)  # type: ignore

        return FuncOrTypeExpressionParserInfo.Create(
            CreateRegions(node, is_compile_time_region, name_leaf),
            bool(is_compile_time_region),
            name_info,
        )
