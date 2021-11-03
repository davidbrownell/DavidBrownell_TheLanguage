# ----------------------------------------------------------------------
# |
# |  YieldStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 09:29:20
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the YieldStatement object"""

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

    from ....Parser.Statements.YieldStatementParserInfo import (
        ExpressionParserInfo,
        YieldStatementParserInfo,
    )


# ----------------------------------------------------------------------
class YieldStatement(GrammarPhrase):
    """\
    Yields a value to the caller from an async function.

    'yield' ('from'? <expression>)?

    Examples:
        yield
        yield foo
        yield from Foo()
    """

    PHRASE_NAME                             = "Yield Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(YieldStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'yield'
                    "yield",

                    # ('from'? <expression>)?
                    OptionalPhraseItem.Create(
                        name="Suffix",
                        item=[
                            OptionalPhraseItem("from"),
                            DynamicPhrasesType.Expressions,
                        ],
                    ),

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

            # ('from'? <expression>)?
            suffix_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
            if suffix_node is None:
                is_recursive_node = None

                expression_node = None
                expression_info = None

            else:
                suffix_nodes = ExtractSequence(suffix_node)
                assert len(suffix_nodes) == 2

                # 'from'?
                is_recursive_node = cast(
                    Optional[AST.Node],
                    ExtractOptional(cast(Optional[AST.Node], suffix_nodes[0])),
                )

                # <expression>
                expression_node = ExtractDynamic(cast(AST.Node, suffix_nodes[1]))
                expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            return YieldStatementParserInfo(
                CreateParserRegions(node, expression_node, is_recursive_node),  # type: ignore
                expression_info,
                True if is_recursive_node is not None else None,
            )

        # ----------------------------------------------------------------------

        return Impl
