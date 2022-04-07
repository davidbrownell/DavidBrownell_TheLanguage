# ----------------------------------------------------------------------
# |
# |  NormalizedIterator_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 18:06:51
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
import textwrap

import pytest

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..NormalizedIterator import *
    from ..Normalize import Normalize

# ----------------------------------------------------------------------
def test_Standard():
    iter = NormalizedIterator.FromNormalizedContent(
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
    assert iter.line_info.num_dedents is None
    assert iter.line_info.new_indent_value is None

    assert iter.offset == 0
    assert iter.line_info == iter.line_infos[0]
    assert iter.content[iter.offset] == "1"
    assert iter.line == 1
    assert iter.column == 1
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Content
    iter.Advance(1)

    assert iter.offset == 1
    assert iter.line_info == iter.line_infos[0]
    assert iter.content[iter.offset] == "\n"
    assert iter.line == 1
    assert iter.column == 2
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.EndOfLine
    iter.Advance(1)

    assert iter.AtEnd() == False

    # Second line
    assert iter.line_info.num_dedents is None
    assert iter.line_info.new_indent_value == 4

    assert iter.offset == 2
    assert iter.line_info == iter.line_infos[1]
    assert iter.content[iter.offset : iter.offset + 4] == "    "
    assert iter.line == 2
    assert iter.column == 1
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Indent
    iter.SkipWhitespacePrefix()

    assert iter.offset == 6
    assert iter.line_info == iter.line_infos[1]
    assert iter.content[iter.offset : iter.offset + 2] == "22"
    assert iter.line == 2
    assert iter.column == 5
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Content
    iter.Advance(2)

    assert iter.offset == 8
    assert iter.line_info == iter.line_infos[1]
    assert iter.content[iter.offset] == "\n"
    assert iter.line == 2
    assert iter.column == 7
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.EndOfLine

    iter.Advance(1)
    assert iter.AtEnd() == False

    # Third line
    assert iter.line_info.num_dedents is None
    assert iter.line_info.new_indent_value == 8

    assert iter.offset == 9
    assert iter.line_info == iter.line_infos[2]
    assert iter.content[iter.offset : iter.offset + 8] == "        "
    assert iter.line == 3
    assert iter.column == 1
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Indent

    iter.SkipWhitespacePrefix()

    assert iter.offset == 17
    assert iter.line_info == iter.line_infos[2]
    assert iter.content[iter.offset : iter.offset + 3] == "333"
    assert iter.line == 3
    assert iter.column == 9
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Content

    iter.Advance(3)

    assert iter.offset == 20
    assert iter.line_info == iter.line_infos[2]
    assert iter.content[iter.offset] == "\n"
    assert iter.line == 3
    assert iter.column == 12
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.EndOfLine

    iter.Advance(1)
    assert iter.AtEnd() == False

    # Fourth line
    assert iter.line_info.num_dedents == 1
    assert iter.line_info.new_indent_value is None

    assert iter.offset == 21
    assert iter.line_info == iter.line_infos[3]
    assert iter.content[iter.offset : iter.offset + 4] == "    "
    assert iter.line == 4
    assert iter.column == 1
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Dedent

    iter.ConsumeDedent()
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.WhitespacePrefix

    iter.SkipWhitespacePrefix()

    assert iter.offset == 25
    assert iter.line_info == iter.line_infos[3]
    assert iter.content[iter.offset : iter.offset + 4] == "4444"
    assert iter.line == 4
    assert iter.column == 5
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Content

    iter.Advance(4)

    assert iter.offset == 29
    assert iter.line_info == iter.line_infos[3]
    assert iter.content[iter.offset] == "\n"
    assert iter.line == 4
    assert iter.column == 9
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.EndOfLine

    iter.Advance(1)
    assert iter.AtEnd() == False

    # Fifth line
    assert iter.line_info.num_dedents is None
    assert iter.line_info.new_indent_value == 8

    assert iter.offset == 30
    assert iter.line_info == iter.line_infos[4]
    assert iter.content[iter.offset : iter.offset + 8] == "        "
    assert iter.line == 5
    assert iter.column == 1
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Indent

    iter.SkipWhitespacePrefix()

    assert iter.offset == 38
    assert iter.line_info == iter.line_infos[4]
    assert iter.content[iter.offset : iter.offset + 5] == "55555"
    assert iter.line == 5
    assert iter.column == 9
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Content

    iter.Advance(5)

    assert iter.offset == 43
    assert iter.line_info == iter.line_infos[4]
    assert iter.content[iter.offset] == "\n"
    assert iter.line == 5
    assert iter.column == 14
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.EndOfLine

    iter.Advance(1)

    assert iter.AtEnd() == False

    # Sixth line
    assert iter.line_info.num_dedents is None
    assert iter.line_info.new_indent_value is None

    assert iter.offset == 44
    assert iter.line_info == iter.line_infos[5]
    assert iter.content[iter.offset : iter.offset + 8] == "        "
    assert iter.line == 6
    assert iter.column == 1
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.WhitespacePrefix

    iter.SkipWhitespacePrefix()

    assert iter.offset == 52
    assert iter.line_info == iter.line_infos[5]
    assert iter.content[iter.offset : iter.offset + 6] == "666666"
    assert iter.line == 6
    assert iter.column == 9
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Content

    iter.Advance(2)
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Content

    iter.Advance(2)
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Content

    iter.Advance(2)

    assert iter.offset == 58
    assert iter.line_info == iter.line_infos[5]
    assert iter.content[iter.offset] == "\n"
    assert iter.line == 6
    assert iter.column == 15
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.EndOfLine

    iter.Advance(1)

    assert iter.AtEnd() == False

    # Final dedents
    assert iter.has_end_of_file_dedents
    assert iter.IsBlankLine() == False

    assert iter.line_info.num_dedents == 2
    assert iter.line_info.new_indent_value is None

    assert iter.offset == 59
    assert iter.line_info == iter.line_infos[6]
    assert iter.line == 7
    assert iter.column == 1
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Dedent

    iter.ConsumeDedent()
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Dedent
    iter.ConsumeDedent()
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.EndOfFile

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_NoFinalDedents():
    assert not NormalizedIterator.FromNormalizedContent(
        Normalize(
            textwrap.dedent(
                """\
                one
                two
                three
                """,
            ),
        ),
    ).has_end_of_file_dedents

# ----------------------------------------------------------------------
def test_SkipWhitespacePrefix():
    iter = NormalizedIterator.FromNormalizedContent(Normalize("    one"))

    assert iter.line == 1
    assert iter.column == 1
    assert iter.offset == 0
    iter.SkipWhitespacePrefix()

    assert iter.line == 1
    assert iter.column == 5
    assert iter.offset == 4

# ----------------------------------------------------------------------
def test_SkipWhitespacePrefixNoPrefix():
    iter = NormalizedIterator.FromNormalizedContent(Normalize("one"))

    assert iter.line == 1
    assert iter.column == 1
    assert iter.offset == 0
    iter.SkipWhitespacePrefix()

    assert iter.line == 1
    assert iter.column == 1
    assert iter.offset == 0

# ----------------------------------------------------------------------
def test_SkipSuffix():
    iter = NormalizedIterator.FromNormalizedContent(Normalize("one    "))

    assert iter.line == 1
    assert iter.column == 1
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Content

    iter.Advance(3)
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.WhitespaceSuffix

    assert iter.line == 1
    assert iter.column == 4
    assert iter.offset == 3
    iter.SkipWhitespaceSuffix()

    assert iter.line == 1
    assert iter.column == 8
    assert iter.offset == 7
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.EndOfLine

# ----------------------------------------------------------------------
def test_SkipSuffixNoSuffix():
    iter = NormalizedIterator.FromNormalizedContent(Normalize("one"))

    assert iter.line == 1
    assert iter.column == 1
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.Content

    iter.Advance(3)

    assert iter.line == 1
    assert iter.column == 4
    assert iter.offset == 3
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.EndOfLine

    iter.SkipWhitespaceSuffix()

    assert iter.line == 1
    assert iter.column == 4
    assert iter.offset == 3
    assert iter.GetNextTokenType() == NormalizedIterator.TokenType.EndOfLine


# ----------------------------------------------------------------------
def test_IsBlankLine():
    iter = NormalizedIterator.FromNormalizedContent(
        Normalize(
            textwrap.dedent(
                """\
                one

                three
                \t
                    \t
                six
                """,
            ),
        ),
    )

    # Line 1
    assert iter.line == 1
    assert iter.column == 1
    assert iter.offset == 0
    assert iter.IsBlankLine() == False

    iter.Advance(3)

    assert iter.line == 1
    assert iter.column == 4
    assert iter.offset == 3

    iter.Advance(1)

    # Line 2
    assert iter.line == 2
    assert iter.column == 1
    assert iter.offset == 4
    assert iter.IsBlankLine()

    iter.SkipWhitespacePrefix()
    iter.SkipWhitespaceSuffix()
    assert iter.line == 2
    assert iter.column == 1
    assert iter.offset == 4

    iter.Advance(1)

    # Line 3
    assert iter.line == 3
    assert iter.column == 1
    assert iter.offset == 5
    assert iter.IsBlankLine() == False

    iter.SkipWhitespacePrefix()
    assert iter.line == 3
    assert iter.column == 1
    assert iter.offset == 5

    iter.Advance(len("three"))

    assert iter.line == 3
    assert iter.column == 6
    assert iter.offset == 10

    iter.SkipWhitespaceSuffix()

    assert iter.line == 3
    assert iter.column == 6
    assert iter.offset == 10

    iter.Advance(1)

    # Line 4
    assert iter.line == 4
    assert iter.column == 1
    assert iter.offset == 11
    assert iter.IsBlankLine()

    iter.SkipWhitespacePrefix()

    assert iter.line == 4
    assert iter.column == 1
    assert iter.offset == 11

    iter.Advance(1)

    # Line 5
    assert iter.line == 5
    assert iter.column == 1
    assert iter.offset == 12
    assert iter.IsBlankLine()

    iter.SkipWhitespacePrefix()

    assert iter.line == 5
    assert iter.column == 1
    assert iter.offset == 12

    iter.SkipWhitespaceSuffix()

    assert iter.line == 5
    assert iter.column == 1
    assert iter.offset == 12

    iter.Advance(1)

    # Line 6
    assert iter.line == 6
    assert iter.column == 1
    assert iter.offset == 13
    assert iter.IsBlankLine() == False

    iter.SkipWhitespacePrefix()

    assert iter.line == 6
    assert iter.column == 1
    assert iter.offset == 13

    iter.Advance(len("six"))

    assert iter.line == 6
    assert iter.column == 4
    assert iter.offset == 16

    assert iter.AtEnd() == False
    iter.Advance(1)

    assert iter.line == 7
    assert iter.column == 1
    assert iter.offset == 17
    assert iter.AtEnd()
    assert iter.IsBlankLine() == False

# ----------------------------------------------------------------------
def test_SkipLine():
    iter = NormalizedIterator.FromNormalizedContent(
        Normalize(
            textwrap.dedent(
                """\
                one
                two

                four
                \t
                    \t
                seven
                """,
            ),
        ),
    )

    assert iter.line == 1
    assert iter.column == 1
    assert iter.offset == 0
    iter.SkipLine()

    assert iter.line == 2
    assert iter.column == 1
    assert iter.offset == 4
    iter.SkipLine()

    assert iter.line == 3
    assert iter.column == 1
    assert iter.offset == 8
    iter.SkipLine()

    assert iter.line == 4
    assert iter.column == 1
    assert iter.offset == 9
    iter.SkipLine()

    assert iter.line == 5
    assert iter.column == 1
    assert iter.offset == 14
    iter.SkipLine()

    assert iter.line == 6
    assert iter.column == 1
    assert iter.offset == 15
    iter.SkipLine()

    assert iter.AtEnd() == False
    assert iter.line == 7
    assert iter.column == 1
    assert iter.offset == 16
    iter.SkipLine()

    assert iter.AtEnd()
    assert iter.line == 8
    assert iter.column == 1
    assert iter.offset == 22

# ----------------------------------------------------------------------
def test_Errors():
    iter = NormalizedIterator.FromNormalizedContent(
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
        iter.SkipWhitespacePrefix()

    # Request more than a newline
    with pytest.raises(AssertionError):
        iter.Advance(2)

    iter.Advance(1)

    # Attempt to skip the suffix at the beginning of the line
    with pytest.raises(AssertionError):
        iter.SkipWhitespaceSuffix()

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
    iter.ConsumeDedent()

    iter.AtEnd()

# TODO: # ----------------------------------------------------------------------
# TODO: def test_Clone():
# TODO:     iter1 = NormalizedIterator.Create(Normalize("12345"))
# TODO:     iter2 = iter1.Clone()
# TODO:
# TODO:     assert iter1 == iter2
# TODO:
# TODO:     iter1.Advance(1)
# TODO:     assert iter1 != iter2
# TODO:
# TODO:     iter2.Advance(2)
# TODO:     assert iter1 != iter2
# TODO:
# TODO:     iter1.Advance(1)
# TODO:     assert iter1 == iter2
# TODO:
