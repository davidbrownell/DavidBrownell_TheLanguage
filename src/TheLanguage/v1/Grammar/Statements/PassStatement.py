# ----------------------------------------------------------------------
# |
# |  PassStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 12:40:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PassStatement object"""

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
        ExtractToken,
        RegexToken,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.ParserInfos.ParserInfo import ParserInfoType

    from ...Parser.ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo


# ----------------------------------------------------------------------
class PassStatement(GrammarPhrase):
    """\
    Noop statement.
    """

    PHRASE_NAME                             = "Pass Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PassStatement, self).__init__(
            DynamicPhrasesType.Statements,
            self.PHRASE_NAME,
            [
                CommonTokens.CreateRegexToken(
                    "Pass",
                    (
                        "__pass!",
                        "pass!",
                        "pass",
                    ),
                ),

                CommonTokens.Newline,
            ],
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        nodes = ExtractSequence(node)
        assert len(nodes) == 2

        value_node = cast(AST.Leaf, nodes[0])
        value_info = ExtractToken(
            value_node,
            return_match_contents=True,
        )

        if value_info.startswith("__"):
            parser_info_type = ParserInfoType.Configuration
        if value_info.endswith("!"):
            parser_info_type = ParserInfoType.TypeCustomization
        else:
            parser_info_type = ParserInfoType.Standard

        return PassStatementParserInfo.Create(
            parser_info_type,
            CreateRegions(node),
        )
