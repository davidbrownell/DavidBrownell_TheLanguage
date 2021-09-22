# ----------------------------------------------------------------------
# |
# |  SequencePhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-22 18:54:53
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

from typing import cast, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.CallOnExit import CallOnExit

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .RecursivePlaceholderPhrase import RecursivePlaceholderPhrase
    from .TokenPhrase import TokenPhrase

    from ..Components.NormalizedIterator import NormalizedIterator
    from ..Components.Phrase import Phrase

    from ..Components.Token import (
        ControlTokenBase,
        DedentToken,
        IndentToken,
        NewlineToken,
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
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        comment_token: RegexToken,
        phrases: List[Phrase],
        name: str=None,
    ):
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
            name = self._CreateDefaultName(phrases)
            name_is_default = True
        else:
            name_is_default = False

        super(SequencePhrase, self).__init__(
            name,
            CommentToken=None,  # type: ignore
        )

        self.CommentToken                   = comment_token
        self.Phrases                        = phrases
        self._name_is_default               = name_is_default

    # ----------------------------------------------------------------------
    async def LexSuffixAsync(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        Phrase.LexResult,
        None,
    ]:
        return await self._LexSequenceItemsAsync(
            1,
            unique_id,
            normalized_iter,
            observer,
            single_threaded,
            1 if ignore_whitespace else 0,
            None,
        )

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ExtractPotentialResults(object):
        Results: List[Phrase.TokenLexResultData]
        IterEnd: Phrase.NormalizedIterator

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _indent_token                           = IndentToken()
    _dedent_token                           = DedentToken()
    _newline_token                          = NewlineToken()

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
                replaced_phrase = phrase.PopulateRecursiveImpl(new_phrase) or replaced_phrase

        if replaced_phrase and self._name_is_default:
            self.Name = self._CreateDefaultName(self.Phrases)

        return replaced_phrase

    # ----------------------------------------------------------------------
    @Interface.override
    async def _LexAsyncImpl(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        Phrase.LexResult,
        None,
    ]:
        success = False

        observer.StartPhrase(unique_id, [self])
        with CallOnExit(lambda: observer.EndPhrase(unique_id, [(self, success)])):
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

            result = await self._LexSequenceItemsAsync(
                0,
                unique_id,
                normalized_iter,
                observer,
                single_threaded,
                ignore_whitespace_ctr,
                ignored_indentation_level,
            )

            if result is None:
                return None

            if result.Success:
                success = result.Success

                if not await observer.OnInternalPhraseAsync(
                    [cast(Phrase.StandardLexResultData, result.Data)],
                    original_normalized_iter,
                    result.IterEnd,
                ):
                    return None

            return result

    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractPotentialWhitespaceToken(
        cls,
        normalized_iter: Phrase.NormalizedIterator,
        consume_indent=True,
        consume_dedent=True,
    ) -> Optional[Phrase.TokenLexResultData]:
        """Eats any whitespace token when requested"""

        normalized_iter_begin = normalized_iter.Clone()
        normalized_iter = normalized_iter.Clone()

        # Potential indent or dedent
        for token in [
            cls._dedent_token,
            cls._indent_token,
        ]:
            if not consume_indent and token == cls._indent_token:
                continue

            if not consume_dedent and token == cls._dedent_token:
                continue

            result = token.Match(normalized_iter)
            if result is not None:
                # <Too many arguments> pylint: disable=E1121
                return Phrase.TokenLexResultData(
                    token,
                    None,
                    result,
                    normalized_iter_begin,
                    normalized_iter,
                    IsIgnored=True,
                )

        # A potential newline
        potential_whitespace = TokenPhrase.ExtractWhitespace(normalized_iter)
        normalized_iter_begin = normalized_iter.Clone()

        result = cls._newline_token.Match(normalized_iter)
        if result is not None:
            # <Too many arguments> pylint: disable=E1121
            return Phrase.TokenLexResultData(
                cls._newline_token,
                potential_whitespace,
                result,
                normalized_iter_begin,
                normalized_iter,
                IsIgnored=True,
            )

        return None

    # ----------------------------------------------------------------------
    def _ExtractPotentialCommentTokens(
        self,
        normalized_iter: Phrase.NormalizedIterator,
        *,
        next_phrase_is_indent: bool,
        next_phrase_is_dedent: bool,
    ) -> Optional["SequencePhrase.ExtractPotentialResults"]:
        """Eats any comment (stand-alone or trailing) when requested"""

        normalized_iter = normalized_iter.Clone()
        next_token = normalized_iter.GetNextToken()

        if next_token == NormalizedIterator.TokenType.Indent:
            # There are 2 scenarios to consider here:
            #
            #     1) The indent that we are looking at is because the comment itself
            #        is indented. Example:
            #
            #           Line 1: Int value = 1       # The first line of the comment
            #           Line 2:                     # The second line of the comment
            #           Line 3: value += 1
            #
            #        In this scenario, Line 2 starts with an indent and Line 3 starts with
            #        a dedent. We want to consume and ignore both the indent and dedent.
            #
            #     2) The indent is a meaningful part of the statement. Example:
            #
            #           Line 1: class Foo():
            #           Line 2:     # A comment
            #           Line 3:     Int value = 1
            #
            #        In this scenario, Line 2 is part of the class declaration and we want
            #        the indent to be officially consumed before we process the comment.

            if next_phrase_is_indent:
                # We are in scenario #2
                return None

            # If here, we are in scenario #1
            at_beginning_of_line = True

            normalized_iter_begin = normalized_iter.Clone()
            normalized_iter.SkipWhitespacePrefix()

            potential_whitespace = (normalized_iter_begin.Offset, normalized_iter.Offset)

        elif next_token == NormalizedIterator.TokenType.WhitespacePrefix:
            at_beginning_of_line = True

            normalized_iter.SkipWhitespacePrefix()
            potential_whitespace = None

        else:
            at_beginning_of_line = (
                normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart
                or normalized_iter.Offset == normalized_iter.LineInfo.PosStart
            )
            potential_whitespace = TokenPhrase.ExtractWhitespace(normalized_iter)

        normalized_iter_begin = normalized_iter.Clone()

        result = self.CommentToken.Match(normalized_iter)
        if result is None:
            return None

        results = [
            # <Too many arguments> pylint: disable=E1121
            Phrase.TokenLexResultData(
                self.CommentToken,
                potential_whitespace,
                result,
                normalized_iter_begin,
                normalized_iter,
                IsIgnored=True,
            ),
        ]

        # Add additional content if we are at the beginning of the line
        if at_beginning_of_line:
            # Capture the trailing newline
            result = self._ExtractPotentialWhitespaceToken(results[-1].IterEnd)
            assert result

            results.append(result)

            # Consume potential dedents, but don't return it with the results (as we absorbed
            # the corresponding indent when we skipped the prefix in the code above)
            if (
                results[0].Whitespace is not None
                and results[-1].IterEnd.GetNextToken() == NormalizedIterator.TokenType.Dedent
                and not next_phrase_is_dedent
            ):
                result = self._ExtractPotentialWhitespaceToken(results[-1].IterEnd)
                assert result

                # Ensure that the iterator is updated to account for the dedent even if
                # it wasn't returned as part of the results. Comments are special beasts.
                return SequencePhrase.ExtractPotentialResults(results, result.IterEnd)

        return SequencePhrase.ExtractPotentialResults(results, results[-1].IterEnd)

    # ----------------------------------------------------------------------
    async def _LexSequenceItemsAsync(
        self,
        phrase_offset: int,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        single_threaded: bool,
        ignore_whitespace_ctr: int,
        ignored_indentation_level: Optional[int],
    ) -> Optional[Phrase.LexResult]:

        original_normalized_iter = normalized_iter.Clone()

        # ----------------------------------------------------------------------
        def ExtractWhitespaceOrComments(
            *,
            next_phrase_is_indent: bool,
            next_phrase_is_dedent: bool,
        ) -> Optional[SequencePhrase.ExtractPotentialResults]:
            nonlocal ignored_indentation_level

            if normalized_iter.Offset == 0:
                # If we are at the beginning of the content, consume any leading
                # newlines. We don't need to worry about a content that starts with
                # newline-comment-newline as the comment extract code will handle
                # the newline(s) that appears after the comment.
                process_whitespace = True
                consume_indent = False
                consume_dedent = False

            elif ignore_whitespace_ctr:
                process_whitespace = True
                consume_indent = True
                consume_dedent = ignored_indentation_level != 0

            else:
                process_whitespace = False
                consume_indent = False
                consume_dedent = False

            if process_whitespace:
                data_item = self._ExtractPotentialWhitespaceToken(
                    normalized_iter,
                    consume_indent=consume_indent,
                    consume_dedent=consume_dedent,
                )

                if data_item is not None:
                    if ignored_indentation_level is not None:
                        if isinstance(data_item.Token, IndentToken):
                            ignored_indentation_level += 1
                        elif isinstance(data_item.Token, DedentToken):
                            assert ignored_indentation_level
                            ignored_indentation_level -= 1

                    return SequencePhrase.ExtractPotentialResults(
                        [data_item],
                        data_item.IterEnd,
                    )

            return self._ExtractPotentialCommentTokens(
                normalized_iter,
                next_phrase_is_indent=next_phrase_is_indent,
                next_phrase_is_dedent=next_phrase_is_dedent,
            )

        # ----------------------------------------------------------------------

        success = True
        data_items: List[Optional[Phrase.LexResultData]] = []

        preserved_ignore_whitespace_ctr: Optional[int] = None

        observer_decorator = Phrase.ObserverDecorator(
            self,
            unique_id,
            observer,
            data_items,
            lambda data_item: data_item,
        )

        if self.Name == "Func Invocation Statement":
            BugBug = 10

        for phrase_index, phrase in enumerate(self.Phrases[phrase_offset:]):
            phrase_index += phrase_offset

            # Extract whitespace or comments
            pre_whitespace_iter = normalized_iter.Clone()

            if isinstance(phrase, TokenPhrase):
                next_phrase_is_indent = isinstance(phrase.Token, IndentToken)
                next_phrase_is_dedent = isinstance(phrase.Token, DedentToken)
            else:
                next_phrase_is_indent = False
                next_phrase_is_dedent = False

            while not normalized_iter.AtEnd():
                potential_prefix_info = ExtractWhitespaceOrComments(
                    next_phrase_is_indent=next_phrase_is_indent,
                    next_phrase_is_dedent=next_phrase_is_dedent,
                )

                if potential_prefix_info is None:
                    break

                data_items += potential_prefix_info.Results
                normalized_iter = potential_prefix_info.IterEnd

            # It shouldn't be considered an error when whitespace/comments
            # were encountered at the end of the content when processing the
            # first phrase in the list of phrases.
            if (
                normalized_iter.AtEnd()
                and normalized_iter.Offset != original_normalized_iter.Offset
                and phrase_index - phrase_offset == 0
            ):
                # This sequence has failed
                success = False

                # <Too many arguments> pylint: disable=E1121
                return Phrase.LexResult(
                    True,
                    original_normalized_iter,
                    normalized_iter,
                    # <Too many arguments> pylint: disable=E1121
                    Phrase.StandardLexResultData(
                        # Note that this phrase will never be used directly, but
                        # needs to be of a type that is expected to contain
                        # MultipleStandardLexResultData items.
                        SequencePhrase(
                            self.CommentToken,
                            [
                                TokenPhrase(self.CommentToken),
                                TokenPhrase(self._newline_token),
                            ],
                            name="End of File Whitespace and/or Comment(s)",
                        ),
                        # <Too many arguments> pylint: disable=E1121
                        Phrase.MultipleStandardLexResultData(data_items, True),
                        unique_id,
                    ),
                )

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

                continue

            # Process the phrase
            result = await phrase.LexAsync(
                unique_id + ("Sequence: {} [{}]".format(phrase.Name, phrase_index), ),
                normalized_iter.Clone(),
                observer_decorator,
                ignore_whitespace=ignore_whitespace_ctr != 0,
                single_threaded=single_threaded,
            )

            if result is None:
                return None

            # Preserve the results
            if result.Data is not None:
                data_items.append(result.Data)

            # Update the iterator
            if result.IterEnd == normalized_iter:
                # Nothing was matched, so revert back to the iterator before whitespace was consumed
                normalized_iter = pre_whitespace_iter
            else:
                normalized_iter = result.IterEnd.Clone()

            if not result.Success:
                success = False
                break

        # <Too many arguments> pylint: disable=E1121
        return Phrase.LexResult(
            success,
            original_normalized_iter,
            normalized_iter,
            # <Too many arguments> pylint: disable=E1121
            Phrase.StandardLexResultData(
                self,
                # <Too many arguments> pylint: disable=E1121
                Phrase.MultipleStandardLexResultData(data_items, True),
                unique_id,
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateDefaultName(
        phrases: List[Phrase],
    ) -> str:
        return "Sequence: [{}]".format(", ".join([phrase.Name for phrase in phrases]))
