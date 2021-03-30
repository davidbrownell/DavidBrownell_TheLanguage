# ----------------------------------------------------------------------
# |
# |  Normalize_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-03-27 11:00:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Normalize"""

import os
import sys
import textwrap

from typing import List, Tuple

import pytest

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

sys.path.insert(0, os.path.join(_script_dir, ".."))
with CallOnExit(lambda: sys.path.pop(0)):
    from Errors import *
    from Normalize import *

# ----------------------------------------------------------------------
class TestNormalize:
    # ----------------------------------------------------------------------
    @staticmethod
    def Test(
        content: str,
        expected_items: List[Tuple[str, int]],
    ):
        results = Normalize("source", content)

        for result, expected in zip(results, expected_items):
            if isinstance(result.Value, tuple):
                assert content[result.Value[0]:result.Value[1]] == expected[0]

            assert result.Indentation == expected[1]

        assert len(results) == len(expected_items)

    # ----------------------------------------------------------------------
    def test_SingleLine(self):
        self.Test("single line", [("single line", 0)])

    # ----------------------------------------------------------------------
    def test_MultipleLines(self):
        self.Test(
            textwrap.dedent(
                """\
                first line
                second line
                trailing
                """,
            ),
            [
                ("first line", 0),
                ("second line", 0),
                ("trailing", 0),
            ],
        )

    # ----------------------------------------------------------------------
    def test_Indentation(self):
        # With spaces
        self.Test(
            textwrap.dedent(
                """\
                1
                  2
                    3
                      4
                    5
                  6
                    7
                8
                """,
            ),
            [
                ("1", 0),
                ("2", 2),
                ("3", 4),
                ("4", 6),
                ("5", 4),
                ("6", 2),
                ("7", 4),
                ("8", 0),
            ],
        )

        # With tabs
        self.Test(
            textwrap.dedent(
                """\
                1
                \t2
                \t\t3
                \t\t\t4
                \t\t5
                \t6
                \t\t7
                8
                """,
            ),
            [
                ("1", 0),
                ("2", 2),
                ("3", 4),
                ("4", 6),
                ("5", 4),
                ("6", 2),
                ("7", 4),
                ("8", 0),
            ],
        )

    # ----------------------------------------------------------------------
    def test_EmptyLines(self):
        self.Test(
            textwrap.dedent(
                """\
                first line

                third line
                last line
                """,
            ),
            [
                ("first line", 0),
                ("", 0),
                ("third line", 0),
                ("last line", 0),
            ],
        )

    # ----------------------------------------------------------------------
    def test_BlankLines(self):
        self.Test(
            # Note: not using textwrap.dedent here as my helpful editor keeps removing the empty whitespace in the blank line
            "first line\n    \nlast line\n",
            [
                ("first line", 0),
                ("", 4),
                ("last line", 0),
            ],
        )

    # ----------------------------------------------------------------------
    def test_CommentExtraction(self):
        self.Test(
            textwrap.dedent(
                """\
                0 # the comment
                1# comment
                2 #comment
                3#comment
                    4
                # comment
                5
                """,
            ),
            [
                ("0", 0),
                ("1", 0),
                ("2", 0),
                ("3", 0),
                ("4", 4),
                ("", 0),
                ("5", 0),
            ],
        )

        self.Test(
            # Note: not using textwrap.dedent here as my helpful editor keeps removing the empty whitespace in the blank line
            "1\n    # a comment\n2",
            [
                ("1", 0),
                ("", 4),
                ("2", 0),
            ],
        )

    # ----------------------------------------------------------------------
    def test_MultilineStrings(self):
        # Single line
        self.Test(
            textwrap.dedent(
                '''\
                Before
                    """
                    Single line
                    """
                After
                ''',
            ),
            [
                ("Before", 0),
                ('"Single line"', 4),
                ("", 4),
                ("", 4),
                ("After", 0),
            ],
        )

        # Multi line
        self.Test(
            textwrap.dedent(
                '''\
                Before
                    """
                    Line 1
                      Line 2
                        Line 3
                    """
                    After
                Final
                ''',
            ),
            [
                ("Before", 0),
                ('"Line 1\n  Line 2\n    Line 3"', 4),
                ("", 4),
                ("", 4),
                ("", 4),
                ("", 4),
                ("After", 4),
                ("Final", 0),
            ],
        )

        # Content with Empty lines
        self.Test(
            textwrap.dedent(
                '''\
                Before
                    """
                    Line 1

                        Line 3
                    """
                After
                ''',
            ),
            [
                ("Before", 0),
                ('"Line 1\n\n    Line 3"', 4),
                ("", 4),
                ("", 4),
                ("", 4),
                ("", 4),
                ("After", 0),
            ],
        )

        # first line has whitespace
        self.Test(
            textwrap.dedent(
                '''\
                Before
                    """
                      Line 1
                      Line 2
                        Line 3
                    """
                After
                ''',
            ),
            [
                ("Before", 0),
                ('"  Line 1\n  Line 2\n    Line 3"', 4),
                ("", 4),
                ("", 4),
                ("", 4),
                ("", 4),
                ("After", 0),
            ],
        )

        # last line has whitespace
        self.Test(
            'Before\n"""\nLine 1\n  Line 2\n  \nLine 3\n"""\nAfter',
            [
                ("Before", 0),
                ('"Line 1\n  Line 2\n  \nLine 3"', 0),
                ("", 0),
                ("", 0),
                ("", 0),
                ("", 0),
                ("", 0),
                ("After", 0),
            ],
        )

        # Trailing line
        self.Test(
            textwrap.dedent(
                '''\
                Before
                    """
                    Line 1
                      Line 2
                        Line 3


                    """
                After
                ''',
            ),
            [
                ("Before", 0),
                ('"Line 1\n  Line 2\n    Line 3\n\n"', 4),
                ("", 4),
                ("", 4),
                ("", 4),
                ("", 4),
                ("", 4),
                ("", 4),
                ("After", 0),
            ],
        )

        # No content
        self.Test(
            textwrap.dedent(
                '''\
                Before
                    """
                    """
                After
                ''',
            ),
            [
                ("Before", 0),
                ('""', 4),
                ("", 4),
                ("After", 0),
            ],
        )

        # Escaped quotes
        self.Test(
            textwrap.dedent(
                '''\
                Before
                """
                The "content"!
                """
                    After
                ''',
            ),
            [
                ("Before", 0),
                ('"The \\"content\\"!"', 0),
                ("", 0),
                ("", 0),
                ("After", 4),
            ],
        )

    # ----------------------------------------------------------------------
    class TestMultilineCommentErrors:
        # ----------------------------------------------------------------------
        @staticmethod
        def Impl(expected_exception_type, content):
            with pytest.raises(expected_exception_type) as ex:
                Normalize("foo", content)

            ex = ex.value

            assert ex.Source == "foo"
            return ex

        # ----------------------------------------------------------------------
        def test_MissingTerminator(self):
            ex = self.Impl(
                MissingMultilineStringTerminatorError,
                textwrap.dedent(
                    '''\
                    Before
                        """
                    After
                    ''',
                ),
            )

            assert ex.Message == "The closing token for this multiline string was not found."
            assert ex.Line == 2
            assert ex.Column == 5

        # ----------------------------------------------------------------------
        def test_InvalidOpeningToken(self):
            ex = self.Impl(
                MissingMultilineTokenNewlineSuffixError,
                textwrap.dedent(
                    '''
                    Before
                        """After
                        """
                    ''',
                ),
            )

            assert ex.Message == "This multiline string token must be followed by a newline."
            assert ex.Line == 2
            assert ex.Column == 8

        # ----------------------------------------------------------------------
        def test_InvalidClosingToken(self):
            ex = self.Impl(
                MissingMultilineTokenNewlineSuffixError,
                textwrap.dedent(
                    '''
                    Before
                        """
                        Content
                        """After
                    ''',
                ),
            )

            assert ex.Message == "This multiline string token must be followed by a newline."
            assert ex.Line == 4
            assert ex.Column == 8

        # ----------------------------------------------------------------------
        def test_InvalidPrefixes(self):
            expected_message = "The prefix for this multiline string is not valid; each line must be aligned with the opening token."

            # First line is dedented to col 1
            ex = self.Impl(
                InvalidMultilineStringPrefixError,
                textwrap.dedent(
                    '''\
                    Line 1
                        """
                    In comment
                        """
                    ''',
                ),
            )

            assert ex.Message == expected_message
            assert ex.Line == 3
            assert ex.Column == 1

            # First line is dedented to col 3
            ex = self.Impl(
                InvalidMultilineStringPrefixError,
                textwrap.dedent(
                    '''\
                    Line 1
                        """
                      In comment
                        """
                    ''',
                ),
            )

            assert ex.Message == expected_message
            assert ex.Line == 3
            assert ex.Column == 3

            # Terminator is dedented to col 1
            ex = self.Impl(
                InvalidMultilineStringPrefixError,
                textwrap.dedent(
                    '''\
                    Line 1
                        """
                        In comment
                    """
                    ''',
                ),
            )

            assert ex.Message == expected_message
            assert ex.Line == 4
            assert ex.Column == 1

            # Terminator is dedented to col 3
            ex = self.Impl(
                InvalidMultilineStringPrefixError,
                textwrap.dedent(
                    '''\
                    Line 1
                        """
                        In comment
                      """
                    ''',
                ),
            )

            assert ex.Message == expected_message
            assert ex.Line == 4
            assert ex.Column == 3

            # Whitespace, no content
            ex = self.Impl(
                InvalidMultilineStringPrefixError,
                '    """\n  \n    """\n',
            )

            assert ex.Message == expected_message
            assert ex.Line == 2
            assert ex.Column == 3

            # Mix of tabs and spaces
            ex = self.Impl(
                InvalidMultilineStringPrefixError,
                '    """\n    \n\tTest\n    """\n',
            )

            assert ex.Message == expected_message
            assert ex.Line == 3
            assert ex.Column == 2
