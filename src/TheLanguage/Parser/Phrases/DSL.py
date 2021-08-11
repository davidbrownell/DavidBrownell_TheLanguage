# ----------------------------------------------------------------------
# |
# |  DSL.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-09 13:35:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that provides a simple Domain Specific Language (DLS) for creating phrase hierarchies"""

import os
import re
import textwrap

from enum import auto, Enum
from typing import cast, List, Optional, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .DynamicPhrase import DynamicPhrase
    from .OrPhrase import OrPhrase
    from .RecursivePlaceholderPhrase import RecursivePlaceholderPhrase
    from .RepeatPhrase import RepeatPhrase
    from .SequencePhrase import SequencePhrase
    from .TokenPhrase import TokenPhrase

    from ..Components.AST import Leaf, Node
    from ..Components.Phrase import Phrase
    from ..Components.Token import RegexToken, Token


# ----------------------------------------------------------------------
CommentToken                                = RegexToken(
    "Comment",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Prefix                      )\#(?#
                Content                     )[^\n]*(?#
            ))""",
        ),
    ),
    is_always_ignored=True,
)


# ----------------------------------------------------------------------
class DynamicPhrasesType(Enum):
    Expressions                             = auto()    # Phrase that returns a value
    Names                                   = auto()    # Phrase that can be used as a name
    Statements                              = auto()    # Phrase that doesn't return a value
    Types                                   = auto()    # Phrase that can be used as a type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PhraseItem(object):
    # ----------------------------------------------------------------------
    # |  Public Types
    ItemType                                = Union[
        "PhraseItem",
        Phrase,
        Token,                              # Converts to a TokenPhrase
        str,                                # Converts to a TokenPhrase (using a very simple RegexToken)
        DynamicPhrasesType,                 # Converts to a DynamicPhrase
        List["ItemType"],                   # Converts to a SequencePhrase
        Tuple["ItemType", ...],             # Converts to an OrPhrase
        None,                               # Converts to a RecursivePlaceholderPhrase
    ]

    # ----------------------------------------------------------------------
    # |  Public Data
    item: ItemType
    name: Optional[str]                     = field(default=None)
    arity: Union[
        str,                                # Valid values are "?", "*", "+"
        Tuple[int, Optional[int]],
    ]                                       = field(default_factory=lambda: (1, 1))

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __post_init__(self):
        if isinstance(self.arity, str):
            if self.arity == "?":
                value = (0, 1)
            elif self.arity == "*":
                value = (0, None)
            elif self.arity == "+":
                value = (1, None)
            else:
                assert False, self.arity

            object.__setattr__(self, "arity", value)


# ----------------------------------------------------------------------
def CreatePhrase(
    item: PhraseItem.ItemType,
    name: str=None,
    comment_token: RegexToken=None,

    # Most of the time, this flag does not need to be set. However, setting it to True will preent
    # infinite recursion errors for the first phrase in a sequence if that phrase is a DynamicPhrase
    # that includes the parent.
    #
    # For example, the following phrase will suffer from this problem (as the first phrase in the
    # sequence is requesting a collection of dynamic phrases of a category that includes the phrase
    # itself) unless the flag is set:
    #
    #   Name:   AsPhrase
    #   Type:   DyanamicPhrasesType.Expressions
    #   DSL:    [
    #               DynamicPhrasesType.Expressions      # Note that this phrase is requesting a collection of phrases that will include itself
    #               'as'
    #               DynamicPhrasesType.Types,
    #           ]
    #
    suffers_from_infinite_recursion=False,
) -> Phrase:

    comment_token = comment_token or CommentToken

    if suffers_from_infinite_recursion:
        # If this flag is set, we should be looking at a sequence where the first time is a dynamic expression
        if isinstance(item, list):
            first_item = item[0]
        elif isinstance(item, PhraseItem):
            assert isinstance(item.item, list)
            first_item = item.item[0]
        elif isinstance(item, SequencePhrase):
            first_item = item.Phrases[0]
        else:
            assert False, item  # pragma: no cover

        assert isinstance(first_item, (DynamicPhrasesType, DynamicPhrase)), first_item

        suffers_from_infinite_recursion_ctr = 1
    else:
        suffers_from_infinite_recursion_ctr = None

    if name is not None:
        assert item is not None
        assert not isinstance(item, (PhraseItem, Phrase)), item

        phrase = _PopulateItem(
            comment_token,
            PhraseItem(
                item,
                name=name,
            ),
            suffers_from_infinite_recursion_ctr,
        )
    else:
        phrase = _PopulateItem(
            comment_token,
            item,
            suffers_from_infinite_recursion_ctr,
        )

    phrase.PopulateRecursive()

    return phrase


# ----------------------------------------------------------------------
def ExtractToken(
    leaf: Leaf,
) -> Optional[str]:
    assert isinstance(leaf, Leaf), leaf

    if leaf.IsIgnored:
        return None

    if isinstance(leaf.Value, RegexToken.MatchResult):
        groups_dict = leaf.Value.Match.groupdict()

        if len(groups_dict) == 1:
            return next(iter(groups_dict.values()))

    return cast(Token, leaf.Type).Name


# ----------------------------------------------------------------------
def ExtractDynamic(
    node: Node,
) -> Union[Leaf, Node]:
    # Drill into the dynamic node
    assert isinstance(node.Type, DynamicPhrase), node.Type
    assert len(node.Children) == 1
    node = cast(Node, node.Children[0])

    return ExtractOr(node)


# ----------------------------------------------------------------------
def ExtractOr(
    node: Node,
) -> Union[Leaf, Node]:
    # Drill into the or node
    assert isinstance(node.Type, OrPhrase), node.Type
    assert len(node.Children) == 1
    return node.Children[0]


# ----------------------------------------------------------------------
def ExtractRepeat(
    node: Node,
) -> Union[
    # Results for "?"
    Optional[Union[Leaf, Node]],

    # Results for "*", "+"
    List[Union[Leaf, Node]],
]:
    assert isinstance(node.Type, RepeatPhrase), node.Type

    if node.Type.MaxMatches == 1:
        assert node.Children or node.Type.MinMatches == 1, node.Type.MinMatches
        return node.Children[0] if node.Children else None

    return node.Children


# ----------------------------------------------------------------------
def ExtractSequence(
    node: Node,
) -> List[
    Union[
        Tuple[str, Leaf],
        Node,
        None,
    ],
]:
    assert isinstance(node.Type, SequencePhrase), node.Type

    phrases = node.Type.Phrases

    results = []
    child_index = 0

    while child_index != len(node.Children) or len(results) != len(phrases):
        phrase = None

        if len(results) != len(phrases):
            phrase = phrases[len(results)]

            if isinstance(phrase, TokenPhrase) and phrase.Token.IsControlToken:
                results.append(None)
                continue

        child = None

        if child_index != len(node.Children):
            child = node.Children[child_index]
            child_index += 1

            if isinstance(child, Leaf) and child.IsIgnored:
                continue

        else:
            assert isinstance(phrase, RepeatPhrase), phrase
            assert phrase.MinMatches == 0, phrase.MinMatches
            results.append(None if phrase.MaxMatches == 1 else [])

            continue

        assert phrase
        assert child

        if isinstance(phrase, RepeatPhrase) and child.Type != phrase:
            assert child_index != 0
            child_index -= 1

            assert phrase.MinMatches == 0, phrase.MinMatches
            results.append(None if phrase.MaxMatches == 1 else [])

            continue

        if isinstance(child, Leaf):
            results.append((ExtractToken(child), child))
        else:
            results.append(child)

    assert len(results) == len(phrases), (len(results), len(phrases))
    return results


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _PopulateItem(
    comment_token: RegexToken,
    item: PhraseItem.ItemType,
    suffers_from_infinite_recursion_ctr: Optional[int],
) -> Phrase:

    if not isinstance(item, PhraseItem):
        item = PhraseItem(item)

    name = None

    if isinstance(item.item, PhraseItem):
        phrase = _PopulateItem(comment_token, item.item, suffers_from_infinite_recursion_ctr)
        name = item.name

    elif isinstance(item.item, Phrase):
        phrase = item.item
        name = item.name

    elif isinstance(item.item, Token):
        phrase = TokenPhrase(
            item.item,
            name=item.name,
        )

    elif isinstance(item.item, str):
        phrase = TokenPhrase(
            RegexToken(
                item.name or "'{}'".format(item.item),
                re.compile(r"{}{}".format(re.escape(item.item), "\\b" if item.item.isalnum() else "")),
            ),
        )

    elif isinstance(item.item, DynamicPhrasesType):
        dynamic_phrases_value = item.item

        if suffers_from_infinite_recursion_ctr == 0:
            # ----------------------------------------------------------------------
            def GetDyanmicPhrasesWithFilter(
                unique_id: List[str],
                observer,
            ):
                if unique_id[-1] in unique_id[:-1]:
                    return []

                return observer.GetDynamicPhrases(unique_id, dynamic_phrases_value)

            # ----------------------------------------------------------------------

            get_dynamic_phrases_func = GetDyanmicPhrasesWithFilter

        else:
            # ----------------------------------------------------------------------
            def GetDynamicPhrases(
                unique_id: List[str],
                observer,
            ):
                return observer.GetDynamicPhrases(unique_id, dynamic_phrases_value)

            # ----------------------------------------------------------------------

            get_dynamic_phrases_func = GetDynamicPhrases

        phrase = DynamicPhrase(
            get_dynamic_phrases_func,
            name=item.name or str(item.item),
        )

    elif isinstance(item.item, list):
        phrase = SequencePhrase(
            comment_token,
            [
                _PopulateItem(
                    comment_token,
                    i,
                    None if suffers_from_infinite_recursion_ctr is None else suffers_from_infinite_recursion_ctr - 1,
                )
                for i in item.item
            ],
            name=item.name,
        )

    elif isinstance(item.item, tuple):
        phrase = OrPhrase(
            [
                _PopulateItem(
                    comment_token,
                    i,
                    None if suffers_from_infinite_recursion_ctr is None else suffers_from_infinite_recursion_ctr - 1,
                )
                for i in item.item
            ],
            name=item.name,
        )

    elif item.item is None:
        phrase = RecursivePlaceholderPhrase()
        name = item.name

    else:
        assert False, item.item  # pragma: no cover

    assert isinstance(item.arity, tuple), item.arity

    if item.arity[0] == 1 and item.arity[1] == 1:
        return phrase

    return RepeatPhrase(
        phrase,
        item.arity[0],
        item.arity[1],
        name=name,
    )