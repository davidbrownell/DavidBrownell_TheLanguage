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

from typing import Callable, List, Optional, Tuple, Union

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
    Tuple["PhraseItemItemType"],            # Converts to an OrPhrase
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
    ):
        self.item                           = item
        self.name                           = name
        self.exclude_phrases                = exclude_phrases
        self.is_valid_data_func             = is_valid_data_func
        self.ambiguities_resolved_by_order  = ambiguities_resolved_by_order


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
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _PopulateItem(
    comment_token: RegexToken,
    item: PhraseItemItemType,
    name: Optional[str]=None,
    exclude_phrases: Optional[List[Union[str, Phrase]]]=None,
    is_valid_data_func: Optional[Callable[[Phrase.LexResultData], bool]]=None,
    ambiguities_resolved_by_order: Optional[bool]=None,
) -> Phrase:
    if isinstance(item, Phrase):
        assert name is None, name
        assert exclude_phrases is None, exclude_phrases
        assert is_valid_data_func is None, is_valid_data_func
        assert ambiguities_resolved_by_order is None, ambiguities_resolved_by_order

        return item

    if isinstance(item, PhraseItem):
        assert name is None, name
        assert exclude_phrases is None, exclude_phrases
        assert is_valid_data_func is None, is_valid_data_func
        assert ambiguities_resolved_by_order is None, ambiguities_resolved_by_order

        phrase = _PopulateItem(
            comment_token,
            item.item,
            name=item.name,
            exclude_phrases=item.exclude_phrases,
            is_valid_data_func=item.is_valid_data_func,
            ambiguities_resolved_by_order=item.ambiguities_resolved_by_order,
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
            name=name,
        )

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
