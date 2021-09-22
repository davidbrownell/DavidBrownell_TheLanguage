# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-14 16:16:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationStatement object"""

import os

from typing import cast, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ..Expressions.FuncInvocationExpression import FuncInvocationExpression

    from ...GrammarPhrase import GrammarPhrase

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        Node,
    )

    from ....Parser.ParserInfo import GetParserInfo, SetParserInfo
    from ....Parser.Statements.FuncInvocationStatementParserInfo import (
        FuncInvocationStatementParserInfo,
    )


# ----------------------------------------------------------------------
class FuncInvocationStatement(GrammarPhrase):
    """Invokes a function"""

    PHRASE_NAME                             = "Func Invocation Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncInvocationStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    FuncInvocationExpression().Phrase,
                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractParserInfoResult]:
        # ----------------------------------------------------------------------
        def CreateParserInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 2

            func_node = cast(Node, nodes[0])

            SetParserInfo(node, GetParserInfo(func_node))
            SetParserInfo(func_node, None)

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)
