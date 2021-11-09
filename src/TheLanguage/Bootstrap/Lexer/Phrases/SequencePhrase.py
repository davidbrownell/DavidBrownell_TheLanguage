# ----------------------------------------------------------------------
# |
# |  SequencePhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-22 23:06:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SequencePhrase object"""

import os

from typing import cast, List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .RecursivePlaceholderPhrase import RecursivePlaceholderPhrase
    from .TokenPhrase import TokenPhrase

    from ..Components.Phrase import Phrase

    from ..Components.Token import (
        ControlTokenBase,
        DedentToken,
        IndentToken,
        PopIgnoreWhitespaceControlToken,
        PopPreserveWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        PushPreserveWhitespaceControlToken,
        RegexToken,
    )


# ----------------------------------------------------------------------
class SequencePhrase(Phrase):
    """Matches a sequence of phrases"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ExtractCommentResult(object):
        Results: List[Phrase.TokenLexResultData]
        IterEnd: Phrase.NormalizedIterator

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        comment_token: RegexToken,
        phrases: List[Phrase],
        name: Optional[str]=None,
    ):
        assert phrases
        assert all(phrase for phrase in phrases)

        # Ensure that any control tokens that come in pairs have peers
        control_token_tracker = set()

        for phrase_index, phrase in enumerate(phrases):
            if isinstance(phrase, TokenPhrase) and phrase.Token.IsControlToken:
                if phrase_index == 0:
                    assert (
                        isinstance(phrases[-1], TokenPhrase)
                        and cast(TokenPhrase, phrases[-1]).Token.IsControlToken
                    ), "The last phrase must be a control token when the first phrase is a control token"

                control_token = cast(ControlTokenBase, phrase.Token)

                if control_token.ClosingToken is not None:
                    key = type(control_token)
                    if key in control_token_tracker:
                        assert False, key

                    control_token_tracker.add(key)

                if control_token.OpeningToken is not None:
                    key = control_token.OpeningToken

                    if key not in control_token_tracker:
                        assert False, key

                    control_token_tracker.remove(key)

            elif phrase_index == 0:
                assert not (
                    isinstance(phrases[-1], TokenPhrase)
                    and cast(TokenPhrase, phrases[-1]).Token.IsControlToken
                ), "The last phrase must not be a control token when the first phrase is not a control token"

        assert not control_token_tracker, control_token_tracker

        # Initialize the class
        if name is None:
            name = self.__class__._CreateDefaultName(phrases)
            name_is_default = True
        else:
            name_is_default = False

        assert name is not None

        super(SequencePhrase, self).__init__(
            name,
            CommentToken=None,
        )

        self.CommentToken                   = comment_token
        self.Phrases                        = phrases
        self._name_is_default               = name_is_default

    # ----------------------------------------------------------------------
    @Interface.override
    async def LexAsync(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Optional[Phrase.LexResult]:

        result: Optional[Phrase.LexResult] = None

        observer.StartPhrase(unique_id, self)
        with CallOnExit(
            lambda: observer.EndPhrase(unique_id, self, result is not None and result.Success)
        ):
            original_normalized_iter = normalized_iter.Clone()

            ignore_whitespace_ctr = 1 if ignore_whitespace else 0

            # If the first phrase is a control token indicating that whitespace should be
            # ignored, we need to make sure that the trailing dedents aren't greedily consumed,
            # but rather we stop consuming them once we end up at the initial level.
            if (
                isinstance(self.Phrases[0], TokenPhrase)
                and isinstance(self.Phrases[0].Token, PushIgnoreWhitespaceControlToken)
            ):
                ignored_indentation_level = 0
            else:
                ignored_indentation_level = None

            result = await self._LexAsyncImpl(
                unique_id,
                normalized_iter,
                observer,
                single_threaded=single_threaded,
                ignore_whitespace_ctr=ignore_whitespace_ctr,
                ignored_indentation_level=ignored_indentation_level,
                starting_phrase_index=0,
            )

            if result is None:
                return None

            if result.Success and not await observer.OnInternalPhraseAsync(
                cast(Phrase.StandardLexResultData, result.Data),
                original_normalized_iter,
                result.IterEnd,
            ):
                return None

            return result

    # ----------------------------------------------------------------------
    async def LexSuffixAsync(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Optional[Phrase.LexResult]:
        return await self._LexAsyncImpl(
            unique_id,
            normalized_iter,
            observer,
            single_threaded=single_threaded,
            ignore_whitespace_ctr=1 if ignore_whitespace else 0,
            ignored_indentation_level=None,
            starting_phrase_index=1,
        )

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    ) -> bool:
        replaced_phrase = False

        for phrase_index, phrase in enumerate(self.Phrases):
            if isinstance(phrase, RecursivePlaceholderPhrase):
                self.Phrases[phrase_index] = new_phrase
                replaced_phrase = True

            else:
                replaced_phrase = phrase.PopulateRecursive(self, new_phrase) or replaced_phrase

        if replaced_phrase and self._name_is_default:
            self.Name = self.__class__._CreateDefaultName(self.Phrases)

        return replaced_phrase

    # ----------------------------------------------------------------------
    async def _LexAsyncImpl(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        single_threaded: bool,
        ignore_whitespace_ctr: int,
        ignored_indentation_level: Optional[int],
        starting_phrase_index: int,
    ) -> Optional[Phrase.LexResult]:
        original_normalized_iter = normalized_iter.Clone()

        success = False

        data_items: List[Optional[Phrase.LexResultData]] = []
        preserved_ignore_whitespace_ctr: Optional[int] = None

        comments_or_whitespace_data_items: Optional[List[Phrase.TokenLexResultData]] = None
        prev_token_was_pop_control = False

        if self.Name.endswith("Expression") and normalized_iter.Offset == 11159:
            BugBug = 1

        if self.Name == "Func Invocation Expression" and normalized_iter.Line == 249:
            BugBug = 10
        if self.Name == "Tuple Expression" and normalized_iter.Offset == 11159:
            BugBug = 20

        for phrase_index in range(starting_phrase_index, len(self.Phrases)):
            phrase = self.Phrases[phrase_index]

            # Extract whitespace or comments if necessary
            if (
                comments_or_whitespace_data_items is None
                or (isinstance(phrase, TokenPhrase) and not prev_token_was_pop_control)
            ):
                if comments_or_whitespace_data_items:
                    normalized_iter = comments_or_whitespace_data_items[0].IterBegin  # pylint: disable=unsubscriptable-object

                comments_or_whitespace_data_items = []

                if isinstance(phrase, TokenPhrase):
                    next_phrase_is_indent = isinstance(phrase.Token, IndentToken)
                    next_phrase_is_dedent = isinstance(phrase.Token, DedentToken)
                else:
                    next_phrase_is_indent = False
                    next_phrase_is_dedent = False

                potential_comments_or_whitespace_result = TokenPhrase.ExtractPotentialCommentsOrWhitespace(
                    self.CommentToken,
                    normalized_iter,
                    ignored_indentation_level,
                    ignore_whitespace=ignore_whitespace_ctr != 0,
                    next_phrase_is_indent=next_phrase_is_indent,
                    next_phrase_is_dedent=next_phrase_is_dedent,
                )

                if potential_comments_or_whitespace_result is not None:
                    (
                        comments_or_whitespace_data_items,
                        normalized_iter,
                        ignored_indentation_level,
                    ) = potential_comments_or_whitespace_result

            # Process control tokens
            if isinstance(phrase, TokenPhrase) and phrase.Token.IsControlToken:
                if isinstance(phrase.Token, PushIgnoreWhitespaceControlToken):
                    ignore_whitespace_ctr += 1

                elif isinstance(phrase.Token, PopIgnoreWhitespaceControlToken):
                    assert ignore_whitespace_ctr != 0
                    ignore_whitespace_ctr -= 1

                elif isinstance(phrase.Token, PushPreserveWhitespaceControlToken):
                    assert preserved_ignore_whitespace_ctr is None, preserved_ignore_whitespace_ctr
                    preserved_ignore_whitespace_ctr = ignore_whitespace_ctr

                    ignore_whitespace_ctr = 0

                elif isinstance(phrase.Token, PopPreserveWhitespaceControlToken):
                    assert preserved_ignore_whitespace_ctr is not None

                    ignore_whitespace_ctr = preserved_ignore_whitespace_ctr
                    preserved_ignore_whitespace_ctr = None

                else:
                    assert False, phrase.Token  # pragma: no cover

                # If we are pushing a new value, reset the collected comment or whitespace tokens
                # as they might be impacted by the new value. If popping, preserve the tokens that
                # we collected under the previous settings.
                prev_token_was_pop_control = phrase.Token.OpeningToken is not None

                if not prev_token_was_pop_control:
                    if comments_or_whitespace_data_items:
                        normalized_iter = comments_or_whitespace_data_items[0].IterBegin

                    comments_or_whitespace_data_items = None

                continue

            prev_token_was_pop_control = False

            # Process the phrase
            result = await phrase.LexAsync(
                unique_id + ("{} [{}]".format(self.Name, phrase_index), ),
                normalized_iter,
                observer,
                ignore_whitespace=ignore_whitespace_ctr != 0,
                single_threaded=single_threaded,
            )

            if result is None:
                return None

            # Preserve the results
            if result.Data is not None:
                if (
                    result.Success
                    and result.IterEnd != result.IterBegin
                    and comments_or_whitespace_data_items is not None
                ):
                    data_items += comments_or_whitespace_data_items

                    comments_or_whitespace_data_items = None

                data_items.append(result.Data)

            # Update the iterator
            normalized_iter = result.IterEnd.Clone()

            if not result.Success:
                success = False
                break

            success = True

        if success:
            print("BugBug", normalized_iter.Line, normalized_iter.Column)

        if comments_or_whitespace_data_items:
            # If the previous token was a pop, we should consider the output as part of the current
            # phrase. Otherwise, we should consider the tokens as part of the next phrase.
            if prev_token_was_pop_control:
                data_items += comments_or_whitespace_data_items
                normalized_iter = comments_or_whitespace_data_items[-1].IterEnd
            else:
                normalized_iter = comments_or_whitespace_data_items[0].IterBegin

            comments_or_whitespace_data_items = None

        # pylint: disable=too-many-function-args
        return Phrase.LexResult(
            success,
            original_normalized_iter,
            normalized_iter,
            Phrase.StandardLexResultData(
                self,
                Phrase.MultipleLexResultData(data_items, True),
                unique_id,
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateDefaultName(
        phrases: List[Phrase],
    ) -> str:
        return "[{}]".format(", ".join([phrase.Name for phrase in phrases]))
