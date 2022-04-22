# ----------------------------------------------------------------------
# |
# |  Tokens.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-02 10:55:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains building blocks for token processing"""

import os

from typing import List, Optional, Match, Pattern, Type

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Normalize import (
        GetNumMultilineTokenDelimiters,
        multiline_token_delimiter_length,
        OffsetRange,
    )

    from .NormalizedIterator import NormalizedIterator


# ----------------------------------------------------------------------
class Token(Interface.Interface, ObjectReprImplBase):
    """Base class for various `Token` objects"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class MatchResult(ObjectReprImplBase):  # type: ignore
        pass

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    # A Control Token is a token that doesn't consume content, but modifies
    # behavior of a statement. This concept is necessary because we are combining
    # the lexing and parsing passes into 1 pass.
    is_control_token                        = False

    # True if the token should always be ignored (good for comments)
    is_always_ignored                       = False

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
    ):
        super(Token, self).__init__()

        self.name                           = name

    # ----------------------------------------------------------------------
    def __eq__(self, other) -> bool:
        if self.__dict__ != other.__dict__:
            return False

        return self.__class__ == other.__class__

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Match(
        normalized_iter: NormalizedIterator
    ) -> Optional["MatchResult"]:
        """Returns match information if a match was found for the iterator in its current position"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
class NewlineToken(Token):
    """Token that matches 1 or more newlines"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class MatchResult(Token.MatchResult):
        range: OffsetRange

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(NewlineToken.MatchResult, self).__init__()

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        capture_many=True,
        is_always_ignored=False,
    ):
        super(NewlineToken, self).__init__("Newline{}".format("+" if capture_many else ""))

        self.capture_many                   = capture_many
        self.is_always_ignored              = is_always_ignored

    # ----------------------------------------------------------------------
    @Interface.override
    def Match(
        self,
        normalized_iter: NormalizedIterator,
    ) -> Optional[Token.MatchResult]:
        if normalized_iter.GetNextTokenType() != NormalizedIterator.TokenType.EndOfLine:
            return None

        newline_start = normalized_iter.offset

        normalized_iter.Advance(1)

        if self.capture_many:
            while normalized_iter.IsBlankLine():
                normalized_iter.SkipLine()

        return NewlineToken.MatchResult(OffsetRange.Create(newline_start, normalized_iter.offset))


# ----------------------------------------------------------------------
class IndentToken(Token):
    """Token that matches indentations of arbitrary length"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class MatchResult(Token.MatchResult):
        range: OffsetRange
        indent_value: int

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert self.indent_value >= 0

            super(IndentToken.MatchResult, self).__init__()

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(IndentToken, self).__init__("Indent")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Match(
        normalized_iter: NormalizedIterator,
    ) -> Optional[Token.MatchResult]:
        if normalized_iter.GetNextTokenType() != NormalizedIterator.TokenType.Indent:
            return None

        normalized_iter.SkipWhitespacePrefix()

        assert normalized_iter.line_info.new_indent_value is not None

        return IndentToken.MatchResult(
            OffsetRange.Create(
                normalized_iter.line_info.offset_begin,
                normalized_iter.line_info.content_begin,
            ),
            normalized_iter.line_info.new_indent_value,
        )


# ----------------------------------------------------------------------
class DedentToken(Token):
    """Token that matches a single dedent"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class MatchResult(Token.MatchResult):
        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(DedentToken.MatchResult, self).__init__()

    # ----------------------------------------------------------------------
    # |
    # |  Public methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(DedentToken, self).__init__("Dedent")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Match(
        normalized_iter: NormalizedIterator,
    ) -> Optional[Token.MatchResult]:
        if normalized_iter.GetNextTokenType() != NormalizedIterator.TokenType.Dedent:
            return None

        normalized_iter.ConsumeDedent()

        if normalized_iter.GetNextTokenType() == NormalizedIterator.TokenType.WhitespacePrefix:
            normalized_iter.SkipWhitespacePrefix()

        return DedentToken.MatchResult()


# ----------------------------------------------------------------------
class HorizontalWhitespaceToken(Token):
    """Matches horizontal whitespace"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class MatchResult(Token.MatchResult):
        range: OffsetRange

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(HorizontalWhitespaceToken.MatchResult, self).__init__()

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(HorizontalWhitespaceToken, self).__init__("HorizontalWhitespace")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Match(
        normalized_iter: NormalizedIterator,
    ) -> Optional[Token.MatchResult]:
        next_token_type = normalized_iter.GetNextTokenType()

        if next_token_type not in [
            NormalizedIterator.TokenType.Content,
            NormalizedIterator.TokenType.WhitespaceSuffix,
        ]:
            return None

        if next_token_type == NormalizedIterator.TokenType.Content:
            whitespace_range = normalized_iter.GetNextWhitespaceRange()

            if whitespace_range is None or normalized_iter.offset != whitespace_range.begin:
                return None

            normalized_iter.Advance(whitespace_range.end - whitespace_range.begin)

            return HorizontalWhitespaceToken.MatchResult(whitespace_range)

        elif next_token_type == NormalizedIterator.TokenType.WhitespaceSuffix:
            normalized_iter.SkipWhitespaceSuffix()

            line_info = normalized_iter.line_info

            return HorizontalWhitespaceToken.MatchResult(OffsetRange.Create(line_info.content_end, line_info.offset_end))

        else:
            assert False, next_token_type  # pragma: no cover


# ----------------------------------------------------------------------
class RegexToken(Token):
    """Token that matches content based on a regular expression"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class MatchResult(Token.MatchResult):
        match: Match

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(RegexToken.MatchResult, self).__init__()

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        regex: Pattern,
        is_multiline=False,
        is_always_ignored=False,
        exclude_matches: Optional[List[str]]=None,
    ):
        assert name

        super(RegexToken, self).__init__(name)

        if is_multiline:
            pattern = regex.pattern.replace("\\", "")
            pattern_len = len(pattern)

            # Note that these checks are only checking that there is an opening
            # and closing token, but not that the entirety of the tokens are valid
            # (for example, the invalid token "<<<!!" would not be detected).
            # Take special care when working with multiline RegexTokens.

            # Check the opening token
            assert GetNumMultilineTokenDelimiters(
                pattern,
                begin_index=0,
                end_index=min(pattern_len, multiline_token_delimiter_length),
            ) == 1, (pattern, "The opening token must be a multiline phrase token")

            # Check the closing token
            assert GetNumMultilineTokenDelimiters(
                pattern,
                begin_index=max(0, pattern_len - multiline_token_delimiter_length),
                end_index=pattern_len,
            ) == 1, (pattern, "The closing token must be a multiline phrase token")

        self.regex                          = regex
        self.is_multiline                   = is_multiline
        self.is_always_ignored              = is_always_ignored

        if not exclude_matches:
            is_excluded_func = lambda match: False
        else:
            exclude_matches_set = set(exclude_matches)

            is_excluded_func = lambda match: match.group() in exclude_matches_set

        self._is_excluded_func              = is_excluded_func

    # ----------------------------------------------------------------------
    @Interface.override
    def Match(
        self,
        normalized_iter: NormalizedIterator,
    ) -> Optional[Token.MatchResult]:
        if normalized_iter.GetNextTokenType() != NormalizedIterator.TokenType.Content:
            return None

        match = self.regex.match(
            normalized_iter.content,
            pos=normalized_iter.offset,
            endpos=normalized_iter.content_length,
        )

        if match and not self._is_excluded_func(match):
            match_length = match.end() - match.start()

            if self.is_multiline:
                self._AdvanceMultiline(normalized_iter, match_length)
            else:
                normalized_iter.Advance(match_length)

            return RegexToken.MatchResult(match)

        return None

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _AdvanceMultiline(
        normalized_iter: NormalizedIterator,
        delta: int,
    ) -> None:
        # The match may span multiple lines, so we have to be intentional about how we advance
        while delta:
            while normalized_iter.GetNextTokenType() == NormalizedIterator.TokenType.Dedent:
                normalized_iter.ConsumeDedent()

            this_delta = min(delta, normalized_iter.line_info.offset_end - normalized_iter.offset)

            # The amount to advance can be 0 if we are looking at a blank line
            if this_delta != 0:
                normalized_iter.Advance(this_delta)
                delta -= this_delta

            # Skip the newline (if necessary)
            if delta:
                normalized_iter.Advance(1)
                delta -= 1


# ----------------------------------------------------------------------
class ControlTokenBase(Token):
    """Base class for Control tokens. See the definition of `is_control_token` in the base class for more info"""

    is_control_token                        = True

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        closing_token: Optional[Type["ControlTokenBase"]]=None,
        opening_token: Optional[Type["ControlTokenBase"]]=None,
    ):
        super(ControlTokenBase, self).__init__(name)

        # Some control tokens must be paired with other control tokens
        # when they are used (do/undo, push/pop, etc). Set this value
        # if necessary.
        self.closing_token                  = closing_token
        self.opening_token                  = opening_token

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Match(
        normalized_iter: NormalizedIterator,
    ) -> Optional[Token.MatchResult]:
        raise Exception("This method should never be invoked for control tokens")


# ----------------------------------------------------------------------
class PushIgnoreWhitespaceControlToken(ControlTokenBase):
    """\
    Signals that newline, indent, and dedent whitespace should be ignored.

    Note that the tokens themselves will still be captured, they just won't
    participate in matching logic. This token must always be paired with a
    corresponding `PopIgnoreWhitespaceControlToken` to restore meaningful
    whitespace matching.
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PushIgnoreWhitespaceControlToken, self).__init__(
            "PushIgnoreWhitespaceControlToken",
            closing_token=PopIgnoreWhitespaceControlToken,
        )


# ----------------------------------------------------------------------
class PopIgnoreWhitespaceControlToken(ControlTokenBase):
    """\
    Restores whitespace processing.

    See `PushIgnoreWhitespaceControlToken` for more information.
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PopIgnoreWhitespaceControlToken, self).__init__(
            "PopIgnoreWhitespaceControlToken",
            opening_token=PushIgnoreWhitespaceControlToken,
        )


# ----------------------------------------------------------------------
class PushPreserveWhitespaceControlToken(ControlTokenBase):
    """\
    Signals that newline, indent, and dedent whitespace should be preserved.
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PushPreserveWhitespaceControlToken, self).__init__(
            "PushPreserveWhitespaceControlToken",
            closing_token=PopPreserveWhitespaceControlToken,
        )


# ----------------------------------------------------------------------
class PopPreserveWhitespaceControlToken(ControlTokenBase):
    """\
    Restores whitespace processing to what it was prior to `PushPreserveWhitespaceControlToken`'s
    invocation.

    See `PushPreserveWhitespaceControlToken` for more information.
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PopPreserveWhitespaceControlToken, self).__init__(
            "PopPreserveWhitespaceControlToken",
            opening_token=PushPreserveWhitespaceControlToken,
        )
