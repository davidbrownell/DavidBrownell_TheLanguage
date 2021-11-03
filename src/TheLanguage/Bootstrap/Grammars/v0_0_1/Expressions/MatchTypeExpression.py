# ----------------------------------------------------------------------
# |
# |  MatchTypeExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 09:50:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MatchTypeExpression object"""

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
    from ..Common.Impl.MatchExpressionBase import MatchExpressionBase

    from ...GrammarInfo import AST, DynamicPhrasesType, ParserInfo

    from ....Parser.Expressions.MatchTypeExpressionParserInfo import (
        MatchTypeExpressionClauseParserInfo,
        MatchTypeExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class MatchTypeExpression(MatchExpressionBase):
    """\
    Typed version of a match expression.

    Examples:
        int_value = (
            match type Add(1, 2):
                case Int: __match_value
                case String: ConvertToInt(__match_value)
                default: raise UnexpectedType(__match_type)
        )
    """

    PHRASE_NAME                             = "Match Type Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(MatchTypeExpression, self).__init__(DynamicPhrasesType.Types, self.PHRASE_NAME)

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        return cls._ExtractParserInfoImpl(
            MatchTypeExpressionParserInfo,
            MatchTypeExpressionClauseParserInfo,
            node,
        )
