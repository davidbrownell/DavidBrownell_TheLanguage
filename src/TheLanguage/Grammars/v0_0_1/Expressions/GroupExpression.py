# ----------------------------------------------------------------------
# |
# |  GroupExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-02 12:41:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GroupExpression object"""

import os

from typing import Callable, cast, Union

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
        ExtractDynamic,
        ExtractSequence,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo
    from ....Parser.Expressions.GroupExpressionParserInfo import (
        ExpressionParserInfo,
        GroupExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class GroupExpression(GrammarPhrase):
    """\
    Groups an expression.

    '(' <expression> ')'

    Examples:
        (one + two) + three
        one or (two and three)
        (
            one
            + two
            + three
        )
    """

    PHRASE_NAME                             = "Group Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(GroupExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <expression>
                    DynamicPhrasesType.Expressions,

                    # ')'
                    CommonTokens.PopIgnoreWhitespaceControl,
                    ")",
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
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 5

            # <expression>
            expression_node = ExtractDynamic(cast(AST.Node, nodes[2]))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            return GroupExpressionParserInfo(
                CreateParserRegions(node, expression_node),  # type: ignore
                expression_info,
            )

        # ----------------------------------------------------------------------

        return Impl
