# ----------------------------------------------------------------------
# |
# |  MatchExpressionBase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-30 15:09:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MatchExpressionBase object"""

import itertools
import os

from typing import cast, List, Optional, Type

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import Tokens as CommonTokens

    from ....GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from .....Lexer.LexerInfo import GetLexerInfo, LexerInfo, SetLexerInfo

    from .....Lexer.Expressions.ExpressionLexerInfo import ExpressionLexerInfo

    from .....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        Node,
        PhraseItem,
    )


# TODO: Implementation should add the magic values '__MatchType__' and '__match_value__' to the scope

# ----------------------------------------------------------------------
class MatchExpressionBase(GrammarPhrase):
    """\
    Base class for match expressions.

    'match' ('type'|'value') ':'
        (
            'case' <type|expr> (',' <type|expr>)* ','? ':'
                <expr>
        )+
        (
            'default' ':'
                <expr>
        )?

    Examples:
        result = (
            match value Add(1, 2):
                case 1, 2: "Too low"
                case 3:
                    "Correct!"
                default: "Way off"
        )

        result = (match type Add(1, 2):
            case Int: "Expected"
            case String: value
            default:
                "What type is it?"
        )
    """

    # Generally speaking, the difference between statements and expressions is that
    # expressions return a value, are smaller, and don't care about whitespace. Match expressions
    # are a bit of a hybrid between statements and expressions - the return a value, but are
    # large and do care about whitespace.
    #
    # This code takes special care to provide a syntax is flexible where possible but still
    # maintains the structure necessary to infer meaning.

    # ----------------------------------------------------------------------
    def __init__(
        self,
        match_type: DynamicPhrasesType,
        phrase_name: str,
    ):
        if match_type == DynamicPhrasesType.Types:
            type_token = "type"
        elif match_type == DynamicPhrasesType.Expressions:
            type_token = "value"
        else:
            assert False, match_type

        case_items = PhraseItem(
            name="Case Items",
            item=[
                # <token>
                match_type,

                # (',' <token>)*
                PhraseItem(
                    name="Comma and Content",
                    item=[
                        ",",
                        match_type,
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

        case_expression_item = PhraseItem(
            name="Expression",
            item=(
                # <newline> <indent> <expr> <newline> <dedent>
                PhraseItem(
                    name="Multiple Lines",
                    item=[
                        CommonTokens.Newline,
                        CommonTokens.Indent,
                        DynamicPhrasesType.Expressions,
                        CommonTokens.Newline,
                        CommonTokens.Dedent,
                    ],
                ),

                # <expr> <newline>
                PhraseItem(
                    name="Single Line",
                    item=[
                        DynamicPhrasesType.Expressions,
                        CommonTokens.Newline,
                    ],
                ),
            ),
        )

        match_item = PhraseItem(
            name="Match",
            item=[
                # ''match' ('type'|'value') <expr> ':'
                "match",
                type_token,
                DynamicPhrasesType.Expressions,
                ":",
                CommonTokens.Newline,
                CommonTokens.Indent,

                # ('case' <<Case Items>> ':' <case_expression_item>)+
                PhraseItem(
                    name="Case Phrase",
                    item=[
                        "case",

                        # <<Case Items>>
                        PhraseItem(
                            item=(
                                # '(' <case_items> ')'
                                PhraseItem(
                                    name="Grouped",
                                    item=[
                                        # '('
                                        "(",
                                        CommonTokens.PushIgnoreWhitespaceControl,

                                        # <case_items>
                                        case_items,

                                        # ')'
                                        CommonTokens.PopIgnoreWhitespaceControl,
                                        ")",
                                    ],
                                ),

                                # <case_items>
                                case_items,
                            ),

                            # Use the order to disambiguate between group clauses and tuples.
                            ordered_by_priority=True,
                        ),

                        ":",
                        case_expression_item,
                    ],
                    arity="+",
                ),

                # ('default' ':' <case_expression_item>)?
                PhraseItem(
                    name="Default",
                    item=[
                        "default",
                        ":",
                        case_expression_item,
                    ],
                    arity="?",
                ),

                CommonTokens.Dedent,
            ],
        )

        super(MatchExpressionBase, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=phrase_name,
                item=[
                    CommonTokens.PushPreserveWhitespaceControl,

                    PhraseItem(
                        name="Style",
                        item=(
                            # '(' <match_item>
                            # ')'
                            PhraseItem(
                                name="K&R-like",
                                item=[
                                    "(",
                                    match_item,
                                    ")",
                                ],
                            ),

                            # '('
                            #      <match_item>
                            # ')'
                            PhraseItem(
                                name="Allman-like",
                                item=[
                                    "(",
                                    CommonTokens.Newline,
                                    CommonTokens.Indent,
                                    match_item,
                                    CommonTokens.Dedent,
                                    ")",
                                ],
                            ),
                        ),
                    ),

                    CommonTokens.PopPreserveWhitespaceControl,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractLexerInfoImpl(
        cls,
        match_lexer_info_type: Type[LexerInfo],
        case_phrase_lexer_info_type: Type[LexerInfo],
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # Drill into the specific match style.
            match_node = cast(Node, ExtractOr(cast(Node, nodes[1])))
            assert match_node.Type is not None

            if match_node.Type.Name == "K&R-like":
                num_match_nodes = 3
                match_nodes_index = 1
            elif match_node.Type.Name == "Allman-like":
                num_match_nodes = 6
                match_nodes_index = 3
            else:
                assert False, match_node.Type.Name

            match_nodes = ExtractSequence(match_node)
            assert len(match_nodes) == num_match_nodes

            match_node = cast(Node, match_nodes[match_nodes_index])

            # Resume normal extraction
            nodes = ExtractSequence(match_node)
            assert len(nodes) == 9

            # <expr>
            expr_node = cast(Node, ExtractDynamic(cast(Node, nodes[2])))
            expr_info = cast(ExpressionLexerInfo, GetLexerInfo(expr_node))

            # Cases
            cases_node = cast(Node, nodes[6])
            cases_info: List[case_phrase_lexer_info_type] = []

            for case_phrase_node in cast(List[Node], ExtractRepeat(cases_node)):
                case_phrase_nodes = ExtractSequence(case_phrase_node)
                assert len(case_phrase_nodes) == 4

                # Case Items
                case_items_node = cast(Node, ExtractOr(cast(Node, case_phrase_nodes[1])))

                assert case_items_node.Type is not None
                if case_items_node.Type.Name == "Grouped":
                    case_items_node = cast(Node, ExtractSequence(case_items_node)[2])

                case_items_nodes = ExtractSequence(case_items_node)
                assert len(case_items_nodes) == 3

                case_items_info = []

                for case_item_node in itertools.chain(
                    [case_items_nodes[0]],
                    [
                        ExtractSequence(this_node)[1]
                        for this_node in cast(
                            List[Node],
                            ExtractRepeat(cast(Node, case_items_nodes[1])),
                        )
                    ],
                ):
                    case_items_info.append(GetLexerInfo(ExtractDynamic(cast(Node, case_item_node))))

                assert case_items_info

                # <expr>
                case_phrase_expr_node = cast(Node, case_phrase_nodes[3])
                case_phrase_expr_info = cls._ExtractCaseExpression(case_phrase_expr_node)

                cases_info.append(
                    case_phrase_lexer_info_type(
                        CreateLexerRegions(case_phrase_node, case_items_node, case_phrase_expr_node),  # type: ignore
                        case_items_info,  # type: ignore
                        case_phrase_expr_info,
                    ),
                )

            assert cases_info

            # Default
            default_node = cast(Node, ExtractOptional(cast(Node, nodes[7])))

            if default_node is not None:
                default_node = cast(Node, ExtractSequence(default_node)[2])
                default_info = cls._ExtractCaseExpression(default_node)

            else:
                default_info = None

            SetLexerInfo(
                node,
                match_lexer_info_type(
                    CreateLexerRegions(node, expr_node, cases_node, default_node),  # type: ignore
                    expr_info,  # type: ignore
                    cases_info,
                    default_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)

    # ----------------------------------------------------------------------
    @staticmethod
    def _ExtractCaseExpression(
        node: Node,
    ) -> ExpressionLexerInfo:
        node = cast(Node, ExtractOr(node))
        assert node.Type is not None

        if node.Type.Name == "Multiple Lines":
            num_nodes = 5
            node_index = 2

        elif node.Type.Name == "Single Line":
            num_nodes = 2
            node_index = 0

        else:
            assert False, node.Type

        nodes = ExtractSequence(node)
        assert len(nodes) == num_nodes

        data_node = ExtractDynamic(cast(Node, nodes[node_index]))
        return cast(ExpressionLexerInfo, GetLexerInfo(data_node))
