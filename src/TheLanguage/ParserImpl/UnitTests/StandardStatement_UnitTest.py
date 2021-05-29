# ----------------------------------------------------------------------
# |
# |  StandardStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-09 08:34:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for StandardStatement.py"""

import os
import re
import textwrap

from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import pytest

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..StandardStatement import *
    from ..NormalizedIterator import NormalizedIterator
    from ..Normalize import Normalize
    from ..Token import *


# BugBug: Test ignore_whitespace

# ----------------------------------------------------------------------
class TestErrors(object):
    # ----------------------------------------------------------------------
    def test_InvalidName(self):
        with pytest.raises(AssertionError):
            NamedStandardStatement("", [NewlineToken()])

    # ----------------------------------------------------------------------
    def test_InvalidItems(self):
        with pytest.raises(AssertionError):
            StandardStatement([])

    # ----------------------------------------------------------------------
    def test_MissingClosingToken(self):
        with pytest.raises(AssertionError):
            StandardStatement([PushIgnoreWhitespaceControlToken()])

        with pytest.raises(AssertionError):
            StandardStatement([PushIgnoreWhitespaceControlToken(), PopIgnoreWhitespaceControlToken(), PushIgnoreWhitespaceControlToken()])

        with pytest.raises(AssertionError):
            StandardStatement([PushIgnoreWhitespaceControlToken(), PushIgnoreWhitespaceControlToken(), PopIgnoreWhitespaceControlToken()])

    # ----------------------------------------------------------------------
    def test_MissingOpeningToken(self):
        with pytest.raises(AssertionError):
            StandardStatement([PopIgnoreWhitespaceControlToken()])

        with pytest.raises(AssertionError):
            StandardStatement([PushIgnoreWhitespaceControlToken(), PopIgnoreWhitespaceControlToken(), PopIgnoreWhitespaceControlToken()])

# ----------------------------------------------------------------------
@pytest.fixture
def execution_mock():
    mock = Mock()

    mock.executor = ThreadPoolExecutor()
    mock.Enqueue = lambda funcs: [mock.executor.submit(func) for func in funcs]

    return mock

