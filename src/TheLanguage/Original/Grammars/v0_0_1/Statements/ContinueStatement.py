# ----------------------------------------------------------------------
# |
# |  ContinueStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 12:40:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ContinueStatement object"""

import os

from typing import Callable, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
    )

    from ....Parser.Parser import CreateParserRegions

    from ....Parser.Statements.ContinueStatementParserInfo import ContinueStatementParserInfo


# ----------------------------------------------------------------------
class ContinueStatement(GrammarPhrase):
    """
    Continues within a loop.

    'continue'

    Example:
        while foo:
            continue
    """

    PHRASE_NAME                             = "Continue Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ContinueStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "continue",
                    CommonTokens.Newline,
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
        nodes = ExtractSequence(node)
        assert len(nodes) == 2

        return ContinueStatementParserInfo(
            CreateParserRegions(node),  # type: ignore
        )
