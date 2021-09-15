# ----------------------------------------------------------------------
# |
# |  FuncInvocationExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 19:38:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationExpression object"""

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
    from ..Common.Impl.FuncInvocationBase import FuncInvocationBase, Node
    from ...GrammarPhrase import GrammarPhrase

    from ....Lexer.Expressions.FuncInvocationExpressionLexerInfo import (
        FuncInvocationExpressionLexerData,
        FuncInvocationExpressionLexerInfo,
        FuncInvocationExpressionLexerRegions,
    )


# ----------------------------------------------------------------------
class FuncInvocationExpression(FuncInvocationBase):
    """Invokes a function"""

    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncInvocationExpression, self).__init__(
            "Func Invocation Expression",
            GrammarPhrase.Type.Expression,
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractLexerInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        return cls._ExtractLexerInfoImpl(
            FuncInvocationExpressionLexerData,
            FuncInvocationExpressionLexerRegions,
            FuncInvocationExpressionLexerInfo,
            node,
        )
