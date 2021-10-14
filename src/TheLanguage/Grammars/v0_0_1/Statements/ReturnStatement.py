# ----------------------------------------------------------------------
# |
# |  ReturnStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 10:05:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ReturnStatement object"""

import os

from typing import Callable, cast, Optional, Tuple, Union

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
        ExtractOptional,
        ExtractSequence,
        OptionalPhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.ReturnStatementParserInfo import (
        ExpressionParserInfo,
        ReturnStatementParserInfo,
    )


# ----------------------------------------------------------------------
class ReturnStatement(GrammarPhrase):
    """\
    Returns from a function.

    'return' <expr>?

    Examples:
        return
        return foo
    """

    PHRASE_NAME                             = "Return Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ReturnStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'return'
                    "return",

                    # <expr>?
                    OptionalPhraseItem.Create(DynamicPhrasesType.Expressions),

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
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # <expr>?
            expression_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
            if expression_node is None:
                expression_info = None
            else:
                expression_node = cast(AST.Node, ExtractDynamic(expression_node))
                expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            return ReturnStatementParserInfo(
                CreateParserRegions(node, expression_node),  # type: ignore
                expression_info,
            )

        # ----------------------------------------------------------------------

        return Impl
