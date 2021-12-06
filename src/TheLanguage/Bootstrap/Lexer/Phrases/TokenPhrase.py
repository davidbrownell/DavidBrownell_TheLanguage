# ----------------------------------------------------------------------
# |
# |  TokenPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-22 22:17:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TokenPhrase object"""

import os

from typing import List, Optional, Tuple

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Components.Phrase import Phrase

    from ..Components.Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
        Token as TokenClass,
    )


# ----------------------------------------------------------------------
class TokenPhrase(Phrase):
    """Phrase that matches against a token"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        token: TokenClass,
        name: Optional[str]=None,
    ):
        assert token

        if name is None:
            name = token.name

        assert name is not None

        super(TokenPhrase, self).__init__(
            name,
            # Token=lambda token: token.name,
        )

        self.Token                          = token

    # ----------------------------------------------------------------------
    # TODO: Caching opportunity
    @classmethod
    def ExtractPotentialCommentsOrWhitespace(
        cls,
        comment_token: RegexToken,
        normalized_iter: Phrase.NormalizedIterator,
        ignored_indentation_level: Optional[int],
        *,
        ignore_whitespace: bool,
        next_phrase_is_indent: bool,
        next_phrase_is_dedent: bool,
    ) -> Optional[
        Tuple[
            List[Phrase.TokenLexResultData],
            Phrase.NormalizedIterator,
            Optional[int],                              # Updated 'ignored_indentation_level' value
        ]
    ]:
        # Note that this should only be invoked on a phrase associated with a token that represents
        # a comment.
        data_items: List[Phrase.TokenLexResultData] = []

        while not normalized_iter.AtEnd():
            if ignore_whitespace:
                process_whitespace = True
                consume_indent = True
                consume_dedent = ignored_indentation_level != 0

            elif normalized_iter.Offset == 0:
                # If we are at the beginning of the content, consume any leading
                # newlines. We don't need to worry about a content that starts with
                # newline-comment-newline as the comment extract code will handle
                # the newline(s) that appears after the comment.
                process_whitespace = True
                consume_indent = False
                consume_dedent = False

            else:
                process_whitespace = False
                consume_indent = False
                consume_dedent = False

            if process_whitespace:
                data_item = cls.ExtractPotentialWhitespaceToken(
                    normalized_iter,
                    consume_indent=consume_indent,
                    consume_dedent=consume_dedent,
                    consume_newline=True,
                )

                if data_item is not None:
                    if ignored_indentation_level is not None:
                        if isinstance(data_item.Token, IndentToken):
                            ignored_indentation_level += 1
                        elif isinstance(data_item.Token, DedentToken):
                            assert ignored_indentation_level
                            ignored_indentation_level -= 1

                    data_items.append(data_item)
                    normalized_iter = data_item.IterEnd.Clone()

                    continue

            # Check for comments
            potential_comment_items = cls._ExtractPotentialCommentTokens(
                comment_token,
                normalized_iter,
                next_phrase_is_indent=next_phrase_is_indent,
                next_phrase_is_dedent=next_phrase_is_dedent,
            )

            if potential_comment_items is not None:
                potential_comment_items, normalized_iter = potential_comment_items

                data_items += potential_comment_items

                continue

            # If here, we didn't find anything
            break

        if not data_items:
            return None

        return (data_items, normalized_iter, ignored_indentation_level)

    # ----------------------------------------------------------------------
    # TODO: Caching opportunity
    @staticmethod
    def ExtractPotentialWhitespace(
        normalized_iter: Phrase.NormalizedIterator,
    ) -> Optional[Tuple[int, int]]:
        """Consumes any whitespace located at the current offset"""

        if normalized_iter.AtEnd():
            return None

        next_token_type = normalized_iter.GetNextTokenType()

        if next_token_type == Phrase.NormalizedIterator.TokenType.WhitespacePrefix:
            normalized_iter.SkipWhitespacePrefix()

        elif (
            next_token_type == Phrase.NormalizedIterator.TokenType.Content
            or next_token_type == Phrase.NormalizedIterator.TokenType.WhitespaceSuffix
        ):
            start = normalized_iter.Offset

            while (
                normalized_iter.Offset < normalized_iter.LineInfo.OffsetEnd
                and normalized_iter.Content[normalized_iter.Offset].isspace()
                and normalized_iter.Content[normalized_iter.Offset] != "\n"
            ):
                normalized_iter.Advance(1)

            if normalized_iter.Offset != start:
                return start, normalized_iter.Offset

        return None

    # ----------------------------------------------------------------------
    # TODO: Caching Opportunity
    @Interface.override
    async def LexAsync(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Optional[Phrase.LexResult]:

        result: Optional[TokenClass.MatchResult] = None

        observer.StartPhrase(unique_id, self)
        with CallOnExit(lambda: observer.EndPhrase(unique_id, self, result is not None)):
            # We only want to consume whitespace if there is a match that follows; collect
            # it for now, but do not modify the provided iterator.
            potential_iter = normalized_iter.Clone()
            potential_whitespace = self.__class__.ExtractPotentialWhitespace(potential_iter)
            potential_iter_begin = potential_iter.Clone()

            result = self.Token.Match(potential_iter)
            if result is None:
                # pylint: disable=too-many-function-args
                return Phrase.LexResult(
                    False,
                    Phrase.NormalizedIteratorRange(normalized_iter, normalized_iter),
                    Phrase.StandardLexResultData(self, None, None),
                )

            # pylint: disable=too-many-function-args
            data = Phrase.StandardLexResultData(
                self,
                # pylint: disable=too-many-function-args
                Phrase.TokenLexResultData(
                    self.Token,
                    potential_whitespace,
                    result,
                    Phrase.NormalizedIteratorRange(potential_iter_begin, potential_iter),
                    is_ignored=self.Token.is_always_ignored,
                ),
                unique_id,
            )

            if isinstance(self.Token, IndentToken):
                await observer.OnPushScopeAsync(data, potential_iter_begin, potential_iter)
            elif isinstance(self.Token, DedentToken):
                await observer.OnPopScopeAsync(data, potential_iter_begin, potential_iter)
            elif not await observer.OnInternalPhraseAsync(data, potential_iter_begin, potential_iter):
                return None

            # pylint: disable=too-many-function-args
            return Phrase.LexResult(
                True,
                Phrase.NormalizedIteratorRange(normalized_iter.Clone(), potential_iter),
                data,
            )

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _indent_token                           = IndentToken.Create()
    _dedent_token                           = DedentToken.Create()
    _newline_token                          = NewlineToken.Create()

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
        # Nothing downstream has changed
        return False

    # ----------------------------------------------------------------------
    # TODO: Caching opportunity
    @classmethod
    def _ExtractPotentialCommentTokens(
        cls,
        comment_token: RegexToken,
        normalized_iter: Phrase.NormalizedIterator,
        *,
        next_phrase_is_indent: bool,
        next_phrase_is_dedent: bool,
    ) -> Optional[Tuple[List[Phrase.TokenLexResultData], Phrase.NormalizedIterator]]:
        """Eats any comment (stand-along or trailing) when requested"""

        normalized_iter = normalized_iter.Clone()
        next_token_type = normalized_iter.GetNextTokenType()

        if next_token_type == Phrase.NormalizedIterator.TokenType.Indent:
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

            normalized_iter_offset = normalized_iter.Offset
            normalized_iter.SkipWhitespacePrefix()

            assert normalized_iter.Offset > normalized_iter_offset
            potential_whitespace = (normalized_iter_offset, normalized_iter.Offset)

        elif next_token_type == Phrase.NormalizedIterator.TokenType.WhitespacePrefix:
            at_beginning_of_line = True

            normalized_iter.SkipWhitespacePrefix()
            potential_whitespace = None

        else:
            at_beginning_of_line = (
                normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart
                or normalized_iter.Offset == normalized_iter.LineInfo.ContentStart
            )

            potential_whitespace = cls.ExtractPotentialWhitespace(normalized_iter)

        normalized_iter_begin = normalized_iter.Clone()

        result = comment_token.Match(normalized_iter)
        if result is None:
            return None

        results = [
            # pylint: disable=too-many-function-args
            Phrase.TokenLexResultData(
                comment_token,
                potential_whitespace,
                result,
                Phrase.NormalizedIteratorRange(normalized_iter_begin, normalized_iter),
                is_ignored=True,
            ),
        ]

        if at_beginning_of_line:
            # Add additional content to consume the entire line...

            # Capture the trailing newline
            result = cls.ExtractPotentialWhitespaceToken(
                results[-1].IterEnd,
                consume_indent=False,
                consume_dedent=False,
                consume_newline=True,
            )
            assert result

            results.append(result)

            # Consume potential dedents, but don't return it with the results (as we absorbed the
            # corresponding indent above when we skipped the prefix). We need to do this as every
            # dedent must have a matching indent token.
            if (
                results[0].Whitespace is not None
                and results[-1].IterEnd.GetNextTokenType() == Phrase.NormalizedIterator.TokenType.Dedent
                and not next_phrase_is_dedent
            ):
                result = cls.ExtractPotentialWhitespaceToken(
                    results[-1].IterEnd,
                    consume_indent=False,
                    consume_dedent=True,
                    consume_newline=False,
                )
                assert result

                # Even though we aren't sending the dedent token, we need to make sure that the returned
                # iterator is updated to the new position. Comments are special beasts.
                return (results, result.IterEnd)

        return (results, results[-1].IterEnd)

    # ----------------------------------------------------------------------
    # TODO: Caching opportunity
    @classmethod
    def ExtractPotentialWhitespaceToken(
        cls,
        normalized_iter: Phrase.NormalizedIterator,
        *,
        consume_indent: bool,
        consume_dedent: bool,
        consume_newline: bool,
    ) -> Optional[Phrase.TokenLexResultData]:
        """Eats any whitespace token when requested"""

        next_token_type = normalized_iter.GetNextTokenType()

        if next_token_type == Phrase.NormalizedIterator.TokenType.Indent:
            if not consume_indent:
                return None

            normalized_iter_begin = normalized_iter.Clone()

            result = cls._indent_token.Match(normalized_iter)
            assert result

            # pylint: disable=too-many-function-args
            return Phrase.TokenLexResultData(
                cls._indent_token,
                None,
                result,
                Phrase.NormalizedIteratorRange(normalized_iter_begin, normalized_iter),
                is_ignored=True,
            )

        elif next_token_type == Phrase.NormalizedIterator.TokenType.Dedent:
            if not consume_dedent:
                return None

            normalized_iter_begin = normalized_iter.Clone()

            result = cls._dedent_token.Match(normalized_iter)
            assert result

            # pylint: disable=too-many-function-args
            return Phrase.TokenLexResultData(
                cls._dedent_token,
                None,
                result,
                Phrase.NormalizedIteratorRange(normalized_iter_begin, normalized_iter),
                is_ignored=True,
            )

        # Consume potential newlines
        if consume_newline:
            normalized_iter = normalized_iter.Clone()
            normalized_iter_begin = normalized_iter.Clone()

            if next_token_type == Phrase.NormalizedIterator.TokenType.EndOfLine:
                potential_whitespace = None
            else:
                potential_whitespace = cls.ExtractPotentialWhitespace(normalized_iter)

            if normalized_iter.GetNextTokenType() == Phrase.NormalizedIterator.TokenType.EndOfLine:
                result = cls._newline_token.Match(normalized_iter)
                assert result

                # pylint: disable=too-many-function-args
                return Phrase.TokenLexResultData(
                    cls._newline_token,
                    potential_whitespace,
                    result,
                    Phrase.NormalizedIteratorRange(normalized_iter_begin, normalized_iter),
                    is_ignored=True,
                )

        return None
