# ----------------------------------------------------------------------
# |
# |  Statement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-29 16:39:02
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

    from ..Statement import *

    from ..Token import (
        NewlineToken,
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        RegexToken,
    )


# ----------------------------------------------------------------------
@pytest.fixture
def parse_mock():
    mock = Mock()

    mock._executor = ThreadPoolExecutor()
    mock.Enqueue = lambda funcs: [mock._executor.submit(func) for func in funcs]

    return mock

# ----------------------------------------------------------------------
def test_Properties():
    statement = Statement("My Statement", DynamicStatements.Statements, DynamicStatements.Expressions)

    assert statement.Name == "My Statement"
    assert statement.Items == [DynamicStatements.Statements, DynamicStatements.Expressions]

# ----------------------------------------------------------------------
def test_PropertyErrors():
    with pytest.raises(AssertionError):
        Statement("", DynamicStatements.Statements)

    with pytest.raises(AssertionError):
        Statement("My Statement")

# ----------------------------------------------------------------------
def test_InitErrors():
    with pytest.raises(AssertionError):
        Statement("Statement", (Statement("Inner", DynamicStatements.Statements), -1, 10))

    with pytest.raises(AssertionError):
        Statement("Statement", (Statement("Inner", DynamicStatements.Statements), 5, 1))

    with pytest.raises(AssertionError):
        Statement(
            "Statement",
            NewlineToken(),
            PushIgnoreWhitespaceControlToken(),
        )

    with pytest.raises(AssertionError):
        Statement(
            "Statement",
            PushIgnoreWhitespaceControlToken(),
            PopIgnoreWhitespaceControlToken(),
            NewlineToken(),
        )

    with pytest.raises(AssertionError):
        Statement(
            "Statement",
            PushIgnoreWhitespaceControlToken(),
        )

    with pytest.raises(AssertionError):
        Statement(
            "Statement",
            PopIgnoreWhitespaceControlToken(),
        )

