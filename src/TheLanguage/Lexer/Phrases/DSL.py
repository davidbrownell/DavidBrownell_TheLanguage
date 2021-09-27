# ----------------------------------------------------------------------
# |
# |  DSL.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 10:45:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that creates a Domain Specific Language (DSL) for creating complicated phrases"""

import os
import re
import textwrap

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
    from ..Components.Phrase import DynamicPhrasesType, Phrase
    from ..Components.Token import RegexToken, Token


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
DefaultCommentToken                         = RegexToken(
    "<comment>",
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
PhraseItemItemType                          = Union[
    # Arity of 1
    "PhraseItem",
    Phrase,
    Token,                                  # Converts to a TokenPhrase
    str,                                    # Converts to a TokenPhrase (using a very simple RegexToken)
    DynamicPhrasesType,                     # Converts to a DynamicPhrase
    List["PhraseItemItemType"],             # Converts to a SequencePhrase
    Tuple["PhraseItemItemType", ...],       # Converts to an OrPhrase
    "OrPhraseItem",                         # Converts to an OrPhrase
    None,                                   # Converts to a RecursivePlaceholderPhrase

    "CustomArityPhraseItem",                # Arity of (obj.Min, obj.Max)
    "OptionalPhraseItem",                   # Arity of (0, 1)
    "ZeroOrMorePhraseItem",                 # Arity of (0, None)
    "OneOrMorePhraseItem",                  # Arity of (1, None)
]

# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PhraseItem(object):
    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    Item: PhraseItemItemType
    Name: Optional[str]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    # This method is here to provide an interface similar to CreatePhrase (in that arguments begin
    # with lowercase) while still creating an object that follows the upper-case name convention
    # for immutable data.
    @classmethod
    def Create(
        cls,
        item: PhraseItemItemType,
        name: Optional[str]=None,
    ) -> "PhraseItem":
        return PhraseItem(item, name)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class OrPhraseItem(object):
    Items: Optional[List[PhraseItemItemType]]           = field(default=None)

    # ----------------------------------------------------------------------
    def __or__(
        self,
        other: PhraseItemItemType,
    ) -> "OrPhraseItem":
        items = self.Items or []

        if isinstance(other, OrPhraseItem):
            assert other.Items
            items += other.Items
        else:
            items.append(other)

        return OrPhraseItem(items)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class CustomArityPhraseItem(object):
    Item: PhraseItemItemType
    Min: int
    Max: Optional[int]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Min >= 0
        assert self.Max is None or self.Max >= self.Min


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class OptionalPhraseItem(object):
    Item: PhraseItemItemType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ZeroOrMorePhraseItem(object):
    Item: PhraseItemItemType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class OneOrMorePhraseItem(object):
    Item: PhraseItemItemType


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def CreatePhrase(
    item: PhraseItemItemType,
    name: Optional[str]=None,
    comment_token: Optional[RegexToken]=None,
) -> Phrase:
    if comment_token is None:
        comment_token = DefaultCommentToken

    if name is not None:
        assert item is not None
        assert not isinstance(item, (PhraseItem, Phrase)), item

        item = PhraseItem.Create(
            item,
            name=name,
        )

    phrase = _PopulateItem(comment_token, item)

    phrase.PopulateRecursive(phrase)

    return phrase


# ----------------------------------------------------------------------
def ExtractToken(
    leaf: Leaf,
    use_match=False,
) -> Optional[str]:
    assert isinstance(leaf, Leaf), leaf

    if leaf.IsIgnored:
        return None

    if isinstance(leaf.Value, RegexToken.MatchResult):
        groups_dict = leaf.Value.Match.groupdict()

        if len(groups_dict) == 1:
            return next(iter(groups_dict.values()))

        if use_match:
            return leaf.Value.Match.string[leaf.Value.Match.start() : leaf.Value.Match.end()]

    return cast(Token, leaf.Type).Name


# ----------------------------------------------------------------------
def ExtractDynamic(
    node: Node,
) -> Union[Leaf, Node]:
    # Drill into the dynamic node
    if isinstance(node.Type, DynamicPhrase):
        assert len(node.Children) == 1
        node = cast(Node, node.Children[0])

        return ExtractOr(node)

    # Handle the left-recursive scenario
    if (
        node.Parent is not None
        and node == getattr(node.Parent, "Children", [None])[0]
        and isinstance(node.Type, SequencePhrase)
        and isinstance(node.Type.Phrases[0], DynamicPhrase)
    ):
        return node

    assert False, node


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
    node: Optional[Node],
) -> Union[
    # Results for "?"
    Optional[Union[Leaf, Node]],

    # Results for "*", "+"
    List[Union[Leaf, Node]],
]:
    if node is None:
        return []

    assert isinstance(node.Type, RepeatPhrase), node.Type

    if node.Type.MaxMatches == 1:
        assert node.Children or node.Type.MinMatches == 0, node.Type.MinMatches
        return node.Children[0] if node.Children else None

    return node.Children


