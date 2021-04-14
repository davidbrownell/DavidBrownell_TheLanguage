# ----------------------------------------------------------------------
# |
# |  Normalize_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-09 19:46:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Normalize.py"""

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
    from Normalize import *

# ----------------------------------------------------------------------
class TestLineInfo(object):
    # ----------------------------------------------------------------------
    def test_StandardWithPrefixAndSuffix(self):
        li = LineInfo(1, 4, 2, 3, None)

        assert li.OffsetStart == 1
        assert li.OffsetEnd == 4
        assert li.StartPos == 2
        assert li.EndPos == 3
        assert li.IndentationInfo is None

        assert li.HasWhitespacePrefix()
        assert li.HasWhitespaceSuffix()
        assert li.HasNewIndent() == False
        assert li.HasNewDedents() == False
        assert li.NumDedents() == 0

        assert li == li

    # ----------------------------------------------------------------------
    def test_StandardWithPrefix(self):
        li = LineInfo(1, 3, 2, 3, None)

        assert li.OffsetStart == 1
        assert li.OffsetEnd == 3
        assert li.StartPos == 2
        assert li.EndPos == 3
        assert li.IndentationInfo is None

        assert li.HasWhitespacePrefix()
        assert li.HasWhitespaceSuffix() == False
        assert li.HasNewIndent() == False
        assert li.HasNewDedents() == False
        assert li.NumDedents() == 0

        assert li == li

    # ----------------------------------------------------------------------
    def test_StandardWithSuffix(self):
        li = LineInfo(1, 4, 1, 3, None)

        assert li.OffsetStart == 1
        assert li.OffsetEnd == 4
        assert li.StartPos == 1
        assert li.EndPos == 3
        assert li.IndentationInfo is None

        assert li.HasWhitespacePrefix() == False
        assert li.HasWhitespaceSuffix()
        assert li.HasNewIndent() == False
        assert li.HasNewDedents() == False
        assert li.NumDedents() == 0

        assert li == li

    # ----------------------------------------------------------------------
    def test_StandardWithIndentation(self):
        li = LineInfo(1, 4, 1, 3, True)

        assert li.OffsetStart == 1
        assert li.OffsetEnd == 4
        assert li.StartPos == 1
        assert li.EndPos == 3
        assert li.IndentationInfo == True

        assert li.HasWhitespacePrefix() == False
        assert li.HasWhitespaceSuffix()
        assert li.HasNewIndent()
        assert li.HasNewDedents() == False
        assert li.NumDedents() == 0

        assert li == li

    # ----------------------------------------------------------------------
    def test_StandardWithDedents(self):
        li = LineInfo(1, 4, 1, 3, 2)

        assert li.OffsetStart == 1
        assert li.OffsetEnd == 4
        assert li.StartPos == 1
        assert li.EndPos == 3
        assert li.IndentationInfo == 2

        assert li.HasWhitespacePrefix() == False
        assert li.HasWhitespaceSuffix()
        assert li.HasNewIndent() == False
        assert li.HasNewDedents()
        assert li.NumDedents() == 2

        assert li == li

    # ----------------------------------------------------------------------
    def test_Errors(self):
        for args in [
            (-1, 0, 0, 0, None),            # Invalid offset start
            (5, 1, 0, 0, None),             # Invalid offset end
            (5, 10, 2, 10, None),           # Invalid startpos
            (5, 10, 5, 11, None),           # Invalid endpos
            (5, 10, 6, 5, None),            # Invalid startpos/endpos
        ]:
            with pytest.raises(AssertionError):
                LineInfo(*args)


