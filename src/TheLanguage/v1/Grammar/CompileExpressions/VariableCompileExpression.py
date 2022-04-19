# ----------------------------------------------------------------------
# |
# |  VariableCompileExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-18 22:25:31
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableCompileExpression object"""

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

    from ...Parser.Parser import CreateRegions

    from ...Parser.ParserInfos.CompileExpressions.CompileExpressionParserInfo import (
        CompileExpressionParserInfo,
    )

# ----------------------------------------------------------------------
class VariableCompileExpression(GrammarPhrase):
    PHRASE_NAME                             = "Variable CompileExpression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableCompileExpression, self).__init__(
            DynamicPhrasesType.CompileExpressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # Note that needs to be a sequence so that we can properly extract the value

                    # <parameter_name>
                    CommonTokens.CompileParameterName,
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

        # <parameter_name>
        name_leaf = cast(AST.Leaf, nodes[0])
        name_info = ExtractToken(name_leaf)

        # TODO: This should be using a variable-specific ParserInfo object
        return CompileExpressionParserInfo.Create(
            CreateRegions(node),
        )