# ----------------------------------------------------------------------
class TestParseSimple(object):
    _word_token                             = RegexToken("Word Token", re.compile(r"(?P<value>\S+)"))
    _statement                              = Statement("Standard", _word_token, _word_token, NewlineToken())

    # ----------------------------------------------------------------------
    def test_SingleSpaceSep(self, parse_mock):
        iter = NormalizedIterator(Normalize("one two"))

        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

        result = self._statement.Parse(iter, parse_mock)

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
                Newline+ <<7, 8>> ws:None [2, 1]
            """,
        )

        # Iterator is not modified
        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

    # ----------------------------------------------------------------------
    def test_MultipleSpaceSep(self, parse_mock):
        result = self._statement.Parse(
            NormalizedIterator(Normalize("one      two")),
            parse_mock,
        )

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert str(result) == textwrap.dedent(
            """\
            True
            13
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Word Token <<Regex: <_sre.SRE_Match object; span=(9, 12), match='two'>>> ws:(3, 9) [1, 13]
                Newline+ <<12, 13>> ws:None [2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_TabSep(self, parse_mock):
        result = self._statement.Parse(
            NormalizedIterator(Normalize("one\ttwo")),
            parse_mock,
        )

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
                Newline+ <<7, 8>> ws:None [2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_MultipleTabSep(self, parse_mock):
        result = self._statement.Parse(
            NormalizedIterator(Normalize("one\t\ttwo")),
            parse_mock,
        )

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Word Token <<Regex: <_sre.SRE_Match object; span=(5, 8), match='two'>>> ws:(3, 5) [1, 9]
                Newline+ <<8, 9>> ws:None [2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_TrailingSpace(self, parse_mock):
        result = self._statement.Parse(
            NormalizedIterator(Normalize("one two ")),
            parse_mock,
        )

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
                Newline+ <<8, 9>> ws:(7, 8) [2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_MultipleTrailingSpace(self, parse_mock):
        result = self._statement.Parse(
            NormalizedIterator(Normalize("one two    ")),
            parse_mock,
        )

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert str(result) == textwrap.dedent(
            """\
            True
            12
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
                Newline+ <<11, 12>> ws:(7, 11) [2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_TrailingTab(self, parse_mock):
        result = self._statement.Parse(
            NormalizedIterator(Normalize("one two\t")),
            parse_mock,
        )

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
                Newline+ <<8, 9>> ws:(7, 8) [2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_MultipleTrailingTabs(self, parse_mock):
        result = self._statement.Parse(
            NormalizedIterator(Normalize("one two\t\t\t")),
            parse_mock,
        )

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert str(result) == textwrap.dedent(
            """\
            True
            11
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
                Newline+ <<10, 11>> ws:(7, 10) [2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_MultipleLines(self, parse_mock):
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
        result = self._statement.Parse(iter, parse_mock)

        assert result.Iter.AtEnd() == False
        assert result.Iter.Line == 2
        assert result.Iter.Column == 1

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
                Newline+ <<7, 8>> ws:None [2, 1]
            """,
        )

        iter = result.Iter

        # Second line
        result = self._statement.Parse(iter, parse_mock)

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 3
        assert result.Iter.Column == 1

        assert str(result) == textwrap.dedent(
            """\
            True
            19
                Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='three'>>> ws:None [2, 6]
                Word Token <<Regex: <_sre.SRE_Match object; span=(14, 18), match='four'>>> ws:(13, 14) [2, 11]
                Newline+ <<18, 19>> ws:None [3, 1]
            """,
        )

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

    # ----------------------------------------------------------------------
    def test_TrailingWhitespace(self, parse_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("one two\n\n  \n    \n")), parse_mock)

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 5
        assert result.Iter.Column == 1

        assert str(result) == textwrap.dedent(
            """\
            True
            17
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
                Newline+ <<7, 17>> ws:None [5, 1]
            """,
        )

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
        iter = NormalizedIterator(Normalize("one two three"))

        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

        result = self._statement.Parse(iter, parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            False
            7
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
            """,
        )

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        # Iterator is not modified
        assert iter.Line == 1
        assert iter.Column == 1
        assert iter.Offset == 0

    # ----------------------------------------------------------------------
    def test_Clone(self):
        statement = self._statement.Clone()

        assert statement.Name == self._statement.Name
        assert statement.Items == self._statement.Items

# ----------------------------------------------------------------------
class TestParseIndentAndDedent(object):
    _word_token                             = RegexToken("Word", re.compile(r"(?P<value>\S+)"))

    _statement                              = Statement(
        "Statement",
        _word_token,
        NewlineToken(),
        IndentToken(),
        _word_token,
        NewlineToken(),
        _word_token,
        NewlineToken(),
        DedentToken(),
    )

    # ----------------------------------------------------------------------
    def test_Match(self, parse_mock):
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
            parse_mock,
        )

        assert parse_mock.OnIndent.call_count == 1
        assert parse_mock.OnDedent.call_count == 1
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.Line == 4
        assert result.Iter.Column == 1
        assert result.Iter.Offset == 22
        assert result.Iter.AtEnd()

        assert str(result) == textwrap.dedent(
            """\
            True
            22
                Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Newline+ <<3, 4>> ws:None [2, 1]
                Indent <<4, 8, (4)>> ws:None [2, 5]
                Word <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 8]
                Newline+ <<11, 12>> ws:None [3, 1]
                Word <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 10]
                Newline+ <<21, 22>> ws:None [4, 1]
                Dedent <<>> ws:None [4, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
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
            parse_mock,
        )

        # The code stopped parsing after 'two', so only 1 indent was encountered and 0 dedents were
        # encountered
        assert parse_mock.OnIndent.call_count == 1
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.Line == 3
        assert result.Iter.Column == 1
        assert result.Iter.Offset == 12
        assert result.Iter.AtEnd() == False

        assert str(result) == textwrap.dedent(
            """\
            False
            12
                Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Newline+ <<3, 4>> ws:None [2, 1]
                Indent <<4, 8, (4)>> ws:None [2, 5]
                Word <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 8]
                Newline+ <<11, 12>> ws:None [3, 1]
            """,
        )

# ----------------------------------------------------------------------
def test_FinishEarly(parse_mock):
    word_token = RegexToken("Word", re.compile(r"(?P<value>\S+)"))

    statement = Statement("Statement", word_token, NewlineToken(), word_token)

    iter = NormalizedIterator(Normalize("one"))

    assert iter.Line == 1
    assert iter.Column == 1
    assert iter.Offset == 0

    result = statement.Parse(iter, parse_mock)

    assert parse_mock.OnIndent.call_count == 0
    assert parse_mock.OnDedent.call_count == 0
    assert parse_mock.OnInternalStatement.call_count == 0

    assert result.Iter.AtEnd()
    assert result.Iter.Line == 2
    assert result.Iter.Column == 1

    assert str(result) == textwrap.dedent(
        """\
        False
        4
            Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
            Newline+ <<3, 4>> ws:None [2, 1]
        """,
    )

    # Iterator is not modified
    assert iter.Line == 1
    assert iter.Column == 1
    assert iter.Offset == 0

# ----------------------------------------------------------------------
class TestIgnoreWhitespace(object):
    _word_token                             = RegexToken("Word", re.compile(r"(?P<value>\S+)"))
    _lpar_token                             = RegexToken("lpar", re.compile(r"\("))
    _rpar_token                             = RegexToken("rpar", re.compile(r"\)"))

    _statement                              = Statement(
        "Statement",
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
    )

    # ----------------------------------------------------------------------
    def test_MatchNoExtra(self, parse_mock):
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
            parse_mock,
        )

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.AtEnd()
        assert result.Iter.Line == 11
        assert result.Iter.Column == 1
        assert result.Iter.Offset == 60

        assert str(result) == textwrap.dedent(
            """\
            True
            60
                Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                lpar <<Regex: <_sre.SRE_Match object; span=(4, 5), match='('>>> ws:(3, 4) [1, 6]
                Newline+ <<5, 8>> ws:None !Ignored! [4, 1]
                Indent <<8, 12, (4)>> ws:None !Ignored! [4, 5]
                Word <<Regex: <_sre.SRE_Match object; span=(12, 15), match='two'>>> ws:None [4, 8]
                Newline+ <<15, 17>> ws:None !Ignored! [6, 1]
                Indent <<17, 25, (8)>> ws:None !Ignored! [6, 9]
                Word <<Regex: <_sre.SRE_Match object; span=(25, 30), match='three'>>> ws:None [6, 14]
                Newline+ <<30, 31>> ws:None !Ignored! [7, 1]
                Dedent <<>> ws:None !Ignored! [7, 5]
                Word <<Regex: <_sre.SRE_Match object; span=(35, 39), match='four'>>> ws:None [7, 9]
                Newline+ <<39, 40>> ws:None !Ignored! [8, 1]
                Indent <<40, 48, (8)>> ws:None !Ignored! [8, 9]
                Word <<Regex: <_sre.SRE_Match object; span=(48, 52), match='five'>>> ws:None [8, 13]
                Newline+ <<52, 54>> ws:None !Ignored! [10, 1]
                Dedent <<>> ws:None !Ignored! [10, 1]
                Dedent <<>> ws:None !Ignored! [10, 1]
                rpar <<Regex: <_sre.SRE_Match object; span=(54, 55), match=')'>>> ws:None [10, 2]
                Word <<Regex: <_sre.SRE_Match object; span=(56, 59), match='six'>>> ws:(55, 56) [10, 6]
                Newline+ <<59, 60>> ws:None [11, 1]
            """,
        )

# ----------------------------------------------------------------------
def test_IgnoreControlTokens(parse_mock):
    # ----------------------------------------------------------------------
    @Interface.staticderived
    class MyControlToken(ControlTokenBase):
        Name                                = Interface.DerivedProperty("MyControlToken")

    # ----------------------------------------------------------------------

    control_token = MyControlToken()
    regex_token = RegexToken("test", re.compile("test"))

    result = Statement(
        "Statement",
        control_token,
        regex_token,
    ).Parse(NormalizedIterator(Normalize("test")), parse_mock)

    assert parse_mock.OnIndent.call_count == 0
    assert parse_mock.OnDedent.call_count == 0
    assert parse_mock.OnInternalStatement.call_count == 0

    assert result.Iter.Line == 1
    assert result.Iter.Column == 5
    assert result.Iter.AtEnd() == False

    assert str(result) == textwrap.dedent(
        """\
        True
        4
            test <<Regex: <_sre.SRE_Match object; span=(0, 4), match='test'>>> ws:None [1, 5]
        """,
    )

# ----------------------------------------------------------------------
class TestEmbeddedStatements(object):
    _word_token                             = RegexToken("Word", re.compile(r"(?P<value>\S+)"))
    _lpar_token                             = RegexToken("lpar", re.compile(r"(?P<value>\()"))
    _rpar_token                             = RegexToken("rpar", re.compile(r"(?P<value>\))"))

    _inner_statement                        = Statement("inner", _word_token, _word_token)
    _statement                              = Statement(
        "Statement",
        _lpar_token,
        _inner_statement,
        _rpar_token,
    )

    # ----------------------------------------------------------------------
    def test_Match(self, parse_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("( one two )")), parse_mock)

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 1
        assert parse_mock.OnInternalStatement.call_args_list[0][0][0].Statement == self._inner_statement
        assert parse_mock.OnInternalStatement.call_args_list[0][0][1].Offset == 1
        assert parse_mock.OnInternalStatement.call_args_list[0][0][2].Offset == 9

        assert result.Iter.Line == 1
        assert result.Iter.Column == 12
        assert result.Iter.AtEnd() == False

        assert str(result) == textwrap.dedent(
            """\
            True
            11
                lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 2]
                inner
                    Word <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 6]
                    Word <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 10]
                rpar <<Regex: <_sre.SRE_Match object; span=(10, 11), match=')'>>> ws:(9, 10) [1, 12]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatchAllInner(self, parse_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("( one two")), parse_mock)

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 1
        assert parse_mock.OnInternalStatement.call_args_list[0][0][0].Statement == self._inner_statement
        assert parse_mock.OnInternalStatement.call_args_list[0][0][1].Offset == 1
        assert parse_mock.OnInternalStatement.call_args_list[0][0][2].Offset == 9

        assert result.Iter.Line == 1
        assert result.Iter.Column == 10
        assert result.Iter.AtEnd() == False

        assert str(result) == textwrap.dedent(
            """\
            False
            9
                lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 2]
                inner
                    Word <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 6]
                    Word <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 10]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatchPartialInner(self, parse_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("( one ")), parse_mock)

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.Line == 1
        assert result.Iter.Column == 6
        assert result.Iter.AtEnd() == False

        assert str(result) == textwrap.dedent(
            """\
            False
            5
                lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 2]
                inner
                    Word <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 6]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatchFirstOnly(self, parse_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("( ")), parse_mock)

        assert parse_mock.OnIndent.call_count == 0
        assert parse_mock.OnDedent.call_count == 0
        assert parse_mock.OnInternalStatement.call_count == 0

        assert result.Iter.Line == 1
        assert result.Iter.Column == 2
        assert result.Iter.AtEnd() == False

        assert str(result) == textwrap.dedent(
            """\
            False
            1
                lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 2]
                inner
                    <No results>
            """,
        )

