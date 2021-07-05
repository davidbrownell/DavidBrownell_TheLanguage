# ----------------------------------------------------------------------
# |
# |  StatementEx_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-29 07:19:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for StatementEx.py"""

import os
import re
import textwrap

from typing import Any, Dict, Tuple

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
    from ..StatementEx import *

    from ..Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
    )

    from ..StatementImpl.UnitTests import (
        CoroutineMock,
        CreateIterator,
        InternalStatementMethodCallToTuple,
        parse_mock,
        MethodCallsToString,
    )


# ----------------------------------------------------------------------
def OnInternalStatementEqual(
    mock_method_call_result: Union[
        Tuple[
            str,
            Tuple[
                Statement,
                Statement.ParseResultData,
                NormalizedIterator,
                NormalizedIterator,
            ],
            Dict[str, Any],
        ],
        Tuple[
            Statement,
            Statement.ParseResultData,
            NormalizedIterator,
            NormalizedIterator,
        ],
    ],
    statement: Optional[Statement],
    data: Statement.ParseResultData,
    offset_before: int,
    offset_after: int,
):
    """\
    Note that this is defined here rather than using the implementation in
    ..StatementImpl.UnitTests.__init__.py because I can't seem to get pytest
    to rewrite the assertions when it is imported from here. This functionality
    is complex enough that is really helps to have this information available
    when tests fail.
    """

    if len(mock_method_call_result) == 3:
        assert mock_method_call_result[0] == "OnInternalStatementAsync"
        mock_method_call_result = mock_method_call_result[1]
    else:
        mock_method_call_result = mock_method_call_result[0]

    if statement is not None:
        assert statement == mock_method_call_result[0]

    assert data == mock_method_call_result[1]
    assert offset_before == mock_method_call_result[2].Offset
    assert offset_after == mock_method_call_result[3].Offset

# ----------------------------------------------------------------------
_word_token                                 = RegexToken("Word Token", re.compile(r"(?P<value>[a-z]+)"))
_number_token                               = RegexToken("Number Token", re.compile(r"(?P<value>\d+)"))
_upper_token                                = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))
_lpar_token                                 = RegexToken("lpar", re.compile(r"\("))
_rpar_token                                 = RegexToken("rpar", re.compile(r"\)"))

