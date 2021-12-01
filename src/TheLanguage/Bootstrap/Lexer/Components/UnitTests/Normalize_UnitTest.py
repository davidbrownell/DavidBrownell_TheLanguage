# ----------------------------------------------------------------------
# |
# |  Normalize_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 18:04:01
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
import textwrap

import pytest

import CommonEnvironment
from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Normalize import *

# ----------------------------------------------------------------------
class TestLineInfo(object):
    # ----------------------------------------------------------------------
    def test_StandardWithPrefixAndSuffix(self):
        li = LineInfo(1, 4, 2, 3, [])

        assert li.OffsetStart == 1
        assert li.OffsetEnd == 4
        assert li.ContentStart == 2
        assert li.ContentEnd == 3
        assert li.NewIndentationValue is None
        assert li.NumDedents is None
        assert li.NewIndentationValue is None

        assert li.HasWhitespacePrefix()
        assert li.HasContent()
        assert li.HasWhitespaceSuffix()

        assert li == li

    # ----------------------------------------------------------------------
    def test_StandardWithPrefix(self):
        li = LineInfo(1, 3, 2, 3, [])

        assert li.OffsetStart == 1
        assert li.OffsetEnd == 3
        assert li.ContentStart == 2
        assert li.ContentEnd == 3
        assert li.NumDedents is None
        assert li.NewIndentationValue is None

        assert li.HasWhitespacePrefix()
        assert li.HasContent()
        assert li.HasWhitespaceSuffix() == False

        assert li == li

    # ----------------------------------------------------------------------
    def test_StandardWithSuffix(self):
        li = LineInfo(1, 4, 1, 3, [])

        assert li.OffsetStart == 1
        assert li.OffsetEnd == 4
        assert li.ContentStart == 1
        assert li.ContentEnd == 3
        assert li.NumDedents is None
        assert li.NewIndentationValue is None

        assert li.HasWhitespacePrefix() == False
        assert li.HasContent()
        assert li.HasWhitespaceSuffix()

        assert li == li

    # ----------------------------------------------------------------------
    def test_StandardWithIndentation(self):
        li = LineInfo(1, 4, 1, 3, [], None, 10)

        assert li.OffsetStart == 1
        assert li.OffsetEnd == 4
        assert li.ContentStart == 1
        assert li.ContentEnd == 3
        assert li.NumDedents is None
        assert li.NewIndentationValue == 10

        assert li.HasWhitespacePrefix() == False
        assert li.HasContent()
        assert li.HasWhitespaceSuffix()

        assert li == li

    # ----------------------------------------------------------------------
    def test_StandardWithDedents(self):
        li = LineInfo(1, 4, 1, 3, [], 2)

        assert li.OffsetStart == 1
        assert li.OffsetEnd == 4
        assert li.ContentStart == 1
        assert li.ContentEnd == 3
        assert li.NumDedents == 2
        assert li.NewIndentationValue is None

        assert li.HasWhitespacePrefix() == False
        assert li.HasContent()
        assert li.HasWhitespaceSuffix()

        assert li == li

    # ----------------------------------------------------------------------
    def test_Errors(self):
        for args in [
            (5, 1, 0, 0, []),               # Invalid offset end
            (5, 10, 2, 10, []),             # Invalid startpos
            (5, 10, 5, 11, []),             # Invalid endpos
            (5, 10, 6, 5, []),              # Invalid startpos/endpos
        ]:
            with pytest.raises(AssertionError):
                LineInfo(*args)


