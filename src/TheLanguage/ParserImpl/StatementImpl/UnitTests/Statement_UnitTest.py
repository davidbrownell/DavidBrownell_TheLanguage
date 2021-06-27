# ----------------------------------------------------------------------
# |
# |  Statement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-24 07:26:11
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for Statement.py"""

import os
import re

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
    from ..Statement import *

    from ...Normalize import Normalize
    from ...NormalizedIterator import NormalizedIterator


# ----------------------------------------------------------------------
def CreateStatement(result):

    # ----------------------------------------------------------------------
    class TheStatement(Statement):
        # ----------------------------------------------------------------------
        def __init__(self):
            super(TheStatement, self).__init__("The Statement")

            self.parse_mock = Mock(
                return_value=result,
            )

        # ----------------------------------------------------------------------
        @Interface.override
        def Parse(self, *args, **kwargs):
            return self.parse_mock(*args, **kwargs)

    # ----------------------------------------------------------------------

    return TheStatement()

# ----------------------------------------------------------------------
@pytest.fixture
def iterator(
    value="This is the content",
):
    return NormalizedIterator(Normalize(value))

# ----------------------------------------------------------------------
@pytest.fixture
def parse_mock():
    mock = Mock()

    mock._executor = ThreadPoolExecutor()
    mock.Enqueue = lambda funcs: [mock._executor.submit(func) for func in funcs]

    return mock

# ----------------------------------------------------------------------
class TestStandard(object):
    # ----------------------------------------------------------------------
    class MyStatement(Statement):
        @staticmethod
        @Interface.override
        def Parse(*args, **kwargs):
            pass

    # ----------------------------------------------------------------------
    class MyParseResultData(Statement.ParseResultData):
        @staticmethod
        @Interface.override
        def __str__() -> str:
            return "Hello!"

        @staticmethod
        @Interface.override
        def EnumTokens() -> Generator[Statement.TokenParseResultData, None, None]:
            if False:
                yield None

    # ----------------------------------------------------------------------
    def test_Properties(self):
        assert self.MyStatement("The statement name").Name == "The statement name"

    # ----------------------------------------------------------------------
    def test_PropertyErrors(self):
        with pytest.raises(AssertionError):
            self.MyStatement("")

    # ----------------------------------------------------------------------
    def test_Equality(self):
        assert self.MyStatement("hello") == self.MyStatement("hello")
        assert self.MyStatement("goodbye") != self.MyStatement("hello")

    # ----------------------------------------------------------------------
    def test_ParseResultEmptyData(self, iterator):
        assert str(Statement.ParseResult(True, iterator, None)) == textwrap.dedent(
            """\
            True
            0
                <No Data>
            """,
        )

    # ----------------------------------------------------------------------
    def test_ParseResultAdvancedIterator(self, iterator):
        iterator.Advance(5)

        assert str(Statement.ParseResult(True, iterator, None)) == textwrap.dedent(
            """\
            True
            5
                <No Data>
            """,
        )

    # ----------------------------------------------------------------------
    def test_ParseResultWithMyParseResultData(self, iterator):
        assert str(Statement.ParseResult(False, iterator, self.MyParseResultData())) == textwrap.dedent(
            """\
            False
            0
                Hello!
            """,
        )

    # ----------------------------------------------------------------------
    def test_ParseResultWithStandardParseResultData(self, iterator):
        assert str(
            Statement.ParseResult(
                True,
                iterator,
                Statement.StandardParseResultData(
                    CreateStatement(20),
                    self.MyParseResultData(),
                ),
            ),
        ) == textwrap.dedent(
            """\
            True
            0
                The Statement
                    Hello!
            """,
        )

    # ----------------------------------------------------------------------
    def test_StandardParseResultDataEnumWithNone(self):
        data = Statement.StandardParseResultData(
            CreateStatement(20),
            None,
        )

        assert list(data.EnumTokens()) == []

# ----------------------------------------------------------------------
class TestTokenParseResultData(object):
    _token                                  = RegexToken("My Word Token", re.compile(r"(?P<value>[a-zA-Z0-9]+)"))

    # ----------------------------------------------------------------------
    def test_StrStandard(self, iterator):
        after_iterator = iterator.Clone()
        after_iterator.Advance(3)

        assert str(
            Statement.TokenParseResultData(
                self._token,
                None,
                self._token.Regex.match("word"),
                iterator,
                after_iterator,
                False,
            ),
        ) == textwrap.dedent(
            """\
            My Word Token <<<_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 4]
            """,
        ).rstrip()

    # ----------------------------------------------------------------------
    def test_StrWhitespace(self, iterator):
        after_iterator = iterator.Clone()
        after_iterator.Advance(3)

        assert str(
            Statement.TokenParseResultData(
                self._token,
                [5, 10],
                self._token.Regex.match("word"),
                iterator,
                after_iterator,
                False,
            ),
        ) == textwrap.dedent(
            """\
            My Word Token <<<_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:(5, 10) [1, 1 -> 1, 4]
            """,
        ).rstrip()

    # ----------------------------------------------------------------------
    def test_StrIgnored(self, iterator):
        after_iterator = iterator.Clone()
        after_iterator.Advance(3)

        assert str(
            Statement.TokenParseResultData(
                self._token,
                None,
                self._token.Regex.match("word"),
                iterator,
                after_iterator,
                True,
            ),
        ) == textwrap.dedent(
            """\
            My Word Token <<<_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None !Ignored! [1, 1 -> 1, 4]
            """,
        ).rstrip()

    # ----------------------------------------------------------------------
    def test_Enum(self, iterator):
        data = Statement.TokenParseResultData(
            self._token,
            None,
            self._token.Regex.match("word"),
            iterator,
            iterator,
            False,
        )

        assert list(data.EnumTokens()) == [data]

    # ----------------------------------------------------------------------
    def test_StandardParseResultDataEnum(self, iterator):
        data = Statement.StandardParseResultData(
            CreateStatement(20),
            Statement.TokenParseResultData(
                self._token,
                None,
                self._token.Regex.match("word"),
                iterator,
                iterator,
                False,
            ),
        )

        assert list(data.EnumTokens()) == [data.Data]

# ----------------------------------------------------------------------
def test_Parse(iterator, parse_mock):
    result = CreateStatement(1).Parse(iterator, parse_mock)
    assert result == 1

    assert parse_mock.OnIndent.call_count == 0
    assert parse_mock.OnDedent.call_count == 0
    assert parse_mock.OnInternalStatement.call_count == 0

# ----------------------------------------------------------------------
def test_QueueCommandObserver(parse_mock):
    observer = Statement.QueueCommandObserver(parse_mock)

    observer.Enqueue([])

    observer.OnIndent(1)
    assert parse_mock.OnIndent.call_count == 0

    observer.OnInternalStatement(2)
    assert parse_mock.OnInternalStatement.call_count == 0

    observer.OnDedent(3)
    assert parse_mock.OnDedent.call_count == 0

    observer.OnInternalStatement(4)
    assert parse_mock.OnInternalStatement.call_count == 0

    observer.Replay()
    assert parse_mock.OnIndent.call_count == 1
    assert parse_mock.OnDedent.call_count == 1
    assert parse_mock.OnInternalStatement.call_count == 2

    assert parse_mock.method_calls[0] == ("OnIndent", (1,), {})
    assert parse_mock.method_calls[1] == ("OnInternalStatement", (2,), {})
    assert parse_mock.method_calls[2] == ("OnDedent", (3,), {})
    assert parse_mock.method_calls[3] == ("OnInternalStatement", (4,), {})

    # Observer should have been reset and will not replay
    assert observer.Replay()
    assert len(parse_mock.method_calls) == 4

# ----------------------------------------------------------------------
def test_QueueCommandObserverEarlyReturn(parse_mock):
    observer = Statement.QueueCommandObserver(parse_mock)

    parse_mock.OnInternalStatement = Mock(side_effect=[True, False, True])

    observer.OnInternalStatement(1)
    observer.OnInternalStatement(2)
    observer.OnInternalStatement(3)

    assert len(parse_mock.method_calls) == 0
    assert observer.Replay() == False

    assert len(parse_mock.method_calls) == 2
    assert parse_mock.method_calls[0] == ("OnInternalStatement", (1,), {})
    assert parse_mock.method_calls[1] == ("OnInternalStatement", (2,), {})