# ----------------------------------------------------------------------
class TestDynamicStatements(object):
    _word_token                             = RegexToken("Word Token", re.compile(r"(?P<value>\S+)"))
    _number_token                           = RegexToken("Number Token", re.compile(r"(?P<value>\d+)"))

    _word_statement                         = Statement("Word Statement", _word_token, _word_token, NewlineToken())
    _number_statement                       = Statement("Number Statement", _number_token, NewlineToken())

    _statement                              = Statement(
        "Statement",
        DynamicStatements.Statements,
        DynamicStatements.Statements,
        DynamicStatements.Expressions,
    )

    # ----------------------------------------------------------------------
    @staticmethod
    @pytest.fixture
    def modified_parse_mock(parse_mock):
        parse_mock.GetDynamicStatements.side_effect = lambda value: [TestDynamicStatements._word_statement, TestDynamicStatements._number_statement] if value == DynamicStatements.Statements else [TestDynamicStatements._number_statement]
        parse_mock.OnInternalStatement = Mock(return_value=True)

        return parse_mock

    # ----------------------------------------------------------------------
    def test_Match(self, modified_parse_mock):
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
            modified_parse_mock,
        )

        assert modified_parse_mock.OnIndent.call_count == 0
        assert modified_parse_mock.OnDedent.call_count == 0
        assert modified_parse_mock.OnInternalStatement.call_count == 3

        assert modified_parse_mock.OnInternalStatement.call_args_list[0][0][0].Statement == self._word_statement
        assert modified_parse_mock.OnInternalStatement.call_args_list[0][0][1].Offset == 0
        assert modified_parse_mock.OnInternalStatement.call_args_list[0][0][2].Offset == 12

        assert modified_parse_mock.OnInternalStatement.call_args_list[1][0][0].Statement == self._number_statement
        assert modified_parse_mock.OnInternalStatement.call_args_list[1][0][1].Offset == 12
        assert modified_parse_mock.OnInternalStatement.call_args_list[1][0][2].Offset == 16

        assert modified_parse_mock.OnInternalStatement.call_args_list[2][0][0].Statement == self._number_statement
        assert modified_parse_mock.OnInternalStatement.call_args_list[2][0][1].Offset == 16
        assert modified_parse_mock.OnInternalStatement.call_args_list[2][0][2].Offset == 20

        assert result.Iter.Line == 4
        assert result.Iter.Column == 1
        assert result.Iter.AtEnd()

        assert str(result) == textwrap.dedent(
            """\
            True
            20
                DynamicStatements.Statements
                    Or: [Word Statement, Number Statement]
                        Word Statement
                            Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='word1'>>> ws:None [1, 6]
                            Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='word2'>>> ws:(5, 6) [1, 12]
                            Newline+ <<11, 12>> ws:None [2, 1]
                DynamicStatements.Statements
                    Or: [Word Statement, Number Statement]
                        Number Statement
                            Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 4]
                            Newline+ <<15, 16>> ws:None [3, 1]
                DynamicStatements.Expressions
                    Or: [Number Statement]
                        Number Statement
                            Number Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='456'>>> ws:None [3, 4]
                            Newline+ <<19, 20>> ws:None [4, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatch(self, modified_parse_mock):
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
            modified_parse_mock,
        )

        assert result.Iter.Line == 3
        assert result.Iter.Column == 1
        assert result.Iter.AtEnd() == False

        assert str(result) == textwrap.dedent(
            """\
            False
            16
                DynamicStatements.Statements
                    Or: [Word Statement, Number Statement]
                        Word Statement
                            Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='word1'>>> ws:None [1, 6]
                            Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='word2'>>> ws:(5, 6) [1, 12]
                            Newline+ <<11, 12>> ws:None [2, 1]
                DynamicStatements.Statements
                    Or: [Word Statement, Number Statement]
                        Number Statement
                            Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 4]
                            Newline+ <<15, 16>> ws:None [3, 1]
                DynamicStatements.Expressions
                    Or: [Number Statement]
                        Number Statement
                            <No results>
            """,
        )

# ----------------------------------------------------------------------
class TestParseMultiple(object):
    # ----------------------------------------------------------------------
    def test_FirstMatch(self, parse_mock):
        result = Statement.ParseMultiple(
            [
                Statement("1", RegexToken("1t", re.compile("1234"))),
                Statement("2", RegexToken("2t", re.compile("5678"))),
                Statement("3", RegexToken("3t", re.compile("9"))),
            ],
            NormalizedIterator(Normalize("1234")),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or: [1, 2, 3]
                    1
                        1t <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 5]
            """,
        )

    # ----------------------------------------------------------------------
    def test_SecondMatch(self, parse_mock):
        result = Statement.ParseMultiple(
            [
                Statement("1", RegexToken("1t", re.compile("1234"))),
                Statement("2", RegexToken("2t", re.compile("123456"))),
                Statement("3", RegexToken("3t", re.compile("9"))),
            ],
            NormalizedIterator(Normalize("123456")),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            6
                Or: [1, 2, 3]
                    2
                        2t <<Regex: <_sre.SRE_Match object; span=(0, 6), match='123456'>>> ws:None [1, 7]
            """,
        )

    # ----------------------------------------------------------------------
    def test_SecondMatchNoSort(self, parse_mock):
        result = Statement.ParseMultiple(
            [
                Statement("1", RegexToken("1t", re.compile("1234"))),
                Statement("2", RegexToken("2t", re.compile("123456"))),
                Statement("3", RegexToken("3t", re.compile("9"))),
            ],
            NormalizedIterator(Normalize("123456")),
            parse_mock,
            sort_results=False,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or: [1, 2, 3]
                    1
                        1t <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 5]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
        result = Statement.ParseMultiple(
            [
                Statement("1", RegexToken("1t", re.compile("1234"))),
                Statement("2", RegexToken("2t", re.compile("123456"))),
                Statement("3", RegexToken("3t", re.compile("9"))),
            ],
            NormalizedIterator(Normalize("_____")),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            0
                Or: [1, 2, 3]
                    1
                        <No results>
                    2
                        <No results>
                    3
                        <No results>
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatchNoSort(self, parse_mock):
        result = Statement.ParseMultiple(
            [
                Statement("1", RegexToken("1t", re.compile("1234"))),
                Statement("2", RegexToken("2t", re.compile("123456"))),
                Statement("3", RegexToken("3t", re.compile("9"))),
            ],
            NormalizedIterator(Normalize("_____")),
            parse_mock,
            sort_results=False,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            0
                Or: [1, 2, 3]
                    1
                        <No results>
                    2
                        <No results>
                    3
                        <No results>
            """,
        )

    # ----------------------------------------------------------------------
    def test_Cancellation(self, parse_mock):
        statement_mock = Mock(spec=Statement)
        statement_mock.Name = "Early Termination"
        statement_mock.Parse = Mock(return_value=None)

        result = Statement.ParseMultiple(
            [
                statement_mock,
            ],
            NormalizedIterator(Normalize("123456")),
            parse_mock,
        )

        assert result is None

    # ----------------------------------------------------------------------
    def test_SingleStatementOptimization(self, parse_mock):
        result = Statement.ParseMultiple(
            [
                Statement(
                    "Statement",
                    RegexToken("Token", re.compile("1234")),
                ),
            ],
            NormalizedIterator(Normalize("1234")),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or: [Statement]
                    Statement
                        Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 5]
            """,
        )

    # ----------------------------------------------------------------------
    def test_SingleThreaded(self, parse_mock):
        result = Statement.ParseMultiple(
            [
                Statement("1", RegexToken("1t", re.compile("1234"))),
                Statement("2", RegexToken("2t", re.compile("123456"))),
                Statement("3", RegexToken("3t", re.compile("9"))),
            ],
            NormalizedIterator(Normalize("123456")),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            6
                Or: [1, 2, 3]
                    2
                        2t <<Regex: <_sre.SRE_Match object; span=(0, 6), match='123456'>>> ws:None [1, 7]
            """,
        )

    # ----------------------------------------------------------------------
    def test_IgnoreWhitespaceNoMatch(self, parse_mock):
        result = Statement.ParseMultiple(
            [
                Statement("1", RegexToken("1t", re.compile("1234"))),
                Statement("2", RegexToken("2t", re.compile("123456"))),
                Statement("3", RegexToken("3t", re.compile("9"))),
            ],
            NormalizedIterator(Normalize("  123456\n")),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            0
                Or: [1, 2, 3]
                    1
                        <No results>
                    2
                        <No results>
                    3
                        <No results>
            """,
        )

    # ----------------------------------------------------------------------
    def test_IgnoreWhitespaceMatch(self, parse_mock):
        result = Statement.ParseMultiple(
            [
                Statement("1", RegexToken("1t", re.compile("1234"))),
                Statement("2", RegexToken("2t", re.compile("123456"))),
                Statement("3", RegexToken("3t", re.compile("9"))),
            ],
            NormalizedIterator(Normalize("  123456\n")),
            parse_mock,
            ignore_whitespace=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Or: [1, 2, 3]
                    Indent <<0, 2, (2)>> ws:None !Ignored! [1, 3]
                    2
                        2t <<Regex: <_sre.SRE_Match object; span=(2, 8), match='123456'>>> ws:None [1, 9]
            """,
        )

