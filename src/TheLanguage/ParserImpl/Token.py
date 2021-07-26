# ----------------------------------------------------------------------
# |
# |  Token.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-09 22:46:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains various token objects"""

import os
import re

from typing import (
    Match as TypingMatch,
    Optional,
    Pattern,
    Union,
)

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NormalizedIterator import NormalizedIterator

# ----------------------------------------------------------------------
class Token(Interface.Interface):
    """Base class for various Token types"""

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class NewlineMatch(object):
        Start: int
        End: int

        # ----------------------------------------------------------------------
        def __str__(self):
            return "{}, {}".format(self.Start, self.End)

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class IndentMatch(object):
        Start: int
        End: int
        Value: int

        # ----------------------------------------------------------------------
        def __str__(self):
            return "{}, {}, ({})".format(self.Start, self.End, self.Value)

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class DedentMatch(object):
        # ----------------------------------------------------------------------
        def __str__(self):
            return ""

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class RegexMatch(object):
        Match: TypingMatch

        # ----------------------------------------------------------------------
        def __str__(self):
            return "Regex: {}".format(str(self.Match))

    # ----------------------------------------------------------------------
    MatchType                               = Union[
        NewlineMatch,
        IndentMatch,
        DedentMatch,
        RegexMatch,
    ]

    # ----------------------------------------------------------------------
    # A Control Token is a token that doesn't consume content, but modifies
    # behavior of a statement. This concept is necessary because we are combining
    # the lexing and parsing passes into 1 pass.
    IsControlToken                          = False

    # True if the token should always be ignored (good for comments)
    IsAlwaysIgnored                         = False

    # ----------------------------------------------------------------------
    def __hash__(self):
        return tuple(self.__dict__.values()).__hash__()

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
    ) -> Optional["MatchType"]:
        """Returns match information if applicable"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    def __eq__(self, other):
        if self.__dict__ != other.__dict__:
            return False

        return self.__class__ == other.__class__


# ----------------------------------------------------------------------
class NewlineToken(Token):
    """Token that matches 1 or more newlines (depending on `capture_many`)"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        capture_many=True,
        is_always_ignored=False,
    ):
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
    def Match(self, normalized_iter):
        if (
            normalized_iter.Offset == normalized_iter.LineInfo.OffsetEnd
            and normalized_iter.HasConsumedAllDedents()
            and not normalized_iter.AtEnd()
        ):
            newline_start = normalized_iter.Offset

            normalized_iter.Advance(0 if normalized_iter.AtTrailingDedents() else 1)

            if self.CaptureMany:
                while normalized_iter.IsBlankLine():
                    normalized_iter.SkipLine()

            return Token.NewlineMatch(
                newline_start,
                normalized_iter.Offset,
            )

        return None


# ----------------------------------------------------------------------
@Interface.staticderived
class IndentToken(Token):
    """Token that matches indentations"""

    Name                                    = Interface.DerivedProperty("Indent")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Match(normalized_iter):
        if normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart and normalized_iter.LineInfo.HasNewIndent():
            normalized_iter.SkipPrefix()

            return Token.IndentMatch(
                normalized_iter.LineInfo.OffsetStart,
                normalized_iter.LineInfo.StartPos,
                normalized_iter.LineInfo.IndentationValue(),
            )

        return None


# ----------------------------------------------------------------------
@Interface.staticderived
class DedentToken(Token):
    """Token that matches dedents"""

    Name                                    = Interface.DerivedProperty("Dedent")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Match(normalized_iter):
        if (
            normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart
            and not normalized_iter.HasConsumedAllDedents()
        ):
            normalized_iter.ConsumeDedent()

            if normalized_iter.HasConsumedAllDedents():
                normalized_iter.SkipPrefix()

                if normalized_iter.AtTrailingDedents():
                    normalized_iter.Advance(0)

            return Token.DedentMatch()

        return None


# ----------------------------------------------------------------------
class RegexToken(Token):
    """Token that matches content based on the provided regular expression"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        regex: Pattern,
        is_multiline: Optional[bool]=False,
        is_always_ignored: Optional[bool]=False,
    ):
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
    def Match(self, normalized_iter):
        if not normalized_iter.HasConsumedAllDedents():
            return None

        match = self.Regex.match(
            normalized_iter.Content,
            pos=normalized_iter.Offset,
            endpos=normalized_iter.ContentLen if self.IsMultiline else normalized_iter.LineInfo.EndPos,
        )

        if match:
            match_length = match.end() - match.start()

            if self.IsMultiline:
                _AdvanceMultiline(normalized_iter, match_length)
            else:
                normalized_iter.Advance(match_length)

            return Token.RegexMatch(match)

        return None


# ----------------------------------------------------------------------
class MultilineRegexToken(Token):
    """Matches lines until a regex delimiter is encountered"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        *regex_delimiters: Pattern,
        regex_match_group_name="value",
    ):
        assert name
        assert regex_delimiters

        self._name                          = name
        self._match_all_regex               = re.compile(r"(?P<{}>.+)".format(regex_match_group_name), re.DOTALL | re.MULTILINE)

        self.RegexDelimiters                = list(regex_delimiters)

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def Name(self):
        return self._name

    # ----------------------------------------------------------------------
    @Interface.override
    def Match(self, normalized_iter):
        matches = []

        for regex in self.RegexDelimiters:
            match = regex.search(
                normalized_iter.Content,
                pos=normalized_iter.Offset,
                endpos=normalized_iter.ContentLen,
            )

            if not match:
                continue

            match = self._match_all_regex.match(
                normalized_iter.Content,
                pos=normalized_iter.Offset,
                endpos=match.start(),
            )
            assert match

            matches.append(match)

        if matches:
            if len(matches) == 1:
                shortest_match = matches[0]
            else:
                # Find the shortest match
                shortest_match = None
                shortest_match_length = None

                for match in matches:
                    match_length = match.end() - match.start()

                    if shortest_match is None or match_length < shortest_match_length:
                        shortest_match = match
                        shortest_match_length = match_length

            assert shortest_match

            _AdvanceMultiline(normalized_iter, shortest_match.end() - normalized_iter.Offset)
            return Token.RegexMatch(shortest_match)

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
    def Match(normalized_iter):
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
    to_advance: int,
):
    # The match may span multiple lines, so we have to be intentional about how we advance.
    while to_advance:
        line_to_advance = min(to_advance, normalized_iter.LineInfo.OffsetEnd - normalized_iter.Offset)

        # The amount to advance can be 0 if we are looking at a blank line
        if line_to_advance:
            normalized_iter.Advance(line_to_advance)
            to_advance -= line_to_advance

        # Skip the newline (if necessary)
        if to_advance:
            normalized_iter.Advance(1)
            to_advance -= 1
