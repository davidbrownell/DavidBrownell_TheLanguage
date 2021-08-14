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
from typing import cast, Generator, List, Optional, Set, Tuple, Union

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
        str,                                # Valid values are "?", "?-", "*", "+"
        Tuple[int, Optional[int]],
    ]                                       = field(default_factory=lambda: (1, 1))
    non_greedy: bool                        = field(init=False, default=False)

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __post_init__(self):
        if isinstance(self.arity, str):
            if self.arity == "?-":
                value = (0, 1)
                object.__setattr__(self, "non_greedy", True)
            elif self.arity == "?":
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

    # Most of the time, this flag does not need to be set. However, setting it to True will prevent
    # infinite recursion errors for the first phrase in a sequence if that phrase is a DynamicPhrase
    # that includes the parent.
    #
    # For example, the following phrase will suffer from this problem (as the first phrase in the
    # sequence is requesting a collection of dynamic phrases of a category that includes the phrase
    # itself) unless the flag is set:
    #
    #   Name:   AsPhrase
    #   Type:   DynamicPhrasesType.Expressions
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

    assert not _IsNonGreedy(phrase), phrase

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
ExtractSequenceReturnType                   = List[
    Union[
        Tuple[str, Leaf],
        Node,
        List[Node],
        None,
    ],
]

def ExtractSequence(
    node: Node,
) -> ExtractSequenceReturnType:
    # Are we looking at a non-greedy sequence?
    if isinstance(node.Type, OrPhrase):
        node = cast(Node, ExtractOr(node))

        skipped_indexes = getattr(node.Type, _SKIPPED_INDEXES_ATTRIBUTE, None)
        assert skipped_indexes is not None

    else:
        assert isinstance(node.Type, SequencePhrase), node.Type
        skipped_indexes = set()

    assert node.Type is not None
    phrases = node.Type.Phrases  # type: ignore

    num_skipped_phrases = 0

    results = []
    child_index = 0

    while child_index != len(node.Children) or len(results) - num_skipped_phrases != len(phrases):
        if len(results) in skipped_indexes:
            results.append(None)
            num_skipped_phrases += 1

            continue

        phrase = None

        if len(results) - num_skipped_phrases != len(phrases):
            phrase = phrases[len(results) - num_skipped_phrases]

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

        if isinstance(phrase, TokenPhrase):
            results.append((ExtractToken(cast(Leaf, child)), child))

        elif isinstance(phrase, DynamicPhrase):
            results.append(ExtractDynamic(cast(Node, child)))

        elif isinstance(phrase, OrPhrase):
            results.append(ExtractOr(cast(Node, child)))

        elif isinstance(phrase, RepeatPhrase):
            if child.Type != phrase:
                assert child_index != 0
                child_index -= 1

                assert phrase.MinMatches == 0, phrase.MinMatches
                results.append(None if phrase.MaxMatches == 1 else [])

            else:
                results.append(ExtractRepeat(cast(Node, child)))

        elif isinstance(phrase, SequencePhrase):
            # Do not drill into the sequence
            results.append(child)

        else:
            assert False, phrase  # pragma: no cover

    assert len(results) - num_skipped_phrases == len(phrases), (len(results), num_skipped_phrases, len(phrases))
    return results


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
_NON_GREEDY_FLAG_ATTRIBUTE                  = "_non_greedy_flag"
_SKIPPED_INDEXES_ATTRIBUTE                  = "_non-greedy_skipped_indexes"

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
        sequence_phrases = []

        for phrase_item in item.item:
            sequence_phrase = _PopulateItem(
                comment_token,
                phrase_item,
                None if suffers_from_infinite_recursion_ctr is None else suffers_from_infinite_recursion_ctr - 1,
            )

            sequence_phrases.append(sequence_phrase)

        # Non-greedy phrases are tricky, as we want to attempt to match the content with the phrase and
        # also as if the phrase doesn't exist. Furthermore, there can be multiple non-greedy phrases in
        # the sequence. Generate every permutation of the phrases that include and don't include these
        # non-greedy phrases and then wrap them in an OrPhrase.
        all_phrase_options = list(_GenerateNonGreedySequencePhrases(sequence_phrases))

        if len(all_phrase_options) == 1:
            assert sequence_phrases == all_phrase_options[0][0]
            assert not all_phrase_options[0][1], all_phrase_options[0][1]

            phrase = SequencePhrase(
                comment_token,
                sequence_phrases,
                name=item.name,
            )
        else:
            or_phrases = []

            for phrase_options_index, (phrase_options, skipped_indexes) in enumerate(all_phrase_options):
                sequence_phrase = SequencePhrase(
                    comment_token,
                    phrase_options,
                    name="<< Option {} >>".format(phrase_options_index),
                )

                object.__setattr__(sequence_phrase, _SKIPPED_INDEXES_ATTRIBUTE, skipped_indexes)

                or_phrases.append(sequence_phrase)

            phrase = OrPhrase(
                or_phrases,
                sort_results=True,
                name="<< Non Greedy - {} >>".format(item.name),
            )

    elif isinstance(item.item, tuple):
        or_options = []

        for phrase_item in item.item:
            option_phrase = _PopulateItem(
                comment_token,
                phrase_item,
                None if suffers_from_infinite_recursion_ctr is None else suffers_from_infinite_recursion_ctr - 1,
            )

            assert not _IsNonGreedy(option_phrase), option_phrase

            or_options.append(option_phrase)

        phrase = OrPhrase(
            or_options,
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

    assert not _IsNonGreedy(phrase), phrase

    repeat_phrase = RepeatPhrase(
        phrase,
        item.arity[0],
        item.arity[1],
        name=name,
    )

    if item.non_greedy:
        object.__setattr__(repeat_phrase, _NON_GREEDY_FLAG_ATTRIBUTE, True)

    return repeat_phrase


# ----------------------------------------------------------------------
def _IsNonGreedy(
    phrase: Phrase,
):
    return hasattr(phrase, _NON_GREEDY_FLAG_ATTRIBUTE)


# ----------------------------------------------------------------------
def _GenerateNonGreedySequencePhrases(
    phrases: List[Phrase],
    index=0,
    skipped_indexes: Optional[Set[int]]=None,
) -> Generator[
    Tuple[List[Phrase], Set[int]],
    None,
    None,
]:
    if skipped_indexes is None:
        skipped_indexes = set()

    while index < len(phrases):
        phrase = phrases[index]

        if not _IsNonGreedy(phrase):
            index += 1
            continue

        assert isinstance(phrase, RepeatPhrase), phrase

        # This only works for optional RepeatPhrases. We will need to introduce more complex
        # non-greedy algorithms if this turns out to be too great of a limitation.
        assert phrase.MinMatches == 0, phrase.MinMatches
        assert phrase.MaxMatches == 1, phrase.MaxMatches

        object.__delattr__(phrase, _NON_GREEDY_FLAG_ATTRIBUTE)

        phrases = list(phrases)

        # Generate combinations with this phrase as required
        phrases[index] = phrase.Phrase
        yield from _GenerateNonGreedySequencePhrases(phrases, index + 1, skipped_indexes)

        # Generate combinations with this phrase removed
        phrases = list(phrases)
        del phrases[index]

        skipped_indexes = set(skipped_indexes)
        skipped_indexes.add(index)

        yield from _GenerateNonGreedySequencePhrases(phrases, index, skipped_indexes)

        return

    yield phrases, skipped_indexes
