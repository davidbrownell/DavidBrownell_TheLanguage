# ----------------------------------------------------------------------
# |
# |  MatchExpressionBase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 09:09:10
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

from typing import Callable, cast, List, Optional, Type

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import Tokens as CommonTokens

    from ....GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from .....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractRepeat,
        ExtractSequence,
        ExtractOptional,
        ExtractOr,
        OneOrMorePhraseItem,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from .....Parser.Parser import CreateParserRegions, GetParserInfo
    from .....Parser.Expressions.ExpressionParserInfo import ExpressionParserInfo


# ----------------------------------------------------------------------
class MatchExpressionBase(GrammarPhrase):
    """\
    Base class for match expressions.

    '(' 'match' ('type' | 'value') ':'
        (
            'case' <type|expr> (',' <type|expr>)* ','? ':'
                <expression>
        )+
        (
            'default' ':'
                <expression>
        )?
    ')'

    Examples:
        result = (
            match value Add(1, 2):
                case 1, 2: "Too low"
                case 3:
                    "Correct!"
                default: "Way off"
        )

        result = (match type Add(1, 2):
            case Int: "Expected result type"
            case String: value
            default:
                "What type is it?!"
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
            assert False, match_type  # pragma: no cover

        case_items = PhraseItem.Create(
            name="Case Items",
            item=[
                # <token>
                match_type,

                # (',' <token>)*
                ZeroOrMorePhraseItem.Create(
                    name="Comma and Token",
                    item=[
                        ",",
                        match_type,
                    ],
                ),

                # ','?
                OptionalPhraseItem.Create(
                    name="Trailing Comma",
                    item=",",
                ),
            ],
        )

        case_expression_item = PhraseItem.Create(
            name="Case Expression",
            item=(
                # <newline> <indent> <expression> <newline> <dedent>
                PhraseItem.Create(
                    name="Multiple Lines",
                    item=[
                        CommonTokens.Newline,
                        CommonTokens.Indent,
                        DynamicPhrasesType.Expressions,
                        CommonTokens.Newline,
                        CommonTokens.Dedent,
                    ],
                ),

                # <expression> <newline>
                PhraseItem.Create(
                    name="Single Line",
                    item=[
                        DynamicPhrasesType.Expressions,
                        CommonTokens.Newline,
                    ],
                ),
            ),
        )

        match_item = PhraseItem.Create(
            name="Match",
            item=[
                # 'match' ('type'|'value') <expression> ':' <newline> <indent>
                "match",
                type_token,
                DynamicPhrasesType.Expressions,
                ":",
                CommonTokens.Newline,
                CommonTokens.Indent,

                # ('case' <<Case Items>> ':' <case_expression_item>)+
                OneOrMorePhraseItem.Create(
                    name="Case Phrase",
                    item=[
                        # 'case'
                        "case",

                        # <<Case Items>>
                        PhraseItem.Create(
                            item=(
                                # '(' <case_items> ')'
                                PhraseItem.Create(
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
                            ambiguities_resolved_by_order=True,
                        ),

                        # ':' <case_expression_item>
                        ":",
                        case_expression_item,
                    ],
                ),

                # ('default' ':' <case_expression_item>)?
                OptionalPhraseItem.Create(
                    name="Default Phrase",
                    item=[
                        "default",
                        ":",
                        case_expression_item,
                    ],
                ),

                # <dedent>
                CommonTokens.Dedent,
            ],
        )

        super(MatchExpressionBase, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=phrase_name,
                item=[
                    CommonTokens.PushPreserveWhitespaceControl,

                    PhraseItem.Create(
                        name="Style",
                        item=(
                            # '(' <match_item> ')'
                            PhraseItem.Create(
                                name="K&R-Like",
                                item=[
                                    "(",
                                    match_item,
                                    ")",
                                ],
                            ),

                            # '(' <newline> <indent> <match_item> <dedent> ')'
                            PhraseItem.Create(
                                name="Allman-Like",
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
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractParserInfoImpl(
        cls,
        match_parser_info_type: Type[ParserInfo],
        case_phrase_parser_info_type: Type[ParserInfo],
        node: AST.Node,
    ) -> Callable[[], ParserInfo]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # Drill into the specific match style
            match_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[1])))
            assert match_node.Type is not None

            if match_node.Type.Name == "K&R-Like":
                num_match_nodes = 3
                match_nodes_index = 1
            elif match_node.Type.Name == "Allman-Like":
                num_match_nodes = 6
                match_nodes_index = 3
            else:
                assert False, match_node.Type  # pragma: no cover

            match_nodes = ExtractSequence(match_node)
            assert len(match_nodes) == num_match_nodes

            match_node = cast(AST.Node, match_nodes[match_nodes_index])

            # Resume normal extraction
            nodes = ExtractSequence(match_node)
            assert len(nodes) == 9

            # <expression>
            expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[2])))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            # Cases
            cases_node = cast(AST.Node, nodes[6])
            cases_info: List[case_phrase_parser_info_type] = []

            for case_phrase_node in cast(List[AST.Node], ExtractRepeat(cases_node)):
                case_phrase_nodes = ExtractSequence(case_phrase_node)
                assert len(case_phrase_nodes) == 4

                # Case Items
                case_items_node = cast(AST.Node, ExtractOr(cast(AST.Node, case_phrase_nodes[1])))

                assert case_items_node.Type is not None
                if case_items_node.Type.Name == "Grouped":
                    case_items_node = cast(AST.Node, ExtractSequence(case_items_node)[2])

                case_items_nodes = ExtractSequence(case_items_node)
                assert len(case_items_nodes) == 3

                case_items_info: List[ParserInfo] = []

                for case_item_node in itertools.chain(
                    [case_items_nodes[0]],
                    [
                        ExtractSequence(delimited_node)[1]
                        for delimited_node in cast(
                            List[AST.Node],
                            ExtractRepeat(cast(AST.Node, case_items_nodes[1])),
                        )
                    ],
                ):
                    case_items_info.append(
                        cast(
                            ParserInfo,
                            GetParserInfo(ExtractDynamic(cast(AST.Node, case_item_node))),
                        ),
                    )

                assert case_items_info

                # <expression> (case phrase)
                case_phrase_expression_node = cast(AST.Node, case_phrase_nodes[3])
                case_phrase_expression_info = cls._ExtractCasePhraseExpression(case_phrase_expression_node)

                cases_info.append(
                    case_phrase_parser_info_type(
                        CreateParserRegions(case_phrase_node, case_items_node, case_phrase_expression_node),  # type: ignore
                        case_items_info,  # type: ignore
                        case_phrase_expression_info,
                    ),
                )

            assert cases_info

            # Default
            default_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[7])))

            if default_node is None:
                default_info = None
            else:
                default_node = cast(AST.Node, ExtractSequence(default_node)[2])
                default_info = cls._ExtractCasePhraseExpression(default_node)

            return match_parser_info_type(
                CreateParserRegions(node, expression_node, cases_node, default_node),  # type: ignore
                expression_info,  # type: ignore
                cases_info,
                default_info,
            )

        # ----------------------------------------------------------------------

        return Impl

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    def _ExtractCasePhraseExpression(
        node: AST.Node,
    ) -> ExpressionParserInfo:
        node = cast(AST.Node, ExtractOr(node))
        assert node.Type is not None

        if node.Type.Name == "Multiple Lines":
            num_nodes = 5
            node_index = 2
        elif node.Type.Name == "Single Line":
            num_nodes = 2
            node_index = 0
        else:
            assert False, node.Type  # pragma: no cover

        nodes = ExtractSequence(node)
        assert len(nodes) == num_nodes

        info_node = ExtractDynamic(cast(AST.Node, nodes[node_index]))
        return cast(ExpressionParserInfo, GetParserInfo(info_node))
