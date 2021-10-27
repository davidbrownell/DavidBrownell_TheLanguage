# ----------------------------------------------------------------------
# |
# |  ScopedRefStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 12:56:58
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

from typing import Callable, cast, List, Optional, Tuple, Union

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
    from ..Common.TypeModifier import TypeModifier

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.ScopedRefStatementParserInfo import (
        ScopedRefStatementParserInfo,
        StatementParserInfo,
        VariableNameParserInfo,
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
        ref_phrase_item = CommonTokens.GenericLowerName

        refs_expression = PhraseItem.Create(
            name="Refs",
            item=[
                # <generic_name>
                ref_phrase_item,

                # (',' <generic_name>)*
                ZeroOrMorePhraseItem.Create(
                    name="Comma and Ref",
                    item=[
                        ",",
                        ref_phrase_item,
                    ],
                ),

                # ','?
                OptionalPhraseItem.Create(
                    name="Trailing Comma",
                    item=",",
                ),
            ],
        )

        super(ScopedRefStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'with'
                    "with",

                    # Refs
                    PhraseItem.Create(
                        item=(
                            # '(' <refs_expression> ')'
                            PhraseItem.Create(
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
                        ambiguities_resolved_by_order=True,
                    ),

                    # 'as'
                    "as",

                    # 'ref'
                    TypeModifier.ref.name,

                    # ':' <statement>+
                    StatementsPhraseItem.Create(),
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
            assert len(nodes) == 5

            # refs
            refs_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[1])))
            assert refs_node.Type is not None

            if refs_node.Type.Name == "Grouped":
                refs_nodes = ExtractSequence(refs_node)
                assert len(refs_nodes) == 5

                refs_node = cast(AST.Node, refs_nodes[2])

            refs_nodes = ExtractSequence(refs_node)
            assert len(refs_nodes) == 3

            ref_infos: List[VariableNameParserInfo] = []

            for ref_node in itertools.chain(
                [refs_nodes[0]],
                [
                    ExtractSequence(delimited_node)[1]
                    for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, refs_nodes[1])))
                ],
            ):
                variable_leaf = cast(AST.Leaf, ref_node)
                variable_info = cast(str, ExtractToken(variable_leaf))

                if not CommonTokens.VariableNameRegex.match(variable_info):
                    raise CommonTokens.InvalidTokenError.FromNode(variable_leaf, variable_info, "variable")

                ref_infos.append(
                    VariableNameParserInfo(
                        CreateParserRegions(ref_node, variable_leaf),  # type: ignore
                        variable_info,
                    ),
                )

            assert ref_infos

            # <statement>+
            statements_node = cast(AST.Node, nodes[4])
            statements_info = StatementsPhraseItem.ExtractParserInfo(statements_node)

            return ScopedRefStatementParserInfo(
                CreateParserRegions(node, refs_node, statements_node),  # type: ignore
                ref_infos,
                statements_info,
            )

        # ----------------------------------------------------------------------

        return Impl
