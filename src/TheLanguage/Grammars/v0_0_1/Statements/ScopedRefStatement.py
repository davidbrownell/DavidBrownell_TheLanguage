# ----------------------------------------------------------------------
# |
# |  ScopedRefStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-18 15:45:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ScopedRefStatement object"""

import itertools
import os

from typing import cast, List, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import StatementsPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common import TypeModifier

    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import SetLexerInfo
    from ....Lexer.Statements.ScopedRefStatementLexerInfo import (
        ScopedRefStatementLexerInfo,
        VariableNameLexerInfo,
    )

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class ScopedRefStatement(GrammarPhrase):
    """\
    Acquires the reference of a variable while the scope is active.

    'with' (<refs_expression>| '(' <refs_expression> ')') 'as' 'ref' ':'
        <statement>+

    Examples:
        with var1 as ref:
            pass

        with (var1, var2) as ref:
            pass

        with (
            var1,
            var2,
            var3,
        ) as ref:
            pass
    """

    PHRASE_NAME                             = "Scoped Ref Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        refs_expression = PhraseItem(
            name="Refs",
            item=[
                # <ref_expression>
                CommonTokens.GenericName,

                # (',' <ref_expression>)*
                PhraseItem(
                    name="Comma and Ref",
                    item=[
                        ",",
                        CommonTokens.GenericName,
                    ],
                    arity="*",
                ),

                # ','?
                PhraseItem(
                    name="Trailing Comma",
                    item=",",
                    arity="?",
                ),
            ],
        )

        super(ScopedRefStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'with'
                    "with",

                    # Refs
                    PhraseItem(
                        item=(
                            # '(' <refs_expression> ')'
                            PhraseItem(
                                name="Grouped",
                                item=[
                                    # '('
                                    "(",
                                    CommonTokens.PushIgnoreWhitespaceControl,

                                    # <refs_expression>
                                    refs_expression,

                                    # ')'
                                    CommonTokens.PopIgnoreWhitespaceControl,
                                    ")",
                                ],
                            ),

                            # <refs_expression>
                            refs_expression,
                        ),

                        # Use the order to disambiguate between group clauses and tuples.
                        ordered_by_priority=True,
                    ),

                    # 'as'
                    "as",

                    # 'ref'
                    TypeModifier.Enum.ref.name,

                    # ':' <statement>+
                    StatementsPhraseItem.Create(),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractLexerInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 5

            # Refs
            refs_node = cast(Node, ExtractOr(cast(Node, nodes[1])))

            assert refs_node.Type is not None
            if refs_node.Type.Name == "Grouped":
                refs_nodes = ExtractSequence(refs_node)
                assert len(refs_nodes) == 5

                refs_node = cast(Node, refs_nodes[2])

            refs_nodes = ExtractSequence(refs_node)
            assert len(refs_nodes) == 3

            variable_infos: List[VariableNameLexerInfo] = []

            for variable_node in itertools.chain(
                [refs_nodes[0]],
                [
                    ExtractSequence(delimited_node)[1]
                    for delimited_node in cast(List[Node], ExtractRepeat(cast(Node, refs_nodes[1])))
                ],
            ):
                variable_leaf = cast(Leaf, variable_node)
                variable_info = cast(str, ExtractToken(variable_leaf))

                variable_infos.append(
                    VariableNameLexerInfo(
                        CreateLexerRegions(variable_leaf, variable_leaf),  # type: ignore
                        variable_info,
                    ),
                )

            assert variable_infos

            # Statements
            statements_node = cast(Node, nodes[4])
            statements_info = StatementsPhraseItem.ExtractLexerInfo(statements_node)

            SetLexerInfo(
                node,
                ScopedRefStatementLexerInfo(
                    CreateLexerRegions(node, refs_node, statements_node),  # type: ignore
                    variable_infos,
                    statements_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
