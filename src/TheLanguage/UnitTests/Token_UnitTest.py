# ----------------------------------------------------------------------
# |
# |  Token_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-11 20:06:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for Token.py"""

import os
import re
import sys
import textwrap

import pytest

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

sys.path.insert(0, os.path.join(_script_dir, ".."))
with CallOnExit(lambda: sys.path.pop(0)):
    from Token import *
    from Normalize import Normalize
    from NormalizedIterator import NormalizedIterator

# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
def test_NewlineToken():
    iter = NormalizedIterator(
        Normalize(
            textwrap.dedent(
                """\



                last_line

                """,
            ),
        ),
    )

    token = NewlineToken()

    assert token.Name == "Newline"

    assert token.Match(iter) is NewlineToken            # Line 1
    assert token.Match(iter) is NewlineToken            # Line 2
    assert token.Match(iter) is NewlineToken            # Line 3

    # line with 'last_line'
    assert token.Match(iter) is None
    iter.Advance(len("last_line"))
    assert token.Match(iter) is NewlineToken

    assert token.Match(iter) is NewlineToken            # Line 5

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_NewlineTokenWithWhitespace():
    iter = NormalizedIterator(Normalize("\n\n    \nlast_line  \n\n"))

    token = NewlineToken()

    assert token.Name == "Newline"

    assert token.Match(iter) is NewlineToken            # Line 1
    assert token.Match(iter) is NewlineToken            # Line 2

    # Line 3
    assert token.Match(iter) is None
    assert iter.LineInfo.IndentationInfo is None
    iter.SkipPrefix()
    assert token.Match(iter) is NewlineToken            # Line 3

    # line with 'last_line'
    assert token.Match(iter) is None
    iter.Advance(len("last_line"))
    assert token.Match(iter) is NewlineToken

    assert token.Match(iter) is NewlineToken            # Line 5

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_Indent():
    iter = NormalizedIterator(
        Normalize(
            textwrap.dedent(
                """\
                one
                    two
                      three
                      four
                    five
                """,
            ),
        ),
    )

    token = IndentToken()

    assert token.Name == "Indent"

    # Line 1
    assert token.Match(iter) is None
    iter.Advance(len("one"))
    assert token.Match(iter) is None
    iter.Advance(1)

    # Line 2
    assert token.Match(iter) == (4, 8)
    assert token.Match(iter) is None
    iter.Advance(len("two"))
    iter.Advance(1)

    # Line 3
    assert token.Match(iter) == (12, 18)
    assert token.Match(iter) is None
    iter.Advance(len("three"))
    iter.Advance(1)

    # Line 4
    assert token.Match(iter) is None
    iter.SkipPrefix()
    iter.Advance(len("four"))
    iter.Advance(1)

    # Line 5
    assert token.Match(iter) is None
    iter.SkipPrefix()
    iter.Advance(len("five"))
    iter.Advance(1)

    # Skip the dedent line
    assert iter.AtEnd() == False
    assert iter.HasTrailingDedents()
    iter.Advance(0)

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_Dedent():
    iter = NormalizedIterator(
        Normalize(
            textwrap.dedent(
                """\
                one
                    two
                      three
                      four
                five
                    six
                        seven
                    eight
                """,
            ),
        ),
    )

    token = DedentToken()

    assert token.Name == "Dedent"

    # Line 1
    assert token.Match(iter) is None
    iter.Advance(len("one"))
    assert token.Match(iter) is None
    iter.Advance(1)

    # Line 2
    assert token.Match(iter) is None
    iter.SkipPrefix()
    iter.Advance(len("two"))
    iter.Advance(1)

    # Line 3
    assert token.Match(iter) is None
    iter.SkipPrefix()
    iter.Advance(len("three"))
    iter.Advance(1)

    # Line 4
    assert token.Match(iter) is None
    iter.SkipPrefix()
    iter.Advance(len("four"))
    iter.Advance(1)

    # Line 5
    assert token.Match(iter) == [DedentToken, DedentToken]
    iter.Advance(len("five"))
    iter.Advance(1)

    # Line 6
    assert token.Match(iter) is None
    iter.SkipPrefix()
    iter.Advance(len("six"))
    iter.Advance(1)

    # Line 7
    assert token.Match(iter) is None
    iter.SkipPrefix()
    iter.Advance(len("seven"))
    iter.Advance(1)

    # Line 8
    assert token.Match(iter) == [DedentToken]
    iter.Advance(len("eight"))
    iter.Advance(1)

    # Final dedent line
    assert token.Match(iter) == [DedentToken]

    assert iter.AtEnd() == False
    iter.Advance(0)
    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_Regex():
    iter = NormalizedIterator(Normalize("aaabbb bb b ccc"))

    token = RegexToken("test", re.compile("(?P<value>b+)"))

    assert token.Name == "test"

    assert token.Match(iter) is None
    iter.Advance(1)
    assert token.Match(iter) is None
    iter.Advance(1)
    assert token.Match(iter) is None
    iter.Advance(1)

    assert token.Match(iter).group("value") == "bbb"
    iter.Advance(1)                         # Move past the space
    assert token.Match(iter).group("value") == "bb"
    iter.Advance(1)                         # Move past the space
    assert token.Match(iter).group("value") == "b"
    iter.Advance(1)                         # Move past the space

    assert token.Match(iter) is None

# ----------------------------------------------------------------------
def test_RegexErrors():
    with pytest.raises(AssertionError):
        RegexToken(None, "doesn't matter")
