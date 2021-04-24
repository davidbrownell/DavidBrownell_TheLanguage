# ----------------------------------------------------------------------
# |
# |  Statement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-18 14:08:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for Statement.py"""

import os
import re
import sys
import textwrap

from unittest.mock import Mock

import pytest

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

sys.path.insert(0, os.path.join(_script_dir, ".."))
with CallOnExit(lambda: sys.path.pop(0)):
    from Statement import *
    from NormalizedIterator import NormalizedIterator
    from Normalize import Normalize
    from Token import *

# ----------------------------------------------------------------------
class TestErrors(object):
    # ----------------------------------------------------------------------
    def test_InvalidName(self):
        with pytest.raises(AssertionError):
            StandardStatement("", [NewlineToken()])

    # ----------------------------------------------------------------------
    def test_InvalidItems(self):
        with pytest.raises(AssertionError):
            StandardStatement("Invaild", [])

    # ----------------------------------------------------------------------
    def test_MissingClosingToken(self):
        with pytest.raises(AssertionError):
            StandardStatement("Single", [PushIgnoreWhitespaceControlToken()])

        with pytest.raises(AssertionError):
            StandardStatement("Multiple1", [PushIgnoreWhitespaceControlToken(), PopIgnoreWhitespaceControlToken(), PushIgnoreWhitespaceControlToken()])

        with pytest.raises(AssertionError):
            StandardStatement("Multiple2", [PushIgnoreWhitespaceControlToken(), PushIgnoreWhitespaceControlToken(), PopIgnoreWhitespaceControlToken()])

    # ----------------------------------------------------------------------
    def test_MissingOpeningToken(self):
        with pytest.raises(AssertionError):
            StandardStatement("Single", [PopIgnoreWhitespaceControlToken()])

        with pytest.raises(AssertionError):
            StandardStatement("Multiple1", [PushIgnoreWhitespaceControlToken(), PopIgnoreWhitespaceControlToken(), PopIgnoreWhitespaceControlToken()])

