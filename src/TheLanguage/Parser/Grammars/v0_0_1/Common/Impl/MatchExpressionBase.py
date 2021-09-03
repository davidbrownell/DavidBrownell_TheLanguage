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

import os

from typing import cast

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import Tokens as CommonTokens
    from ....GrammarPhrase import GrammarPhrase

    from .....Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
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
                    name="Case",
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