# ----------------------------------------------------------------------
def ExtractOptional(
    node: Optional[Node],
) -> Optional[Union[Leaf, Node]]:
    if node is None:
        return None

    return cast(Optional[Union[Leaf, Node]], ExtractRepeat(node))


# ----------------------------------------------------------------------
def ExtractSequence(
    node: Node,
) -> List[Union[Leaf, Node, None]]:
    assert isinstance(node.Type, SequencePhrase), node.Type
    phrases = node.Type.Phrases

    results = []
    child_index = 0

    while len(results) != len(phrases) or child_index != len(node.Children):
        # Get the phrase
        phrase = None

        if len(results) != len(phrases):
            phrase = phrases[len(results)]

            if isinstance(phrase, TokenPhrase) and phrase.Token.IsControlToken:
                results.append(None)
                continue

        # Get the child node
        child_node = None

        if child_index != len(node.Children):
            child_node = node.Children[child_index]
            child_index += 1

            if isinstance(child_node, Leaf) and child_node.IsIgnored:
                continue

        else:
            # If here, we have exhausted all of the children. This can only happen when we are
            # looking at a RepeatPhrase that supported 0 matches.
            assert isinstance(phrase, RepeatPhrase), phrase
            assert phrase.MinMatches == 0, phrase.MinMatches

            results.append(None)
            continue

        assert phrase is not None
        assert child_node is not None

        if isinstance(phrase, RepeatPhrase) and child_node.Type != phrase:
            assert phrase.MinMatches == 0, phrase.MinMatches
            results.append(None)

            assert child_index != 0
            child_index -= 1

            continue

        results.append(child_node)

    assert len(results) == len(phrases), (len(results), len(phrases))
    return results


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
# ----------------------------------------------------------------------
def _PopulateItem(
    comment_token: RegexToken,
    item: PhraseItemItemType,
) -> Phrase:
    if isinstance(item, CustomArityPhraseItem):
        arity = (item.Min, item.Max)
        item = item.Item
    elif isinstance(item, OptionalPhraseItem):
        arity = (0, 1)
        item = item.Item
    elif isinstance(item, ZeroOrMorePhraseItem):
        arity = (0, None)
        item = item.Item
    elif isinstance(item, OneOrMorePhraseItem):
        arity = (1, None)
        item = item.Item
    else:
        arity = None

    # PhraseItem types that control arity cannot be nested
    assert arity is None or not isinstance(item, (CustomArityPhraseItem, OptionalPhraseItem, ZeroOrMorePhraseItem, OneOrMorePhraseItem)), item

    if not isinstance(item, PhraseItem):
        item = PhraseItem.Create(item)

    # Begin the conversion process
    if isinstance(item.Item, PhraseItem):
        phrase = _PopulateItem(comment_token, item.Item)
        name = item.Name

    elif isinstance(item.Item, Phrase):
        phrase = item.Item
        name = item.Name

    else:
        name = None

        if isinstance(item.Item, Token):
            phrase = TokenPhrase(
                item.Item,
                name=item.Name,
            )

        elif isinstance(item.Item, str):
            phrase = TokenPhrase(
                RegexToken(
                    item.Name or "'{}'".format(item.Item),
                    re.compile(r"{}{}".format(re.escape(item.Item), "\\b" if item.Item.isalnum() else "")),
                ),
            )

        elif isinstance(item.Item, DynamicPhrasesType):
            phrase = DynamicPhrase(
                item.Item,
                lambda unique_id, phrases_type, observer: observer.GetDynamicPhrases(unique_id, phrases_type),
                name=item.Name or str(item.Item),
            )

        elif isinstance(item.Item, list):
            sequence_phrases = [
                _PopulateItem(comment_token, phrase_item) for phrase_item in item.Item
            ]

            phrase = SequencePhrase(
                comment_token,
                sequence_phrases,
                name=item.Name,
            )

        elif isinstance(item.Item, tuple):
            or_phrases = [
                _PopulateItem(comment_token, phrase_item) for phrase_item in item.Item
            ]

            phrase = OrPhrase(
                or_phrases,
                name=item.Name,
            )

        elif isinstance(item.Item, OrPhraseItem):
            assert item.Item.Items

            or_phrases = [
                _PopulateItem(comment_token, phrase_item) for phrase_item in item.Item.Items
            ]

            phrase = OrPhrase(
                or_phrases,
                name=item.Name,
            )

        elif item.Item is None:
            phrase = RecursivePlaceholderPhrase()
            name = item.Name

        else:
            assert False, item.Item  # pragma: no cover

    if arity is not None:
        phrase = RepeatPhrase(
            phrase,
            arity[0],
            arity[1],
            name=name,
        )

    return phrase
