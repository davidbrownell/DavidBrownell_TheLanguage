# ----------------------------------------------------------------------
# |
# |  VariableExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 15:02:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableExpression object"""

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

    from ...Parser.ParserInfos.Expressions.VariableExpressionParserInfo import (
        ParserInfoType,
        VariableExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class VariableExpression(GrammarPhrase):
    PHRASE_NAME                             = "Variable Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            self.PHRASE_NAME,
            [
                # Note that needs to be a sequence so that we can properly extract the value

                # <name>
                CommonTokens.VariableName,
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
        name_info = CommonTokens.VariableName.Extract(name_leaf)  # type: ignore

        if CommonTokens.VariableName.IsCompileTime(name_info):  # type: ignore  # pylint: disable=not-callable
            if CommonTokens.variable_name_configuration_compile_time_regex.match(name_info):
                parser_info_type = ParserInfoType.Configuration
            else:
                parser_info_type = ParserInfoType.TypeCustomization
        else:
            parser_info_type = ParserInfoType.Standard

        return VariableExpressionParserInfo.Create(
            parser_info_type,
            CreateRegions(node, name_leaf),
            name_info,
        )
