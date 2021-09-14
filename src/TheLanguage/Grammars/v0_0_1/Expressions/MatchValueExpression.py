# ----------------------------------------------------------------------
# |
# |  MatchValueExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-30 15:47:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MatchValueExpression object"""

import os

from typing import Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.MatchExpressionBase import MatchExpressionBase

    from ...GrammarPhrase import GrammarPhrase

    from ....Lexer.Expressions.MatchValueExpressionLexerInfo import (
        MatchValueCasePhraseLexerData,
        MatchValueCasePhraseLexerInfo,
        MatchValueCasePhraseLexerRegions,
        MatchValueExpressionLexerData,
        MatchValueExpressionLexerInfo,
        MatchValueExpressionLexerRegions,
    )

    from ....Parser.Phrases.DSL import DynamicPhrasesType, Node


# ----------------------------------------------------------------------
class MatchValueExpression(MatchExpressionBase):
    """\
    Typed version of a match expression.

    Examples:
        match value Add(1, 2):
            case 1, 2: "Too low"
            case 3: "Correct"
            default: "Way off!"
    """

    PHRASE_NAME                             = "Match Value Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(MatchValueExpression, self).__init__(DynamicPhrasesType.Expressions, self.PHRASE_NAME)

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractLexerInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        return cls._ExtractLexerInfoImpl(
            MatchValueExpressionLexerData,
            MatchValueExpressionLexerRegions,
            MatchValueExpressionLexerInfo,
            MatchValueCasePhraseLexerData,
            MatchValueCasePhraseLexerRegions,
            MatchValueCasePhraseLexerInfo,
            node,
        )
