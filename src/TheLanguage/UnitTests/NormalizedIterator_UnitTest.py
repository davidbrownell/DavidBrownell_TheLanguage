# ----------------------------------------------------------------------
# |
# |  NormalizedIterator_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-11 18:14:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for NromalizedIterator.py"""

import os
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
    from NormalizedIterator import *
    from Normalize import Normalize

# ----------------------------------------------------------------------
def test_Standard():
    iter = NormalizedIterator(
        Normalize(
            textwrap.dedent(
                """\
                1
                    22
                        333
                    4444
                        55555
                        666666
                """,
            ),
        ),
    )

    # First line
    assert iter.LineInfo.IndentationInfo is None

    assert iter.Offset == 0
    assert iter.LineInfo == iter.LineInfos[0]
    assert iter.Content[iter.Offset] == "1"
    assert iter.Line == 1
    assert iter.Column == 1
    iter.Advance(1)

    assert iter.Offset == 1
    assert iter.LineInfo == iter.LineInfos[0]
    assert iter.Content[iter.Offset] == "\n"
    assert iter.Line == 1
    assert iter.Column == 2
    iter.Advance(1)

    assert iter.AtEnd() == False

    # Second line
    assert iter.LineInfo.IndentationInfo == True

    assert iter.Offset == 2
    assert iter.LineInfo == iter.LineInfos[1]
    assert iter.Content[iter.Offset : iter.Offset + 4] == "    "
    assert iter.Line == 2
    assert iter.Column == 1
    iter.SkipPrefix()

    assert iter.Offset == 6
    assert iter.LineInfo == iter.LineInfos[1]
    assert iter.Content[iter.Offset : iter.Offset + 2] == "22"
    assert iter.Line == 2
    assert iter.Column == 5
    iter.Advance(2)

    assert iter.Offset == 8
    assert iter.LineInfo == iter.LineInfos[1]
    assert iter.Content[iter.Offset] == "\n"
    assert iter.Line == 2
    assert iter.Column == 7
    iter.Advance(1)

    assert iter.AtEnd() == False

    # Third line
    assert iter.LineInfo.IndentationInfo == True

    assert iter.Offset == 9
    assert iter.LineInfo == iter.LineInfos[2]
    assert iter.Content[iter.Offset : iter.Offset + 8] == "        "
    assert iter.Line == 3
    assert iter.Column == 1
    iter.SkipPrefix()

    assert iter.Offset == 17
    assert iter.LineInfo == iter.LineInfos[2]
    assert iter.Content[iter.Offset : iter.Offset + 3] == "333"
    assert iter.Line == 3
    assert iter.Column == 9
    iter.Advance(3)

    assert iter.Offset == 20
    assert iter.LineInfo == iter.LineInfos[2]
    assert iter.Content[iter.Offset] == "\n"
    assert iter.Line == 3
    assert iter.Column == 12
    iter.Advance(1)

    assert iter.AtEnd() == False

    # Fourth line
    assert iter.LineInfo.IndentationInfo == 1

    assert iter.Offset == 21
    assert iter.LineInfo == iter.LineInfos[3]
    assert iter.Content[iter.Offset : iter.Offset + 4] == "    "
    assert iter.Line == 4
    assert iter.Column == 1
    iter.SkipPrefix()

    assert iter.Offset == 25
    assert iter.LineInfo == iter.LineInfos[3]
    assert iter.Content[iter.Offset : iter.Offset + 4] == "4444"
    assert iter.Line == 4
    assert iter.Column == 5
    iter.Advance(4)

    assert iter.Offset == 29
    assert iter.LineInfo == iter.LineInfos[3]
    assert iter.Content[iter.Offset] == "\n"
    assert iter.Line == 4
    assert iter.Column == 9
    iter.Advance(1)

    assert iter.AtEnd() == False

    # Fifth line
    assert iter.LineInfo.IndentationInfo == True

    assert iter.Offset == 30
    assert iter.LineInfo == iter.LineInfos[4]
    assert iter.Content[iter.Offset : iter.Offset + 8] == "        "
    assert iter.Line == 5
    assert iter.Column == 1
    iter.SkipPrefix()

    assert iter.Offset == 38
    assert iter.LineInfo == iter.LineInfos[4]
    assert iter.Content[iter.Offset : iter.Offset + 5] == "55555"
    assert iter.Line == 5
    assert iter.Column == 9
    iter.Advance(5)

    assert iter.Offset == 43
    assert iter.LineInfo == iter.LineInfos[4]
    assert iter.Content[iter.Offset] == "\n"
    assert iter.Line == 5
    assert iter.Column == 14
    iter.Advance(1)

    assert iter.AtEnd() == False

    # Sixth line
    assert iter.LineInfo.IndentationInfo is None

    assert iter.Offset == 44
    assert iter.LineInfo == iter.LineInfos[5]
    assert iter.Content[iter.Offset : iter.Offset + 8] == "        "
    assert iter.Line == 6
    assert iter.Column == 1
    iter.SkipPrefix()

    assert iter.Offset == 52
    assert iter.LineInfo == iter.LineInfos[5]
    assert iter.Content[iter.Offset : iter.Offset + 6] == "666666"
    assert iter.Line == 6
    assert iter.Column == 9
    iter.Advance(2)
    iter.Advance(2)
    iter.Advance(2)

    assert iter.Offset == 58
    assert iter.LineInfo == iter.LineInfos[5]
    assert iter.Content[iter.Offset] == "\n"
    assert iter.Line == 6
    assert iter.Column == 15
    iter.Advance(1)

    assert iter.AtEnd() == False

    # Final dedents
    assert iter.HasTrailingDedents()

    assert iter.LineInfo.IndentationInfo == 2

    assert iter.Offset == 59
    assert iter.LineInfo == iter.LineInfos[6]
    assert iter.Line == 7
    assert iter.Column == 1
    iter.Advance(0)

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_NoFinalDedents():
    assert not NormalizedIterator(
        Normalize(
            textwrap.dedent(
                """\
                one
                two
                three
                """,
            ),
        ),
    ).HasTrailingDedents()

# ----------------------------------------------------------------------
def test_SkipPrefix():
    iter = NormalizedIterator(Normalize("    one"))

    assert iter.Line == 1
    assert iter.Column == 1
    assert iter.Offset == 0
    iter.SkipPrefix()

    assert iter.Line == 1
    assert iter.Column == 5
    assert iter.Offset == 4

# ----------------------------------------------------------------------
def test_SkipPrefixNoPrefix():
    iter = NormalizedIterator(Normalize("one"))

    assert iter.Line == 1
    assert iter.Column == 1
    assert iter.Offset == 0
    iter.SkipPrefix()

    assert iter.Line == 1
    assert iter.Column == 1
    assert iter.Offset == 0

# ----------------------------------------------------------------------
def test_SkipSuffix():
    iter = NormalizedIterator(Normalize("one    "))

    assert iter.Line == 1
    assert iter.Column == 1

    iter.Advance(3)

    assert iter.Line == 1
    assert iter.Column == 4
    assert iter.Offset == 3
    iter.SkipSuffix()

    assert iter.Line == 1
    assert iter.Column == 8
    assert iter.Offset == 7

# ----------------------------------------------------------------------
def test_SkipSuffixNoSuffix():
    iter = NormalizedIterator(Normalize("one"))

    assert iter.Line == 1
    assert iter.Column == 1

    iter.Advance(3)

    assert iter.Line == 1
    assert iter.Column == 4
    assert iter.Offset == 3
    iter.SkipSuffix()

    assert iter.Line == 1
    assert iter.Column == 4
    assert iter.Offset == 3

# ----------------------------------------------------------------------
def test_Errors():
    iter = NormalizedIterator(
        Normalize(
            textwrap.dedent(
                """\
                one
                    two
                """,
            ),
        ),
    )

    # Request too much content
    with pytest.raises(AssertionError):
        iter.Advance(100)

    iter.Advance(3)                         # Move past the content

    # Attempt to skip prefix when not at the beginning of the line
    with pytest.raises(AssertionError):
        iter.SkipPrefix()

    # Request more than a newline
    with pytest.raises(AssertionError):
        iter.Advance(2)

    iter.Advance(1)

    # Attempt to skip the suffix at the beginning of the line
    with pytest.raises(AssertionError):
        iter.SkipSuffix()

    # Request too little whitespace
    with pytest.raises(AssertionError):
        iter.Advance(1)

    # Request too much whitespace
    with pytest.raises(AssertionError):
        iter.Advance(5)

    iter.Advance(4)                         # Move past the whitespace
    iter.Advance(3)                         # Move past the content
    iter.Advance(1)                         # Move past the newline

    assert iter.AtEnd() == False

    # Request an invalid amount
    with pytest.raises(AssertionError):
        iter.Advance(1)

    assert iter.AtEnd() == False
    iter.Advance(0)
    iter.AtEnd()

# ----------------------------------------------------------------------
def test_Clone():
    iter1 = NormalizedIterator(Normalize("12345"))
    iter2 = iter1.Clone()

    assert iter1 == iter2

    iter1.Advance(1)
    assert iter1 != iter2

    iter2.Advance(2)
    assert iter1 != iter2

    iter1.Advance(1)
    assert iter1 == iter2
