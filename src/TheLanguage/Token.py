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

from typing import List, Match, Optional, Pattern, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

from NormalizedIterator import NormalizedIterator

# ----------------------------------------------------------------------
class Token(Interface.Interface):
    """Base class for various Token types"""

    MatchType                               = Union[
        # Newline
        Tuple[
            "Token",
            int,                            # start range
            int,                            # end range
        ],

        # Indent
        Tuple[
            "Token",
            int,                            # start range
            int,                            # end range
            int,                            # token value
        ],

        # Dedent
        "Token",

        # Regex match
        Match,
    ]

    # ----------------------------------------------------------------------
    # A Control Token is a token that doesn't consume content, but modifies
    # behavior of a statement. This concept is necessary because we are combining
    # the lexing and parsing passes into 1 pass.
    IsControlToken                          = False

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def Name(self):
        """Name of the token"""
        raise Exception("Abstract property")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Match(
        normalized_iter: NormalizedIterator,
    ) -> Optional[Union["MatchType", List["MatchType"]]]:
        """Returns match information if applicable"""
        raise Exception("Abstract method")


# ----------------------------------------------------------------------
@Interface.staticderived
class NewlineToken(Token):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        capture_many=True,
    ):
        self._name                          = "Newline{}".format("+" if capture_many else "")
        self._capture_many                  = capture_many

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def Name(self):
        return self._name

    @property
    def CaptureMany(self):
        return self._capture_many

    # ----------------------------------------------------------------------
    @Interface.override
    def Match(self, normalized_iter):
        if normalized_iter.Offset == normalized_iter.LineInfo.EndPos and not normalized_iter.AtEnd():
            newline_start = normalized_iter.Offset

            normalized_iter.SkipSuffix()
            normalized_iter.Advance(1)

            if self._capture_many:
                while normalized_iter.IsBlankLine():
                    normalized_iter.SkipLine()

            return (NewlineToken, newline_start, normalized_iter.Offset)

        return None


# ----------------------------------------------------------------------
@Interface.staticderived
class IndentToken(Token):
    Name                                    = Interface.DerivedProperty("Indent")

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def Match(cls, normalized_iter):
        if normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart and normalized_iter.LineInfo.HasNewIndent():
            normalized_iter.SkipPrefix()
            return (cls, normalized_iter.LineInfo.OffsetStart, normalized_iter.LineInfo.StartPos)

        return None


# ----------------------------------------------------------------------
@Interface.staticderived
class DedentToken(Token):
    Name                                    = Interface.DerivedProperty("Dedent")

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def Match(cls, normalized_iter):
        if normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart and normalized_iter.LineInfo.NumDedents():
            normalized_iter.SkipPrefix()
            return [cls] * normalized_iter.LineInfo.NumDedents()

        return None


# ----------------------------------------------------------------------
class RegexToken(Token):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        regex: Pattern,
    ):
        assert name

        self._name                          = name
        self._regex                         = regex

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def Name(self):
        return self._name

    # ----------------------------------------------------------------------
    @Interface.override
    def Match(self, normalized_iter):
        match = self._regex.match(
            normalized_iter.Content,
            pos=normalized_iter.Offset,
            endpos=normalized_iter.LineInfo.EndPos,
        )

        if match:
            normalized_iter.Advance(match.end() - match.start())
            return match

        return None


# ----------------------------------------------------------------------
class ControlTokenBase(Token):
    """Base class for Control tokens. See the definition of `IsControlToken` in the base class for more info"""

    IsControlToken                          = True

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


# ----------------------------------------------------------------------
@Interface.staticderived
class PopIgnoreWhitespaceControlToken(ControlTokenBase):
    """\
    Restores whitespace processing.

    See `PushIgnoreWhitespaceControlToken` for more information.
    """

    Name                                    = Interface.DerivedProperty("PopIgnoreWhitespaceControl")
