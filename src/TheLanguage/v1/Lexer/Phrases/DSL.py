# ----------------------------------------------------------------------
# |
# |  DSL.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 08:45:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that creates a Domain Specific Language (DSL) for creating complicated lexing phrases"""

import os
import re
import textwrap

from typing import Callable, cast, List, Optional, Match, Tuple, Union

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
    from ..Components.Tokens import RegexToken, Token


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
    str,                                    # Converts to a TokenPhrase (via a very simple RegexToken)
    DynamicPhrasesType,                     # Converts to a DynamicPhrase
    List["PhraseItemItemType"],             # Converts to a SequencePhrase
    Tuple["PhraseItemItemType", ...],       # Converts to an OrPhrase
    None,                                   # Converts to a RecursivePlaceholderPhrase

    "CustomArityPhraseItem",
]


# ----------------------------------------------------------------------
class PhraseItem(object):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        item: PhraseItemItemType,
        name: Optional[str]=None,

        # List of phrase or phrase names that should never be matched by this phrase item
        exclude_phrases: Optional[List[Union[str, Phrase]]]=None,

        # Func that can be called to determine if a data result is valid in a specific context
        is_valid_data_func: Optional[Callable[[Phrase.LexResultData], bool]]=None,

        # When creating an OrPhrase, any ambiguities are resolved using the order in which they appear (rather than generating an error)
        ambiguities_resolved_by_order: Optional[bool]=None,

        precedence_func: Optional[Callable[[Phrase, List[Phrase.LexResultData.DataItemType]], int]]=None,
    ):
        self.item                           = item
        self.name                           = name
        self.exclude_phrases                = exclude_phrases
        self.is_valid_data_func             = is_valid_data_func
        self.ambiguities_resolved_by_order  = ambiguities_resolved_by_order
        self.precedence_func                = precedence_func


# ----------------------------------------------------------------------
class CustomArityPhraseItem(PhraseItem):    # type: ignore
    # ----------------------------------------------------------------------
    def __init__(
        self,
        item: PhraseItemItemType,
        min_value: int,
        *args,
        max_value: Optional[int]=None,
        **kwargs,
    ):
        assert min_value >= 0
        assert max_value is None or max_value >= min_value

        self.min                            = min_value
        self.max                            = max_value

        super(CustomArityPhraseItem, self).__init__(item, *args, **kwargs)


# ----------------------------------------------------------------------
class OptionalPhraseItem(CustomArityPhraseItem):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        item: PhraseItemItemType,
        *args,
        **kwargs,
    ):
        super(OptionalPhraseItem, self).__init__(
            item=item,
            min_value=0,
            max_value=1,
            *args,
            **kwargs,
        )


# ----------------------------------------------------------------------
class ZeroOrMorePhraseItem(CustomArityPhraseItem):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        item: PhraseItemItemType,
        *args,
        **kwargs,
    ):
        super(ZeroOrMorePhraseItem, self).__init__(
            item=item,
            min_value=0,
            max_value=None,
            *args,
            **kwargs,
        )


# ----------------------------------------------------------------------
class OneOrMorePhraseItem(CustomArityPhraseItem):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        item: PhraseItemItemType,
        *args,
        **kwargs,
    ):
        super(OneOrMorePhraseItem, self).__init__(
            item=item,
            min_value=1,
            max_value=None,
            *args,
            **kwargs,
        )


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
    comment_token = comment_token or DefaultCommentToken

    phrase = _PopulateItem(
        comment_token,
        item,
        name=name,
    )

    phrase.PopulateRecursive(None, phrase)

    return phrase


# ----------------------------------------------------------------------
def ExtractTokenNoThrow(
    leaf: Leaf,
    *,
    return_match_contents=False,
    group_dict_name: Optional[str]=None,
) -> Optional[str]:
    assert isinstance(leaf, Leaf), leaf

    if leaf.is_ignored:
        return None

    if isinstance(leaf.value, RegexToken.MatchResult):
        if group_dict_name is not None:
            return leaf.value.match.group(group_dict_name)

        groups_dict = leaf.value.match.groupdict()

        if len(groups_dict) == 1:
            return next(iter(groups_dict.values()))

        if return_match_contents:
            return leaf.value.match.string[leaf.value.match.start() : leaf.value.match.end()]

    return cast(Token, leaf.type).name