# ----------------------------------------------------------------------
class TestParseSimple(object):
    _statement                              = StatementEx(
        "Statement",
        _word_token,
        _word_token,
        NewlineToken(),
    )

    # ----------------------------------------------------------------------
    def test_SingleSpaceSep(self, parse_mock):
        iter = CreateIterator("one two")

        assert str(iter) == "0 8 0 None None"

        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "0 8 0 None None", "The incoming iterator should not be modified"
        assert str(result.Iter) == "8 8 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                Newline+
                    Newline+ <<7, 8>> ws:None [1, 8 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    def test_MultipleSpaceSep(self, parse_mock):
        iter = CreateIterator("one      two")

        assert str(iter) == "0 13 0 None None"

        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "0 13 0 None None", "The incoming iterator should not be modified"
        assert str(result.Iter) == "13 13 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            13
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(9, 12), match='two'>>> ws:(3, 9) [1, 10 -> 1, 13]
                Newline+
                    Newline+ <<12, 13>> ws:None [1, 13 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    def test_TabSep(self, parse_mock):
        iter = CreateIterator("one\ttwo")

        assert str(iter) == "0 8 0 None None"

        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "0 8 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "8 8 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                Newline+
                    Newline+ <<7, 8>> ws:None [1, 8 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    def test_MultiTabSep(self, parse_mock):
        iter = CreateIterator("one\t\ttwo")

        assert str(iter) == "0 9 0 None None"

        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "0 9 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "9 9 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(5, 8), match='two'>>> ws:(3, 5) [1, 6 -> 1, 9]
                Newline+
                    Newline+ <<8, 9>> ws:None [1, 9 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    def test_TrailingSpace(self, parse_mock):
        iter = CreateIterator("one two ")

        assert str(iter) == "0 9 0 None None"

        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "0 9 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "9 9 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                Newline+
                    Newline+ <<8, 9>> ws:(7, 8) [1, 9 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    def test_MultipleTrailingSpace(self, parse_mock):
        iter = CreateIterator("one two    ")

        assert str(iter) == "0 12 0 None None"

        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "0 12 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "12 12 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            12
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                Newline+
                    Newline+ <<11, 12>> ws:(7, 11) [1, 12 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    def test_TrailingTab(self, parse_mock):
        iter = CreateIterator("one two\t")

        assert str(iter) == "0 9 0 None None"

        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "0 9 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "9 9 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                Newline+
                    Newline+ <<8, 9>> ws:(7, 8) [1, 9 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    def test_MultipleTrailingTab(self, parse_mock):
        iter = CreateIterator("one two\t\t\t\t")

        assert str(iter) == "0 12 0 None None"

        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "0 12 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "12 12 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            12
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                Newline+
                    Newline+ <<11, 12>> ws:(7, 11) [1, 12 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    def test_MultipleLines(self, parse_mock):
        iter = CreateIterator(
            textwrap.dedent(
                """\
                one two
                three four
                """,
            ),
        )

        # Line 1
        assert str(iter) == "0 19 0 None None"

        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "0 19 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "8 19 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                Newline+
                    Newline+ <<7, 8>> ws:None [1, 8 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 12

        iter = result.Iter

        # Line 2
        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "8 19 1 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "19 19 2 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            19
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='three'>>> ws:None [2, 1 -> 2, 6]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(14, 18), match='four'>>> ws:(13, 14) [2, 7 -> 2, 11]
                Newline+
                    Newline+ <<18, 19>> ws:None [2, 11 -> 3, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 24

        assert result.Iter.AtEnd()

    # ----------------------------------------------------------------------
    def test_TrailingWhitespace(self, parse_mock):
        iter = CreateIterator("one two\n\n  \n    \n")

        assert str(iter) == "0 17 0 None None"

        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "0 17 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "17 17 4 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            17
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                Newline+
                    Newline+ <<7, 17>> ws:None [1, 8 -> 5, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 12

        assert result.Iter.AtEnd()

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
        iter = CreateIterator("one two three")

        assert str(iter) == "0 14 0 None None"

        result = self._statement.Parse(iter, parse_mock)
        assert str(iter) == "0 14 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "7 14 0 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            False
            7
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                Newline+
                    None
            """,
        )

        assert len(parse_mock.method_calls) == 10

        assert result.Iter.AtEnd() == False

# ----------------------------------------------------------------------
class TestParseIndentAndDedent(object):
    _statement                              = StatementEx(
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
            CreateIterator(
                textwrap.dedent(
                    """\
                    one
                        two
                        three
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            22
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Newline+
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                Indent
                    Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                Newline+
                    Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 5 -> 3, 10]
                Newline+
                    Newline+ <<21, 22>> ws:None [3, 10 -> 4, 1]
                Dedent
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0, StartStatementCandidate, ['Statement']
            1, StartStatementCandidate, ['Statement', 0, 'Word Token']
            2, OnInternalStatementAsync, ['Statement', 0, 'Word Token']
            3, EndStatementCandidate, ['Statement', 0, 'Word Token']
            4, StartStatementCandidate, ['Statement', 1, 'Newline+']
            5, OnInternalStatementAsync, ['Statement', 1, 'Newline+']
            6, EndStatementCandidate, ['Statement', 1, 'Newline+']
            7, StartStatementCandidate, ['Statement', 2, 'Indent']
            8, OnIndentAsync, ['Statement', 2, 'Indent']
            9, EndStatementCandidate, ['Statement', 2, 'Indent']
            10, StartStatementCandidate, ['Statement', 3, 'Word Token']
            11, OnInternalStatementAsync, ['Statement', 3, 'Word Token']
            12, EndStatementCandidate, ['Statement', 3, 'Word Token']
            13, StartStatementCandidate, ['Statement', 4, 'Newline+']
            14, OnInternalStatementAsync, ['Statement', 4, 'Newline+']
            15, EndStatementCandidate, ['Statement', 4, 'Newline+']
            16, StartStatementCandidate, ['Statement', 5, 'Word Token']
            17, OnInternalStatementAsync, ['Statement', 5, 'Word Token']
            18, EndStatementCandidate, ['Statement', 5, 'Word Token']
            19, StartStatementCandidate, ['Statement', 6, 'Newline+']
            20, OnInternalStatementAsync, ['Statement', 6, 'Newline+']
            21, EndStatementCandidate, ['Statement', 6, 'Newline+']
            22, StartStatementCandidate, ['Statement', 7, 'Dedent']
            23, OnDedentAsync, ['Statement', 7, 'Dedent']
            24, EndStatementCandidate, ['Statement', 7, 'Dedent']
            25, OnInternalStatementAsync, ['Statement']
            26, EndStatementCandidate, ['Statement']
            """,
        )

        assert InternalStatementMethodCallToTuple(parse_mock, 2, use_statement_name=True) == ("Word Token", result.Data.DataItems[0].Data, 0, 3)
        assert InternalStatementMethodCallToTuple(parse_mock, 5, use_statement_name=True) == ("Newline+", result.Data.DataItems[1].Data, 3, 4)
        assert result.Data.DataItems[2].Statement.Name == "Indent"
        assert InternalStatementMethodCallToTuple(parse_mock, 11, use_statement_name=True) == ("Word Token", result.Data.DataItems[3].Data, 8, 11)
        assert InternalStatementMethodCallToTuple(parse_mock, 14, use_statement_name=True) == ("Newline+", result.Data.DataItems[4].Data, 11, 12)
        assert InternalStatementMethodCallToTuple(parse_mock, 17, use_statement_name=True) == ("Word Token", result.Data.DataItems[5].Data, 16, 21)
        assert InternalStatementMethodCallToTuple(parse_mock, 20, use_statement_name=True) == ("Newline+", result.Data.DataItems[6].Data, 21, 22)
        assert result.Data.DataItems[7].Statement.Name == "Dedent"
        assert InternalStatementMethodCallToTuple(parse_mock, 25) == (self._statement, result.Data, 0, 22)

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    one
                        two
                            three
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            12
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Newline+
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                Indent
                    Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                Newline+
                    Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
                Word Token
                    None
            """,
        )

        assert len(parse_mock.method_calls) == 19

    # ----------------------------------------------------------------------
    def test_FinishEarly(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    one
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            4
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Newline+
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 8

# ----------------------------------------------------------------------
class TestIgnoreWhitespace(object):
    _statement                              = StatementEx(
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
            CreateIterator(
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
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            60
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                lpar
                    lpar <<Regex: <_sre.SRE_Match object; span=(4, 5), match='('>>> ws:(3, 4) [1, 5 -> 1, 6]
                Newline+ <<5, 8>> ws:None !Ignored! [1, 6 -> 4, 1]
                Indent <<8, 12, (4)>> ws:None !Ignored! [4, 1 -> 4, 5]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='two'>>> ws:None [4, 5 -> 4, 8]
                Newline+ <<15, 17>> ws:None !Ignored! [4, 8 -> 6, 1]
                Indent <<17, 25, (8)>> ws:None !Ignored! [6, 1 -> 6, 9]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(25, 30), match='three'>>> ws:None [6, 9 -> 6, 14]
                Newline+ <<30, 31>> ws:None !Ignored! [6, 14 -> 7, 1]
                Dedent <<>> ws:None !Ignored! [7, 1 -> 7, 5]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(35, 39), match='four'>>> ws:None [7, 5 -> 7, 9]
                Newline+ <<39, 40>> ws:None !Ignored! [7, 9 -> 8, 1]
                Indent <<40, 48, (8)>> ws:None !Ignored! [8, 1 -> 8, 9]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(48, 52), match='five'>>> ws:None [8, 9 -> 8, 13]
                Newline+ <<52, 54>> ws:None !Ignored! [8, 13 -> 10, 1]
                Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                rpar
                    rpar <<Regex: <_sre.SRE_Match object; span=(54, 55), match=')'>>> ws:None [10, 1 -> 10, 2]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(56, 59), match='six'>>> ws:(55, 56) [10, 3 -> 10, 6]
                Newline+
                    Newline+ <<59, 60>> ws:None [10, 6 -> 11, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 30

# ----------------------------------------------------------------------
class TestEmbeddedStatements(object):
    _inner_statement                        = StatementEx(
        "Inner",
        _word_token,
        _word_token,
    )

    _statement                              = StatementEx(
        "Statement",
        _lpar_token,
        _inner_statement,
        _rpar_token,
    )

    # ----------------------------------------------------------------------
    def test_Match(self, parse_mock):
        result = self._statement.Parse(CreateIterator("( one two )"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            11
                lpar
                    lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                Inner
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 3 -> 1, 6]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 7 -> 1, 10]
                rpar
                    rpar <<Regex: <_sre.SRE_Match object; span=(10, 11), match=')'>>> ws:(9, 10) [1, 11 -> 1, 12]
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0, StartStatementCandidate, ['Statement']
            1, StartStatementCandidate, ['Statement', 0, 'lpar']
            2, OnInternalStatementAsync, ['Statement', 0, 'lpar']
            3, EndStatementCandidate, ['Statement', 0, 'lpar']
            4, StartStatementCandidate, ['Statement', 1, 'Inner']
            5, StartStatementCandidate, ['Statement', 1, 'Inner', 0, 'Word Token']
            6, OnInternalStatementAsync, ['Statement', 1, 'Inner', 0, 'Word Token']
            7, EndStatementCandidate, ['Statement', 1, 'Inner', 0, 'Word Token']
            8, StartStatementCandidate, ['Statement', 1, 'Inner', 1, 'Word Token']
            9, OnInternalStatementAsync, ['Statement', 1, 'Inner', 1, 'Word Token']
            10, EndStatementCandidate, ['Statement', 1, 'Inner', 1, 'Word Token']
            11, OnInternalStatementAsync, ['Statement', 1, 'Inner']
            12, EndStatementCandidate, ['Statement', 1, 'Inner']
            13, StartStatementCandidate, ['Statement', 2, 'rpar']
            14, OnInternalStatementAsync, ['Statement', 2, 'rpar']
            15, EndStatementCandidate, ['Statement', 2, 'rpar']
            16, OnInternalStatementAsync, ['Statement']
            17, EndStatementCandidate, ['Statement']
            """,
        )

        assert InternalStatementMethodCallToTuple(parse_mock, 2, use_statement_name=True) == ("lpar", result.Data.DataItems[0].Data, 0, 1)
        assert InternalStatementMethodCallToTuple(parse_mock, 6, use_statement_name=True) == ("Word Token", result.Data.DataItems[1].Data.DataItems[0].Data, 2, 5)
        assert InternalStatementMethodCallToTuple(parse_mock, 9, use_statement_name=True) == ("Word Token", result.Data.DataItems[1].Data.DataItems[1].Data, 6, 9)
        assert InternalStatementMethodCallToTuple(parse_mock, 11) == (self._inner_statement, result.Data.DataItems[1].Data, 1, 9)
        assert InternalStatementMethodCallToTuple(parse_mock, 14, use_statement_name=True) == ("rpar", result.Data.DataItems[2].Data, 10, 11)
        assert InternalStatementMethodCallToTuple(parse_mock, 16) == (self._statement, result.Data, 0, 11)

    # ----------------------------------------------------------------------
    def test_NoMatchAllInner(self, parse_mock):
        result = self._statement.Parse(CreateIterator("( one two"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            False
            9
                lpar
                    lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                Inner
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 3 -> 1, 6]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 7 -> 1, 10]
                rpar
                    None
            """,
        )

        assert len(parse_mock.method_calls) == 16

    # ----------------------------------------------------------------------
    def test_NoMatchPartialInner(self, parse_mock):
        result = self._statement.Parse(CreateIterator("( one"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            False
            5
                lpar
                    lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                Inner
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 3 -> 1, 6]
                    Word Token
                        None
            """,
        )

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    def test_NoMatchFirstOnly(self, parse_mock):
        result = self._statement.Parse(CreateIterator("( "), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            False
            1
                lpar
                    lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                Inner
                    Word Token
                        None
            """,
        )

        assert len(parse_mock.method_calls) == 9

# ----------------------------------------------------------------------
class TestDynamicStatements(object):
    _word_statement                         = StatementEx(
        "Word Statement",
        _word_token,
        _word_token,
        NewlineToken(),
    )

    _number_statement                       = StatementEx(
        "Number Statement",
        _number_token,
        NewlineToken(),
    )

    _statement                              = StatementEx(
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

        return parse_mock

    # ----------------------------------------------------------------------
    def test_Match(self, modified_parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda wordb
                    123
                    456
                    """,
                ),
            ),
            modified_parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            20
                DynamicStatements.Statements
                    Or [Word Statement, Number Statement]
                        Word Statement
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                            Newline+
                                Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                DynamicStatements.Statements
                    Or [Word Statement, Number Statement]
                        Number Statement
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                            Newline+
                                Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
                DynamicStatements.Expressions
                    Or [Number Statement]
                        Number Statement
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='456'>>> ws:None [3, 1 -> 3, 4]
                            Newline+
                                Newline+ <<19, 20>> ws:None [3, 4 -> 4, 1]
            """,
        )

        assert MethodCallsToString(modified_parse_mock) == textwrap.dedent(
            """\
            0, StartStatementCandidate, ['Statement']
            1, StartStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements']
            2, GetDynamicStatements, DynamicStatements.Statements
            3, StartStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]']
            4, StartStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement']
            5, StartStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement', 0, 'Word Token']
            6, OnInternalStatementAsync, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement', 0, 'Word Token']
            7, EndStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement', 0, 'Word Token']
            8, StartStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement', 1, 'Word Token']
            9, OnInternalStatementAsync, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement', 1, 'Word Token']
            10, EndStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement', 1, 'Word Token']
            11, StartStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement', 2, 'Newline+']
            12, OnInternalStatementAsync, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement', 2, 'Newline+']
            13, EndStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement', 2, 'Newline+']
            14, OnInternalStatementAsync, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement']
            15, EndStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement']
            16, StartStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement']
            17, StartStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement', 0, 'Number Token']
            18, EndStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement', 0, 'Number Token']
            19, EndStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement']
            20, OnInternalStatementAsync, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]']
            21, EndStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]']
            22, OnInternalStatementAsync, ['Statement', 0, 'DynamicStatements.Statements']
            23, EndStatementCandidate, ['Statement', 0, 'DynamicStatements.Statements']
            24, StartStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements']
            25, GetDynamicStatements, DynamicStatements.Statements
            26, StartStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]']
            27, StartStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement']
            28, StartStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement', 0, 'Word Token']
            29, EndStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement', 0, 'Word Token']
            30, EndStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 0, 'Word Statement']
            31, StartStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement']
            32, StartStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement', 0, 'Number Token']
            33, OnInternalStatementAsync, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement', 0, 'Number Token']
            34, EndStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement', 0, 'Number Token']
            35, StartStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement', 1, 'Newline+']
            36, OnInternalStatementAsync, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement', 1, 'Newline+']
            37, EndStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement', 1, 'Newline+']
            38, OnInternalStatementAsync, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement']
            39, EndStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]', 1, 'Number Statement']
            40, OnInternalStatementAsync, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]']
            41, EndStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements', 'Or [Word Statement, Number Statement]']
            42, OnInternalStatementAsync, ['Statement', 1, 'DynamicStatements.Statements']
            43, EndStatementCandidate, ['Statement', 1, 'DynamicStatements.Statements']
            44, StartStatementCandidate, ['Statement', 2, 'DynamicStatements.Expressions']
            45, GetDynamicStatements, DynamicStatements.Expressions
            46, StartStatementCandidate, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]']
            47, StartStatementCandidate, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]', 0, 'Number Statement']
            48, StartStatementCandidate, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]', 0, 'Number Statement', 0, 'Number Token']
            49, OnInternalStatementAsync, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]', 0, 'Number Statement', 0, 'Number Token']
            50, EndStatementCandidate, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]', 0, 'Number Statement', 0, 'Number Token']
            51, StartStatementCandidate, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]', 0, 'Number Statement', 1, 'Newline+']
            52, OnInternalStatementAsync, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]', 0, 'Number Statement', 1, 'Newline+']
            53, EndStatementCandidate, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]', 0, 'Number Statement', 1, 'Newline+']
            54, OnInternalStatementAsync, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]', 0, 'Number Statement']
            55, EndStatementCandidate, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]', 0, 'Number Statement']
            56, OnInternalStatementAsync, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]']
            57, EndStatementCandidate, ['Statement', 2, 'DynamicStatements.Expressions', 'Or [Number Statement]']
            58, OnInternalStatementAsync, ['Statement', 2, 'DynamicStatements.Expressions']
            59, EndStatementCandidate, ['Statement', 2, 'DynamicStatements.Expressions']
            60, OnInternalStatementAsync, ['Statement']
            61, EndStatementCandidate, ['Statement']
            """,
        )

        assert InternalStatementMethodCallToTuple(modified_parse_mock, 6, use_statement_name=True) == ("Word Token", result.Data.DataItems[0].Data.Data.Data.DataItems[0].Data, 0, 5)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 9, use_statement_name=True) == ("Word Token", result.Data.DataItems[0].Data.Data.Data.DataItems[1].Data, 6, 11)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 12, use_statement_name=True) == ("Newline+", result.Data.DataItems[0].Data.Data.Data.DataItems[2].Data, 11, 12)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 14) == (self._word_statement, result.Data.DataItems[0].Data.Data.Data, 0, 12)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 20, use_statement_name=True) == ("Or [Word Statement, Number Statement]", result.Data.DataItems[0].Data.Data, 0, 12)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 22, use_statement_name=True) == ("DynamicStatements.Statements", result.Data.DataItems[0].Data, 0, 12)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 33, use_statement_name=True) == ("Number Token", result.Data.DataItems[1].Data.Data.Data.DataItems[0].Data, 12, 15)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 36, use_statement_name=True) == ("Newline+", result.Data.DataItems[1].Data.Data.Data.DataItems[1].Data, 15, 16)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 38) == (self._number_statement, result.Data.DataItems[1].Data.Data.Data, 12, 16)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 40, use_statement_name=True) == ("Or [Word Statement, Number Statement]", result.Data.DataItems[1].Data.Data, 12, 16)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 42, use_statement_name=True) == ("DynamicStatements.Statements", result.Data.DataItems[1].Data, 12, 16)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 49, use_statement_name=True) == ("Number Token", result.Data.DataItems[2].Data.Data.Data.DataItems[0].Data, 16, 19)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 52, use_statement_name=True) == ("Newline+", result.Data.DataItems[2].Data.Data.Data.DataItems[1].Data, 19, 20)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 54) == (self._number_statement, result.Data.DataItems[2].Data.Data.Data, 16, 20)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 56, use_statement_name=True) == ("Or [Number Statement]", result.Data.DataItems[2].Data.Data, 16, 20)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 58, use_statement_name=True) == ("DynamicStatements.Expressions", result.Data.DataItems[2].Data, 16, 20)
        assert InternalStatementMethodCallToTuple(modified_parse_mock, 60) == (self._statement, result.Data, 0, 20)

    # ----------------------------------------------------------------------
    def test_NoMatch(self, modified_parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda wordb
                    123
                    wordc wordd
                    """,
                ),
            ),
            modified_parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            16
                DynamicStatements.Statements
                    Or [Word Statement, Number Statement]
                        Word Statement
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                            Newline+
                                Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                DynamicStatements.Statements
                    Or [Word Statement, Number Statement]
                        Number Statement
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                            Newline+
                                Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
                DynamicStatements.Expressions
                    Or [Number Statement]
                        Number Statement
                            Number Token
                                None
            """,
        )

        assert len(modified_parse_mock.method_calls) == 54

