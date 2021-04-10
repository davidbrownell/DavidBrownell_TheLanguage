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
    def test_Standard(self):
        li = LineInfo(1, (1, 2), 3, 4, 5)

        assert li.Offset == 1
        assert li.NewIndentation == (1, 2)
        assert li.NumDedents == 3
        assert li.StartPos == 4
        assert li.EndPos == 5

        assert li == li

    # ----------------------------------------------------------------------
    def test_Errors(self):
        for args in [
            (-1, None, 0, 0, 0),            # Invalid offset
            (0, (1, 0), 0, 0, 0),           # Invalid first indentation value
            (1, (1, 0), 0, 0, 0),           # invalid second indentation value
            (1, None, -1, 0, 0),            # Invalid dedent
            (1, None, 0, 0, 0),             # Invalid startpos
            (1, None, 0, 1, 0),             # Invalid endpos
        ]:
            with pytest.raises(AssertionError):
                LineInfo(*args)


# ----------------------------------------------------------------------
class TestNormalizeResult(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        result = NormalizeResult("hello", 5, [LineInfo(1, (1, 2), 3, 4, 5)])

        assert result.Content == "hello"
        assert result.ContentLen == 5
        assert result.LineInfos == [LineInfo(1, (1, 2), 3, 4, 5)]

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
                NormalizeResult(*args)


# ----------------------------------------------------------------------
class TestNormalize(object):
    # ----------------------------------------------------------------------
    @staticmethod
    def Test(content, line_infos):
        assert Normalize(content) == NormalizeResult(content, len(content), line_infos)

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
                LineInfo(0, None, 0, 0, 1),
                LineInfo(2, None, 0, 2, 4),
                LineInfo(5, None, 0, 5, 8),
            ],
        )

        # Indent
        self.Test(
            textwrap.dedent(
                """\
                1
                    22
                        333
                """,
            ),
            [
                LineInfo(0, None, 0, 0, 1),
                LineInfo(2, (2, 6), 0, 6, 8),
                LineInfo(9, (9, 17), 0, 17, 20),
                LineInfo(21, None, 2, 21, 21),
            ],
        )

        # With dedents
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
                LineInfo(0, None, 0, 0, 1),
                LineInfo(2, (2, 6), 0, 6, 8),
                LineInfo(9, (9, 17), 0, 17, 20),
                LineInfo(21, None, 1, 25, 29),
                LineInfo(30, None, 1, 30, 35),
            ],
        )

        # Trailing whitespace
        self.Test(
            # Not using textwrap.dedent as the editor removes the trailing whitespace
            "12  \n 34\n",
            [
                LineInfo(0, None, 0, 0, 2),
                LineInfo(5, (5, 6), 0, 6, 8),
                LineInfo(9, None, 1, 9, 9),
            ],
        )

        # Empty line
        self.Test(
            # Not using textwrap.dedent as the editor removes the empty whitespace
            "12\n\n34\n",
            [
                LineInfo(0, None, 0, 0, 2),
                LineInfo(3, None, 0, 3, 3),
                LineInfo(4, None, 0, 4, 6),
            ],
        )

        # Spaces on empty line
        self.Test(
            # Not using textwrap.dedent as the editor removes the empty whitespace
            "12\n    \n34\n",
            [
                LineInfo(0, None, 0, 0, 2),
                LineInfo(3, None, 0, 7, 7),
                LineInfo(8, None, 0, 8, 10),
            ],
        )

        # Spaces on empty line (with matching indent)
        self.Test(
            # Not using textwrap.dedent as the editor removes the empty whitespace
            "    12\n    \n34\n",
            [
                LineInfo(0, (0, 4), 0, 4, 6),
                LineInfo(7, None, 0, 11, 11),
                LineInfo(12, None, 1, 12, 14),
            ],
        )

        # Tabs vs. spaces
        self.Test(
            # Not using textwrap.dedent so tabs can be embedded
            "1\n  2\n3\n\t4\n\t5\n\t 6\n\t 7\n",
            [
                LineInfo(0, None, 0, 0, 1),             # 1
                LineInfo(2, (2, 4), 0, 4, 5),           # 2
                LineInfo(6, None, 1, 6, 7),             # 3
                LineInfo(8, (8, 9), 0, 9, 10),          # 4
                LineInfo(11, None, 0, 12, 13),          # 5
                LineInfo(14, (14, 16), 0, 16, 17),      # 6
                LineInfo(18, None, 0, 20, 21),          # 7
                LineInfo(22, None, 2, 22, 22),
            ],
        )

        # Tabs vs. spaces
        self.Test(
            # Not using textwrap.dedent so tabs can be embedded
            "1\n  2\n3\n\t4\n\t5\n \t6\n \t7\n",
            [
                LineInfo(0, None, 0, 0, 1),             # 1
                LineInfo(2, (2, 4), 0, 4, 5),           # 2
                LineInfo(6, None, 1, 6, 7),             # 3
                LineInfo(8, (8, 9), 0, 9, 10),          # 4
                LineInfo(11, None, 0, 12, 13),          # 5
                LineInfo(14, (14, 16), 0, 16, 17),      # 6
                LineInfo(18, None, 0, 20, 21),          # 7
                LineInfo(22, None, 2, 22, 22),
            ],
        )

    # ----------------------------------------------------------------------
    def test_NewlineAdded(self):
        assert Normalize("123") == NormalizeResult("123\n", 4, [LineInfo(0, None, 0, 0, 3)])

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