# ----------------------------------------------------------------------
class TestSingleLine(object):
    _word_token                         = RegexToken("Word", re.compile(r"(?P<value>\S+)"))
    _statement                          = NamedStandardStatement("Standard", [_word_token, _word_token, NewlineToken()])

    # ----------------------------------------------------------------------
    def test_Properties(self):
        assert self._statement.Name == "Standard"
        assert self._statement.Items == [self._word_token, self._word_token, NewlineToken()]

    # ----------------------------------------------------------------------
    def test_SingleSpaceSep(self, execution_mock):
        iter = NormalizedIterator(Normalize("one two"))

        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

        result = self._statement.Parse(iter, execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (3, 4)
        assert result.Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 8
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace is None
        assert result.Results[2].Value == Token.NewlineMatch(7, 8)
        assert result.Results[2].Iter.Line == 2
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == False

        # Iterator is not modified
        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

    # ----------------------------------------------------------------------
    def test_MultipleSpaceSep(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("one   two")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (3, 6)
        assert result.Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 10
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace is None
        assert result.Results[2].Value == Token.NewlineMatch(9, 10)
        assert result.Results[2].Iter.Line == 2
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_TabSep(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("one\ttwo")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (3, 4)
        assert result.Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 8
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace is None
        assert result.Results[2].Value == Token.NewlineMatch(7, 8)
        assert result.Results[2].Iter.Line == 2
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_MultipleTabSep(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("one\t\t\ttwo")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (3, 6)
        assert result.Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 10
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace is None
        assert result.Results[2].Value == Token.NewlineMatch(9, 10)
        assert result.Results[2].Iter.Line == 2
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_TrailingSpace(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("one two ")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (3, 4)
        assert result.Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 8
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace == (7, 8)
        assert result.Results[2].Value == Token.NewlineMatch(8, 9)
        assert result.Results[2].Iter.Line == 2
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_MultipleTrailingSpace(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("one two   ")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (3, 4)
        assert result.Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 8
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace == (7, 10)
        assert result.Results[2].Value == Token.NewlineMatch(10, 11)
        assert result.Results[2].Iter.Line == 2
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_TrailingTab(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("one two\t")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (3, 4)
        assert result.Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 8
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace == (7, 8)
        assert result.Results[2].Value == Token.NewlineMatch(8, 9)
        assert result.Results[2].Iter.Line == 2
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_MultipleTrailingTabs(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("one two\t\t\t\t")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (3, 4)
        assert result.Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 8
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace == (7, 11)
        assert result.Results[2].Value == Token.NewlineMatch(11, 12)
        assert result.Results[2].Iter.Line == 2
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_MultipleLines(self, execution_mock):
        iter = NormalizedIterator(
            Normalize(
                textwrap.dedent(
                    """\
                    one two
                    three four
                    """,
                ),
            ),
        )

        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

        # First Line
        result = self._statement.Parse(iter, execution_mock)

        assert result.Success

        assert result.Iter.AtEnd() == False
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (3, 4)
        assert result.Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 8
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace is None
        assert result.Results[2].Value == Token.NewlineMatch(7, 8)
        assert result.Results[2].Iter.Line == 2
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == False

        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

        iter = result.Iter

        # Second Line
        result = self._statement.Parse(iter, execution_mock)

        assert result.Success

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 3
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "three"
        assert result.Results[0].Iter.Line == 2
        assert result.Results[0].Iter.Column == 6
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (13, 14)
        assert result.Results[1].Value.Match.group("value") == "four"
        assert result.Results[1].Iter.Line == 2
        assert result.Results[1].Iter.Column == 11
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace is None
        assert result.Results[2].Value == Token.NewlineMatch(18, 19)
        assert result.Results[2].Iter.Line == 3
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == False

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

    # ----------------------------------------------------------------------
    def test_TrailingWhitespace(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("one two\n\n  \n    \n")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 5
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (3, 4)
        assert result.Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 8
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace is None
        assert result.Results[2].Value == Token.NewlineMatch(7, 17)
        assert result.Results[2].Iter.Line == 5
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_NoMatch(self, execution_mock):
        iter = NormalizedIterator(Normalize("one two three"))

        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

        result = self._statement.Parse(iter, execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success == False

        assert result.Iter.AtEnd() == False
        assert result.Iter.Line == 1
        assert result.Iter.Column == 8

        assert len(result.Results) == 2

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == self._word_token

        assert result.Results[1].Whitespace == (3, 4)
        assert result.Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 8
        assert result.Results[1].IsIgnored == False

        # Iterator is not modified
        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

# ----------------------------------------------------------------------
class TestIndentAndDedent(object):
    _word_token                         = RegexToken("Word", re.compile(r"(?P<value>\S+)"))

    _statement                          = StandardStatement(
        [
            _word_token,
            NewlineToken(),
            IndentToken(),
            _word_token,
            NewlineToken(),
            _word_token,
            NewlineToken(),
            DedentToken(),
        ],
    )

    # ----------------------------------------------------------------------
    def test_Match(self, execution_mock):
        result = self._statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        one
                            two
                            three
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert execution_mock.OnIndent.call_count == 1
        assert execution_mock.OnDedent.call_count == 1
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success
        assert result.Iter.Line == 4
        assert result.Iter.Column == 1
        assert result.Iter.Offset == 22
        assert result.Iter.AtEnd()

        assert len(result.Results) == 8

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == NewlineToken()

        assert result.Results[1].Whitespace is None
        assert result.Results[1].Value == Token.NewlineMatch(3, 4)
        assert result.Results[1].Iter.Line == 2
        assert result.Results[1].Iter.Column == 1
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == IndentToken()

        assert result.Results[2].Whitespace is None
        assert result.Results[2].Value == Token.IndentMatch(4, 8, 4)
        assert result.Results[2].Iter.Line == 2
        assert result.Results[2].Iter.Column == 5
        assert result.Results[2].IsIgnored == False

        assert result.Results[3].Token == self._word_token

        assert result.Results[3].Whitespace is None
        assert result.Results[3].Value.Match.group("value") == "two"
        assert result.Results[3].Iter.Line == 2
        assert result.Results[3].Iter.Column == 8
        assert result.Results[3].IsIgnored == False

        assert result.Results[4].Token == NewlineToken()

        assert result.Results[4].Whitespace is None
        assert result.Results[4].Value == Token.NewlineMatch(11, 12)
        assert result.Results[4].Iter.Line == 3
        assert result.Results[4].Iter.Column == 1
        assert result.Results[4].IsIgnored == False

        assert result.Results[5].Token == self._word_token

        assert result.Results[5].Whitespace is None
        assert result.Results[5].Value.Match.group("value") == "three"
        assert result.Results[5].Iter.Line == 3
        assert result.Results[5].Iter.Column == 10
        assert result.Results[5].IsIgnored == False

        assert result.Results[6].Token == NewlineToken()

        assert result.Results[6].Whitespace is None
        assert result.Results[6].Value == Token.NewlineMatch(21, 22)
        assert result.Results[6].Iter.Line == 4
        assert result.Results[6].Iter.Column == 1
        assert result.Results[6].IsIgnored == False

        assert result.Results[7].Token == DedentToken()

        assert result.Results[7].Whitespace is None
        assert result.Results[7].Value == Token.DedentMatch()
        assert result.Results[7].Iter.Line == 4
        assert result.Results[7].Iter.Column == 1
        assert result.Results[7].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_NoMatch(self, execution_mock):
        result = self._statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        one
                            two
                                three
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        # The code stopped parsing after 'two', so only 1 indent was encountered and 0 dedents were
        # encountered
        assert execution_mock.OnIndent.call_count == 1
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success == False
        assert result.Iter.Line == 3
        assert result.Iter.Column == 1
        assert result.Iter.Offset == 12
        assert result.Iter.AtEnd() == False

        assert len(result.Results) == 5

        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Token == NewlineToken()

        assert result.Results[1].Whitespace is None
        assert result.Results[1].Value == Token.NewlineMatch(3, 4)
        assert result.Results[1].Iter.Line == 2
        assert result.Results[1].Iter.Column == 1
        assert result.Results[1].IsIgnored == False

        assert result.Results[2].Token == IndentToken()

        assert result.Results[2].Whitespace is None
        assert result.Results[2].Value == Token.IndentMatch(4, 8, 4)
        assert result.Results[2].Iter.Line == 2
        assert result.Results[2].Iter.Column == 5
        assert result.Results[2].IsIgnored == False

        assert result.Results[3].Token == self._word_token

        assert result.Results[3].Whitespace is None
        assert result.Results[3].Value.Match.group("value") == "two"
        assert result.Results[3].Iter.Line == 2
        assert result.Results[3].Iter.Column == 8
        assert result.Results[3].IsIgnored == False

        assert result.Results[4].Token == NewlineToken()

        assert result.Results[4].Whitespace is None
        assert result.Results[4].Value == Token.NewlineMatch(11, 12)
        assert result.Results[4].Iter.Line == 3
        assert result.Results[4].Iter.Column == 1
        assert result.Results[4].IsIgnored == False

# ----------------------------------------------------------------------
def test_FinishEarly(execution_mock):
    word_token = RegexToken("Word", re.compile(r"(?P<value>\S+)"))

    statement = StandardStatement([word_token, NewlineToken(), word_token])

    iter = NormalizedIterator(Normalize("one"))

    assert iter.Line == 1
    assert iter.Column == 1
    assert iter.Offset == 0

    result = statement.Parse(iter, execution_mock)

    assert execution_mock.OnIndent.call_count == 0
    assert execution_mock.OnDedent.call_count == 0
    assert execution_mock.OnInternalStatement.call_count == 0

    assert result.Success == False

    assert result.Iter.AtEnd()
    assert result.Iter.Line == 2
    assert result.Iter.Column == 1

    assert len(result.Results) == 2

    assert result.Results[0].Token == word_token

    assert result.Results[0].Whitespace is None
    assert result.Results[0].Value.Match.group("value") == "one"
    assert result.Results[0].Iter.Line == 1
    assert result.Results[0].Iter.Column == 4
    assert result.Results[0].IsIgnored == False

    assert result.Results[1].Token == NewlineToken()

    assert result.Results[1].Whitespace is None
    assert result.Results[1].Value == Token.NewlineMatch(3, 4)
    assert result.Results[1].Iter.Line == 2
    assert result.Results[1].Iter.Column == 1
    assert result.Results[1].IsIgnored == False

    # Iterator is not modified
    assert iter.Line == 1
    assert iter.Column == 1
    assert iter.Offset == 0

# ----------------------------------------------------------------------
class TestIgnoreWhitespace(object):
    _word_token                             = RegexToken("Word", re.compile(r"(?P<value>\S+)"))
    _lpar_token                             = RegexToken("lpar", re.compile(r"\("))
    _rpar_token                             = RegexToken("rpar", re.compile(r"\)"))

    _statement                              = StandardStatement(
        [
            _word_token,
            _lpar_token,
            PushIgnoreWhitespaceControlToken(),
            _word_token,
            _word_token,
            _word_token,
            _word_token,
            PopIgnoreWhitespaceControlToken(),
            _rpar_token,
            _word_token,
            NewlineToken(),
        ],
    )

    # ----------------------------------------------------------------------
    def test_MatchNoExtra(self, execution_mock):
        result = self._statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        one (


                            two

                                three
                            four
                                five

                        ) six
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 11
        assert result.Iter.Column == 1
        assert result.Iter.Offset == 60

        assert len(result.Results) == 20

        # Line 1
        assert result.Results[0].Token == self._word_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "one"
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 4
        assert result.Results[0].IsIgnored == False

        # lpar
        assert result.Results[1].Token == self._lpar_token

        assert result.Results[1].Whitespace == (3, 4)
        assert result.Results[1].Value.Match
        assert result.Results[1].Iter.Line == 1
        assert result.Results[1].Iter.Column == 6
        assert result.Results[1].IsIgnored == False

        # Line 2-3
        assert result.Results[2].Token == NewlineToken()

        assert result.Results[2].Whitespace is None
        assert result.Results[2].Value == Token.NewlineMatch(5, 8)
        assert result.Results[2].Iter.Line == 4
        assert result.Results[2].Iter.Column == 1
        assert result.Results[2].IsIgnored == True

        # Line 4
        assert result.Results[3].Token == IndentToken()

        assert result.Results[3].Whitespace is None
        assert result.Results[3].Value == Token.IndentMatch(8, 12, 4)
        assert result.Results[3].Iter.Line == 4
        assert result.Results[3].Iter.Column == 5
        assert result.Results[3].IsIgnored == True

        assert result.Results[4].Token == self._word_token

        assert result.Results[4].Whitespace is None
        assert result.Results[4].Value.Match.group("value") == "two"
        assert result.Results[4].Iter.Line == 4
        assert result.Results[4].Iter.Column == 8
        assert result.Results[4].IsIgnored == False

        # Line 5
        assert result.Results[5].Token == NewlineToken()

        assert result.Results[5].Whitespace is None
        assert result.Results[5].Value == Token.NewlineMatch(15, 17)
        assert result.Results[5].Iter.Line == 6
        assert result.Results[5].Iter.Column == 1
        assert result.Results[5].IsIgnored == True

        # Line 6
        assert result.Results[6].Token == IndentToken()

        assert result.Results[6].Whitespace is None
        assert result.Results[6].Value == Token.IndentMatch(17, 25, 8)
        assert result.Results[6].Iter.Line == 6
        assert result.Results[6].Iter.Column == 9
        assert result.Results[6].IsIgnored == True

        assert result.Results[7].Token == self._word_token

        assert result.Results[7].Whitespace is None
        assert result.Results[7].Value.Match.group("value") == "three"
        assert result.Results[7].Iter.Line == 6
        assert result.Results[7].Iter.Column == 14
        assert result.Results[7].IsIgnored == False

        assert result.Results[8].Token == NewlineToken()

        assert result.Results[8].Whitespace is None
        assert result.Results[8].Value == Token.NewlineMatch(30, 31)
        assert result.Results[8].Iter.Line == 7
        assert result.Results[8].Iter.Column == 1
        assert result.Results[8].IsIgnored == True

        # Line 7
        assert result.Results[9].Token == DedentToken()

        assert result.Results[9].Whitespace is None
        assert result.Results[9].Value == Token.DedentMatch()
        assert result.Results[9].Iter.Line == 7
        assert result.Results[9].Iter.Column == 5
        assert result.Results[9].IsIgnored == True

        assert result.Results[10].Token == self._word_token

        assert result.Results[10].Whitespace is None
        assert result.Results[10].Value.Match.group("value") == "four"
        assert result.Results[10].Iter.Line == 7
        assert result.Results[10].Iter.Column == 9
        assert result.Results[10].IsIgnored == False

        assert result.Results[11].Token == NewlineToken()

        assert result.Results[11].Whitespace is None
        assert result.Results[11].Value == Token.NewlineMatch(39, 40)
        assert result.Results[11].Iter.Line == 8
        assert result.Results[11].Iter.Column == 1
        assert result.Results[11].IsIgnored == True

        # Line 8
        assert result.Results[12].Token == IndentToken()

        assert result.Results[12].Whitespace is None
        assert result.Results[12].Value == Token.IndentMatch(40, 48, 8)
        assert result.Results[12].Iter.Line == 8
        assert result.Results[12].Iter.Column == 9
        assert result.Results[12].IsIgnored == True

        assert result.Results[13].Token == self._word_token

        assert result.Results[13].Whitespace is None
        assert result.Results[13].Value.Match.group("value") == "five"
        assert result.Results[13].Iter.Line == 8
        assert result.Results[13].Iter.Column == 13
        assert result.Results[13].IsIgnored == False

        assert result.Results[14].Token == NewlineToken()

        assert result.Results[14].Whitespace is None
        assert result.Results[14].Value == Token.NewlineMatch(52, 54)
        assert result.Results[14].Iter.Line == 10
        assert result.Results[14].Iter.Column == 1
        assert result.Results[14].IsIgnored == True

        # Line 10
        assert result.Results[15].Token == DedentToken()

        assert result.Results[15].Whitespace is None
        assert result.Results[15].Value == Token.DedentMatch()
        assert result.Results[15].Iter.Line == 10
        assert result.Results[15].Iter.Column == 1
        assert result.Results[15].IsIgnored == True

        assert result.Results[16].Token == DedentToken()

        assert result.Results[16].Whitespace is None
        assert result.Results[16].Value == Token.DedentMatch()
        assert result.Results[16].Iter.Line == 10
        assert result.Results[16].Iter.Column == 1
        assert result.Results[16].IsIgnored == True

        # rpar
        assert result.Results[17].Token == self._rpar_token

        assert result.Results[17].Whitespace is None
        assert result.Results[17].Value.Match
        assert result.Results[17].Iter.Line == 10
        assert result.Results[17].Iter.Column == 2
        assert result.Results[17].IsIgnored == False

        assert result.Results[18].Token == self._word_token

        assert result.Results[18].Whitespace == (55, 56)
        assert result.Results[18].Value.Match.group("value") == "six"
        assert result.Results[18].Iter.Line == 10
        assert result.Results[18].Iter.Column == 6
        assert result.Results[18].IsIgnored == False

        assert result.Results[19].Token == NewlineToken()

        assert result.Results[19].Whitespace is None
        assert result.Results[19].Value == Token.NewlineMatch(59, 60)
        assert result.Results[19].Iter.Line == 11
        assert result.Results[19].Iter.Column == 1
        assert result.Results[19].Iter.AtEnd()
        assert result.Results[19].IsIgnored == False

# ----------------------------------------------------------------------
def test_IgnoreControlTokens(execution_mock):
    # ----------------------------------------------------------------------
    @Interface.staticderived
    class MyControlToken(ControlTokenBase):
        Name                                = Interface.DerivedProperty("MyControlToken")

    # ----------------------------------------------------------------------

    control_token = MyControlToken()
    regex_token = RegexToken("test", re.compile("test"))

    result = StandardStatement(
        [
            control_token,
            regex_token,
        ],
    ).Parse(NormalizedIterator(Normalize("test")), execution_mock)

    assert execution_mock.OnIndent.call_count == 0
    assert execution_mock.OnDedent.call_count == 0
    assert execution_mock.OnInternalStatement.call_count == 0

    assert result.Success

    assert result.Iter.Line == 1
    assert result.Iter.Column == 5
    assert result.Iter.AtEnd() == False

    assert len(result.Results) == 1

    assert result.Results[0].Token == regex_token

    assert result.Results[0].Whitespace is None
    assert result.Results[0].Value
    assert result.Results[0].Iter.Line == 1
    assert result.Results[0].Iter.Column == 5
    assert result.Results[0].IsIgnored == False

# ----------------------------------------------------------------------
class TestEmbeddedStatements(object):
    _word_token                             = RegexToken("Word", re.compile(r"(?P<value>\S+)"))
    _lpar_token                             = RegexToken("lpar", re.compile(r"(?P<value>\()"))
    _rpar_token                             = RegexToken("rpar", re.compile(r"(?P<value>\))"))

    _inner_statement                        = StandardStatement([_word_token, _word_token])
    _statement                              = StandardStatement(
        [
            _lpar_token,
            _inner_statement,
            _rpar_token,
        ],
    )

    # ----------------------------------------------------------------------
    def test_Match(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("( one two )")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 1
        assert execution_mock.OnInternalStatement.call_args_list[0][0][0].Statement == self._inner_statement
        assert execution_mock.OnInternalStatement.call_args_list[0][0][1].Offset == 1
        assert execution_mock.OnInternalStatement.call_args_list[0][0][2].Offset == 9

        assert result.Success

        assert result.Iter.Line == 1
        assert result.Iter.Column == 12
        assert result.Iter.AtEnd() == False

        assert len(result.Results) == 3

        assert result.Results[0].Token == self._lpar_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "("
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 2
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Statement == self._inner_statement

        assert len(result.Results[1].Results) == 2

        assert result.Results[1].Results[0].Token == self._word_token

        assert result.Results[1].Results[0].Whitespace == (1, 2)
        assert result.Results[1].Results[0].Value.Match.group("value") == "one"
        assert result.Results[1].Results[0].Iter.Line == 1
        assert result.Results[1].Results[0].Iter.Column == 6
        assert result.Results[1].Results[0].IsIgnored == False

        assert result.Results[1].Results[1].Token == self._word_token

        assert result.Results[1].Results[1].Whitespace == (5, 6)
        assert result.Results[1].Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Results[1].Iter.Line == 1
        assert result.Results[1].Results[1].Iter.Column == 10
        assert result.Results[1].Results[1].IsIgnored == False

        assert result.Results[2].Token == self._rpar_token

        assert result.Results[2].Whitespace == (9, 10)
        assert result.Results[2].Value.Match.group("value") == ")"
        assert result.Results[2].Iter.Line == 1
        assert result.Results[2].Iter.Column == 12
        assert result.Results[2].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_NoMatchAllInner(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("( one two")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 1
        assert execution_mock.OnInternalStatement.call_args_list[0][0][0].Statement == self._inner_statement
        assert execution_mock.OnInternalStatement.call_args_list[0][0][1].Offset == 1
        assert execution_mock.OnInternalStatement.call_args_list[0][0][2].Offset == 9

        assert result.Success == False

        assert result.Iter.Line == 1
        assert result.Iter.Column == 10
        assert result.Iter.AtEnd() == False

        assert len(result.Results) == 2

        assert result.Results[0].Token == self._lpar_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "("
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 2
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Statement == self._inner_statement

        assert len(result.Results[1].Results) == 2

        assert result.Results[1].Results[0].Token == self._word_token

        assert result.Results[1].Results[0].Whitespace == (1, 2)
        assert result.Results[1].Results[0].Value.Match.group("value") == "one"
        assert result.Results[1].Results[0].Iter.Line == 1
        assert result.Results[1].Results[0].Iter.Column == 6
        assert result.Results[1].Results[0].IsIgnored == False

        assert result.Results[1].Results[1].Token == self._word_token

        assert result.Results[1].Results[1].Whitespace == (5, 6)
        assert result.Results[1].Results[1].Value.Match.group("value") == "two"
        assert result.Results[1].Results[1].Iter.Line == 1
        assert result.Results[1].Results[1].Iter.Column == 10
        assert result.Results[1].Results[1].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_NoMatchPartialInner(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("( one ")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success == False

        assert result.Iter.Line == 1
        assert result.Iter.Column == 6
        assert result.Iter.AtEnd() == False

        assert len(result.Results) == 2

        assert result.Results[0].Token == self._lpar_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "("
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 2
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Statement == self._inner_statement

        assert len(result.Results[1].Results) == 1

        assert result.Results[1].Results[0].Token == self._word_token

        assert result.Results[1].Results[0].Whitespace == (1, 2)
        assert result.Results[1].Results[0].Value.Match.group("value") == "one"
        assert result.Results[1].Results[0].Iter.Line == 1
        assert result.Results[1].Results[0].Iter.Column == 6
        assert result.Results[1].Results[0].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_NoMatchFirstOnly(self, execution_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("( ")), execution_mock)

        assert execution_mock.OnIndent.call_count == 0
        assert execution_mock.OnDedent.call_count == 0
        assert execution_mock.OnInternalStatement.call_count == 0

        assert result.Success == False

        assert result.Iter.Line == 1
        assert result.Iter.Column == 2
        assert result.Iter.AtEnd() == False

        assert len(result.Results) == 2

        assert result.Results[0].Token == self._lpar_token

        assert result.Results[0].Whitespace is None
        assert result.Results[0].Value.Match.group("value") == "("
        assert result.Results[0].Iter.Line == 1
        assert result.Results[0].Iter.Column == 2
        assert result.Results[0].IsIgnored == False

        assert result.Results[1].Statement == self._inner_statement
        assert result.Results[1].Results == []

# ----------------------------------------------------------------------
class TestDynamicStatements(object):
    _word_token                             = RegexToken("Word", re.compile(r"(?P<value>\S+)"))
    _number_token                           = RegexToken("Number", re.compile(r"(?P<value>\d+)"))

    _word_statement                         = StandardStatement([_word_token, _word_token, NewlineToken()])
    _number_statement                       = StandardStatement([_number_token, NewlineToken()])

    _statement                              = StandardStatement(
        [
            DynamicStatements.Statements,
            DynamicStatements.Statements,
            DynamicStatements.Expressions,
        ],
    )

    # ----------------------------------------------------------------------
    @staticmethod
    @pytest.fixture
    def modified_execution_mock(execution_mock):
        execution_mock.GetDynamicStatements.side_effect = lambda value: [TestDynamicStatements._word_statement, TestDynamicStatements._number_statement] if value == DynamicStatements.Statements else [TestDynamicStatements._number_statement]
        execution_mock.OnInternalStatement = Mock(return_value=True)

        return execution_mock

    # ----------------------------------------------------------------------
    def test_Match(self, modified_execution_mock):
        result = self._statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        word1 word2
                        123
                        456
                        """,
                    ),
                ),
            ),
            modified_execution_mock,
        )

        assert modified_execution_mock.OnIndent.call_count == 0
        assert modified_execution_mock.OnDedent.call_count == 0
        assert modified_execution_mock.OnInternalStatement.call_count == 3

        assert modified_execution_mock.OnInternalStatement.call_args_list[0][0][0].Statement == self._word_statement
        assert modified_execution_mock.OnInternalStatement.call_args_list[0][0][1].Offset == 0
        assert modified_execution_mock.OnInternalStatement.call_args_list[0][0][2].Offset == 12

        assert modified_execution_mock.OnInternalStatement.call_args_list[1][0][0].Statement == self._number_statement
        assert modified_execution_mock.OnInternalStatement.call_args_list[1][0][1].Offset == 12
        assert modified_execution_mock.OnInternalStatement.call_args_list[1][0][2].Offset == 16

        assert modified_execution_mock.OnInternalStatement.call_args_list[2][0][0].Statement == self._number_statement
        assert modified_execution_mock.OnInternalStatement.call_args_list[2][0][1].Offset == 16
        assert modified_execution_mock.OnInternalStatement.call_args_list[2][0][2].Offset == 20

        assert result.Success
        assert result.Iter.Line == 4
        assert result.Iter.Column == 1
        assert result.Iter.AtEnd()

        assert len(result.Results) == 3

        # Line 1
        assert result.Results[0].Statement == DynamicStatements.Statements

        assert len(result.Results[0].Results) == 1
        assert result.Results[0].Results[0].Statement == self._word_statement

        assert len(result.Results[0].Results[0].Results) == 3

        assert result.Results[0].Results[0].Results[0].Token == self._word_token
        assert result.Results[0].Results[0].Results[0].Whitespace is None
        assert result.Results[0].Results[0].Results[0].Value.Match.group("value") == "word1"
        assert result.Results[0].Results[0].Results[0].Iter.Line == 1
        assert result.Results[0].Results[0].Results[0].Iter.Column == 6
        assert result.Results[0].Results[0].Results[0].IsIgnored == False

        assert result.Results[0].Results[0].Results[1].Token == self._word_token
        assert result.Results[0].Results[0].Results[1].Whitespace == (5, 6)
        assert result.Results[0].Results[0].Results[1].Value.Match.group("value") == "word2"
        assert result.Results[0].Results[0].Results[1].Iter.Line == 1
        assert result.Results[0].Results[0].Results[1].Iter.Column == 12
        assert result.Results[0].Results[0].Results[1].IsIgnored == False

        assert result.Results[0].Results[0].Results[2].Token == NewlineToken()
        assert result.Results[0].Results[0].Results[2].Whitespace is None
        assert result.Results[0].Results[0].Results[2].Value == Token.NewlineMatch(11, 12)
        assert result.Results[0].Results[0].Results[2].Iter.Line == 2
        assert result.Results[0].Results[0].Results[2].Iter.Column == 1
        assert result.Results[0].Results[0].Results[2].IsIgnored == False

        # Line 2
        assert result.Results[1].Statement == DynamicStatements.Statements

        assert len(result.Results[1].Results) == 1
        assert result.Results[1].Results[0].Statement == self._number_statement

        assert len(result.Results[1].Results[0].Results) == 2

        assert result.Results[1].Results[0].Results[0].Token == self._number_token
        assert result.Results[1].Results[0].Results[0].Whitespace is None
        assert result.Results[1].Results[0].Results[0].Value.Match.group("value") == "123"
        assert result.Results[1].Results[0].Results[0].Iter.Line == 2
        assert result.Results[1].Results[0].Results[0].Iter.Column == 4
        assert result.Results[1].Results[0].Results[0].IsIgnored == False

        assert result.Results[1].Results[0].Results[1].Token == NewlineToken()
        assert result.Results[1].Results[0].Results[1].Whitespace is None
        assert result.Results[1].Results[0].Results[1].Value == Token.NewlineMatch(15, 16)
        assert result.Results[1].Results[0].Results[1].Iter.Line == 3
        assert result.Results[1].Results[0].Results[1].Iter.Column == 1
        assert result.Results[1].Results[0].Results[1].IsIgnored == False

        # Line 3
        assert result.Results[2].Statement == DynamicStatements.Expressions

        assert len(result.Results[2].Results) == 1
        assert result.Results[2].Results[0].Statement == self._number_statement

        assert len(result.Results[2].Results[0].Results) == 2

        assert result.Results[2].Results[0].Results[0].Token == self._number_token
        assert result.Results[2].Results[0].Results[0].Whitespace is None
        assert result.Results[2].Results[0].Results[0].Value.Match.group("value") == "456"
        assert result.Results[2].Results[0].Results[0].Iter.Line == 3
        assert result.Results[2].Results[0].Results[0].Iter.Column == 4
        assert result.Results[2].Results[0].Results[0].IsIgnored == False

        assert result.Results[2].Results[0].Results[1].Token == NewlineToken()
        assert result.Results[2].Results[0].Results[1].Whitespace is None
        assert result.Results[2].Results[0].Results[1].Value == Token.NewlineMatch(19, 20)
        assert result.Results[2].Results[0].Results[1].Iter.Line == 4
        assert result.Results[2].Results[0].Results[1].Iter.Column == 1
        assert result.Results[2].Results[0].Results[1].IsIgnored == False

    # ----------------------------------------------------------------------
    def test_NoMatch(self, modified_execution_mock):
        result = self._statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        word1 word2
                        123
                        word3 word4
                        """,
                    ),
                ),
            ),
            modified_execution_mock,
        )

        assert result.Success == False
        assert result.Iter.Line == 3
        assert result.Iter.Column == 1
        assert result.Iter.AtEnd() == False

        assert len(result.Results) == 3

        # Line 1
        assert result.Results[0].Statement == DynamicStatements.Statements

        assert len(result.Results[0].Results) == 1
        assert result.Results[0].Results[0].Statement == self._word_statement

        assert len(result.Results[0].Results[0].Results) == 3

        assert result.Results[0].Results[0].Results[0].Token == self._word_token
        assert result.Results[0].Results[0].Results[0].Whitespace is None
        assert result.Results[0].Results[0].Results[0].Value.Match.group("value") == "word1"
        assert result.Results[0].Results[0].Results[0].Iter.Line == 1
        assert result.Results[0].Results[0].Results[0].Iter.Column == 6
        assert result.Results[0].Results[0].Results[0].IsIgnored == False

        assert result.Results[0].Results[0].Results[1].Token == self._word_token
        assert result.Results[0].Results[0].Results[1].Whitespace == (5, 6)
        assert result.Results[0].Results[0].Results[1].Value.Match.group("value") == "word2"
        assert result.Results[0].Results[0].Results[1].Iter.Line == 1
        assert result.Results[0].Results[0].Results[1].Iter.Column == 12
        assert result.Results[0].Results[0].Results[1].IsIgnored == False

        assert result.Results[0].Results[0].Results[2].Token == NewlineToken()
        assert result.Results[0].Results[0].Results[2].Whitespace is None
        assert result.Results[0].Results[0].Results[2].Value == Token.NewlineMatch(11, 12)
        assert result.Results[0].Results[0].Results[2].Iter.Line == 2
        assert result.Results[0].Results[0].Results[2].Iter.Column == 1
        assert result.Results[0].Results[0].Results[2].IsIgnored == False

        # Line 2
        assert result.Results[1].Statement == DynamicStatements.Statements

        assert len(result.Results[1].Results) == 1
        assert result.Results[1].Results[0].Statement == self._number_statement

        assert len(result.Results[1].Results[0].Results) == 2

        assert result.Results[1].Results[0].Results[0].Token == self._number_token
        assert result.Results[1].Results[0].Results[0].Whitespace is None
        assert result.Results[1].Results[0].Results[0].Value.Match.group("value") == "123"
        assert result.Results[1].Results[0].Results[0].Iter.Line == 2
        assert result.Results[1].Results[0].Results[0].Iter.Column == 4
        assert result.Results[1].Results[0].Results[0].IsIgnored == False

        assert result.Results[1].Results[0].Results[1].Token == NewlineToken()
        assert result.Results[1].Results[0].Results[1].Whitespace is None
        assert result.Results[1].Results[0].Results[1].Value == Token.NewlineMatch(15, 16)
        assert result.Results[1].Results[0].Results[1].Iter.Line == 3
        assert result.Results[1].Results[0].Results[1].Iter.Column == 1
        assert result.Results[1].Results[0].Results[1].IsIgnored == False

        # Line 3
        assert result.Results[2].Statement == DynamicStatements.Expressions

        assert len(result.Results[2].Results) == 1
        assert result.Results[2].Results[0].Statement == self._number_statement

        assert result.Results[2].Results[0].Results == []

# ----------------------------------------------------------------------
class TestOrStatements(object):
    _number_token                           = RegexToken("Number Token", re.compile(r"(?P<value>[0-9]+)"))
    _lower_token                            = RegexToken("Lower Token", re.compile(r"(?P<value>[a-z]+)"))
    _upper_token                            = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))

    _number_statement                       = StandardStatement([_number_token, NewlineToken()])
    _lower_statement                        = StandardStatement([_lower_token])
    _upper_statement                        = StandardStatement([_upper_token])

    _or_statement                           = StandardStatement(
        [
            _number_statement,
            [_lower_statement, _upper_statement],
            NewlineToken(),
        ],
    )

    # ----------------------------------------------------------------------
    def test_Lower(self, execution_mock):
        result = self._or_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        123
                        lower
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 3
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Statement == self._number_statement

        assert len(result.Results[0].Results) == 2
        assert result.Results[0].Results[0].Value.Match.group("value") == "123"
        assert result.Results[0].Results[1].Value == Token.NewlineMatch(3, 4)

        assert result.Results[1].Statement == [self._lower_statement, self._upper_statement]

        assert len(result.Results[1].Results) == 1
        assert result.Results[1].Results[0].Statement == self._lower_statement

        assert len(result.Results[1].Results[0].Results) == 1
        assert result.Results[1].Results[0].Results[0].Value.Match.group("value") == "lower"

        assert result.Results[2].Value == Token.NewlineMatch(9, 10)

    # ----------------------------------------------------------------------
    def test_Upper(self, execution_mock):
        result = self._or_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        123
                        UPPER
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 3
        assert result.Iter.Column == 1

        assert len(result.Results) == 3

        assert result.Results[0].Statement == self._number_statement

        assert len(result.Results[0].Results) == 2
        assert result.Results[0].Results[0].Value.Match.group("value") == "123"
        assert result.Results[0].Results[1].Value == Token.NewlineMatch(3, 4)

        assert result.Results[1].Statement == [self._lower_statement, self._upper_statement]

        assert len(result.Results[1].Results) == 1
        assert result.Results[1].Results[0].Statement == self._upper_statement

        assert len(result.Results[1].Results[0].Results) == 1
        assert result.Results[1].Results[0].Results[0].Value.Match.group("value") == "UPPER"

        assert result.Results[2].Value == Token.NewlineMatch(9, 10)

    # ----------------------------------------------------------------------
    def test_NoMatch(self, execution_mock):
        result = self._or_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        123
                        456789
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success == False
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert len(result.Results) == 2

        assert result.Results[0].Statement == self._number_statement

        assert len(result.Results[0].Results) == 2
        assert result.Results[0].Results[0].Value.Match.group("value") == "123"
        assert result.Results[0].Results[1].Value == Token.NewlineMatch(3, 4)

        assert result.Results[1].Statement == [self._lower_statement, self._upper_statement]

        assert len(result.Results[1].Results) == 2

        assert result.Results[1].Results[0].Statement == self._lower_statement
        assert result.Results[1].Results[0].Results == []

        assert result.Results[1].Results[1].Statement == self._upper_statement
        assert result.Results[1].Results[1].Results == []
