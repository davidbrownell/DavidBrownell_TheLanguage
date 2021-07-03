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

from unittest.mock import Mock

import pytest

from asynctest import CoroutineMock

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import CreateIterator, parse_mock

    from ..Statement import *
    from ..TokenStatement import RegexToken, TokenStatement

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
        async def ParseAsync(self, *args, **kwargs):
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
class TestStandard(object):
    # ----------------------------------------------------------------------
    class MyStatement(Statement):
        @staticmethod
        @Interface.override
        async def ParseAsync(*args, **kwargs):
            pass

    # ----------------------------------------------------------------------
    class MyParseResultData(Statement.ParseResultData):
        @staticmethod
        @Interface.override
        def ToString(
            verbose=False,
        ) -> str:
            return "Hello!"

        @staticmethod
        @Interface.override
        def Enum() -> Generator[
            Tuple[
                Optional[Statement],
                Optional[Statement.TokenParseResultData],
            ],
            None,
            None
        ]:
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
        statement = CreateStatement(20)

        data = Statement.StandardParseResultData(
            statement,
            None,
        )

        assert list(data.Enum()) == [
            (statement, None),
        ]

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

        assert list(data.Enum()) == [
            (None, data),
        ]

    # ----------------------------------------------------------------------
    def test_StandardParseResultDataEnum(self, iterator):
        statement = CreateStatement(20)

        data = Statement.StandardParseResultData(
            statement,
            Statement.TokenParseResultData(
                self._token,
                None,
                self._token.Regex.match("word"),
                iterator,
                iterator,
                False,
            ),
        )

        assert list(data.Enum()) == [
            (statement, data.Data),
        ]

# ----------------------------------------------------------------------
class TestMultipleParseResultData(object):
    _token                                  = RegexToken("My Word Token", re.compile(r"(?P<value>[a-zA-Z0-9]+)"))
    _statement                              = TokenStatement(_token)
    _iterator                               = CreateIterator("one two")

    _data                                   = Statement.MultipleStandardParseResultData(
        [
            Statement.StandardParseResultData(
                _statement,
                Statement.TokenParseResultData(
                    _token,
                    None,
                    _token.Regex.match("one"),
                    _iterator,
                    _iterator,
                    False,
                ),
            ),
            Statement.StandardParseResultData(
                _statement,
                Statement.TokenParseResultData(
                    _token,
                    None,
                    _token.Regex.match("two"),
                    _iterator,
                    _iterator,
                    False,
                ),
            ),
        ],
    )

    # ----------------------------------------------------------------------
    def test_String(self):
        assert str(self._data) == textwrap.dedent(
            """\
            My Word Token
                My Word Token <<<_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 1]
            My Word Token
                My Word Token <<<_sre.SRE_Match object; span=(0, 3), match='two'>>> ws:None [1, 1 -> 1, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_Enum(self):
        assert list(self._data.Enum()) == [
            (self._statement, self._data.DataItems[0].Data),
            (self._statement, self._data.DataItems[1].Data),
        ]

# ----------------------------------------------------------------------
def test_Parse(iterator, parse_mock):
    result = CreateStatement(1).Parse(iterator, parse_mock)
    assert result == 1

    assert parse_mock.OnIndent.call_count == 0
    assert parse_mock.OnDedent.call_count == 0
    assert parse_mock.OnInternalStatement.call_count == 0

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_QueueCommandObserver(parse_mock):
    parse_mock.OnIndentAsync = CoroutineMock()
    parse_mock.OnDedentAsync = CoroutineMock()
    parse_mock.OnInternalStatementAsync = CoroutineMock()

    observer = Statement.QueueCommandObserver(parse_mock)

    await observer.OnIndentAsync(1)
    assert parse_mock.OnIndentAsync.call_count == 0

    await observer.OnInternalStatementAsync(2)
    assert parse_mock.OnInternalStatementAsync.call_count == 0

    await observer.OnDedentAsync(3)
    assert parse_mock.OnDedentAsync.call_count == 0

    await observer.OnInternalStatementAsync(4)
    assert parse_mock.OnInternalStatementAsync.call_count == 0

    await observer.ReplayAsync()
    assert parse_mock.OnIndentAsync.call_count == 1
    assert parse_mock.OnDedentAsync.call_count == 1
    assert parse_mock.OnInternalStatementAsync.call_count == 2

    assert parse_mock.method_calls[0] == ("OnIndentAsync", (1,), {})
    assert parse_mock.method_calls[1] == ("OnInternalStatementAsync", (2,), {})
    assert parse_mock.method_calls[2] == ("OnDedentAsync", (3,), {})
    assert parse_mock.method_calls[3] == ("OnInternalStatementAsync", (4,), {})

    # Observer should have been reset and will not replay
    assert await observer.ReplayAsync()
    assert len(parse_mock.method_calls) == 4

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_QueueCommandObserverEarlyReturn(parse_mock):
    observer = Statement.QueueCommandObserver(parse_mock)

    parse_mock.OnInternalStatementAsync = CoroutineMock(side_effect=[True, False, True])

    await observer.OnInternalStatementAsync(1)
    await observer.OnInternalStatementAsync(2)
    await observer.OnInternalStatementAsync(3)

    assert len(parse_mock.method_calls) == 0
    assert await observer.ReplayAsync() == False

    assert len(parse_mock.method_calls) == 2
    assert parse_mock.method_calls[0] == ("OnInternalStatementAsync", (1,), {})
    assert parse_mock.method_calls[1] == ("OnInternalStatementAsync", (2,), {})