# ----------------------------------------------------------------------
class TestSingleLine(object):
    _word_token                         = RegexToken("Word", re.compile(r"(?P<value>\S+)"))
    _statement                          = StandardStatement("Standard", [_word_token, _word_token, NewlineToken()])

    # ----------------------------------------------------------------------
    def test_Properties(self):
        assert self._statement.Name == "Standard"
        assert self._statement.Items == [self._word_token, self._word_token, NewlineToken()]

    # ----------------------------------------------------------------------
    def test_SingleSpaceSep(self):
        iter = NormalizedIterator(Normalize("one two"))

        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

        mock = Mock()
        result = self._statement.Parse(iter, mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success

        assert result.iter.AtEnd()
        assert result.iter.Line == 2
        assert result.iter.Column == 1

        assert len(result.results) == 3

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (3, 4)
        assert result.results[1].value.match.group("value") == "two"
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 8
        assert result.results[1].is_ignored == False

        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace is None
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 7, 8)
        assert result.results[2].iter.Line == 2
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == False

        # Iterator is not modified
        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

    # ----------------------------------------------------------------------
    def test_MultipleSpaceSep(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("one   two")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success

        assert result.iter.AtEnd()
        assert result.iter.Line == 2
        assert result.iter.Column == 1

        assert len(result.results) == 3

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (3, 6)
        assert result.results[1].value.match.group("value") == "two"
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 10
        assert result.results[1].is_ignored == False

        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace is None
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 9, 10)
        assert result.results[2].iter.Line == 2
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == False

    # ----------------------------------------------------------------------
    def test_TabSep(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("one\ttwo")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success

        assert result.iter.AtEnd()
        assert result.iter.Line == 2
        assert result.iter.Column == 1

        assert len(result.results) == 3

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (3, 4)
        assert result.results[1].value.match.group("value") == "two"
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 8
        assert result.results[1].is_ignored == False

        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace is None
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 7, 8)
        assert result.results[2].iter.Line == 2
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == False

    # ----------------------------------------------------------------------
    def test_MultipleTabSep(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("one\t\t\ttwo")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success

        assert result.iter.AtEnd()
        assert result.iter.Line == 2
        assert result.iter.Column == 1

        assert len(result.results) == 3

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (3, 6)
        assert result.results[1].value.match.group("value") == "two"
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 10
        assert result.results[1].is_ignored == False

        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace is None
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 9, 10)
        assert result.results[2].iter.Line == 2
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == False

    # ----------------------------------------------------------------------
    def test_TrailingSpace(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("one two ")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success

        assert result.iter.AtEnd()
        assert result.iter.Line == 2
        assert result.iter.Column == 1

        assert len(result.results) == 3

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (3, 4)
        assert result.results[1].value.match.group("value") == "two"
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 8
        assert result.results[1].is_ignored == False

        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace == (7, 8)
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 8, 9)
        assert result.results[2].iter.Line == 2
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == False

    # ----------------------------------------------------------------------
    def test_MultipleTrailingSpace(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("one two   ")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success

        assert result.iter.AtEnd()
        assert result.iter.Line == 2
        assert result.iter.Column == 1

        assert len(result.results) == 3

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (3, 4)
        assert result.results[1].value.match.group("value") == "two"
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 8
        assert result.results[1].is_ignored == False

        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace == (7, 10)
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 10, 11)
        assert result.results[2].iter.Line == 2
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == False

    # ----------------------------------------------------------------------
    def test_TrailingTab(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("one two\t")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success

        assert result.iter.AtEnd()
        assert result.iter.Line == 2
        assert result.iter.Column == 1

        assert len(result.results) == 3

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (3, 4)
        assert result.results[1].value.match.group("value") == "two"
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 8
        assert result.results[1].is_ignored == False

        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace == (7, 8)
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 8, 9)
        assert result.results[2].iter.Line == 2
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == False

    # ----------------------------------------------------------------------
    def test_MultipleTrailingTabs(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("one two\t\t\t\t")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success

        assert result.iter.AtEnd()
        assert result.iter.Line == 2
        assert result.iter.Column == 1

        assert len(result.results) == 3

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (3, 4)
        assert result.results[1].value.match.group("value") == "two"
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 8
        assert result.results[1].is_ignored == False

        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace == (7, 11)
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 11, 12)
        assert result.results[2].iter.Line == 2
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == False

    # ----------------------------------------------------------------------
    def test_MultipleLines(self):
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

        mock = Mock()

        # First Line
        result = self._statement.Parse(iter, mock)

        assert result.success

        assert result.iter.AtEnd() == False
        assert result.iter.Line == 2
        assert result.iter.Column == 1

        assert len(result.results) == 3

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (3, 4)
        assert result.results[1].value.match.group("value") == "two"
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 8
        assert result.results[1].is_ignored == False

        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace is None
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 7, 8)
        assert result.results[2].iter.Line == 2
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == False

        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

        iter = result.iter

        # Second Line
        result = self._statement.Parse(iter, mock)

        assert result.success

        assert result.iter.AtEnd()
        assert result.iter.Line == 3
        assert result.iter.Column == 1

        assert len(result.results) == 3

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "three"
        assert result.results[0].iter.Line == 2
        assert result.results[0].iter.Column == 6
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (13, 14)
        assert result.results[1].value.match.group("value") == "four"
        assert result.results[1].iter.Line == 2
        assert result.results[1].iter.Column == 11
        assert result.results[1].is_ignored == False

        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace is None
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 18, 19)
        assert result.results[2].iter.Line == 3
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == False

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

    # ----------------------------------------------------------------------
    def test_TrailingWhitespace(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("one two\n\n  \n    \n")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success

        assert result.iter.AtEnd()
        assert result.iter.Line == 5
        assert result.iter.Column == 1

        assert len(result.results) == 3

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (3, 4)
        assert result.results[1].value.match.group("value") == "two"
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 8
        assert result.results[1].is_ignored == False

        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace is None
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 7, 17)
        assert result.results[2].iter.Line == 5
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == False

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        iter = NormalizedIterator(Normalize("one two three"))

        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

        mock = Mock()
        result = self._statement.Parse(iter, mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success == False

        assert result.iter.AtEnd() == False
        assert result.iter.Line == 1
        assert result.iter.Column == 8

        assert len(result.results) == 2

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == self._word_token

        assert result.results[1].whitespace == (3, 4)
        assert result.results[1].value.match.group("value") == "two"
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 8
        assert result.results[1].is_ignored == False

        # Iterator is not modified
        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

# ----------------------------------------------------------------------
class TestIndentAndDedent(object):
    _word_token                         = RegexToken("Word", re.compile(r"(?P<value>\S+)"))

    _statement                          = StandardStatement(
        "IndentAndDednet",
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
    def test_Match(self):
        mock = Mock()

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
            mock,
        )

        assert mock.OnIndent.call_count == 1
        assert mock.OnDedent.call_count == 1

        assert result.success
        assert result.iter.Line == 4
        assert result.iter.Column == 1
        assert result.iter.Offset == 22
        assert result.iter.AtEnd()

        assert len(result.results) == 8

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == NewlineToken()

        assert result.results[1].whitespace is None
        assert result.results[1].value == Token.NewlineMatch(NewlineToken, 3, 4)
        assert result.results[1].iter.Line == 2
        assert result.results[1].iter.Column == 1
        assert result.results[1].is_ignored == False

        assert result.results[2].token == IndentToken()

        assert result.results[2].whitespace is None
        assert result.results[2].value == Token.IndentMatch(IndentToken, 4, 8, 4)
        assert result.results[2].iter.Line == 2
        assert result.results[2].iter.Column == 5
        assert result.results[2].is_ignored == False

        assert result.results[3].token == self._word_token

        assert result.results[3].whitespace is None
        assert result.results[3].value.match.group("value") == "two"
        assert result.results[3].iter.Line == 2
        assert result.results[3].iter.Column == 8
        assert result.results[3].is_ignored == False

        assert result.results[4].token == NewlineToken()

        assert result.results[4].whitespace is None
        assert result.results[4].value == Token.NewlineMatch(NewlineToken, 11, 12)
        assert result.results[4].iter.Line == 3
        assert result.results[4].iter.Column == 1
        assert result.results[4].is_ignored == False

        assert result.results[5].token == self._word_token

        assert result.results[5].whitespace is None
        assert result.results[5].value.match.group("value") == "three"
        assert result.results[5].iter.Line == 3
        assert result.results[5].iter.Column == 10
        assert result.results[5].is_ignored == False

        assert result.results[6].token == NewlineToken()

        assert result.results[6].whitespace is None
        assert result.results[6].value == Token.NewlineMatch(NewlineToken, 21, 22)
        assert result.results[6].iter.Line == 4
        assert result.results[6].iter.Column == 1
        assert result.results[6].is_ignored == False

        assert result.results[7].token == DedentToken()

        assert result.results[7].whitespace is None
        assert result.results[7].value == Token.DedentMatch(DedentToken)
        assert result.results[7].iter.Line == 4
        assert result.results[7].iter.Column == 1
        assert result.results[7].is_ignored == False

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        mock = Mock()

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
            mock,
        )

        # The code stopped parsing after 'two', so only 1 indent was encountered and 0 dedents were
        # encountered
        assert mock.OnIndent.call_count == 1
        assert mock.OnDedent.call_count == 0

        assert result.success == False
        assert result.iter.Line == 3
        assert result.iter.Column == 1
        assert result.iter.Offset == 12
        assert result.iter.AtEnd() == False

        assert len(result.results) == 5

        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        assert result.results[1].token == NewlineToken()

        assert result.results[1].whitespace is None
        assert result.results[1].value == (NewlineToken, 3, 4)
        assert result.results[1].iter.Line == 2
        assert result.results[1].iter.Column == 1
        assert result.results[1].is_ignored == False

        assert result.results[2].token == IndentToken()

        assert result.results[2].whitespace is None
        assert result.results[2].value == (IndentToken, 4, 8, 4)
        assert result.results[2].iter.Line == 2
        assert result.results[2].iter.Column == 5
        assert result.results[2].is_ignored == False

        assert result.results[3].token == self._word_token

        assert result.results[3].whitespace is None
        assert result.results[3].value.match.group("value") == "two"
        assert result.results[3].iter.Line == 2
        assert result.results[3].iter.Column == 8
        assert result.results[3].is_ignored == False

        assert result.results[4].token == NewlineToken()

        assert result.results[4].whitespace is None
        assert result.results[4].value == (NewlineToken, 11, 12)
        assert result.results[4].iter.Line == 3
        assert result.results[4].iter.Column == 1
        assert result.results[4].is_ignored == False

