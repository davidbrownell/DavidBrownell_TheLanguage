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
    def test_SingleLine(self):
        assert Normalize(None, "single line") == (
            ["single line"],
            [Indentation(0, 0)],
        )

    # ----------------------------------------------------------------------
    def test_MultipleLines(self):
        assert Normalize(
            None,
            textwrap.dedent(
                """\
                first line
                second line
                trailing
                """,
            ).rstrip(),
        ) == (
            [
                "first line",
                "second line",
                "trailing",
            ],
            [
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
            ],
        )

    # ----------------------------------------------------------------------
    def test_Indentation(self):
        # With spaces
        assert Normalize(
            None,
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
        ) == (
            [
                "1",
                "  2",
                "    3",
                "      4",
                "    5",
                "  6",
                "    7",
                "8",
            ],
            [
                Indentation(0, 0),
                Indentation(2, 2),
                Indentation(4, 4),
                Indentation(6, 6),
                Indentation(4, 4),
                Indentation(2, 2),
                Indentation(4, 4),
                Indentation(0, 0),
            ],
        )

        # With tabs
        assert Normalize(
            None,
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
        ) == (
            [
                "1",
                "\t2",
                "\t\t3",
                "\t\t\t4",
                "\t\t5",
                "\t6",
                "\t\t7",
                "8",
            ],
            [
                Indentation(0, 0),
                Indentation(2, 1),
                Indentation(4, 2),
                Indentation(6, 3),
                Indentation(4, 2),
                Indentation(2, 1),
                Indentation(4, 2),
                Indentation(0, 0),
            ],
        )

    # ----------------------------------------------------------------------
    def test_EmptyLines(self):
        assert Normalize(
            None,
            textwrap.dedent(
                """\
                first line

                third line
                last line
                """,
            ),
        ) == (
            [
                "first line",
                "",
                "third line",
                "last line",
            ],
            [
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
            ],
        )

    # ----------------------------------------------------------------------
    def test_BlankLines(self):
        assert Normalize(
            None,
            # Note: not using textwrap.dedent here as my helpful editor keeps removing the empty whitespace in the blank line
            "first line\n    \nlast line\n",
        ) == (
            [
                "first line",
                "",
                "last line",
            ],
            [
                Indentation(0, 0),
                Indentation(4, 4),
                Indentation(0, 0),
            ],
        )

    # ----------------------------------------------------------------------
    def test_CommentExtraction(self):
        assert Normalize(
            None,
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
        ) == (
            [
                "0",
                "1",
                "2",
                "3",
                "    4",
                "",
                "5",
            ],
            [
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(4, 4),
                Indentation(0, 0),
                Indentation(0, 0),
            ],
        )

        assert Normalize(
            None,
            # Note: not using textwrap.dedent here as my helpful editor keeps removing the empty whitespace in the blank line
            "1\n    # a comment\n2",
        ) == (
            [
                "1",
                "",
                "2",
            ],
            [
                Indentation(0, 0),
                Indentation(4, 4),
                Indentation(0, 0),
            ],
        )

    # ----------------------------------------------------------------------
    def test_MultilineStrings(self):
        # Single line
        assert Normalize(
            None,
            textwrap.dedent(
                '''\
                Before
                    """
                    Single line
                    """
                After
                ''',
            ),
        ) == (
            [
                "Before",
                '"Single line"',
                "",
                "",
                "After",
            ],
            [
                Indentation(0, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(0, 0),
            ],
        )

        # Multi line
        assert Normalize(
            None,
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
        ) == (
            [
                "Before",
                '"Line 1\n  Line 2\n    Line 3"',
                "",
                "",
                "",
                "",
                "After",
            ],
            [
                Indentation(0, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(0, 0),
            ],
        )

        # Content with Empty lines
        assert Normalize(
            None,
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
        ) == (
            [
                "Before",
                '"Line 1\n\n    Line 3"',
                "",
                "",
                "",
                "",
                "After",
            ],
            [
                Indentation(0, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(0, 0),
            ],
        )

        # first line has whitespace
        assert Normalize(
            None,
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
        ) == (
            [
                "Before",
                '"  Line 1\n  Line 2\n    Line 3"',
                "",
                "",
                "",
                "",
                "After",
            ],
            [
                Indentation(0, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(0, 0),
            ],
        )

        # last line has whitespace
        assert Normalize(
            None,
            'Before\n"""\nLine 1\n  Line 2\n  \nLine 3\n"""\nAfter',
        ) == (
            [
                "Before",
                '"Line 1\n  Line 2\n  \nLine 3"',
                "",
                "",
                "",
                "",
                "",
                "After",
            ],
            [
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
            ],
        )

        # Trailing line
        assert Normalize(
            None,
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
        ) == (
            [
                "Before",
                '"Line 1\n  Line 2\n    Line 3\n\n"',
                "",
                "",
                "",
                "",
                "",
                "",
                "After",
            ],
            [
                Indentation(0, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(0, 0),
            ],
        )

        # No content
        assert Normalize(
            None,
            textwrap.dedent(
                '''\
                Before
                    """
                    """
                After
                ''',
            ),
        ) == (
            [
                "Before",
                '""',
                "",
                "After",
            ],
            [
                Indentation(0, 0),
                Indentation(4, 0),
                Indentation(4, 0),
                Indentation(0, 0),
            ],
        )

        # Escaped quotes
        assert Normalize(
            None,
            textwrap.dedent(
                '''\
                Before
                """
                The "content"!
                """
                After
                ''',
            ),
        ) == (
            [
                "Before",
                '"The \\"content\\"!"',
                "",
                "",
                "After",
            ],
            [
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
                Indentation(0, 0),
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