# ----------------------------------------------------------------------
def ExtractToken(
    leaf: Leaf,
    *,
    return_match_contents=False,
    group_dict_name: Optional[str]=None,
) -> str:
    result = ExtractTokenNoThrow(
        leaf,
        return_match_contents=return_match_contents,
        group_dict_name=group_dict_name,
    )

    assert result is not None
    return result


# ----------------------------------------------------------------------
def ExtractTokenRangeNoThrow(
    leaf: Leaf,
    group_dict_name: str,
    regex_match: Optional[Match]=None,
) -> Optional[Phrase.NormalizedIteratorRange]:
    """\
    Returns the iterators range associated with the start and end of a group within a match
    (or None if the group didn't match).
    """

    assert isinstance(leaf, Leaf), leaf
    assert isinstance(leaf.value, RegexToken.MatchResult), leaf.value

    if regex_match is not None:
        start = regex_match.start(group_dict_name)
        end = regex_match.end(group_dict_name)
    else:
        start = leaf.value.match.start(group_dict_name)
        end = leaf.value.match.end(group_dict_name)

        if start != -1:
            assert start >= leaf.iter_range.begin.offset
            start -= leaf.iter_range.begin.offset

        if end != -1:
            assert end >= leaf.iter_range.begin.offset
            end -= leaf.iter_range.begin.offset

    if start == end:
        return None

    assert start < end, (start, end)

    begin_iter = leaf.iter_range.begin.Clone()
    begin_iter.Advance(start)

    end_iter = leaf.iter_range.begin.Clone()
    end_iter.Advance(end)

    return Phrase.NormalizedIteratorRange.Create(begin_iter, end_iter)


# ----------------------------------------------------------------------
def ExtractTokenRange(
    leaf: Leaf,
    group_dict_name: str,
    regex_match: Optional[Match]=None,
) -> Phrase.NormalizedIteratorRange:
    result = ExtractTokenRangeNoThrow(leaf, group_dict_name, regex_match)

    assert result is not None
    return result


# ----------------------------------------------------------------------
def ExtractDynamic(
    node: Node,
) -> Union[Leaf, Node]:
    assert isinstance(node, Node), node
    assert isinstance(node.type, DynamicPhrase), node.type
    assert len(node.children) == 1

    node = cast(Node, node.children[0])

    return ExtractOr(node)


# ----------------------------------------------------------------------
def ExtractOr(
    node: Node,
) -> Union[Leaf, Node]:
    assert isinstance(node, Node), node
    assert isinstance(node.type, OrPhrase), node.type
    assert len(node.children) == 1

    return node.children[0]


# ----------------------------------------------------------------------
def ExtractRepeat(
    node: Optional[Node],
) -> List[Union[Leaf, Node]]:
    if node is None:
        return []

    assert isinstance(node, Node), node
    assert isinstance(node.type, RepeatPhrase), node.type

    return node.children


# ----------------------------------------------------------------------
def ExtractOptional(
    node: Optional[Node],
) -> Optional[Union[Leaf, Node]]:
    result = ExtractRepeat(node)

    return result[0] if result else None


