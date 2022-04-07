# ----------------------------------------------------------------------
# |
# |  SequencePhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-03 13:29:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SequencePhrase object"""

import os
import sys

from typing import Callable, List, Optional, TextIO, Tuple, Union

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

    from ..Components.Phrase import NormalizedIterator, Phrase

    from ..Components.Tokens import (
        DedentToken,
        HorizontalWhitespaceToken,
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
        precedence_func: Optional[Callable[[Phrase, List[Phrase.LexResultData.DataItemType]], int]]=None,
        name: Optional[str]=None,
    ):
        assert phrases
        assert all(phrases)

        precedence_func = precedence_func or (lambda *args, **kwargs: sys.maxsize)

        if name is None:
            name = self.__class__._CreateDefaultName(phrases)  # type: ignore  # pylint: disable=protected-access
            name_is_default = True
        else:
            name_is_default = False

        assert name is not None
        super(SequencePhrase, self).__init__(name)

        self.comment_token                  = comment_token
        self.phrases                        = phrases
        self._precedence_func               = precedence_func
        self._name_is_default               = name_is_default

    # ----------------------------------------------------------------------
    @Interface.override
    def Lex(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: NormalizedIterator,
        observer: Phrase.Observer,
        *,
        single_threaded=False,
        ignore_whitespace=False,
    ) -> Optional[Phrase.LexResult]:
        result: Optional[Phrase.LexResult] = None

        observer.StartPhrase(unique_id, self)
        with CallOnExit(lambda: observer.EndPhrase(unique_id, self, result is not None and result.success)):
            # If the first phrase is a control token indicating that whitespace should be
            # ignored, we need to make sure that the trailing dedents aren't greedily consumed,
            # but rather we stop consuming them once we end up at the initial level.
            if isinstance(self.phrases[0], TokenPhrase) and isinstance(self.phrases[0].token, PushIgnoreWhitespaceControlToken):
                ignored_indentation_level = 0
            else:
                ignored_indentation_level = None

            result = self._LexImpl(
                unique_id,
                normalized_iter,
                observer,
                ignore_whitespace_ctr=1 if ignore_whitespace else 0,
                ignored_indentation_level=ignored_indentation_level,
                starting_phrase_index=0,
                single_threaded=single_threaded,
            )

            if result is None:
                return None

            if result.success and not observer.OnInternalPhrase(result.iter_range, result.data):
                return None

            return result

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def PrettyPrint(
        indentation: str,
        data: Phrase.LexResultData.DataItemType,
        output_stream: TextIO,
    ) -> None:
        assert isinstance(data, list), data

        output_stream.write("{}[[[\n".format(indentation))

        this_indentation = indentation + "    "

        for item in data:
            if isinstance(item, Phrase.TokenLexResultData):
                assert item.is_ignored
                continue

            assert isinstance(item, Phrase.LexResultData), item
            item.phrase.PrettyPrint(this_indentation, item.data, output_stream)

        output_stream.write("{}]]]\n".format(indentation))

    # ----------------------------------------------------------------------
    def LexSuffix(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: NormalizedIterator,
        observer: Phrase.Observer,
        *,
        single_threaded=False,
        ignore_whitespace=False,
    ) -> Optional[Phrase.LexResult]:
        return self._LexImpl(
            unique_id,
            normalized_iter,
            observer,
            ignore_whitespace_ctr=1 if ignore_whitespace else 0,
            ignored_indentation_level=None,
            starting_phrase_index=1,
            single_threaded=single_threaded,
        )

    # ----------------------------------------------------------------------
    def CalcPrecedence(
        self,
        data_items: List[Phrase.LexResultData.DataItemType],
    ) -> int:
        """\
        Returns the precedence of this phrase.

        Values with lower values are considered to have higher precedence and will be grouped
        together when lexing left- and right-recursive phrases. For example, the statement:

            1 + 2 * 3 - 4

        will be grouped as:

            (1 + (2 * 3)) - 4

        because multiplication has higher precedence than addition.
        """

        return self._precedence_func(self, data_items)

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _indent_token                           = IndentToken()
    _dedent_token                           = DedentToken()
    _horizontal_whitespace_token            = HorizontalWhitespaceToken()
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

        for phrase_index, phrase in enumerate(self.phrases):
            if isinstance(phrase, RecursivePlaceholderPhrase):
                self.phrases[phrase_index] = new_phrase
                replaced_phrase = True
            else:
                replaced_phrase = phrase.PopulateRecursive(self, new_phrase) or replaced_phrase

        if replaced_phrase and self._name_is_default:
            self.name = self.__class__._CreateDefaultName(self.phrases)  # type: ignore  # pylint: disable=protected-access

        return replaced_phrase

    # ----------------------------------------------------------------------
    def _LexImpl(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace_ctr: int,
        ignored_indentation_level: Optional[int],
        starting_phrase_index: int,
        single_threaded: bool,
    ) -> Optional[Phrase.LexResult]:
        working_iter = normalized_iter.Clone()

        # ----------------------------------------------------------------------
        @dataclass(frozen=True)
        class IgnoredDataInfo(object):
            data_items: List[Phrase.TokenLexResultData]
            iter_range: Phrase.NormalizedIteratorRange

        # ----------------------------------------------------------------------
        def GetIgnoredDataInfo() -> IgnoredDataInfo:
            nonlocal ignored_indentation_level
            nonlocal working_iter

            at_content_begin = working_iter.offset == 0
            eat_next_newline = False

            data_items: List[Phrase.TokenLexResultData] = []
            start_iter = working_iter.Clone()

            while not working_iter.AtEnd():
                next_token_type = working_iter.GetNextTokenType()

                if next_token_type == NormalizedIterator.TokenType.Indent:
                    if ignore_whitespace_ctr == 0 and ignored_indentation_level is None:
                        break

                    prev_iter = working_iter.Clone()

                    result = self._indent_token.Match(working_iter)
                    assert result is not None

                    data_items.append(
                        Phrase.TokenLexResultData.Create(
                            self._indent_token,
                            result,
                            Phrase.NormalizedIteratorRange.Create(prev_iter, working_iter.Clone()),
                            is_ignored=True,
                        ),
                    )

                    if ignored_indentation_level is not None:
                        ignored_indentation_level += 1

                elif next_token_type == NormalizedIterator.TokenType.Dedent:
                    if ignore_whitespace_ctr == 0 and ignored_indentation_level is None:
                        break
                    elif ignore_whitespace_ctr != 0 and ignored_indentation_level == 0:
                        break

                    prev_iter = working_iter.Clone()

                    result = self._dedent_token.Match(working_iter)
                    assert result is not None

                    data_items.append(
                        Phrase.TokenLexResultData.Create(
                            self._dedent_token,
                            result,
                            Phrase.NormalizedIteratorRange.Create(prev_iter, working_iter.Clone()),
                            is_ignored=True,
                        ),
                    )

                    if ignored_indentation_level is not None:
                        assert ignored_indentation_level
                        ignored_indentation_level -= 1

                elif next_token_type == NormalizedIterator.TokenType.WhitespacePrefix:
                    # No content to add to data_items, as this implies that the current line's
                    # indentation is at the same level as the previous line's indentation.
                    working_iter.SkipWhitespacePrefix()

                elif next_token_type == NormalizedIterator.TokenType.Content:
                    num_data_items = len(data_items)

                    prev_iter = working_iter.Clone()

                    # Are we looking at horizontal whitespace?
                    result = self._horizontal_whitespace_token.Match(working_iter)

                    if result is not None:
                        data_items.append(
                            Phrase.TokenLexResultData.Create(
                                self._horizontal_whitespace_token,
                                result,
                                Phrase.NormalizedIteratorRange.Create(prev_iter, working_iter.Clone()),
                                is_ignored=True,
                            ),
                        )

                    # Are we looking at a comment?
                    at_beginning_of_line = working_iter.offset == working_iter.line_info.content_begin

                    result = self.comment_token.Match(working_iter)

                    if result is not None:
                        data_items.append(
                            Phrase.TokenLexResultData.Create(
                                self.comment_token,
                                result,
                                Phrase.NormalizedIteratorRange.Create(prev_iter, working_iter.Clone()),
                                is_ignored=True,
                            ),
                        )

                        eat_next_newline = at_beginning_of_line

                    if len(data_items) != num_data_items:
                        continue

                    break

                elif next_token_type == NormalizedIterator.TokenType.WhitespaceSuffix:
                    prev_iter = working_iter.Clone()

                    result = self._horizontal_whitespace_token.Match(working_iter)
                    assert result is not None

                    data_items.append(
                        Phrase.TokenLexResultData.Create(
                            self._horizontal_whitespace_token,
                            result,
                            Phrase.NormalizedIteratorRange.Create(prev_iter, working_iter.Clone()),
                            is_ignored=True,
                        ),
                    )

                elif next_token_type == NormalizedIterator.TokenType.EndOfLine:
                    # Newlines are meaningful, unless they fall at the beginning of the file
                    if (
                        not eat_next_newline
                        and not at_content_begin
                        and ignore_whitespace_ctr == 0
                        and ignored_indentation_level is None
                    ):
                        break

                    prev_iter = working_iter.Clone()

                    result = self._newline_token.Match(working_iter)
                    assert result is not None

                    data_items.append(
                        Phrase.TokenLexResultData.Create(
                            self._newline_token,
                            result,
                            Phrase.NormalizedIteratorRange.Create(prev_iter, working_iter.Clone()),
                            is_ignored=True,
                        ),
                    )

                    eat_next_newline = False

                else:
                    assert False, next_token_type  # pragma: no cover

            return IgnoredDataInfo(
                data_items,
                Phrase.NormalizedIteratorRange.Create(start_iter, working_iter.Clone()),
            )

        # ----------------------------------------------------------------------

        success = False
        data_items: List[Union[Phrase.LexResultData, Phrase.TokenLexResultData]] = []
        ignored_data_info: Optional[IgnoredDataInfo] = None
        preserved_ignore_whitespace_ctr: Optional[int] = None
        prev_token_was_pop_control = False

        for phrase_index in range(starting_phrase_index, len(self.phrases)):
            phrase = self.phrases[phrase_index]

            is_control_token = isinstance(phrase, TokenPhrase) and phrase.token.is_control_token

            if ignored_data_info is None:
                ignored_data_info = GetIgnoredDataInfo()

                if working_iter.AtEnd() and not is_control_token:
                    success = False
                    break

            # Process control tokens
            if is_control_token:
                assert isinstance(phrase, TokenPhrase)

                if isinstance(phrase.token, PushIgnoreWhitespaceControlToken):
                    ignore_whitespace_ctr += 1

                elif isinstance(phrase.token, PopIgnoreWhitespaceControlToken):
                    assert ignore_whitespace_ctr != 0
                    ignore_whitespace_ctr -= 1

                elif isinstance(phrase.token, PushPreserveWhitespaceControlToken):
                    assert preserved_ignore_whitespace_ctr is None
                    preserved_ignore_whitespace_ctr = ignore_whitespace_ctr

                    ignore_whitespace_ctr = 0

                elif isinstance(phrase.token, PopPreserveWhitespaceControlToken):
                    assert preserved_ignore_whitespace_ctr is not None

                    ignore_whitespace_ctr = preserved_ignore_whitespace_ctr
                    preserved_ignore_whitespace_ctr = None

                else:
                    assert False, phrase.token  # pragma: no cover

                # If we are pushing a new value, we have to reset the ignored data items previously
                # collected as the collection criteria may change based on the control token just
                # consumed.
                prev_token_was_pop_control = phrase.token.opening_token is not None

                if not prev_token_was_pop_control and ignored_data_info is not None:
                    working_iter = ignored_data_info.iter_range.begin
                    ignored_data_info = None

                continue

            # Process other phrase types
            result = phrase.Lex(
                unique_id + ("{} [{}]".format(self.name, phrase_index),),
                working_iter.Clone(),
                observer,
                single_threaded=single_threaded,
                ignore_whitespace=ignore_whitespace_ctr != 0,
            )

            if result is None:
                return None

            if (
                result.success
                and result.iter_range.begin != result.iter_range.end
                and ignored_data_info is not None
            ):
                data_items += ignored_data_info.data_items
                ignored_data_info = None

            data_items.append(result.data)

            working_iter = result.iter_range.end.Clone()

            if not result.success:
                success = False
                break

            success = True

        if ignored_data_info is not None:
            # If the previous token as a pop, we should consider the ignored output as part of the current phrase.
            # Otherwise, we should consider the tokens as part of the next phrase.
            if prev_token_was_pop_control:
                data_items += ignored_data_info.data_items
                working_iter = ignored_data_info.iter_range.end
            else:
                working_iter = ignored_data_info.iter_range.begin

            ignored_data_info = None

        return Phrase.LexResult.Create(
            success,
            Phrase.NormalizedIteratorRange.Create(normalized_iter.Clone(), working_iter),
            Phrase.LexResultData.Create(self, unique_id, data_items, None),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateDefaultName(
        phrases: List[Phrase],
    ) -> str:
        return "[{}]".format(", ".join(phrase.name for phrase in phrases))