# ----------------------------------------------------------------------
class TestNormalizedContent(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        result = NormalizedContent("hello", 5, [LineInfo(1, 4, 3, 4, None)])

        assert result.Content == "hello"
        assert result.ContentLen == 5
        assert result.LineInfos == [LineInfo(1, 4, 3, 4, None)]

        assert result == result

    # ----------------------------------------------------------------------
    def test_Errors(self):
        for args in [
            (None, 10, [1, 2, 3]),          # Invalid content
            ("", 10, [1, 2, 3]),            # Invalid content
            ("hello", 0, [1, 2, 3]),        # Invalid length
            ("hello", 5, None),             # Invalid LineInfos
            ("hello", 5, []),               # Invalid LineInfos
        ]:
            with pytest.raises(AssertionError):
                NormalizedContent(*args)


# ----------------------------------------------------------------------
class TestNormalize(object):
    # ----------------------------------------------------------------------
    @staticmethod
    def Test(content, line_infos):
        assert Normalize(content) == NormalizedContent(content, len(content), line_infos)

    # ----------------------------------------------------------------------
    def test_Simple(self):
        # No indent
        self.Test(
            textwrap.dedent(
                """\
                1
                22
                333
                """,
            ),
            [
                LineInfo(0, 1, 0, 1, None),
                LineInfo(2, 4, 2, 4, None),
                LineInfo(5, 8, 5, 8, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_Indent(self):
        self.Test(
            textwrap.dedent(
                """\
                1
                    22
                        333
                """,
            ),
            [
                LineInfo(0, 1, 0, 1, None),
                LineInfo(2, 8, 6, 8, True),
                LineInfo(9, 20, 17, 20, True),
                LineInfo(21, 21, 21, 21, 2),
            ],
        )

    # ----------------------------------------------------------------------
    def test_IndentWithDedents(self):
        self.Test(
            textwrap.dedent(
                """\
                1
                    22
                        333
                    4444
                55555
                """,
            ),
            [
                LineInfo(0, 1, 0, 1, None),
                LineInfo(2, 8, 6, 8, True),
                LineInfo(9, 20, 17, 20, True),
                LineInfo(21, 29, 25, 29, 1),
                LineInfo(30, 35, 30, 35, 1),
            ],
        )

    # ----------------------------------------------------------------------
    def test_TrailingWhitespace(self):
        self.Test(
            # Not using textwrap.dedent as the editor removes the trailing whitespace
            "12  \n 34\n",
            [
                LineInfo(0, 4, 0, 2, None),
                LineInfo(5, 8, 6, 8, True),
                LineInfo(9, 9, 9, 9, 1),
            ],
        )

    # ----------------------------------------------------------------------
    def test_EmptyLine(self):
        self.Test(
            # Not using textwrap.dedent as the editor removes the empty whitespace
            "12\n\n34\n",
            [
                LineInfo(0, 2, 0, 2, None),
                LineInfo(3, 3, 3, 3, None),
                LineInfo(4, 6, 4, 6, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_SpacesOnEmptyLine(self):
        self.Test(
            # Not using textwrap.dedent as the editor removes the empty whitespace
            "12\n    \n34\n",
            [
                LineInfo(0, 2, 0, 2, None),
                LineInfo(3, 7, 7, 7, None),
                LineInfo(8, 10, 8, 10, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_SpacesOnEmptyLineWithMatchingIndent(self):
        self.Test(
            # Not using textwrap.dedent as the editor removes the empty whitespace
            "    12\n    \n34\n",
            [
                LineInfo(0, 6, 4, 6, True),
                LineInfo(7, 11, 11, 11, None),
                LineInfo(12, 14, 12, 14, 1),
            ],
        )

    # ----------------------------------------------------------------------
    def test_TabsVsSpaces1(self):
        self.Test(
            # Not using textwrap.dedent so tabs can be embedded
            "1\n  2\n3\n\t4\n\t5\n\t 6\n\t 7\n",
            [
                LineInfo(0, 1, 0, 1, None),             # 1
                LineInfo(2, 5, 4, 5, True),             # 2
                LineInfo(6, 7, 6, 7, 1),                # 3
                LineInfo(8, 10, 9, 10, True),           # 4
                LineInfo(11, 13, 12, 13, None),         # 5
                LineInfo(14, 17, 16, 17, True),         # 6
                LineInfo(18, 21, 20, 21, None),         # 7
                LineInfo(22, 22, 22, 22, 2),
            ],
        )

    # ----------------------------------------------------------------------
    def test_TabsVsSpaces2(self):
        self.Test(
            # Not using textwrap.dedent so tabs can be embedded
            "1\n  2\n3\n\t4\n\t5\n \t6\n \t7\n",
            [
                LineInfo(0, 1, 0, 1, None),             # 1
                LineInfo(2, 5, 4, 5, True),             # 2
                LineInfo(6, 7, 6, 7, 1),                # 3
                LineInfo(8, 10, 9, 10, True),           # 4
                LineInfo(11, 13, 12, 13, None),         # 5
                LineInfo(14, 17, 16, 17, True),         # 6
                LineInfo(18, 21, 20, 21, None),         # 7
                LineInfo(22, 22, 22, 22, 2),
            ],
        )

    # ----------------------------------------------------------------------
    def test_NewlineAdded(self):
        assert Normalize("123") == NormalizedContent("123\n", 4, [LineInfo(0, 3, 0, 3, None)])

    # ----------------------------------------------------------------------
    def test_TabAndSpaceMix(self):
        with pytest.raises(InvalidTabsAndSpacesNormalizeException) as ex:
            Normalize("   One\n\t\t\tTwo\n")

        assert ex.value.Line == 2
        assert ex.value.Column == 4

        with pytest.raises(InvalidTabsAndSpacesNormalizeException) as ex:
            Normalize("if True:\n  \tone\n \t two")

        assert ex.value.Line == 3
        assert ex.value.Column == 4

    # ----------------------------------------------------------------------
    def test_InvalidIndentation(self):
        with pytest.raises(InvalidIndentationNormalizeException) as ex:
            Normalize(
                textwrap.dedent(
                    """\
                    1
                            22
                        333 # Invalid indentation
                    4444
                    """,
                ),
            )

        assert ex.value.Line == 3
        assert ex.value.Column == 5