# ----------------------------------------------------------------------
def ExtractSequence(
    node: Node,
) -> List[Union[Leaf, Node, None]]:
    assert isinstance(node, Node), node
    assert isinstance(node.type, SequencePhrase), node.type

    phrases = node.type.phrases

    results: List[Union[Leaf, Node, None]] = []
    child_index = 0

    while len(results) != len(phrases) or child_index != len(node.children):
        # Get the phrase
        phrase = None

        if len(results) != len(phrases):
            phrase = phrases[len(results)]

            if isinstance(phrase, TokenPhrase) and phrase.token.is_control_token:
                results.append(None)
                continue

        # Get the child node
        child_node = None

        if child_index != len(node.children):
            child_node = node.children[child_index]
            child_index += 1

            if isinstance(child_node, Leaf) and child_node.is_ignored:
                continue

        else:
            # If here, we have exhausted all of the children. This can only happen when we are
            # looking at a RepeatPhrase that suppors 0 matches.
            assert isinstance(phrase, RepeatPhrase), phrase
            assert phrase.min_matches == 0, phrase.min_matches

            results.append(None)
            continue

        assert phrase is not None
        assert child_node is not None

        if isinstance(phrase, RepeatPhrase) and child_node.type != phrase:
            assert phrase.min_matches == 0, phrase.min_matches
            results.append(None)

            assert child_index != 0
            child_index -= 1

            continue

        results.append(child_node)

    assert len(results) == len(phrases), (len(results), len(phrases))
    return results


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _PopulateItem(
    comment_token: RegexToken,
    item: PhraseItemItemType,
    name: Optional[str]=None,
    exclude_phrases: Optional[List[Union[str, Phrase]]]=None,
    is_valid_data_func: Optional[Callable[[Phrase.LexResultData], bool]]=None,
    ambiguities_resolved_by_order: Optional[bool]=None,
    precedence_func: Optional[Callable[[Phrase, List[Phrase.LexResultData.DataItemType]], int]]=None,
) -> Phrase:
    if isinstance(item, Phrase):
        assert name is None, name
        assert exclude_phrases is None, exclude_phrases
        assert is_valid_data_func is None, is_valid_data_func
        assert ambiguities_resolved_by_order is None, ambiguities_resolved_by_order
        assert precedence_func is None

        return item

    if isinstance(item, PhraseItem):
        assert name is None, name
        assert exclude_phrases is None, exclude_phrases
        assert is_valid_data_func is None, is_valid_data_func
        assert ambiguities_resolved_by_order is None, ambiguities_resolved_by_order
        assert precedence_func is None

        phrase = _PopulateItem(
            comment_token,
            item.item,
            name=item.name,
            exclude_phrases=item.exclude_phrases,
            is_valid_data_func=item.is_valid_data_func,
            ambiguities_resolved_by_order=item.ambiguities_resolved_by_order,
            precedence_func=item.precedence_func,
        )

        if isinstance(item, CustomArityPhraseItem):
            phrase = RepeatPhrase(
                phrase,
                min_matches=item.min,
                max_matches=item.max,
                name=name,
            )

        return phrase

    if isinstance(item, DynamicPhrasesType):
        assert ambiguities_resolved_by_order is None, ambiguities_resolved_by_order
        assert precedence_func is None, precedence_func

        return DynamicPhrase(
            item,
            lambda unique_id, phrases_type, observer: observer.GetDynamicPhrases(unique_id, phrases_type),
            exclude_phrases=exclude_phrases,
            is_valid_data_func=is_valid_data_func,
            name=name or str(item),
        )

    assert exclude_phrases is None, exclude_phrases
    assert is_valid_data_func is None, is_valid_data_func

    if isinstance(item, tuple):
        assert precedence_func is None, precedence_func

        or_phrases = [_PopulateItem(comment_token, phrase_item) for phrase_item in item]

        return OrPhrase(
            or_phrases,
            ambiguities_resolved_by_order=ambiguities_resolved_by_order,
            name=name,
        )

    assert ambiguities_resolved_by_order is None, ambiguities_resolved_by_order

    if isinstance(item, list):
        sequence_phrases = [_PopulateItem(comment_token, phrase_item) for phrase_item in item]

        return SequencePhrase(
            comment_token,
            sequence_phrases,
            precedence_func=precedence_func,
            name=name,
        )

    assert precedence_func is None, precedence_func

    if isinstance(item, Token):
        return TokenPhrase(
            item,
            name=name,
        )

    if isinstance(item, str):
        return TokenPhrase(
            RegexToken(
                name or "'{}'".format(item),
                re.compile(r"{}{}".format(re.escape(item), "\\b" if item.isalnum() else "")),
            ),
        )

    if item is None:
        return RecursivePlaceholderPhrase()

    assert False, item  # pragma: no cover
