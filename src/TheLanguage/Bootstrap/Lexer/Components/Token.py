# ----------------------------------------------------------------------
# |
# |  Token.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-22 16:49:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains building blocks for token processing"""

import os

from typing import Any, Callable, Match as TypingMatch, Optional, Pattern as TypingPattern


from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

the_language_output_dir = os.getenv("THE_LANGUAGE_OUTPUT_DIR")
if the_language_output_dir is not None:
    import sys
    sys.path.insert(0, the_language_output_dir)
    from Lexer_TheLanguage.Components_TheLanguage.Token_TheLanguage import *
    sys.path.pop(0)

    USE_THE_LANGUAGE_GENERATED_CODE = True
else:
    USE_THE_LANGUAGE_GENERATED_CODE = False

    with InitRelativeImports():
        from .Normalize import GetNumMultilineTokenDelimiters, multiline_token_delimiter_length as MULTILINE_TOKEN_DELIMITER_ITEM_LENGTH
        from .NormalizedIterator import NormalizedIterator


    # ----------------------------------------------------------------------
    class Token(Interface.Interface, YamlRepr.ObjectReprImplBase):
        """Base class for various Token objects"""

        # ----------------------------------------------------------------------
        # |
        # |  Public Types
        # |
        # ----------------------------------------------------------------------
        @dataclass(frozen=True, repr=False)
        class MatchResult(YamlRepr.ObjectReprImplBase):
            # ----------------------------------------------------------------------
            def __post_init__(
                self,
                **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
            ):
                YamlRepr.ObjectReprImplBase.__init__(self, **custom_display_funcs)

        # ----------------------------------------------------------------------
        # |
        # |  Public Data
        # |
        # ----------------------------------------------------------------------
        # A Control Token is a token that doesn't consume content, but modifies
        # behavior of a statement. This concept is necessary because we are combining
        # the lexing and parsing passes into 1 pass.
        is_control_token                          = False

        # True if the token should always be ignored (good for comments)
        IsAlwaysIgnored                         = False

        # ----------------------------------------------------------------------
        # |
        # |  Public Methods
        # |
        # ----------------------------------------------------------------------
        def __eq__(self, other):
            if self.__dict__ != other.__dict__:
                return False

            return self.__class__ == other.__class__

        # ----------------------------------------------------------------------
        @Interface.abstractproperty
        def Name(self):
            """Name of the token"""
            raise Exception("Abstract property")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def Match(
            normalized_iter: NormalizedIterator,
        ) -> Optional["MatchResult"]:
            """Returns match information if a match was found for the iterator in its current position"""
            raise Exception("Abstract method")  # pragma: no cover


    # ----------------------------------------------------------------------
    class NewlineToken(Token):
        """Token that matches 1 or more newline"""

        # ----------------------------------------------------------------------
        # |
        # |  Public Types
        # |
        # ----------------------------------------------------------------------
        @dataclass(frozen=True, repr=False)
        class MatchResult(Token.MatchResult):
            Start: int
            End: int

            # ----------------------------------------------------------------------
            def __post_init__(self):
                assert self.Start >= 0, self
                assert self.End > self.Start, self

                super(NewlineToken.MatchResult, self).__post_init__()

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
            super(NewlineToken, self).__init__()

            self._name                          = "Newline{}".format("+" if capture_many else "")
            self.CaptureMany                    = capture_many
            self.IsAlwaysIgnored                = is_always_ignored

        # ----------------------------------------------------------------------
        @property
        @Interface.override
        def Name(self):
            return self._name

        # ----------------------------------------------------------------------
        @Interface.override
        def Match(
            self,
            normalized_iter: NormalizedIterator,
        ) -> Optional[Token.MatchResult]:
            if normalized_iter.GetNextTokenType() != NormalizedIterator.TokenType.EndOfLine:
                return None

            newline_start = normalized_iter.Offset

            normalized_iter.Advance(1)

            if self.CaptureMany:
                while normalized_iter.IsBlankLine():
                    normalized_iter.SkipLine()

            return NewlineToken.MatchResult(newline_start, normalized_iter.Offset)


    # ----------------------------------------------------------------------
    @Interface.staticderived
    class IndentToken(Token):
        """Token that matches indentations of arbitrary length"""

        # ----------------------------------------------------------------------
        # |
        # |  Public Types
        # |
        # ----------------------------------------------------------------------
        @dataclass(frozen=True, repr=False)
        class MatchResult(Token.MatchResult):
            Start: int
            End: int
            Value: int

            # ----------------------------------------------------------------------
            def __post_init__(self):
                assert self.Start >= 0, self
                assert self.End > self.Start, self
                assert self.Value >= 0, self

                super(IndentToken.MatchResult, self).__post_init__()

        # ----------------------------------------------------------------------
        # |
        # |  Public Data
        # |
        # ----------------------------------------------------------------------
        Name                                    = Interface.DerivedProperty("Indent")  # type: ignore

        # ----------------------------------------------------------------------
        # |
        # |  Public Methods
        # |
        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        def Match(
            normalized_iter: NormalizedIterator,
        ) -> Optional[Token.MatchResult]:
            if normalized_iter.GetNextTokenType() != NormalizedIterator.TokenType.Indent:
                return None

            normalized_iter.SkipWhitespacePrefix()

            assert normalized_iter.LineInfo.NewIndentationValue is not None

            return IndentToken.MatchResult(
                normalized_iter.LineInfo.OffsetStart,
                normalized_iter.LineInfo.ContentStart,
                normalized_iter.LineInfo.NewIndentationValue,
            )


    # ----------------------------------------------------------------------
    @Interface.staticderived
    class DedentToken(Token):
        """Token that matches a single dedent"""

        # ----------------------------------------------------------------------
        # |
        # |  Public Types
        # |
        # ----------------------------------------------------------------------
        @dataclass(frozen=True, repr=False)
        class MatchResult(Token.MatchResult):
            pass

        # ----------------------------------------------------------------------
        # |
        # |  Public Data
        # |
        # ----------------------------------------------------------------------
        Name                                    = Interface.DerivedProperty("Dedent")  # type: ignore

        # ----------------------------------------------------------------------
        # |
        # |  Public Methods
        # |
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
    class RegexToken(Token):
        """Token that matches content based on a regular expression"""

        # ----------------------------------------------------------------------
        # |
        # |  Public Types
        # |
        # ----------------------------------------------------------------------
        @dataclass(frozen=True, repr=False)
        class MatchResult(Token.MatchResult):
            Match: TypingMatch

        # ----------------------------------------------------------------------
        # |
        # |  Public Methods
        # |
        # ----------------------------------------------------------------------
        def __init__(
            self,
            name: str,
            regex: TypingPattern,
            is_multiline=False,
            is_always_ignored=False,
        ):
            super(RegexToken, self).__init__()

            assert name

            # Validate the regular expression
            pattern = regex.pattern.replace("\\", "")
            pattern_len = len(pattern)

            if is_multiline:
                # Note that these checks are only checking that there is an opening
                # and closing token, but not that the entirety of the tokens are valid
                # (for example, the invalid token "<<<!!" would not be detected).
                # Take special care when working with multiline RegexTokens.

                # Check the opening token
                assert GetNumMultilineTokenDelimiters(
                    pattern,
                    start_index=0,
                    end_index=min(pattern_len, MULTILINE_TOKEN_DELIMITER_ITEM_LENGTH),
                ) == 1, (pattern, "The opening token must be a multiline phrase token")

                # Check the closing token
                assert GetNumMultilineTokenDelimiters(
                    pattern,
                    start_index=max(0, pattern_len - MULTILINE_TOKEN_DELIMITER_ITEM_LENGTH),
                    end_index=pattern_len,
                ) == 1, (pattern, "The closing token must be a multiline phrase token")

            # else:
            #     assert GetNumMultilineTokenDelimiters(
            #         pattern,
            #         start_index=0,
            #         end_index=pattern_len,
            #     ) == 0, (pattern, "The regex must not match a multiline phrase token")

            # Commit the data
            self._name                          = name

            self.Regex                          = regex
            self.IsMultiline                    = is_multiline
            self.IsAlwaysIgnored                = is_always_ignored

        # ----------------------------------------------------------------------
        @property
        @Interface.override
        def Name(self):
            return self._name

        # ----------------------------------------------------------------------
        @Interface.override
        def Match(
            self,
            normalized_iter: NormalizedIterator,
        ) -> Optional[Token.MatchResult]:
            if normalized_iter.GetNextTokenType() != NormalizedIterator.TokenType.Content:
                return None

            match = self.Regex.match(
                normalized_iter.Content,
                pos=normalized_iter.Offset,
                endpos=normalized_iter.ContentLength if self.IsMultiline else normalized_iter.LineInfo.ContentEnd,
            )

            if match:
                match_length = match.end() - match.start()

                if self.IsMultiline:
                    _AdvanceMultiline(normalized_iter, match_length)
                else:
                    normalized_iter.Advance(match_length)

                return RegexToken.MatchResult(match)

            return None


    # ----------------------------------------------------------------------
    class ControlTokenBase(Token):
        """Base class for Control tokens. See the definition of `is_control_token` in the base class for more info"""

        is_control_token                          = True

        # Some control tokens must be paired with other control tokens
        # when they are used (do/undo, push/pop, etc). Set this value
        # if necessary.
        ClosingToken: Optional["ControlTokenBase"]          = None
        OpeningToken: Optional["ControlTokenBase"]          = None

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        def Match(
            normalized_iter: NormalizedIterator,
        ) -> Optional[Token.MatchResult]:
            raise Exception("This method should never be invoked for control tokens")


    # ----------------------------------------------------------------------
    @Interface.staticderived
    class PushIgnoreWhitespaceControlToken(ControlTokenBase):
        """\
        Signals that newline, indent, and dedent whitespace should be ignored.

        Note that the tokens themselves will still be captured, they just won't
        participate in matching logic. This token must always be paired with a
        corresponding `PopIgnoreWhitespaceControlToken` to restore meaningful
        whitespace matching.
        """

        Name                                    = Interface.DerivedProperty("PushIgnoreWhitespaceControl")  # type: ignore
        ClosingToken                            = "PopIgnoreWhitespaceControlToken"   # type: ignore # Set below


    # ----------------------------------------------------------------------
    @Interface.staticderived
    class PopIgnoreWhitespaceControlToken(ControlTokenBase):
        """\
        Restores whitespace processing.

        See `PushIgnoreWhitespaceControlToken` for more information.
        """

        Name                                    = Interface.DerivedProperty("PopIgnoreWhitespaceControl")  # type: ignore
        OpeningToken                            = PushIgnoreWhitespaceControlToken  # type: ignore


    PushIgnoreWhitespaceControlToken.ClosingToken           = PopIgnoreWhitespaceControlToken  # type: ignore


    # ----------------------------------------------------------------------
    @Interface.staticderived
    class PushPreserveWhitespaceControlToken(ControlTokenBase):
        """\
        Signals that newline, indent, and dedent whitespace should be preserved.
        """

        Name                                    = Interface.DerivedProperty("PushPreserveWhitespaceControlToken")  # type: ignore
        ClosingToken                            = "PopIgnoreWhitespaceControlToken"  # type: ignore # Set below


    # ----------------------------------------------------------------------
    @Interface.staticderived
    class PopPreserveWhitespaceControlToken(ControlTokenBase):
        """\
        Restores whitespace processing to what it was prior to `PushPreserveWhitespaceControlToken`
        begin invoked.

        See `PushPreserveWhitespaceControlToken` for more information.
        """

        Name                                    = Interface.DerivedProperty("PopPreserveWhitespaceControlToken")  # type: ignore
        OpeningToken                            = PushPreserveWhitespaceControlToken  # type: ignore


    PushPreserveWhitespaceControlToken.ClosingToken         = PopPreserveWhitespaceControlToken  # type: ignore


    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _AdvanceMultiline(
        normalized_iter: NormalizedIterator,
        delta: int,
    ):
        # The match may span multiple lines, so we have to be intentional about how we advance
        while delta:
            while normalized_iter.GetNextTokenType() == NormalizedIterator.TokenType.Dedent:
                normalized_iter.ConsumeDedent()

            this_delta = min(delta, normalized_iter.LineInfo.OffsetEnd - normalized_iter.Offset)

            # The amount to advance can be 0 if we are looking at a blank line
            if this_delta != 0:
                normalized_iter.Advance(this_delta)
                delta -= this_delta

            # Skip the newline (if necessary)
            if delta:
                normalized_iter.Advance(1)
                delta -= 1
