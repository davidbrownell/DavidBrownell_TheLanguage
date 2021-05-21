# ----------------------------------------------------------------------
# |
# |  RepeatStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-16 09:29:42
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for RepeatStatement.py"""

import os
import re
import textwrap

from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Normalize import Normalize
    from ..NormalizedIterator import NormalizedIterator
    from ..RepeatStatement import *
    from ..StandardStatement import StandardStatement

    from ..Token import (
        NewlineToken,
        RegexToken,
        Token,
    )


# ----------------------------------------------------------------------
class TestProperties(object):
    # ----------------------------------------------------------------------
    @staticmethod
    def CreateStatement(min_matches, max_matches):
        return RepeatStatement(
            StandardStatement([RegexToken("Word", re.compile(r"(?P<value>\S+)")), NewlineToken()]),
            min_matches,
            max_matches,
        )

    # ----------------------------------------------------------------------
    def test_InvalidCreation(self):
        with pytest.raises(AssertionError):
            RepeatStatement(None, 1, 2)
        with pytest.raises(AssertionError):
            self.CreateStatement(-1, 2)
        with pytest.raises(AssertionError):
            self.CreateStatement(10, 5)

    # ----------------------------------------------------------------------
    def test_Optional(self):
        statement = self.CreateStatement(0, 1)

        assert statement.IsOptional
        assert statement.IsOneOrMore == False
        assert statement.IsZeroOrMore == False
        assert statement.IsCollection == False

    # ----------------------------------------------------------------------
    def test_OneOrMore(self):
        statement = self.CreateStatement(1, None)

        assert statement.IsOptional == False
        assert statement.IsOneOrMore
        assert statement.IsZeroOrMore == False
        assert statement.IsCollection

    # ----------------------------------------------------------------------
    def test_ZeroOrMore(self):
        statement = self.CreateStatement(0, None)

        assert statement.IsOptional == False
        assert statement.IsOneOrMore == False
        assert statement.IsZeroOrMore
        assert statement.IsCollection

    # ----------------------------------------------------------------------
    def test_Collection(self):
        statement = self.CreateStatement(1, 10)

        assert statement.IsOptional == False
        assert statement.IsOneOrMore == False
        assert statement.IsZeroOrMore == False
        assert statement.IsCollection


# ----------------------------------------------------------------------
class TestStandard(object):
    _word_token                             = RegexToken("Word Token", re.compile(r"(?P<value>[a-z]+)"))
    _word_statement                         = StandardStatement([_word_token, NewlineToken()])

    _optional_statement                     = RepeatStatement(_word_statement, 0, 1)
    _one_or_more_statement                  = RepeatStatement(_word_statement, 1, None)
    _zero_or_more_statement                 = RepeatStatement(_word_statement, 0, None)
    _collection_statement                   = RepeatStatement(_word_statement, 2, 2)

    # ----------------------------------------------------------------------
    @staticmethod
    @pytest.fixture
    def execution_mock():
        mock = Mock()

        mock.executor = ThreadPoolExecutor()
        mock.Enqueue = lambda funcs: [mock.executor.submit(func) for func in funcs]

        return mock

    # ----------------------------------------------------------------------
    def test_OptionalNoMatchNoContent(self, execution_mock):
        result = self._optional_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\

                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 1
        assert result.Iter.Column == 1
        assert result.Results == []

    # ----------------------------------------------------------------------
    def test_OptionalNoMatchContent(self, execution_mock):
        result = self._optional_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        12345
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 1
        assert result.Iter.Column == 1
        assert result.Results == []

    # ----------------------------------------------------------------------
    def test_OptionalMatchSingleContent(self, execution_mock):
        result = self._optional_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        abcdef
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 1
        assert result.Results[0].Statement == self._word_statement

        assert len(result.Results[0].Results) == 2
        assert result.Results[0].Results[0].Value.Match.group("value") == "abcdef"
        assert result.Results[0].Results[1].Value == Token.NewlineMatch(6, 7)

    # ----------------------------------------------------------------------
    def test_OptionalMatchMultipleContent(self, execution_mock):
        result = self._optional_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        abcdef
                        ghijkl
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 1
        assert result.Results[0].Statement == self._word_statement

        assert len(result.Results[0].Results) == 2
        assert result.Results[0].Results[0].Value.Match.group("value") == "abcdef"
        assert result.Results[0].Results[1].Value == Token.NewlineMatch(6, 7)

    # ----------------------------------------------------------------------
    def test_OneOrMoreOneMatch(self, execution_mock):
        result = self._one_or_more_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        abcdef
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 1
        assert result.Results[0].Statement == self._word_statement

        assert len(result.Results[0].Results) == 2
        assert result.Results[0].Results[0].Value.Match.group("value") == "abcdef"
        assert result.Results[0].Results[1].Value == Token.NewlineMatch(6, 7)

    # ----------------------------------------------------------------------
    def test_OneOrMoreMoreMatch(self, execution_mock):
        result = self._one_or_more_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        abcdef
                        ghijkl
                        mno
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 4
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Statement == self._word_statement

        assert len(result.Results[0].Results) == 2
        assert result.Results[0].Results[0].Value.Match.group("value") == "abcdef"
        assert result.Results[0].Results[1].Value == Token.NewlineMatch(6, 7)

        assert result.Results[1].Statement == self._word_statement

        assert len(result.Results[1].Results) == 2
        assert result.Results[1].Results[0].Value.Match.group("value") == "ghijkl"
        assert result.Results[1].Results[1].Value == Token.NewlineMatch(13, 14)

        assert result.Results[2].Statement == self._word_statement

        assert len(result.Results[2].Results) == 2
        assert result.Results[2].Results[0].Value.Match.group("value") == "mno"
        assert result.Results[2].Results[1].Value == Token.NewlineMatch(17, 18)

    # ----------------------------------------------------------------------
    def test_OneOrMoreNoMatch(self, execution_mock):
        result = self._one_or_more_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        123456
                        abcdef
                        ghijkl
                        mno
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success == False
        assert result.Iter.Line == 1
        assert result.Iter.Column == 1
        assert result.Results == []

    # ----------------------------------------------------------------------
    def test_ZeroOrMoreOneMatch(self, execution_mock):
        result = self._zero_or_more_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        abcdef
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 1
        assert result.Results[0].Statement == self._word_statement

        assert len(result.Results[0].Results) == 2
        assert result.Results[0].Results[0].Value.Match.group("value") == "abcdef"
        assert result.Results[0].Results[1].Value == Token.NewlineMatch(6, 7)

    # ----------------------------------------------------------------------
    def test_ZeroOrMoreMoreMatch(self, execution_mock):
        result = self._zero_or_more_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        abcdef
                        ghijkl
                        mno
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 4
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Statement == self._word_statement

        assert len(result.Results[0].Results) == 2
        assert result.Results[0].Results[0].Value.Match.group("value") == "abcdef"
        assert result.Results[0].Results[1].Value == Token.NewlineMatch(6, 7)

        assert result.Results[1].Statement == self._word_statement

        assert len(result.Results[1].Results) == 2
        assert result.Results[1].Results[0].Value.Match.group("value") == "ghijkl"
        assert result.Results[1].Results[1].Value == Token.NewlineMatch(13, 14)

        assert result.Results[2].Statement == self._word_statement

        assert len(result.Results[2].Results) == 2
        assert result.Results[2].Results[0].Value.Match.group("value") == "mno"
        assert result.Results[2].Results[1].Value == Token.NewlineMatch(17, 18)

    # ----------------------------------------------------------------------
    def test_ZeroOrMoreNoMatch(self, execution_mock):
        result = self._zero_or_more_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        123456
                        abcdef
                        ghijkl
                        mno
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 1
        assert result.Iter.Column == 1
        assert result.Results == []

    # ----------------------------------------------------------------------
    def test_CollectionMatch(self, execution_mock):
        result = self._collection_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        abcdef
                        ghi
                        mno
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 3
        assert result.Iter.Column == 1

        assert len(result.Results) == 2

        assert result.Results[0].Statement == self._word_statement

        assert len(result.Results[0].Results) == 2
        assert result.Results[0].Results[0].Value.Match.group("value") == "abcdef"
        assert result.Results[0].Results[1].Value == Token.NewlineMatch(6, 7)

        assert result.Results[1].Statement == self._word_statement

        assert len(result.Results[1].Results) == 2
        assert result.Results[1].Results[0].Value.Match.group("value") == "ghi"
        assert result.Results[1].Results[1].Value == Token.NewlineMatch(10, 11)