# ----------------------------------------------------------------------
def test_FinishEarly():
    word_token = RegexToken("Word", re.compile(r"(?P<value>\S+)"))

    statement = StandardStatement("FinishEarly", [word_token, NewlineToken(), word_token])

    iter = NormalizedIterator(Normalize("one"))

    assert iter.Line == 1
    assert iter.Column == 1
    assert iter.Offset == 0

    mock = Mock()
    result = statement.Parse(iter, mock)

    assert mock.OnIndent.call_count == 0
    assert mock.OnDedent.call_count == 0

    assert result.success == False

    assert result.iter.AtEnd()
    assert result.iter.Line == 2
    assert result.iter.Column == 1

    assert len(result.results) == 2

    assert result.results[0].token == word_token

    assert result.results[0].whitespace is None
    assert result.results[0].value.match.group("value") == "one"
    assert result.results[0].iter.Line == 1
    assert result.results[0].iter.Column == 4
    assert result.results[0].is_ignored == False

    assert result.results[1].token == NewlineToken()

    assert result.results[1].whitespace is None
    assert result.results[1].value == (NewlineToken, 3, 4)
    assert result.results[1].iter.Line == 2
    assert result.results[1].iter.Column == 1
    assert result.results[1].is_ignored == False

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
        "IndentAndDednet",
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
    def test_MatchNoExtra(self):
        mock = Mock()

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
            mock,
        )

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success

        assert result.iter.AtEnd()
        assert result.iter.Line == 11
        assert result.iter.Column == 1
        assert result.iter.Offset == 60

        assert len(result.results) == 20

        # Line 1
        assert result.results[0].token == self._word_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "one"
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 4
        assert result.results[0].is_ignored == False

        # lpar
        assert result.results[1].token == self._lpar_token

        assert result.results[1].whitespace == (3, 4)
        assert result.results[1].value.match
        assert result.results[1].iter.Line == 1
        assert result.results[1].iter.Column == 6
        assert result.results[1].is_ignored == False

        # Line 2-3
        assert result.results[2].token == NewlineToken()

        assert result.results[2].whitespace is None
        assert result.results[2].value == Token.NewlineMatch(NewlineToken, 5, 8)
        assert result.results[2].iter.Line == 4
        assert result.results[2].iter.Column == 1
        assert result.results[2].is_ignored == True

        # Line 4
        assert result.results[3].token == IndentToken()

        assert result.results[3].whitespace is None
        assert result.results[3].value == Token.IndentMatch(IndentToken, 8, 12, 4)
        assert result.results[3].iter.Line == 4
        assert result.results[3].iter.Column == 5
        assert result.results[3].is_ignored == True

        assert result.results[4].token == self._word_token

        assert result.results[4].whitespace is None
        assert result.results[4].value.match.group("value") == "two"
        assert result.results[4].iter.Line == 4
        assert result.results[4].iter.Column == 8
        assert result.results[4].is_ignored == False

        # Line 5
        assert result.results[5].token == NewlineToken()

        assert result.results[5].whitespace is None
        assert result.results[5].value == Token.NewlineMatch(NewlineToken, 15, 17)
        assert result.results[5].iter.Line == 6
        assert result.results[5].iter.Column == 1
        assert result.results[5].is_ignored == True

        # Line 6
        assert result.results[6].token == IndentToken()

        assert result.results[6].whitespace is None
        assert result.results[6].value == Token.IndentMatch(IndentToken, 17, 25, 8)
        assert result.results[6].iter.Line == 6
        assert result.results[6].iter.Column == 9
        assert result.results[6].is_ignored == True

        assert result.results[7].token == self._word_token

        assert result.results[7].whitespace is None
        assert result.results[7].value.match.group("value") == "three"
        assert result.results[7].iter.Line == 6
        assert result.results[7].iter.Column == 14
        assert result.results[7].is_ignored == False

        assert result.results[8].token == NewlineToken()

        assert result.results[8].whitespace is None
        assert result.results[8].value == Token.NewlineMatch(NewlineToken, 30, 31)
        assert result.results[8].iter.Line == 7
        assert result.results[8].iter.Column == 1
        assert result.results[8].is_ignored == True

        # Line 7
        assert result.results[9].token == DedentToken()

        assert result.results[9].whitespace is None
        assert result.results[9].value == Token.DedentMatch(DedentToken)
        assert result.results[9].iter.Line == 7
        assert result.results[9].iter.Column == 5
        assert result.results[9].is_ignored == True

        assert result.results[10].token == self._word_token

        assert result.results[10].whitespace is None
        assert result.results[10].value.match.group("value") == "four"
        assert result.results[10].iter.Line == 7
        assert result.results[10].iter.Column == 9
        assert result.results[10].is_ignored == False

        assert result.results[11].token == NewlineToken()

        assert result.results[11].whitespace is None
        assert result.results[11].value == Token.NewlineMatch(NewlineToken, 39, 40)
        assert result.results[11].iter.Line == 8
        assert result.results[11].iter.Column == 1
        assert result.results[11].is_ignored == True

        # Line 8
        assert result.results[12].token == IndentToken()

        assert result.results[12].whitespace is None
        assert result.results[12].value == Token.IndentMatch(IndentToken, 40, 48, 8)
        assert result.results[12].iter.Line == 8
        assert result.results[12].iter.Column == 9
        assert result.results[12].is_ignored == True

        assert result.results[13].token == self._word_token

        assert result.results[13].whitespace is None
        assert result.results[13].value.match.group("value") == "five"
        assert result.results[13].iter.Line == 8
        assert result.results[13].iter.Column == 13
        assert result.results[13].is_ignored == False

        assert result.results[14].token == NewlineToken()

        assert result.results[14].whitespace is None
        assert result.results[14].value == Token.NewlineMatch(NewlineToken, 52, 54)
        assert result.results[14].iter.Line == 10
        assert result.results[14].iter.Column == 1
        assert result.results[14].is_ignored == True

        # Line 10
        assert result.results[15].token == DedentToken()

        assert result.results[15].whitespace is None
        assert result.results[15].value == Token.DedentMatch(DedentToken)
        assert result.results[15].iter.Line == 10
        assert result.results[15].iter.Column == 1
        assert result.results[15].is_ignored == True

        assert result.results[16].token == DedentToken()

        assert result.results[16].whitespace is None
        assert result.results[16].value == Token.DedentMatch(DedentToken)
        assert result.results[16].iter.Line == 10
        assert result.results[16].iter.Column == 1
        assert result.results[16].is_ignored == True

        # rpar
        assert result.results[17].token == self._rpar_token

        assert result.results[17].whitespace is None
        assert result.results[17].value.match
        assert result.results[17].iter.Line == 10
        assert result.results[17].iter.Column == 2
        assert result.results[17].is_ignored == False

        assert result.results[18].token == self._word_token

        assert result.results[18].whitespace == (55, 56)
        assert result.results[18].value.match.group("value") == "six"
        assert result.results[18].iter.Line == 10
        assert result.results[18].iter.Column == 6
        assert result.results[18].is_ignored == False

        assert result.results[19].token == NewlineToken()

        assert result.results[19].whitespace is None
        assert result.results[19].value == Token.NewlineMatch(NewlineToken, 59, 60)
        assert result.results[19].iter.Line == 11
        assert result.results[19].iter.Column == 1
        assert result.results[19].iter.AtEnd()
        assert result.results[19].is_ignored == False