# ----------------------------------------------------------------------
class TestNormalizedContent(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        result = NormalizedContent.Create("hello", 5, [LineInfo(1, 4, 3, 4, [])])

        assert result.Content == "hello"
        assert result.ContentLength == 5
        assert result.LineInfos == [LineInfo(1, 4, 3, 4, [])]

        assert result == result

    # Not Needed: # ----------------------------------------------------------------------
    # Not Needed: def test_Errors(self):
    # Not Needed:     for args in [
    # Not Needed:         (None, 10, [1, 2, 3]),          # Invalid content
    # Not Needed:         ("", 10, [1, 2, 3]),            # Invalid content
    # Not Needed:         ("hello", 0, [1, 2, 3]),        # Invalid length
    # Not Needed:         ("hello", 5, None),             # Invalid LineInfos
    # Not Needed:         ("hello", 5, []),               # Invalid LineInfos
    # Not Needed:     ]:
    # Not Needed:         with pytest.raises(AssertionError):
    # Not Needed:             NormalizedContent.Create(*args)


# ----------------------------------------------------------------------
class TestNormalize(object):
    # ----------------------------------------------------------------------
    @staticmethod
    def Test(content, line_infos):
        assert Normalize(content) == NormalizedContent.Create(content, len(content), line_infos)

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
                LineInfo(0, 1, 0, 1, []),
                LineInfo(2, 4, 2, 4, []),
                LineInfo(5, 8, 5, 8, []),
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
                LineInfo(0, 1, 0, 1, []),
                LineInfo(2, 8, 6, 8, [
                    LineInfo.WhitespaceRange(2, 6),
                ], None, 4),
                LineInfo(9, 20, 17, 20, [
                    LineInfo.WhitespaceRange(9, 17),
                ], None, 8),
                LineInfo(21, 21, 21, 21, [], 2, None),
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
                LineInfo(0, 1, 0, 1, []),
                LineInfo(2, 8, 6, 8, [
                    LineInfo.WhitespaceRange(2, 6),
                ], None, 4),
                LineInfo(9, 20, 17, 20, [
                    LineInfo.WhitespaceRange(9, 17),
                ], None, 8),
                LineInfo(21, 29, 25, 29, [
                    LineInfo.WhitespaceRange(21, 25),
                ], 1, None),
                LineInfo(30, 35, 30, 35, [], 1, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_WithUnusualIndent(self):
        self.Test(
            textwrap.dedent(
                """\
                1
                    22
                  333
                """,
            ),
            [
                LineInfo(0, 1, 0, 1, []),
                LineInfo(2, 8, 6, 8, [
                    LineInfo.WhitespaceRange(2, 6),
                ], None, 4),
                LineInfo(9, 14, 11, 14, [
                    LineInfo.WhitespaceRange(9, 11),
                ], 1, 2),
                LineInfo(15, 15, 15, 15, [], 1, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_TrailingWhitespace(self):
        self.Test(
            # Not using textwrap.dedent as the editor removes the trailing whitespace
            "12  \n 34\n",
            [
                LineInfo(0, 4, 0, 2, [
                    LineInfo.WhitespaceRange(2, 4),
                ]),
                LineInfo(5, 8, 6, 8, [
                    LineInfo.WhitespaceRange(5, 6),
                ], None, 1),
                LineInfo(9, 9, 9, 9, [], 1, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_EmptyLine(self):
        self.Test(
            # Not using textwrap.dedent as the editor removes the empty whitespace
            "12\n\n34\n",
            [
                LineInfo(0, 2, 0, 2, []),
                LineInfo(3, 3, 3, 3, []),
                LineInfo(4, 6, 4, 6, []),
            ],
        )

    # ----------------------------------------------------------------------
    def test_SpacesOnEmptyLine(self):
        self.Test(
            # Not using textwrap.dedent as the editor removes the empty whitespace
            "12\n    \n34\n",
            [
                LineInfo(0, 2, 0, 2, []),
                LineInfo(3, 7, 7, 7, [LineInfo.WhitespaceRange(3, 7)]),
                LineInfo(8, 10, 8, 10, []),
            ],
        )

    # ----------------------------------------------------------------------
    def test_SpacesOnEmptyLineWithMatchingIndent(self):
        self.Test(
            # Not using textwrap.dedent as the editor removes the empty whitespace
            "    12\n    \n34\n",
            [
                LineInfo(0, 6, 4, 6, [LineInfo.WhitespaceRange(0, 4)], None, 4),
                LineInfo(7, 11, 11, 11, [LineInfo.WhitespaceRange(7, 11)]),
                LineInfo(12, 14, 12, 14, [], 1, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_TabsVsSpaces1(self):
        self.Test(
            # Not using textwrap.dedent so tabs can be embedded
            "1\n  2\n3\n\t4\n\t5\n\t 6\n\t 7\n",
            [
                LineInfo(0, 1, 0, 1, []),                   # 1
                LineInfo(2, 5, 4, 5, [LineInfo.WhitespaceRange(2, 4)], None, 2),          # 2
                LineInfo(6, 7, 6, 7, [], 1, None),          # 3
                LineInfo(8, 10, 9, 10, [LineInfo.WhitespaceRange(8, 9)], None, 100),      # 4
                LineInfo(11, 13, 12, 13, [LineInfo.WhitespaceRange(11, 12)]),               # 5
                LineInfo(14, 17, 16, 17, [LineInfo.WhitespaceRange(14, 16)], None, 101),    # 6
                LineInfo(18, 21, 20, 21, [LineInfo.WhitespaceRange(18, 20)]),               # 7
                LineInfo(22, 22, 22, 22, [], 2, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_TabsVsSpaces2(self):
        self.Test(
            # Not using textwrap.dedent so tabs can be embedded
            "1\n  2\n3\n\t4\n\t5\n \t6\n \t7\n",
            [
                LineInfo(0, 1, 0, 1, []),                   # 1
                LineInfo(2, 5, 4, 5, [LineInfo.WhitespaceRange(2, 4)], None, 2),          # 2
                LineInfo(6, 7, 6, 7, [], 1, None),          # 3
                LineInfo(8, 10, 9, 10, [LineInfo.WhitespaceRange(8, 9)], None, 100),      # 4
                LineInfo(11, 13, 12, 13, [LineInfo.WhitespaceRange(11, 12)]),               # 5
                LineInfo(14, 17, 16, 17, [LineInfo.WhitespaceRange(14, 16)], None, 201),    # 6
                LineInfo(18, 21, 20, 21, [LineInfo.WhitespaceRange(18, 20)]),               # 7
                LineInfo(22, 22, 22, 22, [], 2, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_NewlineAdded(self):
        assert Normalize("123") == NormalizedContent.Create("123\n", 4, [LineInfo(0, 3, 0, 3, [])])

    # ----------------------------------------------------------------------
    def test_TabAndSpaceMix(self):
        with pytest.raises(InvalidTabsAndSpacesError) as ex:
            Normalize("   One\n\t\t\tTwo\n")

        assert ex.value.Line == 2
        assert ex.value.Column == 4

        with pytest.raises(InvalidTabsAndSpacesError) as ex:
            Normalize("if True:\n  \tone\n \t two")

        assert ex.value.Line == 3
        assert ex.value.Column == 4

    # ----------------------------------------------------------------------
    def test_MultilineUniformToken(self):
        self.Test(
            textwrap.dedent(
                """\
                if True:
                    !!!
                    One
                        Two
                  Three
                    Four
                    !!!

                    StatementA
                StatementB
                """,
            ),
            [
                LineInfo(0, 8, 0, 8, [LineInfo.WhitespaceRange(2, 3)]),
                LineInfo(9, 16, 13, 16, [LineInfo.WhitespaceRange(9, 13)], None, 4),
                LineInfo(17, 24, 21, 24, [LineInfo.WhitespaceRange(17, 21)]),
                LineInfo(25, 36, 33, 36, [LineInfo.WhitespaceRange(25, 33)]),
                LineInfo(37, 44, 39, 44, [LineInfo.WhitespaceRange(37, 39)]),
                LineInfo(45, 53, 49, 53, [LineInfo.WhitespaceRange(45, 49)]),
                LineInfo(54, 61, 58, 61, [LineInfo.WhitespaceRange(54, 58)]),
                LineInfo(62, 62, 62, 62, []),
                LineInfo(63, 77, 67, 77, [LineInfo.WhitespaceRange(63, 67)]),
                LineInfo(78, 88, 78, 88, [], 1, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_MultilineDifferntToken(self):
        self.Test(
            textwrap.dedent(
                """\
                if True:
                    !!!
                    One
                        Two
                  Three
                    Four
                    >>>

                    StatementA
                StatementB
                """,
            ),
            [
                LineInfo(0, 8, 0, 8, [LineInfo.WhitespaceRange(2, 3)]),
                LineInfo(9, 16, 13, 16, [LineInfo.WhitespaceRange(9, 13)], None, 4),
                LineInfo(17, 24, 21, 24, [LineInfo.WhitespaceRange(17, 21)], ),
                LineInfo(25, 36, 33, 36, [LineInfo.WhitespaceRange(25, 33)]),
                LineInfo(37, 44, 39, 44, [LineInfo.WhitespaceRange(37, 39)]),
                LineInfo(45, 53, 49, 53, [LineInfo.WhitespaceRange(45, 49)]),
                LineInfo(54, 61, 58, 61, [LineInfo.WhitespaceRange(54, 58)]),
                LineInfo(62, 62, 62, 62, []),
                LineInfo(63, 77, 67, 77, [LineInfo.WhitespaceRange(63, 67)]),
                LineInfo(78, 88, 78, 88, [], 1, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_MultilineMultipartToken(self):
        self.Test(
            textwrap.dedent(
                """\
                if True:
                    <<<!!!
                    One
                        Two
                  Three
                    Four
                    !!!>>>

                    StatementA
                StatementB
                """,
            ),
            [
                LineInfo(0, 8, 0, 8, [LineInfo.WhitespaceRange(2, 3)]),
                LineInfo(9, 19, 13, 19, [LineInfo.WhitespaceRange(9, 13)], None, 4),
                LineInfo(20, 27, 24, 27, [LineInfo.WhitespaceRange(20, 24)], ),
                LineInfo(28, 39, 36, 39, [LineInfo.WhitespaceRange(28, 36)], ),
                LineInfo(40, 47, 42, 47, [LineInfo.WhitespaceRange(40, 42)], ),
                LineInfo(48, 56, 52, 56, [LineInfo.WhitespaceRange(48, 52)], ),
                LineInfo(57, 67, 61, 67, [LineInfo.WhitespaceRange(57, 61)], ),
                LineInfo(68, 68, 68, 68, [], ),
                LineInfo(69, 83, 73, 83, [LineInfo.WhitespaceRange(69, 73)], ),
                LineInfo(84, 94, 84, 94, [], 1, None),
            ],
        )

    # ----------------------------------------------------------------------
    def test_NoClosingMultilineTokenError(self):
        with pytest.raises(NoClosingMultilineTokenError) as ex:
            Normalize("\n    <<<\n    Never-ending\n")

        ex = ex.value

        assert ex.Line == 2
        assert ex.Column == 5

        with pytest.raises(NoClosingMultilineTokenError) as ex:
            Normalize(
                textwrap.dedent(
                    """\
                    <<<Invalid open
                    >>>
                    """,
                ),
            )

        ex = ex.value

        assert ex.Line == 2
        assert ex.Column == 1