# ----------------------------------------------------------------------
class TestOrStatements(object):
    _word_statement                         = StatementEx(
        "Word Statement",
        _word_token,
        NewlineToken(),
    )

    _number_statement                       = StatementEx(
        "Number Statement",
        _number_token,
        NewlineToken(),
    )

    _upper_statement                        = StatementEx(
        "Upper Statement",
        _upper_token,
        NewlineToken(),
    )

    _statement                              = StatementEx(
        "Statement",
        [_word_statement, _number_statement, _upper_statement],
    )

    # ----------------------------------------------------------------------
    def test_WordMatch(self, parse_mock):
        result = self._statement.Parse(CreateIterator("word"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            5
                Or [Word Statement, Number Statement, Upper Statement]
                    Word Statement
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
                        Newline+
                            Newline+ <<4, 5>> ws:None [1, 5 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 23

    # ----------------------------------------------------------------------
    def test_NumberMatch(self, parse_mock):
        result = self._statement.Parse(CreateIterator("1234"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            5
                Or [Word Statement, Number Statement, Upper Statement]
                    Number Statement
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 1 -> 1, 5]
                        Newline+
                            Newline+ <<4, 5>> ws:None [1, 5 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 23

    # ----------------------------------------------------------------------
    def test_UpperMatch(self, parse_mock):
        result = self._statement.Parse(CreateIterator("WORD"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            5
                Or [Word Statement, Number Statement, Upper Statement]
                    Upper Statement
                        Upper Token
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='WORD'>>> ws:None [1, 1 -> 1, 5]
                        Newline+
                            Newline+ <<4, 5>> ws:None [1, 5 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 23

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator("this is not a match"),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            4
                Or [Word Statement, Number Statement, Upper Statement]
                    Word Statement
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='this'>>> ws:None [1, 1 -> 1, 5]
                        Newline+
                            None
                    Number Statement
                        Number Token
                            None
                    Upper Statement
                        Upper Token
                            None
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0, StartStatementCandidate, ['Statement']
            1, StartStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]']
            2, StartStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 0, 'Word Statement']
            3, StartStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 0, 'Word Statement', 0, 'Word Token']
            4, OnInternalStatementAsync, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 0, 'Word Statement', 0, 'Word Token']
            5, EndStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 0, 'Word Statement', 0, 'Word Token']
            6, StartStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 0, 'Word Statement', 1, 'Newline+']
            7, EndStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 0, 'Word Statement', 1, 'Newline+']
            8, EndStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 0, 'Word Statement']
            9, StartStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 1, 'Number Statement']
            10, StartStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 1, 'Number Statement', 0, 'Number Token']
            11, EndStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 1, 'Number Statement', 0, 'Number Token']
            12, EndStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 1, 'Number Statement']
            13, StartStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 2, 'Upper Statement']
            14, StartStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 2, 'Upper Statement', 0, 'Upper Token']
            15, EndStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 2, 'Upper Statement', 0, 'Upper Token']
            16, EndStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]', 2, 'Upper Statement']
            17, EndStatementCandidate, ['Statement', 0, 'Or [Word Statement, Number Statement, Upper Statement]']
            18, EndStatementCandidate, ['Statement']
            """,
        )

        assert InternalStatementMethodCallToTuple(parse_mock, 4, use_statement_name=True) == (
            "Word Token",
            result
                .Data.DataItems[0]          # Statement
                .Data.DataItems[0]          # [Generated] Or Statement
                .Data.DataItems[0]          # Word Statement
                .Data,                      # [Generated] Word Token
            0,
            4,
        )

    # ----------------------------------------------------------------------
    def test_EarlyTermination(self, parse_mock):
        parse_mock.OnInternalStatementAsync = CoroutineMock(
            side_effect=[True, False],
        )

        result = self._statement.Parse(CreateIterator("word"), parse_mock)

        assert result is None
        assert len(parse_mock.method_calls) == 20

# ----------------------------------------------------------------------
class TestRepeatStatements(object):
    _word_statement                         = StatementEx(
        "Word Statement",
        _word_token,
        NewlineToken(),
    )

    _number_statement                       = StatementEx(
        "Number Statement",
        _number_token,
        NewlineToken(),
    )

    _upper_statement                        = StatementEx(
        "Upper Statement",
        _upper_token,
        NewlineToken(),
    )

    _statement                              = StatementEx(
        "Statement",
        (_word_statement, 0, None),
        (_number_statement, 1, None),
        (_upper_statement, 0, 1),
        (_word_statement, 1, None),
    )

    # ----------------------------------------------------------------------
    def test_Match1(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
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
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            44
                Repeat: (Word Statement, 0, None)
                    Word Statement
                        0) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                           Newline+
                               Newline+ <<5, 6>> ws:None [1, 6 -> 2, 1]
                        1) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:None [2, 1 -> 2, 6]
                           Newline+
                               Newline+ <<11, 12>> ws:None [2, 6 -> 3, 1]
                Repeat: (Number Statement, 1, None)
                    Number Statement
                        0) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(12, 14), match='12'>>> ws:None [3, 1 -> 3, 3]
                           Newline+
                               Newline+ <<14, 15>> ws:None [3, 3 -> 4, 1]
                        1) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(15, 19), match='3456'>>> ws:None [4, 1 -> 4, 5]
                           Newline+
                               Newline+ <<19, 20>> ws:None [4, 5 -> 5, 1]
                Repeat: (Upper Statement, 0, 1)
                    Upper Statement
                        0) Upper Token
                               Upper Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='UPPER'>>> ws:None [5, 1 -> 5, 6]
                           Newline+
                               Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
                Repeat: (Word Statement, 1, None)
                    Word Statement
                        0) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(26, 31), match='wordc'>>> ws:None [6, 1 -> 6, 6]
                           Newline+
                               Newline+ <<31, 32>> ws:None [6, 6 -> 7, 1]
                        1) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(32, 37), match='wordd'>>> ws:None [7, 1 -> 7, 6]
                           Newline+
                               Newline+ <<37, 38>> ws:None [7, 6 -> 8, 1]
                        2) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(38, 43), match='worde'>>> ws:None [8, 1 -> 8, 6]
                           Newline+
                               Newline+ <<43, 44>> ws:None [8, 6 -> 9, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 95

    # ----------------------------------------------------------------------
    def test_Match2(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
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
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            32
                Repeat: (Word Statement, 0, None)
                    Word Statement
                        <No Results>
                Repeat: (Number Statement, 1, None)
                    Number Statement
                        0) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                           Newline+
                               Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        1) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                           Newline+
                               Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                Repeat: (Upper Statement, 0, 1)
                    Upper Statement
                        0) Upper Token
                               Upper Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='UPPER'>>> ws:None [3, 1 -> 3, 6]
                           Newline+
                               Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                Repeat: (Word Statement, 1, None)
                    Word Statement
                        0) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordc'>>> ws:None [4, 1 -> 4, 6]
                           Newline+
                               Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                        1) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='wordd'>>> ws:None [5, 1 -> 5, 6]
                           Newline+
                               Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
                        2) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(26, 31), match='worde'>>> ws:None [6, 1 -> 6, 6]
                           Newline+
                               Newline+ <<31, 32>> ws:None [6, 6 -> 7, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 77

    # ----------------------------------------------------------------------
    def test_Match3(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
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
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            32
                Repeat: (Word Statement, 0, None)
                    Word Statement
                        0) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                           Newline+
                               Newline+ <<5, 6>> ws:None [1, 6 -> 2, 1]
                Repeat: (Number Statement, 1, None)
                    Number Statement
                        0) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(6, 8), match='12'>>> ws:None [2, 1 -> 2, 3]
                           Newline+
                               Newline+ <<8, 9>> ws:None [2, 3 -> 3, 1]
                        1) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(9, 13), match='3456'>>> ws:None [3, 1 -> 3, 5]
                           Newline+
                               Newline+ <<13, 14>> ws:None [3, 5 -> 4, 1]
                Repeat: (Upper Statement, 0, 1)
                    Upper Statement
                        <No Results>
                Repeat: (Word Statement, 1, None)
                    Word Statement
                        0) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordc'>>> ws:None [4, 1 -> 4, 6]
                           Newline+
                               Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                        1) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='wordd'>>> ws:None [5, 1 -> 5, 6]
                           Newline+
                               Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
                        2) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(26, 31), match='worde'>>> ws:None [6, 1 -> 6, 6]
                           Newline+
                               Newline+ <<31, 32>> ws:None [6, 6 -> 7, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 81

    # ----------------------------------------------------------------------
    def test_Match4(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
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
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            26
                Repeat: (Word Statement, 0, None)
                    Word Statement
                        <No Results>
                Repeat: (Number Statement, 1, None)
                    Number Statement
                        0) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                           Newline+
                               Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        1) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                           Newline+
                               Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                Repeat: (Upper Statement, 0, 1)
                    Upper Statement
                        <No Results>
                Repeat: (Word Statement, 1, None)
                    Word Statement
                        0) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                           Newline+
                               Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                        1) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordd'>>> ws:None [4, 1 -> 4, 6]
                           Newline+
                               Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                        2) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='worde'>>> ws:None [5, 1 -> 5, 6]
                           Newline+
                               Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0, StartStatementCandidate, ['Statement']
            1, StartStatementCandidate, ['Statement', 0, 'Repeat: (Word Statement, 0, None)']
            2, StartStatementCandidate, ['Statement', 0, 'Repeat: (Word Statement, 0, None)', 0, 'Word Statement']
            3, StartStatementCandidate, ['Statement', 0, 'Repeat: (Word Statement, 0, None)', 0, 'Word Statement', 0, 'Word Token']
            4, EndStatementCandidate, ['Statement', 0, 'Repeat: (Word Statement, 0, None)', 0, 'Word Statement', 0, 'Word Token']
            5, EndStatementCandidate, ['Statement', 0, 'Repeat: (Word Statement, 0, None)', 0, 'Word Statement']
            6, OnInternalStatementAsync, ['Statement', 0, 'Repeat: (Word Statement, 0, None)']
            7, EndStatementCandidate, ['Statement', 0, 'Repeat: (Word Statement, 0, None)']
            8, StartStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)']
            9, StartStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 0, 'Number Statement']
            10, StartStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 0, 'Number Statement', 0, 'Number Token']
            11, OnInternalStatementAsync, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 0, 'Number Statement', 0, 'Number Token']
            12, EndStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 0, 'Number Statement', 0, 'Number Token']
            13, StartStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 0, 'Number Statement', 1, 'Newline+']
            14, OnInternalStatementAsync, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 0, 'Number Statement', 1, 'Newline+']
            15, EndStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 0, 'Number Statement', 1, 'Newline+']
            16, OnInternalStatementAsync, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 0, 'Number Statement']
            17, EndStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 0, 'Number Statement']
            18, StartStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 1, 'Number Statement']
            19, StartStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 1, 'Number Statement', 0, 'Number Token']
            20, OnInternalStatementAsync, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 1, 'Number Statement', 0, 'Number Token']
            21, EndStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 1, 'Number Statement', 0, 'Number Token']
            22, StartStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 1, 'Number Statement', 1, 'Newline+']
            23, OnInternalStatementAsync, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 1, 'Number Statement', 1, 'Newline+']
            24, EndStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 1, 'Number Statement', 1, 'Newline+']
            25, OnInternalStatementAsync, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 1, 'Number Statement']
            26, EndStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 1, 'Number Statement']
            27, StartStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 2, 'Number Statement']
            28, StartStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 2, 'Number Statement', 0, 'Number Token']
            29, EndStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 2, 'Number Statement', 0, 'Number Token']
            30, EndStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)', 2, 'Number Statement']
            31, OnInternalStatementAsync, ['Statement', 1, 'Repeat: (Number Statement, 1, None)']
            32, EndStatementCandidate, ['Statement', 1, 'Repeat: (Number Statement, 1, None)']
            33, StartStatementCandidate, ['Statement', 2, 'Repeat: (Upper Statement, 0, 1)']
            34, StartStatementCandidate, ['Statement', 2, 'Repeat: (Upper Statement, 0, 1)', 0, 'Upper Statement']
            35, StartStatementCandidate, ['Statement', 2, 'Repeat: (Upper Statement, 0, 1)', 0, 'Upper Statement', 0, 'Upper Token']
            36, EndStatementCandidate, ['Statement', 2, 'Repeat: (Upper Statement, 0, 1)', 0, 'Upper Statement', 0, 'Upper Token']
            37, EndStatementCandidate, ['Statement', 2, 'Repeat: (Upper Statement, 0, 1)', 0, 'Upper Statement']
            38, OnInternalStatementAsync, ['Statement', 2, 'Repeat: (Upper Statement, 0, 1)']
            39, EndStatementCandidate, ['Statement', 2, 'Repeat: (Upper Statement, 0, 1)']
            40, StartStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)']
            41, StartStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 0, 'Word Statement']
            42, StartStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 0, 'Word Statement', 0, 'Word Token']
            43, OnInternalStatementAsync, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 0, 'Word Statement', 0, 'Word Token']
            44, EndStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 0, 'Word Statement', 0, 'Word Token']
            45, StartStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 0, 'Word Statement', 1, 'Newline+']
            46, OnInternalStatementAsync, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 0, 'Word Statement', 1, 'Newline+']
            47, EndStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 0, 'Word Statement', 1, 'Newline+']
            48, OnInternalStatementAsync, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 0, 'Word Statement']
            49, EndStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 0, 'Word Statement']
            50, StartStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 1, 'Word Statement']
            51, StartStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 1, 'Word Statement', 0, 'Word Token']
            52, OnInternalStatementAsync, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 1, 'Word Statement', 0, 'Word Token']
            53, EndStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 1, 'Word Statement', 0, 'Word Token']
            54, StartStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 1, 'Word Statement', 1, 'Newline+']
            55, OnInternalStatementAsync, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 1, 'Word Statement', 1, 'Newline+']
            56, EndStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 1, 'Word Statement', 1, 'Newline+']
            57, OnInternalStatementAsync, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 1, 'Word Statement']
            58, EndStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 1, 'Word Statement']
            59, StartStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 2, 'Word Statement']
            60, StartStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 2, 'Word Statement', 0, 'Word Token']
            61, OnInternalStatementAsync, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 2, 'Word Statement', 0, 'Word Token']
            62, EndStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 2, 'Word Statement', 0, 'Word Token']
            63, StartStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 2, 'Word Statement', 1, 'Newline+']
            64, OnInternalStatementAsync, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 2, 'Word Statement', 1, 'Newline+']
            65, EndStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 2, 'Word Statement', 1, 'Newline+']
            66, OnInternalStatementAsync, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 2, 'Word Statement']
            67, EndStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)', 2, 'Word Statement']
            68, OnInternalStatementAsync, ['Statement', 3, 'Repeat: (Word Statement, 1, None)']
            69, EndStatementCandidate, ['Statement', 3, 'Repeat: (Word Statement, 1, None)']
            70, OnInternalStatementAsync, ['Statement']
            71, EndStatementCandidate, ['Statement']
            """,
        )

        assert InternalStatementMethodCallToTuple(parse_mock, 6, use_statement_name=True) == ("Repeat: (Word Statement, 0, None)", result.Data.DataItems[0].Data, 0, 0)
        assert InternalStatementMethodCallToTuple(parse_mock, 11, use_statement_name=True) == ("Number Token", result.Data.DataItems[1].Data.DataItems[0].DataItems[0].Data, 0, 2)
        assert InternalStatementMethodCallToTuple(parse_mock, 14, use_statement_name=True) == ("Newline+", result.Data.DataItems[1].Data.DataItems[0].DataItems[1].Data, 2, 3)
        assert InternalStatementMethodCallToTuple(parse_mock, 16) == (self._number_statement, result.Data.DataItems[1].Data.DataItems[0], 0, 3)
        assert InternalStatementMethodCallToTuple(parse_mock, 20, use_statement_name=True) == ("Number Token", result.Data.DataItems[1].Data.DataItems[1].DataItems[0].Data, 3, 7)
        assert InternalStatementMethodCallToTuple(parse_mock, 23, use_statement_name=True) == ("Newline+", result.Data.DataItems[1].Data.DataItems[1].DataItems[1].Data, 7, 8)
        assert InternalStatementMethodCallToTuple(parse_mock, 25) == (self._number_statement, result.Data.DataItems[1].Data.DataItems[1], 3, 8)
        assert InternalStatementMethodCallToTuple(parse_mock, 31, use_statement_name=True) == ("Repeat: (Number Statement, 1, None)", result.Data.DataItems[1].Data, 0, 8)
        assert InternalStatementMethodCallToTuple(parse_mock, 38, use_statement_name=True) == ("Repeat: (Upper Statement, 0, 1)", result.Data.DataItems[2].Data, 8, 8)
        assert InternalStatementMethodCallToTuple(parse_mock, 43, use_statement_name=True) == ("Word Token", result.Data.DataItems[3].Data.DataItems[0].DataItems[0].Data, 8, 13)
        assert InternalStatementMethodCallToTuple(parse_mock, 46, use_statement_name=True) == ("Newline+", result.Data.DataItems[3].Data.DataItems[0].DataItems[1].Data, 13, 14)
        assert InternalStatementMethodCallToTuple(parse_mock, 48) == (self._word_statement, result.Data.DataItems[3].Data.DataItems[0], 8, 14)
        assert InternalStatementMethodCallToTuple(parse_mock, 52, use_statement_name=True) == ("Word Token", result.Data.DataItems[3].Data.DataItems[1].DataItems[0].Data, 14, 19)
        assert InternalStatementMethodCallToTuple(parse_mock, 55, use_statement_name=True) == ("Newline+", result.Data.DataItems[3].Data.DataItems[1].DataItems[1].Data, 19, 20)
        assert InternalStatementMethodCallToTuple(parse_mock, 57) == (self._word_statement, result.Data.DataItems[3].Data.DataItems[1], 14, 20)
        assert InternalStatementMethodCallToTuple(parse_mock, 61, use_statement_name=True) == ("Word Token", result.Data.DataItems[3].Data.DataItems[2].DataItems[0].Data, 20, 25)
        assert InternalStatementMethodCallToTuple(parse_mock, 64, use_statement_name=True) == ("Newline+", result.Data.DataItems[3].Data.DataItems[2].DataItems[1].Data, 25, 26)
        assert InternalStatementMethodCallToTuple(parse_mock, 66) == (self._word_statement, result.Data.DataItems[3].Data.DataItems[2], 20, 26)
        assert InternalStatementMethodCallToTuple(parse_mock, 68, use_statement_name=True) == ("Repeat: (Word Statement, 1, None)", result.Data.DataItems[3].Data, 8, 26)
        assert InternalStatementMethodCallToTuple(parse_mock, 70) == (self._statement, result.Data, 0, 26)

    # ----------------------------------------------------------------------
    def test_NoMatch1(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
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
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            12
                Repeat: (Word Statement, 0, None)
                    Word Statement
                        0) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                           Newline+
                               Newline+ <<5, 6>> ws:None [1, 6 -> 2, 1]
                        1) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:None [2, 1 -> 2, 6]
                           Newline+
                               Newline+ <<11, 12>> ws:None [2, 6 -> 3, 1]
                Repeat: (Number Statement, 1, None)
                    Number Statement
                        0) Number Token
                               None
            """,
        )

        assert len(parse_mock.method_calls) == 33

    # ----------------------------------------------------------------------
    def test_NoMatch2(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    12
                    3456
                    UPPER
                    999
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            14
                Repeat: (Word Statement, 0, None)
                    Word Statement
                        <No Results>
                Repeat: (Number Statement, 1, None)
                    Number Statement
                        0) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                           Newline+
                               Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        1) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                           Newline+
                               Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                Repeat: (Upper Statement, 0, 1)
                    Upper Statement
                        0) Upper Token
                               Upper Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='UPPER'>>> ws:None [3, 1 -> 3, 6]
                           Newline+
                               Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                Repeat: (Word Statement, 1, None)
                    Word Statement
                        0) Word Token
                               None
            """,
        )

        assert len(parse_mock.method_calls) == 52

    # ----------------------------------------------------------------------
    def test_EarlyTermination(self, parse_mock):
        parse_mock.OnInternalStatementAsync = CoroutineMock(
            side_effect=[True, True, True, True, False],
        )

        result = self._statement.Parse(
            CreateIterator(
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
            parse_mock,
        )

        assert result is None

# ----------------------------------------------------------------------
class TestRepeatSimilarStatements(object):
    # Ensure that the first statement doesn't eat the word so that it isn't available to the
    # second statement.
    _statement                              = StatementEx(
        "Statement",
        (
            StatementEx(
                "Word & Number",
                _word_token,
                _number_token,
            ),
            0,
            None,
        ),
        (_word_token, 0, 1),
    )

    # ----------------------------------------------------------------------
    def test_LargeMatch(self, parse_mock):
        result = self._statement.Parse(CreateIterator("word 123"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Repeat: (Word & Number, 0, None)
                    Word & Number
                        0) Word Token
                               Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
                           Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(5, 8), match='123'>>> ws:(4, 5) [1, 6 -> 1, 9]
                Repeat: (Word Token, 0, 1)
                    Word Token
                        <No Results>
            """,
        )

    # ----------------------------------------------------------------------
    def test_SmallMatch(self, parse_mock):
        result = self._statement.Parse(CreateIterator("word"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Repeat: (Word & Number, 0, None)
                    Word & Number
                        <No Results>
                Repeat: (Word Token, 0, 1)
                    Word Token
                        0) Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

    # ----------------------------------------------------------------------
    def test_IgnoreWhitespace(self, parse_mock):
        # No Clone support at this time
        return

        statement = self._statement.Clone()

        assert statement.Statements

        statement.Statements.insert(0, TokenStatement(PushIgnoreWhitespaceControlToken()))
        statement.Statements.append(TokenStatement(PopIgnoreWhitespaceControlToken()))

        result = statement.Parse(
            CreateIterator(
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
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            """,
        )

# ----------------------------------------------------------------------
class TestNamedStatements(object):
    _word_line_statement                    = StatementEx(
        "Word Line",
        _word_token,
        NewlineToken(),
    )

    _upper_line_statement                   = StatementEx(
        "Upper Line",
        _upper_token,
        NewlineToken(),
    )

    _number_line_statement                  = StatementEx(
        "Number Line",
        _number_token,
        NewlineToken(),
    )

    _statement                              = StatementEx(
        "Statement",
        StatementEx.NamedItem("__Dynamic__", DynamicStatements.Statements),
        StatementEx.NamedItem("__Or__", [_word_line_statement, _upper_line_statement]),
        StatementEx.NamedItem("__Repeat__", (_number_line_statement, 2, 2)),
    )

    # ----------------------------------------------------------------------
    @staticmethod
    @pytest.fixture
    def modified_parse_mock(parse_mock):
        parse_mock.GetDynamicStatements.side_effect = lambda value: [TestNamedStatements._word_line_statement]

        return parse_mock

    # ----------------------------------------------------------------------
    def test_Match(self, modified_parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    WORDB
                    123
                    456
                    """,
                ),
            ),
            modified_parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            20
                __Dynamic__
                    Or [Word Line]
                        Word Line
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                            Newline+
                                Newline+ <<5, 6>> ws:None [1, 6 -> 2, 1]
                __Or__
                    Upper Line
                        Upper Token
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='WORDB'>>> ws:None [2, 1 -> 2, 6]
                        Newline+
                            Newline+ <<11, 12>> ws:None [2, 6 -> 3, 1]
                __Repeat__
                    Number Line
                        0) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [3, 1 -> 3, 4]
                           Newline+
                               Newline+ <<15, 16>> ws:None [3, 4 -> 4, 1]
                        1) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='456'>>> ws:None [4, 1 -> 4, 4]
                           Newline+
                               Newline+ <<19, 20>> ws:None [4, 4 -> 5, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatch(self, modified_parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    WORDB
                    123
                    """,
                ),
            ),
            modified_parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            16
                __Dynamic__
                    Or [Word Line]
                        Word Line
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                            Newline+
                                Newline+ <<5, 6>> ws:None [1, 6 -> 2, 1]
                __Or__
                    Upper Line
                        Upper Token
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='WORDB'>>> ws:None [2, 1 -> 2, 6]
                        Newline+
                            Newline+ <<11, 12>> ws:None [2, 6 -> 3, 1]
                __Repeat__
                    Number Line
                        0) Number Token
                               Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [3, 1 -> 3, 4]
                           Newline+
                               Newline+ <<15, 16>> ws:None [3, 4 -> 4, 1]
            """,
        )

# ----------------------------------------------------------------------
class TestComments(object):
    _word_line_statement                    = StatementEx(
        "Word Line",
        _word_token,
        NewlineToken(),
    )

    _upper_line_statement                   = StatementEx(
        "Upper Line",
        _upper_token,
        NewlineToken(),
    )

    _number_line_statement                  = StatementEx(
        "Number Line",
        _number_token,
        NewlineToken(),
    )

    _multiline_statement                    = StatementEx(
        "Multiline",
        (
            StatementEx(
                "Repeat",
                _word_line_statement,
                _upper_line_statement,
                _number_line_statement,
            ),
            1,
            None,
        ),
    )

    _indent_statement                       = StatementEx(
        "Inner",
        _word_token,
        RegexToken("Colon", re.compile(r":")),
        NewlineToken(),
        IndentToken(),
        _upper_line_statement,
        _number_line_statement,
        DedentToken(),
    )

    # ----------------------------------------------------------------------
    def test_Multiline(self, parse_mock):
        result = self._multiline_statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    one # Comment 1
                    TWO
                    3
                    four
                    FIVE                    # Comment 5
                    66
                    seven
                    EIGHT
                    999     # Comment 9
                    ten      # Comment 10
                    ELEVEN   # Comment 11
                    12       # Comment 12
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            164
                Repeat: (Repeat, 1, None)
                    Repeat
                        0) Word Line
                               Word Token
                                   Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                               Comment <<Regex: <_sre.SRE_Match object; span=(4, 15), match='# Comment 1'>>> ws:(3, 4) !Ignored! [1, 5 -> 1, 16]
                               Newline+
                                   Newline+ <<15, 16>> ws:None [1, 16 -> 2, 1]
                           Upper Line
                               Upper Token
                                   Upper Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                               Newline+
                                   Newline+ <<19, 20>> ws:None [2, 4 -> 3, 1]
                           Number Line
                               Number Token
                                   Number Token <<Regex: <_sre.SRE_Match object; span=(20, 21), match='3'>>> ws:None [3, 1 -> 3, 2]
                               Newline+
                                   Newline+ <<21, 22>> ws:None [3, 2 -> 4, 1]
                        1) Word Line
                               Word Token
                                   Word Token <<Regex: <_sre.SRE_Match object; span=(22, 26), match='four'>>> ws:None [4, 1 -> 4, 5]
                               Newline+
                                   Newline+ <<26, 27>> ws:None [4, 5 -> 5, 1]
                           Upper Line
                               Upper Token
                                   Upper Token <<Regex: <_sre.SRE_Match object; span=(27, 31), match='FIVE'>>> ws:None [5, 1 -> 5, 5]
                               Comment <<Regex: <_sre.SRE_Match object; span=(51, 62), match='# Comment 5'>>> ws:(31, 51) !Ignored! [5, 25 -> 5, 36]
                               Newline+
                                   Newline+ <<62, 63>> ws:None [5, 36 -> 6, 1]
                           Number Line
                               Number Token
                                   Number Token <<Regex: <_sre.SRE_Match object; span=(63, 65), match='66'>>> ws:None [6, 1 -> 6, 3]
                               Newline+
                                   Newline+ <<65, 66>> ws:None [6, 3 -> 7, 1]
                        2) Word Line
                               Word Token
                                   Word Token <<Regex: <_sre.SRE_Match object; span=(66, 71), match='seven'>>> ws:None [7, 1 -> 7, 6]
                               Newline+
                                   Newline+ <<71, 72>> ws:None [7, 6 -> 8, 1]
                           Upper Line
                               Upper Token
                                   Upper Token <<Regex: <_sre.SRE_Match object; span=(72, 77), match='EIGHT'>>> ws:None [8, 1 -> 8, 6]
                               Newline+
                                   Newline+ <<77, 78>> ws:None [8, 6 -> 9, 1]
                           Number Line
                               Number Token
                                   Number Token <<Regex: <_sre.SRE_Match object; span=(78, 81), match='999'>>> ws:None [9, 1 -> 9, 4]
                               Comment <<Regex: <_sre.SRE_Match object; span=(86, 97), match='# Comment 9'>>> ws:(81, 86) !Ignored! [9, 9 -> 9, 20]
                               Newline+
                                   Newline+ <<97, 98>> ws:None [9, 20 -> 10, 1]
                        3) Word Line
                               Word Token
                                   Word Token <<Regex: <_sre.SRE_Match object; span=(98, 101), match='ten'>>> ws:None [10, 1 -> 10, 4]
                               Comment <<Regex: <_sre.SRE_Match object; span=(107, 119), match='# Comment 10'>>> ws:(101, 107) !Ignored! [10, 10 -> 10, 22]
                               Newline+
                                   Newline+ <<119, 120>> ws:None [10, 22 -> 11, 1]
                           Upper Line
                               Upper Token
                                   Upper Token <<Regex: <_sre.SRE_Match object; span=(120, 126), match='ELEVEN'>>> ws:None [11, 1 -> 11, 7]
                               Comment <<Regex: <_sre.SRE_Match object; span=(129, 141), match='# Comment 11'>>> ws:(126, 129) !Ignored! [11, 10 -> 11, 22]
                               Newline+
                                   Newline+ <<141, 142>> ws:None [11, 22 -> 12, 1]
                           Number Line
                               Number Token
                                   Number Token <<Regex: <_sre.SRE_Match object; span=(142, 144), match='12'>>> ws:None [12, 1 -> 12, 3]
                               Comment <<Regex: <_sre.SRE_Match object; span=(151, 163), match='# Comment 12'>>> ws:(144, 151) !Ignored! [12, 10 -> 12, 22]
                               Newline+
                                   Newline+ <<163, 164>> ws:None [12, 22 -> 13, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_Indent(self, parse_mock):
        iterator = CreateIterator(
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
                    999                     # Comment 9
                ten:            # Comment 10
                    ELEVEN      # Comment 11
                    12          # Comment 12
                """,
            ),
        )

        # 1-3
        result = self._indent_statement.Parse(iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            32
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Colon
                    Colon <<Regex: <_sre.SRE_Match object; span=(3, 4), match=':'>>> ws:None [1, 4 -> 1, 5]
                Comment <<Regex: <_sre.SRE_Match object; span=(6, 17), match='# Comment 1'>>> ws:(4, 6) !Ignored! [1, 7 -> 1, 18]
                Newline+
                    Newline+ <<17, 18>> ws:None [1, 18 -> 2, 1]
                Indent
                    Indent <<18, 22, (4)>> ws:None [2, 1 -> 2, 5]
                Upper Line
                    Upper Token
                        Upper Token <<Regex: <_sre.SRE_Match object; span=(22, 25), match='TWO'>>> ws:None [2, 5 -> 2, 8]
                    Newline+
                        Newline+ <<25, 26>> ws:None [2, 8 -> 3, 1]
                Number Line
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(30, 31), match='3'>>> ws:None [3, 5 -> 3, 6]
                    Newline+
                        Newline+ <<31, 32>> ws:None [3, 6 -> 4, 1]
                Dedent
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
            """,
        )

        iterator = result.Iter

        # 4-6
        result = self._indent_statement.Parse(iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            66
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(32, 36), match='four'>>> ws:None [4, 1 -> 4, 5]
                Colon
                    Colon <<Regex: <_sre.SRE_Match object; span=(36, 37), match=':'>>> ws:None [4, 5 -> 4, 6]
                Newline+
                    Newline+ <<37, 38>> ws:None [4, 6 -> 5, 1]
                Indent
                    Indent <<38, 42, (4)>> ws:None [5, 1 -> 5, 5]
                Upper Line
                    Upper Token
                        Upper Token <<Regex: <_sre.SRE_Match object; span=(42, 46), match='FIVE'>>> ws:None [5, 5 -> 5, 9]
                    Comment <<Regex: <_sre.SRE_Match object; span=(47, 58), match='# Comment 5'>>> ws:(46, 47) !Ignored! [5, 10 -> 5, 21]
                    Newline+
                        Newline+ <<58, 59>> ws:None [5, 21 -> 6, 1]
                Number Line
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(63, 65), match='66'>>> ws:None [6, 5 -> 6, 7]
                    Newline+
                        Newline+ <<65, 66>> ws:None [6, 7 -> 7, 1]
                Dedent
                    Dedent <<>> ws:None [7, 1 -> 7, 1]
            """,
        )

        iterator = result.Iter

        # 7-9
        result = self._indent_statement.Parse(iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            123
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(66, 71), match='seven'>>> ws:None [7, 1 -> 7, 6]
                Colon
                    Colon <<Regex: <_sre.SRE_Match object; span=(71, 72), match=':'>>> ws:None [7, 6 -> 7, 7]
                Newline+
                    Newline+ <<72, 73>> ws:None [7, 7 -> 8, 1]
                Indent
                    Indent <<73, 77, (4)>> ws:None [8, 1 -> 8, 5]
                Upper Line
                    Upper Token
                        Upper Token <<Regex: <_sre.SRE_Match object; span=(77, 82), match='EIGHT'>>> ws:None [8, 5 -> 8, 10]
                    Newline+
                        Newline+ <<82, 83>> ws:None [8, 10 -> 9, 1]
                Number Line
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(87, 90), match='999'>>> ws:None [9, 5 -> 9, 8]
                    Comment <<Regex: <_sre.SRE_Match object; span=(111, 122), match='# Comment 9'>>> ws:(90, 111) !Ignored! [9, 29 -> 9, 40]
                    Newline+
                        Newline+ <<122, 123>> ws:None [9, 40 -> 10, 1]
                Dedent
                    Dedent <<>> ws:None [10, 1 -> 10, 1]
            """,
        )

        iterator = result.Iter

        # 10-12
        result = self._indent_statement.Parse(iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            210
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(123, 126), match='ten'>>> ws:None [10, 1 -> 10, 4]
                Colon
                    Colon <<Regex: <_sre.SRE_Match object; span=(126, 127), match=':'>>> ws:None [10, 4 -> 10, 5]
                Comment <<Regex: <_sre.SRE_Match object; span=(139, 151), match='# Comment 10'>>> ws:(127, 139) !Ignored! [10, 17 -> 10, 29]
                Newline+
                    Newline+ <<151, 152>> ws:None [10, 29 -> 11, 1]
                Indent
                    Indent <<152, 156, (4)>> ws:None [11, 1 -> 11, 5]
                Upper Line
                    Upper Token
                        Upper Token <<Regex: <_sre.SRE_Match object; span=(156, 162), match='ELEVEN'>>> ws:None [11, 5 -> 11, 11]
                    Comment <<Regex: <_sre.SRE_Match object; span=(168, 180), match='# Comment 11'>>> ws:(162, 168) !Ignored! [11, 17 -> 11, 29]
                    Newline+
                        Newline+ <<180, 181>> ws:None [11, 29 -> 12, 1]
                Number Line
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(185, 187), match='12'>>> ws:None [12, 5 -> 12, 7]
                    Comment <<Regex: <_sre.SRE_Match object; span=(197, 209), match='# Comment 12'>>> ws:(187, 197) !Ignored! [12, 17 -> 12, 29]
                    Newline+
                        Newline+ <<209, 210>> ws:None [12, 29 -> 13, 1]
                Dedent
                    Dedent <<>> ws:None [13, 1 -> 13, 1]
            """,
        )

        iterator = result.Iter

        assert iterator.AtEnd()

