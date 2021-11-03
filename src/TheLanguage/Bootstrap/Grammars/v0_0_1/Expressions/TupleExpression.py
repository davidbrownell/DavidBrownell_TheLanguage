# ----------------------------------------------------------------------
# |
# |  TupleExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 08:26:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleExpression object"""

import os

from typing import Callable, cast, List, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.TupleBase import TupleBase

    from ...GrammarInfo import AST, DynamicPhrasesType, ParserInfo

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Expressions.TupleExpressionParserInfo import (
        ExpressionParserInfo,
        TupleExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class TupleExpression(TupleBase):
    """\
    A tuple of expressions.

    '(' (<expression> ',')+ ')'

    Examples:
        value1 = (a,)
        value2 = (a, b, c, d, e)
        Func((a, b), (d,))
    """

    PHRASE_NAME                             = "Tuple Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleExpression, self).__init__(DynamicPhrasesType.Expressions, self.PHRASE_NAME)

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
        # ----------------------------------------------------------------------
        def Impl():
            expressions: List[ExpressionParserInfo] = []

            for expression_node in cast(List[AST.Node], cls._EnumNodes(node)):
                expressions.append(cast(ExpressionParserInfo, GetParserInfo(expression_node)))

            return TupleExpressionParserInfo(
                CreateParserRegions(node),  # type: ignore
                expressions,
            )

        # ----------------------------------------------------------------------

        return Impl