# ----------------------------------------------------------------------
def test_IgnoreControlTokens():
    # ----------------------------------------------------------------------
    @Interface.staticderived
    class MyControlToken(ControlTokenBase):
        Name                                = Interface.DerivedProperty("MyControlToken")

    # ----------------------------------------------------------------------

    mock = Mock()

    control_token = MyControlToken()
    regex_token = RegexToken("test", re.compile("test"))

    result = StandardStatement(
        "IgnoreControlTokens",
        [
            control_token,
            regex_token,
        ],
    ).Parse(NormalizedIterator(Normalize("test")), mock)

    assert mock.OnIndent.call_count == 0
    assert mock.OnDedent.call_count == 0

    assert result.success

    assert result.iter.Line == 1
    assert result.iter.Column == 5
    assert result.iter.AtEnd() == False

    assert len(result.results) == 1

    assert result.results[0].token == regex_token

    assert result.results[0].whitespace is None
    assert result.results[0].value
    assert result.results[0].iter.Line == 1
    assert result.results[0].iter.Column == 5
    assert result.results[0].is_ignored == False

# ----------------------------------------------------------------------
class TestEmbeddedStatements(object):
    _word_token                             = RegexToken("Word", re.compile(r"(?P<value>\S+)"))
    _lpar_token                             = RegexToken("lpar", re.compile(r"(?P<value>\()"))
    _rpar_token                             = RegexToken("rpar", re.compile(r"(?P<value>\))"))

    _inner_statement                        = StandardStatement("Inner", [_word_token, _word_token])
    _statement                              = StandardStatement(
        "Outer",
        [
            _lpar_token,
            _inner_statement,
            _rpar_token,
        ],
    )

    # ----------------------------------------------------------------------
    def test_Match(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("( one two )")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success

        assert result.iter.Line == 1
        assert result.iter.Column == 12
        assert result.iter.AtEnd() == False

        assert len(result.results) == 3

        assert result.results[0].token == self._lpar_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "("
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 2
        assert result.results[0].is_ignored == False

        assert result.results[1].statement == self._inner_statement

        assert len(result.results[1].results) == 2

        assert result.results[1].results[0].token == self._word_token

        assert result.results[1].results[0].whitespace == (1, 2)
        assert result.results[1].results[0].value.match.group("value") == "one"
        assert result.results[1].results[0].iter.Line == 1
        assert result.results[1].results[0].iter.Column == 6
        assert result.results[1].results[0].is_ignored == False

        assert result.results[1].results[1].token == self._word_token

        assert result.results[1].results[1].whitespace == (5, 6)
        assert result.results[1].results[1].value.match.group("value") == "two"
        assert result.results[1].results[1].iter.Line == 1
        assert result.results[1].results[1].iter.Column == 10
        assert result.results[1].results[1].is_ignored == False

        assert result.results[2].token == self._rpar_token

        assert result.results[2].whitespace == (9, 10)
        assert result.results[2].value.match.group("value") == ")"
        assert result.results[2].iter.Line == 1
        assert result.results[2].iter.Column == 12
        assert result.results[2].is_ignored == False

    # ----------------------------------------------------------------------
    def test_NoMatchAllInner(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("( one two")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success == False

        assert result.iter.Line == 1
        assert result.iter.Column == 10
        assert result.iter.AtEnd() == False

        assert len(result.results) == 2

        assert result.results[0].token == self._lpar_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "("
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 2
        assert result.results[0].is_ignored == False

        assert result.results[1].statement == self._inner_statement

        assert len(result.results[1].results) == 2

        assert result.results[1].results[0].token == self._word_token

        assert result.results[1].results[0].whitespace == (1, 2)
        assert result.results[1].results[0].value.match.group("value") == "one"
        assert result.results[1].results[0].iter.Line == 1
        assert result.results[1].results[0].iter.Column == 6
        assert result.results[1].results[0].is_ignored == False

        assert result.results[1].results[1].token == self._word_token

        assert result.results[1].results[1].whitespace == (5, 6)
        assert result.results[1].results[1].value.match.group("value") == "two"
        assert result.results[1].results[1].iter.Line == 1
        assert result.results[1].results[1].iter.Column == 10
        assert result.results[1].results[1].is_ignored == False

    # ----------------------------------------------------------------------
    def test_NoMatchPartialInner(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("( one ")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success == False

        assert result.iter.Line == 1
        assert result.iter.Column == 6
        assert result.iter.AtEnd() == False

        assert len(result.results) == 2

        assert result.results[0].token == self._lpar_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "("
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 2
        assert result.results[0].is_ignored == False

        assert result.results[1].statement == self._inner_statement

        assert len(result.results[1].results) == 1

        assert result.results[1].results[0].token == self._word_token

        assert result.results[1].results[0].whitespace == (1, 2)
        assert result.results[1].results[0].value.match.group("value") == "one"
        assert result.results[1].results[0].iter.Line == 1
        assert result.results[1].results[0].iter.Column == 6
        assert result.results[1].results[0].is_ignored == False

    # ----------------------------------------------------------------------
    def test_NoMatchFirstOnly(self):
        mock = Mock()
        result = self._statement.Parse(NormalizedIterator(Normalize("( ")), mock)

        assert mock.OnIndent.call_count == 0
        assert mock.OnDedent.call_count == 0

        assert result.success == False

        assert result.iter.Line == 1
        assert result.iter.Column == 2
        assert result.iter.AtEnd() == False

        assert len(result.results) == 1

        assert result.results[0].token == self._lpar_token

        assert result.results[0].whitespace is None
        assert result.results[0].value.match.group("value") == "("
        assert result.results[0].iter.Line == 1
        assert result.results[0].iter.Column == 2
        assert result.results[0].is_ignored == False