# ----------------------------------------------------------------------
def test_ParseResultStrNoResults():
    assert str(Statement.ParseResult(True, [], NormalizedIterator(Normalize("1234")))) == textwrap.dedent(
        """\
        True
        0
            <No results>
        """,
    )

# ----------------------------------------------------------------------
def test_OnInternalStatementTermination(parse_mock):
    parse_mock.OnInternalStatement = Mock(return_value=False)

    result = Statement(
        "Statement",
        Statement("Inner", NewlineToken()),
    ).Parse(
        NormalizedIterator(Normalize("\n\n\n")),
        parse_mock,
    )

    assert result is None

# ----------------------------------------------------------------------
class TestRepeat(object):
    _word_token                             = RegexToken("Word Token", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number Token", re.compile(r"(?P<value>\d+)"))
    _upper_token                            = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))

    _word_statement                         = Statement("Word Statement", _word_token, NewlineToken())
    _number_statement                       = Statement("Number Statement", _number_token, NewlineToken())
    _upper_statement                        = Statement("Upper Statement", _upper_token, NewlineToken())

    _statement                              = Statement(
        "Statement",
        (_word_statement, 0, None),
        (_number_statement, 1, None),
        (_upper_statement, 0, 1),
        (_word_statement, 1, None),
    )

    # ----------------------------------------------------------------------
    def test_Match1(self, parse_mock):
        assert str(
            self._statement.Parse(
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            worda
                            wordb
                            12
                            3456
                            UPPER
                            wordc
                            wordd
                            worde
                            """,
                        ),
                    ),
                ),
                parse_mock,
            ),
        ) == textwrap.dedent(
            """\
            True
            44
                Repeat: (Word Statement, 0, None)
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 6]
                        Newline+ <<5, 6>> ws:None [2, 1]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:None [2, 6]
                        Newline+ <<11, 12>> ws:None [3, 1]
                Repeat: (Number Statement, 1, None)
                    Number Statement
                        Number Token <<Regex: <_sre.SRE_Match object; span=(12, 14), match='12'>>> ws:None [3, 3]
                        Newline+ <<14, 15>> ws:None [4, 1]
                    Number Statement
                        Number Token <<Regex: <_sre.SRE_Match object; span=(15, 19), match='3456'>>> ws:None [4, 5]
                        Newline+ <<19, 20>> ws:None [5, 1]
                Repeat: (Upper Statement, 0, 1)
                    Upper Statement
                        Upper Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='UPPER'>>> ws:None [5, 6]
                        Newline+ <<25, 26>> ws:None [6, 1]
                Repeat: (Word Statement, 1, None)
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(26, 31), match='wordc'>>> ws:None [6, 6]
                        Newline+ <<31, 32>> ws:None [7, 1]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(32, 37), match='wordd'>>> ws:None [7, 6]
                        Newline+ <<37, 38>> ws:None [8, 1]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(38, 43), match='worde'>>> ws:None [8, 6]
                        Newline+ <<43, 44>> ws:None [9, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_Match2(self, parse_mock):
        assert str(
            self._statement.Parse(
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            12
                            3456
                            UPPER
                            wordc
                            wordd
                            worde
                            """,
                        ),
                    ),
                ),
                parse_mock,
            ),
        ) == textwrap.dedent(
            """\
            True
            32
                Repeat: (Word Statement, 0, None)
                    <No results>
                Repeat: (Number Statement, 1, None)
                    Number Statement
                        Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 3]
                        Newline+ <<2, 3>> ws:None [2, 1]
                    Number Statement
                        Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 5]
                        Newline+ <<7, 8>> ws:None [3, 1]
                Repeat: (Upper Statement, 0, 1)
                    Upper Statement
                        Upper Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='UPPER'>>> ws:None [3, 6]
                        Newline+ <<13, 14>> ws:None [4, 1]
                Repeat: (Word Statement, 1, None)
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordc'>>> ws:None [4, 6]
                        Newline+ <<19, 20>> ws:None [5, 1]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='wordd'>>> ws:None [5, 6]
                        Newline+ <<25, 26>> ws:None [6, 1]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(26, 31), match='worde'>>> ws:None [6, 6]
                        Newline+ <<31, 32>> ws:None [7, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_Match3(self, parse_mock):
        assert str(
            self._statement.Parse(
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            worda
                            12
                            3456
                            wordc
                            wordd
                            worde
                            """,
                        ),
                    ),
                ),
                parse_mock,
            ),
        ) == textwrap.dedent(
            """\
            True
            32
                Repeat: (Word Statement, 0, None)
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 6]
                        Newline+ <<5, 6>> ws:None [2, 1]
                Repeat: (Number Statement, 1, None)
                    Number Statement
                        Number Token <<Regex: <_sre.SRE_Match object; span=(6, 8), match='12'>>> ws:None [2, 3]
                        Newline+ <<8, 9>> ws:None [3, 1]
                    Number Statement
                        Number Token <<Regex: <_sre.SRE_Match object; span=(9, 13), match='3456'>>> ws:None [3, 5]
                        Newline+ <<13, 14>> ws:None [4, 1]
                Repeat: (Upper Statement, 0, 1)
                    <No results>
                Repeat: (Word Statement, 1, None)
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordc'>>> ws:None [4, 6]
                        Newline+ <<19, 20>> ws:None [5, 1]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='wordd'>>> ws:None [5, 6]
                        Newline+ <<25, 26>> ws:None [6, 1]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(26, 31), match='worde'>>> ws:None [6, 6]
                        Newline+ <<31, 32>> ws:None [7, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_Match4(self, parse_mock):
        assert str(
            self._statement.Parse(
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            12
                            3456
                            wordc
                            wordd
                            worde
                            """,
                        ),
                    ),
                ),
                parse_mock,
            ),
        ) == textwrap.dedent(
            """\
            True
            26
                Repeat: (Word Statement, 0, None)
                    <No results>
                Repeat: (Number Statement, 1, None)
                    Number Statement
                        Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 3]
                        Newline+ <<2, 3>> ws:None [2, 1]
                    Number Statement
                        Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 5]
                        Newline+ <<7, 8>> ws:None [3, 1]
                Repeat: (Upper Statement, 0, 1)
                    <No results>
                Repeat: (Word Statement, 1, None)
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 6]
                        Newline+ <<13, 14>> ws:None [4, 1]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordd'>>> ws:None [4, 6]
                        Newline+ <<19, 20>> ws:None [5, 1]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='worde'>>> ws:None [5, 6]
                        Newline+ <<25, 26>> ws:None [6, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatch1(self, parse_mock):
        assert str(
            self._statement.Parse(
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            worda
                            wordb
                            UPPER
                            wordc
                            wordd
                            worde
                            """,
                        ),
                    ),
                ),
                parse_mock,
            ),
        ) == textwrap.dedent(
            """\
            False
            12
                Repeat: (Word Statement, 0, None)
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 6]
                        Newline+ <<5, 6>> ws:None [2, 1]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:None [2, 6]
                        Newline+ <<11, 12>> ws:None [3, 1]
                Repeat: (Number Statement, 1, None)
                    <No results>
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatch2(self, parse_mock):
        assert str(
            self._statement.Parse(
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            12
                            3456
                            UPPER
                            999
                            """,
                        ),
                    ),
                ),
                parse_mock,
            ),
        ) == textwrap.dedent(
            """\
            False
            14
                Repeat: (Word Statement, 0, None)
                    <No results>
                Repeat: (Number Statement, 1, None)
                    Number Statement
                        Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 3]
                        Newline+ <<2, 3>> ws:None [2, 1]
                    Number Statement
                        Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 5]
                        Newline+ <<7, 8>> ws:None [3, 1]
                Repeat: (Upper Statement, 0, 1)
                    Upper Statement
                        Upper Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='UPPER'>>> ws:None [3, 6]
                        Newline+ <<13, 14>> ws:None [4, 1]
                Repeat: (Word Statement, 1, None)
                    <No results>
            """,
        )

    # ----------------------------------------------------------------------
    def test_EarlyTermination(self, parse_mock):
        parse_mock.OnInternalStatement = Mock(
            side_effect=[True, True, True, True, False],
        )

        result = self._statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        worda
                        wordb
                        12
                        3456
                        wordc
                        wordd
                        worde
                        """,
                    ),
                ),
            ),
            parse_mock,
        )

        assert result is None

# ----------------------------------------------------------------------
class TestRepeatToken(object):
    _word_token                             = RegexToken("Word Token", re.compile(r"(?P<value>[a-z]+)"))
    _word_statement                         = Statement(
        "Statement",
        (_word_token, 0, 3),
    )

    # ----------------------------------------------------------------------
    def test_MaxItems(self, parse_mock):
        result = self._word_statement.Parse(NormalizedIterator(Normalize("one two three")), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            13
                Repeat: (Word Token, 0, 3)
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                    Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
                    Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='three'>>> ws:(7, 8) [1, 14]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoItems(self, parse_mock):
        result = self._word_statement.Parse(NormalizedIterator(Normalize("")), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            0
                Repeat: (Word Token, 0, 3)
                    <No results>
            """,
        )

class TestRepeatSimilarStatements(object):
    _word_token                             = RegexToken("Word Token", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number Token", re.compile(r"(?P<value>\d+)"))

    # Ensure that the first statement doesn't eat the word so that it isn't available to the
    # second statement.
    _statement                              = Statement(
        "Statement",
        (Statement("Word & Number", _word_token, _number_token), 0, None),
        (_word_token, 0, 1),
    )

    # ----------------------------------------------------------------------
    def test_LargeMatch(self, parse_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("word 123")), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Repeat: (Word & Number, 0, None)
                    Word & Number
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 5]
                        Number Token <<Regex: <_sre.SRE_Match object; span=(5, 8), match='123'>>> ws:(4, 5) [1, 9]
                Repeat: (Word Token, 0, 1)
                    <No results>
            """,
        )

    # ----------------------------------------------------------------------
    def test_IgnoreWhitespace(self, parse_mock):
        statement = self._statement.Clone()

        statement.Items.insert(0, PushIgnoreWhitespaceControlToken())
        statement.Items.append(PopIgnoreWhitespaceControlToken())

        result = statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        one 1
                            two 2
                                three 3

                            four 4
                                        five 5
                        six
                        """,
                    ),
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            71
                Repeat: (Word & Number, 0, None)
                    Word & Number
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                        Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='1'>>> ws:(3, 4) [1, 6]
                    Newline+ <<5, 6>> ws:None !Ignored! [2, 1]
                    Indent <<6, 10, (4)>> ws:None !Ignored! [2, 5]
                    Word & Number
                        Word Token <<Regex: <_sre.SRE_Match object; span=(10, 13), match='two'>>> ws:None [2, 8]
                        Number Token <<Regex: <_sre.SRE_Match object; span=(14, 15), match='2'>>> ws:(13, 14) [2, 10]
                    Newline+ <<15, 16>> ws:None !Ignored! [3, 1]
                    Indent <<16, 24, (8)>> ws:None !Ignored! [3, 9]
                    Word & Number
                        Word Token <<Regex: <_sre.SRE_Match object; span=(24, 29), match='three'>>> ws:None [3, 14]
                        Number Token <<Regex: <_sre.SRE_Match object; span=(30, 31), match='3'>>> ws:(29, 30) [3, 16]
                    Newline+ <<31, 33>> ws:None !Ignored! [5, 1]
                    Dedent <<>> ws:None !Ignored! [5, 5]
                    Word & Number
                        Word Token <<Regex: <_sre.SRE_Match object; span=(37, 41), match='four'>>> ws:None [5, 9]
                        Number Token <<Regex: <_sre.SRE_Match object; span=(42, 43), match='4'>>> ws:(41, 42) [5, 11]
                    Newline+ <<43, 44>> ws:None !Ignored! [6, 1]
                    Indent <<44, 60, (16)>> ws:None !Ignored! [6, 17]
                    Word & Number
                        Word Token <<Regex: <_sre.SRE_Match object; span=(60, 64), match='five'>>> ws:None [6, 21]
                        Number Token <<Regex: <_sre.SRE_Match object; span=(65, 66), match='5'>>> ws:(64, 65) [6, 23]
                Newline+ <<66, 67>> ws:None !Ignored! [7, 1]
                Dedent <<>> ws:None !Ignored! [7, 1]
                Dedent <<>> ws:None !Ignored! [7, 1]
                Repeat: (Word Token, 0, 1)
                    Word Token <<Regex: <_sre.SRE_Match object; span=(67, 70), match='six'>>> ws:None [7, 4]
                Newline+ <<70, 71>> ws:None !Ignored! [8, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_SmallMatch(self, parse_mock):
        result = self._statement.Parse(NormalizedIterator(Normalize("word")), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Repeat: (Word & Number, 0, None)
                    <No results>
                Repeat: (Word Token, 0, 1)
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 5]
            """,
        )

# ----------------------------------------------------------------------
class TestOr(object):
    _word_token                             = RegexToken("Word Token", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number Token", re.compile(r"(?P<value>\d+)"))
    _upper_token                            = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))

    _word_statement                         = Statement("Word Statement", _word_token, NewlineToken())
    _number_statement                       = Statement("Number Statement", _number_token, NewlineToken())
    _upper_statement                        = Statement("Upper Statement", _upper_token, NewlineToken())

    _statement                              = Statement(
        "Statement",
        [_word_statement, _number_statement, _upper_statement],
    )

    # ----------------------------------------------------------------------
    def test_WordMatch(self, parse_mock):
        assert str(self._statement.Parse(NormalizedIterator(Normalize("word")), parse_mock)) == textwrap.dedent(
            """\
            True
            5
                Or: [Word Statement, Number Statement, Upper Statement]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 5]
                        Newline+ <<4, 5>> ws:None [2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NumberMatch(self, parse_mock):
        assert str(self._statement.Parse(NormalizedIterator(Normalize("12345678")), parse_mock)) == textwrap.dedent(
            """\
            True
            9
                Or: [Word Statement, Number Statement, Upper Statement]
                    Number Statement
                        Number Token <<Regex: <_sre.SRE_Match object; span=(0, 8), match='12345678'>>> ws:None [1, 9]
                        Newline+ <<8, 9>> ws:None [2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_UppserMatch(self, parse_mock):
        assert str(self._statement.Parse(NormalizedIterator(Normalize("UP")), parse_mock)) == textwrap.dedent(
            """\
            True
            3
                Or: [Word Statement, Number Statement, Upper Statement]
                    Upper Statement
                        Upper Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='UP'>>> ws:None [1, 3]
                        Newline+ <<2, 3>> ws:None [2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
        assert str(self._statement.Parse(NormalizedIterator(Normalize("this is not a match")), parse_mock)) == textwrap.dedent(
            """\
            False
            4
                Or: [Word Statement, Number Statement, Upper Statement]
                    Word Statement
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='this'>>> ws:None [1, 5]
                    Number Statement
                        <No results>
                    Upper Statement
                        <No results>
            """,
        )

    # ----------------------------------------------------------------------
    def test_EarlyTermination(self, parse_mock):
        parse_mock.OnInternalStatement = Mock(side_effect=[True, False])

        result = self._statement.Parse(NormalizedIterator(Normalize("word")), parse_mock)

        assert result is None

# ----------------------------------------------------------------------
class TestComments(object):
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _number_token                           = RegexToken("Number", re.compile(r"(?P<value>[0-9]+)"))

    _lower_line_statement                   = Statement("Lower Line", _lower_token, NewlineToken())
    _upper_line_statement                   = Statement("Upper Line", _upper_token, NewlineToken())
    _number_line_statement                  = Statement("Number Line", _number_token, NewlineToken())

    _multiline_statement                    = Statement(
        "Multiline",
        (
            Statement(
                "Repeat",
                _lower_line_statement,
                _upper_line_statement,
                _number_line_statement,
            ),
            1,
            None,
        ),
    )

    _indent_statement                       = Statement(
        "Indent",
        _lower_token,
        RegexToken("Colon", re.compile(":")),
        NewlineToken(),
        IndentToken(),
        _upper_line_statement,
        _number_line_statement,
        DedentToken(),
    )

    # ----------------------------------------------------------------------
    def test_Multiline(self, parse_mock):
        result = self._multiline_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        one # Comment 1
                        TWO
                        3
                        four
                        FIVE                # Comment 5
                        66
                        seven
                        EIGHT
                        999    # Comment 9
                        ten     # Comment 10
                        ELEVEN  # Comment 11
                        12      # Comment 12
                        """,
                    ),
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            156
                Repeat: (Repeat, 1, None)
                    Repeat
                        Lower Line
                            Lower <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                            Comment <<Regex: <_sre.SRE_Match object; span=(4, 15), match='# Comment 1'>>> ws:(3, 4) !Ignored! [1, 16]
                            Newline+ <<15, 16>> ws:None [2, 1]
                        Upper Line
                            Upper <<Regex: <_sre.SRE_Match object; span=(16, 19), match='TWO'>>> ws:None [2, 4]
                            Newline+ <<19, 20>> ws:None [3, 1]
                        Number Line
                            Number <<Regex: <_sre.SRE_Match object; span=(20, 21), match='3'>>> ws:None [3, 2]
                            Newline+ <<21, 22>> ws:None [4, 1]
                    Repeat
                        Lower Line
                            Lower <<Regex: <_sre.SRE_Match object; span=(22, 26), match='four'>>> ws:None [4, 5]
                            Newline+ <<26, 27>> ws:None [5, 1]
                        Upper Line
                            Upper <<Regex: <_sre.SRE_Match object; span=(27, 31), match='FIVE'>>> ws:None [5, 5]
                            Comment <<Regex: <_sre.SRE_Match object; span=(47, 58), match='# Comment 5'>>> ws:(31, 47) !Ignored! [5, 32]
                            Newline+ <<58, 59>> ws:None [6, 1]
                        Number Line
                            Number <<Regex: <_sre.SRE_Match object; span=(59, 61), match='66'>>> ws:None [6, 3]
                            Newline+ <<61, 62>> ws:None [7, 1]
                    Repeat
                        Lower Line
                            Lower <<Regex: <_sre.SRE_Match object; span=(62, 67), match='seven'>>> ws:None [7, 6]
                            Newline+ <<67, 68>> ws:None [8, 1]
                        Upper Line
                            Upper <<Regex: <_sre.SRE_Match object; span=(68, 73), match='EIGHT'>>> ws:None [8, 6]
                            Newline+ <<73, 74>> ws:None [9, 1]
                        Number Line
                            Number <<Regex: <_sre.SRE_Match object; span=(74, 77), match='999'>>> ws:None [9, 4]
                            Comment <<Regex: <_sre.SRE_Match object; span=(81, 92), match='# Comment 9'>>> ws:(77, 81) !Ignored! [9, 19]
                            Newline+ <<92, 93>> ws:None [10, 1]
                    Repeat
                        Lower Line
                            Lower <<Regex: <_sre.SRE_Match object; span=(93, 96), match='ten'>>> ws:None [10, 4]
                            Comment <<Regex: <_sre.SRE_Match object; span=(101, 113), match='# Comment 10'>>> ws:(96, 101) !Ignored! [10, 21]
                            Newline+ <<113, 114>> ws:None [11, 1]
                        Upper Line
                            Upper <<Regex: <_sre.SRE_Match object; span=(114, 120), match='ELEVEN'>>> ws:None [11, 7]
                            Comment <<Regex: <_sre.SRE_Match object; span=(122, 134), match='# Comment 11'>>> ws:(120, 122) !Ignored! [11, 21]
                            Newline+ <<134, 135>> ws:None [12, 1]
                        Number Line
                            Number <<Regex: <_sre.SRE_Match object; span=(135, 137), match='12'>>> ws:None [12, 3]
                            Comment <<Regex: <_sre.SRE_Match object; span=(143, 155), match='# Comment 12'>>> ws:(137, 143) !Ignored! [12, 21]
                            Newline+ <<155, 156>> ws:None [13, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_Indent(self, parse_mock):
        iterator = NormalizedIterator(
            Normalize(
                textwrap.dedent(
                    """\
                    one:  # Comment 1
                        TWO
                        3
                    four:
                        FIVE # Comment 5
                        66
                    seven:
                        EIGHT
                        999                 # Comment 9
                    ten:            # Comment 10
                        ELEVEN      # Comment 11
                        12          # Comment 12
                    """,
                ),
            ),
        )

        result = self._indent_statement.Parse(iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            32
                Lower <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                Colon <<Regex: <_sre.SRE_Match object; span=(3, 4), match=':'>>> ws:None [1, 5]
                Comment <<Regex: <_sre.SRE_Match object; span=(6, 17), match='# Comment 1'>>> ws:(4, 6) !Ignored! [1, 18]
                Newline+ <<17, 18>> ws:None [2, 1]
                Indent <<18, 22, (4)>> ws:None [2, 5]
                Upper Line
                    Upper <<Regex: <_sre.SRE_Match object; span=(22, 25), match='TWO'>>> ws:None [2, 8]
                    Newline+ <<25, 26>> ws:None [3, 1]
                Number Line
                    Number <<Regex: <_sre.SRE_Match object; span=(30, 31), match='3'>>> ws:None [3, 6]
                    Newline+ <<31, 32>> ws:None [4, 1]
                Dedent <<>> ws:None [4, 1]
            """,
        )
        iterator = result.Iter

        result = self._indent_statement.Parse(iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            66
                Lower <<Regex: <_sre.SRE_Match object; span=(32, 36), match='four'>>> ws:None [4, 5]
                Colon <<Regex: <_sre.SRE_Match object; span=(36, 37), match=':'>>> ws:None [4, 6]
                Newline+ <<37, 38>> ws:None [5, 1]
                Indent <<38, 42, (4)>> ws:None [5, 5]
                Upper Line
                    Upper <<Regex: <_sre.SRE_Match object; span=(42, 46), match='FIVE'>>> ws:None [5, 9]
                    Comment <<Regex: <_sre.SRE_Match object; span=(47, 58), match='# Comment 5'>>> ws:(46, 47) !Ignored! [5, 21]
                    Newline+ <<58, 59>> ws:None [6, 1]
                Number Line
                    Number <<Regex: <_sre.SRE_Match object; span=(63, 65), match='66'>>> ws:None [6, 7]
                    Newline+ <<65, 66>> ws:None [7, 1]
                Dedent <<>> ws:None [7, 1]
            """,
        )
        iterator = result.Iter

        result = self._indent_statement.Parse(iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            119
                Lower <<Regex: <_sre.SRE_Match object; span=(66, 71), match='seven'>>> ws:None [7, 6]
                Colon <<Regex: <_sre.SRE_Match object; span=(71, 72), match=':'>>> ws:None [7, 7]
                Newline+ <<72, 73>> ws:None [8, 1]
                Indent <<73, 77, (4)>> ws:None [8, 5]
                Upper Line
                    Upper <<Regex: <_sre.SRE_Match object; span=(77, 82), match='EIGHT'>>> ws:None [8, 10]
                    Newline+ <<82, 83>> ws:None [9, 1]
                Number Line
                    Number <<Regex: <_sre.SRE_Match object; span=(87, 90), match='999'>>> ws:None [9, 8]
                    Comment <<Regex: <_sre.SRE_Match object; span=(107, 118), match='# Comment 9'>>> ws:(90, 107) !Ignored! [9, 36]
                    Newline+ <<118, 119>> ws:None [10, 1]
                Dedent <<>> ws:None [10, 1]
            """,
        )
        iterator = result.Iter

        result = self._indent_statement.Parse(iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            206
                Lower <<Regex: <_sre.SRE_Match object; span=(119, 122), match='ten'>>> ws:None [10, 4]
                Colon <<Regex: <_sre.SRE_Match object; span=(122, 123), match=':'>>> ws:None [10, 5]
                Comment <<Regex: <_sre.SRE_Match object; span=(135, 147), match='# Comment 10'>>> ws:(123, 135) !Ignored! [10, 29]
                Newline+ <<147, 148>> ws:None [11, 1]
                Indent <<148, 152, (4)>> ws:None [11, 5]
                Upper Line
                    Upper <<Regex: <_sre.SRE_Match object; span=(152, 158), match='ELEVEN'>>> ws:None [11, 11]
                    Comment <<Regex: <_sre.SRE_Match object; span=(164, 176), match='# Comment 11'>>> ws:(158, 164) !Ignored! [11, 29]
                    Newline+ <<176, 177>> ws:None [12, 1]
                Number Line
                    Number <<Regex: <_sre.SRE_Match object; span=(181, 183), match='12'>>> ws:None [12, 7]
                    Comment <<Regex: <_sre.SRE_Match object; span=(193, 205), match='# Comment 12'>>> ws:(183, 193) !Ignored! [12, 29]
                    Newline+ <<205, 206>> ws:None [13, 1]
                Dedent <<>> ws:None [13, 1]
            """,
        )
        iterator = result.Iter
