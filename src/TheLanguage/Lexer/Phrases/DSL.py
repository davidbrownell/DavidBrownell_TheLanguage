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
    from .LeftRecursiveSequencePhraseWrapper import LeftRecursiveSequencePhraseWrapper
    from .OrPhrase import OrPhrase
    from .RecursivePlaceholderPhrase import RecursivePlaceholderPhrase
    from .RepeatPhrase import RepeatPhrase
    from .SequencePhrase import SequencePhrase
    from .TokenPhrase import TokenPhrase

    from ..Components.AST import Leaf, Node
    from ..Components.Phrase import DynamicPhrasesType, Phrase
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
    exclude: List[Union[str, Phrase]]       = field(default_factory=list)
    ordered_by_priority: Optional[bool]     = field(default=None)

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
) -> Phrase:

    comment_token = comment_token or CommentToken

    if name is not None:
        assert item is not None
        assert not isinstance(item, (PhraseItem, Phrase)), item

        item = PhraseItem(
            item,
            name=name,
        )

    phrase = _PopulateItem(comment_token, item)

    phrase.PopulateRecursive()

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
    assert isinstance(node.Type, SequencePhrase)
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
            results.append(None)

            continue

        assert phrase
        assert child

        if isinstance(phrase, RepeatPhrase) and child.Type != phrase:
            assert phrase.MinMatches == 0, phrase.MinMatches
            results.append(None)

            assert child_index != 0
            child_index -= 1

            continue

        results.append(child)

    assert len(results) == len(phrases), (len(results), len(phrases))
    return results


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _PopulateItem(
    comment_token: RegexToken,
    item: PhraseItem.ItemType,
) -> Phrase:

    if not isinstance(item, PhraseItem):
        item = PhraseItem(item)

    name = None

    assert not item.exclude or isinstance(item.item, (DynamicPhrasesType, DynamicPhrase)), item

    # Phrase priorities should only be used for OrPhrases
    assert item.ordered_by_priority is None or isinstance(item.item, (tuple, OrPhrase))

    if isinstance(item.item, PhraseItem):
        phrase = _PopulateItem(comment_token, item.item)
        name = item.name

    elif isinstance(item.item, Phrase):
        phrase = item.item
        name = item.name

    else:
        if isinstance(item.item, Token):
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
            if item.exclude:
                exclude_names = set(
                    [
                        phrase.Name if isinstance(phrase, Phrase) else phrase
                        for phrase in item.exclude
                    ],
                )

                # ----------------------------------------------------------------------
                def GetDynamicPhrases(
                    unique_id: Tuple[str, ...],
                    phrases_type: DynamicPhrasesType,
                    observer: Phrase.Observer,
                ) -> Tuple[Optional[str], List[Phrase]]:
                    name, phrases = observer.GetDynamicPhrases(unique_id, phrases_type)

                    updated_phrases = []

                    for phrase in phrases:
                        if isinstance(phrase, LeftRecursiveSequencePhraseWrapper):
                            phrase.ExcludePhrases(exclude_names)

                        if phrase.Name in exclude_names:
                            continue

                        updated_phrases.append(phrase)

                    return name, updated_phrases

                # ----------------------------------------------------------------------

                func = GetDynamicPhrases

            else:
                func = lambda unique_id, phrases_type, observer: observer.GetDynamicPhrases(unique_id, phrases_type)

            phrase = DynamicPhrase(
                item.item,
                func,
                name=item.name or str(item.item),
            )

        elif isinstance(item.item, list):
            sequence_phrases = [
                _PopulateItem(comment_token, phrase_item) for phrase_item in item.item
            ]

            phrase = SequencePhrase(
                comment_token,
                sequence_phrases,
                name=item.name,
            )

        elif isinstance(item.item, tuple):
            or_phrases = [
                _PopulateItem(comment_token, phrase_item) for phrase_item in item.item
            ]

            phrase = OrPhrase(
                or_phrases,
                name=item.name,
                ordered_by_priority=item.ordered_by_priority,
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