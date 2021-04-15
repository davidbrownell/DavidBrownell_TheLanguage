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
        "Token",                            # Newline, Dedent
        Tuple[int, int],                    # Indent
        Match,                              # Regex match
    ]

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
    Name                                    = Interface.DerivedProperty("Newline")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Match(normalized_iter):
        if normalized_iter.Offset == normalized_iter.LineInfo.EndPos and not normalized_iter.AtEnd():
            normalized_iter.SkipSuffix()
            normalized_iter.Advance(1)

            return NewlineToken

        return None


# ----------------------------------------------------------------------
@Interface.staticderived
class IndentToken(Token):
    Name                                    = Interface.DerivedProperty("Indent")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Match(normalized_iter):
        if normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart and normalized_iter.LineInfo.HasNewIndent():
            normalized_iter.SkipPrefix()
            return (normalized_iter.LineInfo.OffsetStart, normalized_iter.LineInfo.StartPos)

        return None


# ----------------------------------------------------------------------
@Interface.staticderived
class DedentToken(Token):
    Name                                    = Interface.DerivedProperty("Dedent")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Match(normalized_iter):
        if normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart and normalized_iter.LineInfo.NumDedents():
            normalized_iter.SkipPrefix()
            return [DedentToken] * normalized_iter.LineInfo.NumDedents()

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
