# ----------------------------------------------------------------------
# |
# |  Token.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-07 23:51:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the building blocks for token processing"""

import os

from typing import cast, Match as TypingMatch, Optional, Pattern

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
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
        pass

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    # A Control Token is a token that doesn't consume content, but modifies
    # behavior of a statement. This concept is necessary because we are combining
    # the lexing and parsing passes into 1 pass.
    IsControlToken                          = False

    # True if the token should always be ignored (good for comments)
    IsAlwaysIgnored                         = False

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __hash__(self):
        return tuple(self.__dict__.values()).__hash__()

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
        """Returns match information if applicable to the iterator at its current position"""
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
        # ----------------------------------------------------------------------
        Start: int
        End: int

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert self.Start >= 0, self
            assert self.End > self.Start, self

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
    ) -> Optional["MatchResult"]:
        if (
            not normalized_iter.AtEnd()
            and normalized_iter.Offset == normalized_iter.LineInfo.OffsetEnd
            and normalized_iter.HasConsumedAllDedents()
        ):
            newline_start = normalized_iter.Offset

            normalized_iter.Advance(0 if normalized_iter.AtTrailingDedents() else 1)

            if self.CaptureMany:
                while normalized_iter.IsBlankLine():
                    normalized_iter.SkipLine()

            return NewlineToken.MatchResult(newline_start, normalized_iter.Offset)

        return None


# ----------------------------------------------------------------------
@Interface.staticderived
class IndentToken(Token):
    """Token that matches indentations"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class MatchResult(Token.MatchResult):
        # ----------------------------------------------------------------------
        Start: int
        End: int
        Value: int

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert self.Start >= 0, self
            assert self.End > self.Start, self
            assert self.Value >= 0, self

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    Name                                    = Interface.DerivedProperty("Indent")

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Match(
        normalized_iter: NormalizedIterator,
    ) -> Optional["MatchResult"]:
        if normalized_iter.AtEnd():
            return None

        if (
            not normalized_iter.AtEnd()
            and normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart
            and normalized_iter.LineInfo.HasNewIndent()
        ):
            normalized_iter.SkipPrefix()

            return IndentToken.MatchResult(
                normalized_iter.LineInfo.OffsetStart,
                normalized_iter.LineInfo.PosStart,
                cast(int, normalized_iter.LineInfo.IndentationValue()),
            )

        return None


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
    Name                                    = Interface.DerivedProperty("Dedent")

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Match(
        normalized_iter: NormalizedIterator,
    ) -> Optional["MatchResult"]:
        if (
            not normalized_iter.AtEnd()
            and normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart
            and not normalized_iter.HasConsumedAllDedents()
        ):
            normalized_iter.ConsumeDedent()

            if normalized_iter.HasConsumedAllDedents():
                normalized_iter.SkipPrefix()

                if normalized_iter.AtTrailingDedents():
                    normalized_iter.Advance(0)

            return DedentToken.MatchResult()

        return None


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
        # ----------------------------------------------------------------------
        Match: TypingMatch

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
    ):
        super(RegexToken, self).__init__()

        assert name

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
    ) -> Optional["MatchResult"]:
        if normalized_iter.AtEnd() or not normalized_iter.HasConsumedAllDedents():
            return None

        match = self.Regex.match(
            normalized_iter.Content,
            pos=normalized_iter.Offset,
            endpos=normalized_iter.ContentLen if self.IsMultiline else normalized_iter.LineInfo.PosEnd,
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
    """Base class for Control tokens. See the definition of `IsControlToken` in the base class for more info"""

    IsControlToken                          = True

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

    Name                                    = Interface.DerivedProperty("PushIgnoreWhitespaceControl")
    ClosingToken                            = "PopIgnoreWhitespaceControlToken" # Set below


# ----------------------------------------------------------------------
@Interface.staticderived
class PopIgnoreWhitespaceControlToken(ControlTokenBase):
    """\
    Restores whitespace processing.

    See `PushIgnoreWhitespaceControlToken` for more information.
    """

    Name                                    = Interface.DerivedProperty("PopIgnoreWhitespaceControl")
    OpeningToken                            = PushIgnoreWhitespaceControlToken


PushIgnoreWhitespaceControlToken.ClosingToken           = PopIgnoreWhitespaceControlToken  # type: ignore


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _AdvanceMultiline(
    normalized_iter: NormalizedIterator,
    delta: int,
):
    # The match may span multiple lines, so we have to be intentional about how we advance
    while delta:
        this_delta = min(delta, normalized_iter.LineInfo.PosEnd - normalized_iter.Offset)

        # The amount to advance can be 0 if we are looking at a blank line
        if this_delta:
            normalized_iter.Advance(this_delta)
            delta -= this_delta

        # Skip the newline (if necessary)
        if delta:
            normalized_iter.Advance(1)
            delta -= 1