# ----------------------------------------------------------------------
class TestRecursiveStatements(object):
    _statement                              = StatementEx(
        "Recursive Statement",
        _lpar_token,
        [
            _word_token,
            None,
        ],
        _rpar_token,
        populate_empty=True,
    )

    # ----------------------------------------------------------------------
    def test_NoRecursion(self, parse_mock):
        result = self._statement.Parse(CreateIterator("( hello )"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                lpar
                    lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                Or [Word Token, Recursive Statement]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(2, 7), match='hello'>>> ws:(1, 2) [1, 3 -> 1, 8]
                rpar
                    rpar <<Regex: <_sre.SRE_Match object; span=(8, 9), match=')'>>> ws:(7, 8) [1, 9 -> 1, 10]
            """,
        )

    # ----------------------------------------------------------------------
    def test_SingleRecursion(self, parse_mock):
        result = self._statement.Parse(CreateIterator("((hello))"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                lpar
                    lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                Or [Word Token, Recursive Statement]
                    Recursive Statement
                        lpar
                            lpar <<Regex: <_sre.SRE_Match object; span=(1, 2), match='('>>> ws:None [1, 2 -> 1, 3]
                        Or [Word Token, Recursive Statement]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(2, 7), match='hello'>>> ws:None [1, 3 -> 1, 8]
                        rpar
                            rpar <<Regex: <_sre.SRE_Match object; span=(7, 8), match=')'>>> ws:None [1, 8 -> 1, 9]
                rpar
                    rpar <<Regex: <_sre.SRE_Match object; span=(8, 9), match=')'>>> ws:None [1, 9 -> 1, 10]
            """,
        )

    # ----------------------------------------------------------------------
    def test_DoubleRecursion(self, parse_mock):
        result = self._statement.Parse(CreateIterator("( ( ( hello)))"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            14
                lpar
                    lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                Or [Word Token, Recursive Statement]
                    Recursive Statement
                        lpar
                            lpar <<Regex: <_sre.SRE_Match object; span=(2, 3), match='('>>> ws:(1, 2) [1, 3 -> 1, 4]
                        Or [Word Token, Recursive Statement]
                            Recursive Statement
                                lpar
                                    lpar <<Regex: <_sre.SRE_Match object; span=(4, 5), match='('>>> ws:(3, 4) [1, 5 -> 1, 6]
                                Or [Word Token, Recursive Statement]
                                    Word Token
                                        Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='hello'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                rpar
                                    rpar <<Regex: <_sre.SRE_Match object; span=(11, 12), match=')'>>> ws:None [1, 12 -> 1, 13]
                        rpar
                            rpar <<Regex: <_sre.SRE_Match object; span=(12, 13), match=')'>>> ws:None [1, 13 -> 1, 14]
                rpar
                    rpar <<Regex: <_sre.SRE_Match object; span=(13, 14), match=')'>>> ws:None [1, 14 -> 1, 15]
            """,
        )

    # ----------------------------------------------------------------------
    def test_ErrorParseWithoutPopulate(self, parse_mock):
        statement = StatementEx(
            "Recursive Statement",
            _lpar_token,
            [
                _word_token,
                None,
            ],
            _rpar_token,
        )

        with pytest.raises(Exception) as ex:
            statement.Parse("(test)", parse_mock)

        ex = ex.value

        assert str(ex) == "The statement has not been populated by an upstream statement"

    # ----------------------------------------------------------------------
    def test_NestedWithoutPopulation(self):
        StatementEx(
            "Statement 1",
            [
                None,
            ],
        )

        StatementEx(
            "Statement 2",
            (
                None,
                0,
                None,
            ),
        )

# ----------------------------------------------------------------------
def test_IgnoreWhitespace(parse_mock):
    statement = StatementEx(
        "Statement",
        PushIgnoreWhitespaceControlToken(),
        _word_token,
        _word_token,
        PopIgnoreWhitespaceControlToken(),
    )

    result = statement.Parse(
        CreateIterator(
            textwrap.dedent(
                """\



                            worda

                    wordb

                """,
            ),
        ),
        parse_mock,
    )

    assert str(result) == textwrap.dedent(
        """\
        True
        25
            Newline+ <<0, 3>> ws:None !Ignored! [1, 1 -> 4, 1]
            Indent <<3, 11, (8)>> ws:None !Ignored! [4, 1 -> 4, 9]
            Word Token
                Word Token <<Regex: <_sre.SRE_Match object; span=(11, 16), match='worda'>>> ws:None [4, 9 -> 4, 14]
            Newline+ <<16, 18>> ws:None !Ignored! [4, 14 -> 6, 1]
            Dedent <<>> ws:None !Ignored! [6, 1 -> 6, 1]
            Word Token
                Word Token <<Regex: <_sre.SRE_Match object; span=(18, 23), match='wordb'>>> ws:None [6, 1 -> 6, 6]
            Newline+ <<23, 25>> ws:None !Ignored! [6, 6 -> 8, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_StatementWithNestedStatement(parse_mock):
    statement = StatementEx(
        "Statement",
        TokenStatement(_word_token),
    )

    result = statement.Parse(CreateIterator("test"), parse_mock)

    assert str(result) == textwrap.dedent(
        """\
        True
        4
            Word Token
                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='test'>>> ws:None [1, 1 -> 1, 5]
        """,
    )
