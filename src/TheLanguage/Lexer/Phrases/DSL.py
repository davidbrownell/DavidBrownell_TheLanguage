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
    Item: PhraseItemItemType
    Name: Optional[str]

    # List of phrase or phrase names that should never be matched by this phrase item
    Excludes: Optional[List[Union[str, Phrase]]]        = field(default=None)

    # When creating an OrPhrase, any ambiguities are resolved using the order in which they appear
    AmbiguitiesResolvedByOrder: Optional[bool]          = field(default=None)

    # ----------------------------------------------------------------------
    # This method is here to provide an interface similar to CreatePhrase (in that arguments begin
    # with lowercase) while still creating an object that follows the upper-case name convention
    # for immutable data.
    @staticmethod
    def Create(
        item: PhraseItemItemType,
        name: Optional[str]=None,
        excludes: Optional[List[Union[str, Phrase]]]=None,
        ambiguities_resolved_by_order: Optional[bool]=None,
    ) -> "PhraseItem":
        return PhraseItem(item, name, excludes, ambiguities_resolved_by_order)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class OrPhraseItem(object):
    Items: Optional[List[PhraseItemItemType]]           = field(default=None)
    Name: Optional[str]                                 = field(default=None)

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
    # This method is here to provide an interface similar to CreatePhrase (in that arguments begin
    # with lowercase) while still creating an object that follows the upper-case name convention
    # for immutable data.
    @staticmethod
    def Create(
        items: Optional[List[PhraseItemItemType]]=None,
        name: Optional[str]=None,
    ) -> "OrPhraseItem":
        return OrPhraseItem(items, name)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class CustomArityPhraseItem(object):
    Item: PhraseItemItemType
    Min: int
    Max: Optional[int]
    Name: Optional[str]                     = field(default=None)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Min >= 0
        assert self.Max is None or self.Max >= self.Min

    # ----------------------------------------------------------------------
    # This method is here to provide an interface similar to CreatePhrase (in that arguments begin
    # with lowercase) while still creating an object that follows the upper-case name convention
    # for immutable data.
    @staticmethod
    def Create(
        item: PhraseItemItemType,
        min: int,
        max: Optional[int],
        name: Optional[str]=None,
    ) -> "CustomArityPhraseItem":
        return CustomArityPhraseItem(item, min, max, name)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class OptionalPhraseItem(object):
    Item: PhraseItemItemType
    Name: Optional[str]                     = field(default=None)

    # ----------------------------------------------------------------------
    # This method is here to provide an interface similar to CreatePhrase (in that arguments begin
    # with lowercase) while still creating an object that follows the upper-case name convention
    # for immutable data.
    @staticmethod
    def Create(
        item: PhraseItemItemType,
        name: Optional[str]=None,
    ) -> "OptionalPhraseItem":
        return OptionalPhraseItem(item, name)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ZeroOrMorePhraseItem(object):
    Item: PhraseItemItemType
    Name: Optional[str]                     = field(default=None)

    # ----------------------------------------------------------------------
    # This method is here to provide an interface similar to CreatePhrase (in that arguments begin
    # with lowercase) while still creating an object that follows the upper-case name convention
    # for immutable data.
    @staticmethod
    def Create(
        item: PhraseItemItemType,
        name: Optional[str]=None,
    ) -> "ZeroOrMorePhraseItem":
        return ZeroOrMorePhraseItem(item, name)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class OneOrMorePhraseItem(object):
    Item: PhraseItemItemType
    Name: Optional[str]                     = field(default=None)

    # ----------------------------------------------------------------------
    # This method is here to provide an interface similar to CreatePhrase (in that arguments begin
    # with lowercase) while still creating an object that follows the upper-case name convention
    # for immutable data.
    @staticmethod
    def Create(
        item: PhraseItemItemType,
        name: Optional[str]=None,
    ) -> "OneOrMorePhraseItem":
        return OneOrMorePhraseItem(item, name)


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

    phrase.PopulateRecursive(None, phrase)

    return phrase


# ----------------------------------------------------------------------
def ExtractToken(
    leaf: Leaf,
    *,
    use_match=False,
    group_dict_name: Optional[str]=None,
) -> Optional[str]:
    assert isinstance(leaf, Leaf), leaf

    if leaf.IsIgnored:
        return None

    if isinstance(leaf.Value, RegexToken.MatchResult):
        if group_dict_name is not None:
            return leaf.Value.Match.group(group_dict_name)

        groups_dict = leaf.Value.Match.groupdict()

        if len(groups_dict) == 1:
            return next(iter(groups_dict.values()))

        if use_match:
            return leaf.Value.Match.string[leaf.Value.Match.start() : leaf.Value.Match.end()]

    return cast(Token, leaf.Type).Name


# ----------------------------------------------------------------------
def ExtractTokenSpan(
    leaf: Leaf,
    match_group_name: str,
) -> Optional[Tuple[Phrase.NormalizedIterator, Phrase.NormalizedIterator]]:
    """\
    Returns the iterators associated with the start and end of a group within a match (or None if the
    group didn't match).
    """

    assert isinstance(leaf.Value, RegexToken.MatchResult)

    start = leaf.Value.Match.start(match_group_name)
    end = leaf.Value.Match.end(match_group_name)

    if start == end:
        return None

    assert start >= leaf.IterBegin.Offset
    assert end >= leaf.IterBegin.Offset
    assert start < end, (start, end)

    start -= leaf.IterBegin.Offset
    end -= leaf.IterBegin.Offset

    begin_iter = leaf.IterBegin.Clone()
    begin_iter.Advance(start)

    end_iter = leaf.IterBegin.Clone()
    end_iter.Advance(end)

    return begin_iter, end_iter


# ----------------------------------------------------------------------
def ExtractDynamic(
    node: Node,
) -> Union[Leaf, Node]:
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
    excludes = None
    ambiguities_resolved_by_order = None

    # Get a custom name
    if isinstance(item, Phrase):
        name = item.Name
    elif isinstance(item, PhraseItem):
        name = item.Name
        excludes = item.Excludes
        ambiguities_resolved_by_order = item.AmbiguitiesResolvedByOrder
        item = item.Item
    else:
        name = None

    # Get a custom arity
    if isinstance(
        item,
        (
            CustomArityPhraseItem,
            OptionalPhraseItem,
            ZeroOrMorePhraseItem,
            OneOrMorePhraseItem,
        ),
    ):
        if isinstance(item, CustomArityPhraseItem):
            arity = (item.Min, item.Max)
        elif isinstance(item, OptionalPhraseItem):
            arity = (0, 1)
        elif isinstance(item, ZeroOrMorePhraseItem):
            arity = (0, None)
        elif isinstance(item, OneOrMorePhraseItem):
            arity = (1, None)
        else:
            assert False, item  # pragma: no cover

        if name is not None:
            repeat_phrase_name = name
            name = item.Name
        else:
            repeat_phrase_name = item.Name

        item = item.Item

    else:
        arity = None
        repeat_phrase_name = None

    # We can have a PhraseItem that wraps (for example) OptionalPhraseItem or
    # an OptionalPhaseItem that wraps a PhraseItem. The code above handles a
    # PhraseItem that wraps an OptionalPhraseItem; the seemingly redundant code
    # below handles the OptionalPhraseItem that wraps a PhraseItem.
    if isinstance(item, PhraseItem):
        assert name is None
        assert excludes is None
        assert ambiguities_resolved_by_order is None
        assert arity is not None

        name = item.Name
        excludes = item.Excludes
        ambiguities_resolved_by_order = item.AmbiguitiesResolvedByOrder
        item = item.Item

    assert not isinstance(
        item,
        (
            PhraseItem,
            CustomArityPhraseItem,
            OptionalPhraseItem,
            ZeroOrMorePhraseItem,
            OneOrMorePhraseItem,
        ),
    ), item

    # Certain PhraseItem decorators can only be used with certain item types
    assert excludes is None or (excludes and isinstance(item, DynamicPhrasesType)), (excludes, item)
    assert ambiguities_resolved_by_order is None or (ambiguities_resolved_by_order and isinstance(item, (tuple, OrPhrase))), (ambiguities_resolved_by_order, item)

    # Begin the conversion process
    if isinstance(item, Phrase):
        phrase = item

    elif isinstance(item, Token):
        phrase = TokenPhrase(
            item,
            name=name,
        )

    elif isinstance(item, str):
        phrase = TokenPhrase(
            RegexToken(
                name or "'{}'".format(item),
                re.compile(r"{}{}".format(re.escape(item), "\\b" if item.isalnum() else "")),
            ),
        )

    elif isinstance(item, DynamicPhrasesType):
        phrase = DynamicPhrase(
            item,
            lambda unique_id, phrases_type, observer: observer.GetDynamicPhrases(unique_id, phrases_type),
            exclude_names=excludes,
            name=name or str(item),
        )

    elif isinstance(item, list):
        sequence_phrases = [
            _PopulateItem(comment_token, phrase_item) for phrase_item in item
        ]

        phrase = SequencePhrase(
            comment_token,
            sequence_phrases,
            name=name,
        )

    elif isinstance(item, tuple):
        or_phrases = [
            _PopulateItem(comment_token, phrase_item) for phrase_item in item
        ]

        phrase = OrPhrase(
            or_phrases,
            name=name,
            ambiguities_resolved_by_order=ambiguities_resolved_by_order,
        )

    elif isinstance(item, OrPhraseItem):
        assert item.Items

        or_phrases = [
            _PopulateItem(comment_token, phrase_item) for phrase_item in item.Items
        ]

        phrase = OrPhrase(
            or_phrases,
            name=name,
            ambiguities_resolved_by_order=ambiguities_resolved_by_order,
        )

    elif item is None:
        phrase = RecursivePlaceholderPhrase()

    else:
        assert False, item  # pragma: no cover

    if arity is not None:
        phrase = RepeatPhrase(
            phrase,
            arity[0],
            arity[1],
            name=repeat_phrase_name,
        )

    return phrase
