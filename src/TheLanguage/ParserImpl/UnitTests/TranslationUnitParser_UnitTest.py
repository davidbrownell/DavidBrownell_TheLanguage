# ----------------------------------------------------------------------
# |
# |  TranslationUnitParser_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-01 15:39:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for TranslationUnit.py"""

import os
import re
import textwrap

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..StatementEx import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
        StatementEx,
    )

    from ..TranslationUnitParser import *

    from ..StatementImpl.UnitTests import (
        CoroutineMock,
        CreateIterator,
        parse_mock as parse_mock_impl,
    )

# ----------------------------------------------------------------------
@pytest.fixture
def parse_mock(parse_mock_impl):
    parse_mock_impl.OnIndentAsync = CoroutineMock()
    parse_mock_impl.OnDedentAsync = CoroutineMock()
    parse_mock_impl.OnStatementCompleteAsync = CoroutineMock()

    return parse_mock_impl

# ----------------------------------------------------------------------
def OnStatementCompleteEqual(
    mock_method_call_result: Tuple[
        Statement,
        Statement.ParseResultData,
        NormalizedIterator,
        NormalizedIterator,
    ],
    statement: Optional[Statement],
    data: Statement.ParseResultData,
    offset_before: int,
    offset_after: int,
):
    mock_method_call_result = mock_method_call_result[0]

    if statement is not None:
        assert statement == mock_method_call_result[0]

    assert data == mock_method_call_result[1]
    assert offset_before == mock_method_call_result[2].Offset
    assert offset_after == mock_method_call_result[3].Offset

# ----------------------------------------------------------------------
_upper_token                                = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
_lower_token                                = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
_number_token                               = RegexToken("Number", re.compile(r"(?P<value>\d+)"))

# ----------------------------------------------------------------------
class TestSimple(object):
    _upper_statement                        = StatementEx("Upper Statement", _upper_token, NewlineToken())
    _lower_statement                        = StatementEx("Lower Statement", _lower_token, NewlineToken())
    _number_statement                       = StatementEx("Number Statement", _number_token, NewlineToken())

    _statements                             = DynamicStatementInfo(
        [_upper_statement, _lower_statement, _number_statement],
        [],
    )

    # ----------------------------------------------------------------------
    def test_MatchStandard(self, parse_mock):
        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                    two
                    33333
                    """,
                ),
            ),
            parse_mock,
        )

        assert "".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Upper Statement, Lower Statement, Number Statement]
                Upper Statement
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            [Upper Statement, Lower Statement, Number Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                    Newline+
                        Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            [Upper Statement, Lower Statement, Number Statement]
                Number Statement
                    Number
                        Number <<Regex: <_sre.SRE_Match object; span=(8, 13), match='33333'>>> ws:None [3, 1 -> 3, 6]
                    Newline+
                        Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 6
        assert len(parse_mock.OnStatementCompleteAsync.call_args_list) == 6

        # Line 1
        OnStatementCompleteEqual(
            parse_mock.OnStatementCompleteAsync.call_args_list[0],
            self._upper_statement,
            results[0].Data.Data,
            0,
            4,
        )

        OnStatementCompleteEqual(
            parse_mock.OnStatementCompleteAsync.call_args_list[1],
            None, # Or Statement
            results[0].Data,
            0,
            4,
        )

        # Line 2
        OnStatementCompleteEqual(
            parse_mock.OnStatementCompleteAsync.call_args_list[2],
            self._lower_statement,
            results[1].Data.Data,
            4,
            8,
        )

        OnStatementCompleteEqual(
            parse_mock.OnStatementCompleteAsync.call_args_list[3],
            None, # Or Statement
            results[1].Data,
            4,
            8,
        )

        # Line 3
        OnStatementCompleteEqual(
            parse_mock.OnStatementCompleteAsync.call_args_list[4],
            self._number_statement,
            results[2].Data.Data,
            8,
            14,
        )

        OnStatementCompleteEqual(
            parse_mock.OnStatementCompleteAsync.call_args_list[5],
            None, # Or Statement
            results[2].Data,
            8,
            14,
        )

    # ----------------------------------------------------------------------
    def test_MatchReverse(self, parse_mock):
        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    33
                    twooooooooo
                    ONE
                    """,
                ),
            ),
            parse_mock,
        )

        assert "".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Upper Statement, Lower Statement, Number Statement]
                Number Statement
                    Number
                        Number <<Regex: <_sre.SRE_Match object; span=(0, 2), match='33'>>> ws:None [1, 1 -> 1, 3]
                    Newline+
                        Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
            [Upper Statement, Lower Statement, Number Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(3, 14), match='twooooooooo'>>> ws:None [2, 1 -> 2, 12]
                    Newline+
                        Newline+ <<14, 15>> ws:None [2, 12 -> 3, 1]
            [Upper Statement, Lower Statement, Number Statement]
                Upper Statement
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(15, 18), match='ONE'>>> ws:None [3, 1 -> 3, 4]
                    Newline+
                        Newline+ <<18, 19>> ws:None [3, 4 -> 4, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 6
        assert len(parse_mock.OnStatementCompleteAsync.call_args_list) == 6

    # ----------------------------------------------------------------------
    def test_EarlyTermination(self, parse_mock):
        parse_mock.OnStatementCompleteAsync = CoroutineMock(
            side_effect=[True, False],
        )

        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    33
                    twooooooooo
                    ONE
                    """,
                ),
            ),
            parse_mock,
        )

        assert results is None

# ----------------------------------------------------------------------
class TestIndentation(object):
    _statement                              = StatementEx(
        "Statement",
        _upper_token,
        NewlineToken(),
        IndentToken(),
        _upper_token,
        _upper_token,
        NewlineToken(),
        DedentToken(),
    )

    _statements                             = DynamicStatementInfo(
        [_statement],
        [],
    )

    # ----------------------------------------------------------------------
    def test_Match(self, parse_mock):
        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                        TWO      THREE
                    """,
                ),
            ),
            parse_mock,
        )

        assert "".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Statement]
                Statement
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(8, 11), match='TWO'>>> ws:None [2, 5 -> 2, 8]
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(17, 22), match='THREE'>>> ws:(11, 17) [2, 14 -> 2, 19]
                    Newline+
                        Newline+ <<22, 23>> ws:None [2, 19 -> 3, 1]
                    Dedent
                        Dedent <<>> ws:None [3, 1 -> 3, 1]
            """,
        )

# ----------------------------------------------------------------------
class TestNewStatements(object):
    _upper_statement                        = StatementEx("Upper Statement", _upper_token)
    _lower_statement                        = StatementEx("Lower Statement", _lower_token, NewlineToken())

    _statements                             = DynamicStatementInfo([_upper_statement], [])
    _new_statements                         = DynamicStatementInfo([_lower_statement], [])

    # ----------------------------------------------------------------------
    def test_Match(self, parse_mock):
        parse_mock.OnStatementCompleteAsync = CoroutineMock(
            side_effect=[self._new_statements, True, True, True],
        )

        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE two
                    """,
                ),
            ),
            parse_mock,
        )

        assert "".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Upper Statement]
                Upper Statement
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
            [Upper Statement] / [Lower Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    Newline+
                        Newline+ <<7, 8>> ws:None [1, 8 -> 2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            Parse(
                self._statements,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        ONE two
                        """,
                    ),
                ),
                parse_mock,
            )

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 1
        assert ex.Column == 4

        assert ex.ToString() == textwrap.dedent(
            """\
            The syntax is not recognized [1, 4]

            [Upper Statement]
                Upper Statement
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
            [Upper Statement]
                Upper Statement
                    Upper
                        None
            """,
        )

# ----------------------------------------------------------------------
class TestNewScopedStatements(object):
    _upper_statement                        = StatementEx("Upper Statement", _upper_token)
    _lower_statement                        = StatementEx("Lower Statement", _lower_token)

    _newline_statement                      = StatementEx("Newline Statement", NewlineToken())
    _indent_statement                       = StatementEx("Indent Statement", IndentToken())
    _dedent_statement                       = StatementEx("Dedent Statement", DedentToken())

    _statements                             = DynamicStatementInfo([_upper_statement, _newline_statement, _indent_statement, _dedent_statement], [])
    _new_statements                         = DynamicStatementInfo([_lower_statement], [])

    # ----------------------------------------------------------------------
    def test_Match(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=self._new_statements,
        )

        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                        two
                    """,
                ),
            ),
            parse_mock,
        )

        assert "".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                Upper Statement
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                Newline Statement
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                Indent Statement
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement] / [Lower Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement] / [Lower Statement]
                Newline Statement
                    Newline+
                        Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement] / [Lower Statement]
                Dedent Statement
                    Dedent
                        Dedent <<>> ws:None [3, 1 -> 3, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=self._new_statements,
        )

        with pytest.raises(SyntaxInvalidError) as ex:
            Parse(
                self._statements,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        ONE
                            two

                        nomatch
                        """,
                    ),
                ),
                parse_mock,
            )

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 4
        assert ex.Column == 1

        assert ex.ToString() == textwrap.dedent(
            """\
            The syntax is not recognized [4, 1]

            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                Upper Statement
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                Newline Statement
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                Indent Statement
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement] / [Lower Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement] / [Lower Statement]
                Newline Statement
                    Newline+
                        Newline+ <<11, 13>> ws:None [2, 8 -> 4, 1]
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement] / [Lower Statement]
                Dedent Statement
                    Dedent
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            [Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                Upper Statement
                    Upper
                        None
                Newline Statement
                    Newline+
                        None
                Indent Statement
                    Indent
                        None
                Dedent Statement
                    Dedent
                        None
            """,
        )

# ----------------------------------------------------------------------
class TestEmbeddedStatements(object):
    _upper_lower_statement                  = StatementEx("Upper Lower Statement", _upper_token, _lower_token, NewlineToken())

    _uul_statement                          = StatementEx("uul", _upper_token, _upper_lower_statement)
    _lul_statement                          = StatementEx("lul", _lower_token, _upper_lower_statement)

    _statements                             = DynamicStatementInfo([_uul_statement, _lul_statement], [])

    # ----------------------------------------------------------------------
    def test_Match(self, parse_mock):
        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE TWO  three
                    four    FIVE six
                    """,
                ),
            ),
            parse_mock,
        )

        assert "".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [uul, lul]
                uul
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                    Upper Lower Statement
                        Upper
                            Upper <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:(3, 4) [1, 5 -> 1, 8]
                        Lower
                            Lower <<Regex: <_sre.SRE_Match object; span=(9, 14), match='three'>>> ws:(7, 9) [1, 10 -> 1, 15]
                        Newline+
                            Newline+ <<14, 15>> ws:None [1, 15 -> 2, 1]
            [uul, lul]
                lul
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(15, 19), match='four'>>> ws:None [2, 1 -> 2, 5]
                    Upper Lower Statement
                        Upper
                            Upper <<Regex: <_sre.SRE_Match object; span=(23, 27), match='FIVE'>>> ws:(19, 23) [2, 9 -> 2, 13]
                        Lower
                            Lower <<Regex: <_sre.SRE_Match object; span=(28, 31), match='six'>>> ws:(27, 28) [2, 14 -> 2, 17]
                        Newline+
                            Newline+ <<31, 32>> ws:None [2, 17 -> 3, 1]
            """,
        )

# ----------------------------------------------------------------------
class TestVariedLengthMatches(object):
    _upper_statement                        = StatementEx("Upper", _upper_token, NewlineToken())
    _lower_statement                        = StatementEx("Lower", _lower_token, _lower_token, NewlineToken())
    _number_statement                       = StatementEx("Number", _number_token, _number_token, _number_token, NewlineToken())

    _statements                             = DynamicStatementInfo(
        [_upper_statement, _lower_statement, _number_statement],
        [],
    )

    # ----------------------------------------------------------------------
    def test_Match(self, parse_mock):
        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    one two
                    1 2 3
                    WORD
                    """,
                ),
            ),
            parse_mock,
        )

        assert "".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Upper, Lower, Number]
                Lower
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    Newline+
                        Newline+ <<7, 8>> ws:None [1, 8 -> 2, 1]
            [Upper, Lower, Number]
                Number
                    Number
                        Number <<Regex: <_sre.SRE_Match object; span=(8, 9), match='1'>>> ws:None [2, 1 -> 2, 2]
                    Number
                        Number <<Regex: <_sre.SRE_Match object; span=(10, 11), match='2'>>> ws:(9, 10) [2, 3 -> 2, 4]
                    Number
                        Number <<Regex: <_sre.SRE_Match object; span=(12, 13), match='3'>>> ws:(11, 12) [2, 5 -> 2, 6]
                    Newline+
                        Newline+ <<13, 14>> ws:None [2, 6 -> 3, 1]
            [Upper, Lower, Number]
                Upper
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(14, 18), match='WORD'>>> ws:None [3, 1 -> 3, 5]
                    Newline+
                        Newline+ <<18, 19>> ws:None [3, 5 -> 4, 1]
            """,
        )

# ----------------------------------------------------------------------
def test_EmptyDynamicStatementInfo(parse_mock):
    parse_mock.OnStatementCompleteAsync = CoroutineMock(
        return_value=DynamicStatementInfo([], []),
    )

    results = Parse(
        DynamicStatementInfo(
            [
                StatementEx("Newline Statement", NewlineToken()),
                StatementEx("Lower Statement", _lower_token, NewlineToken()),
            ],
            [],
        ),
        CreateIterator(
            textwrap.dedent(
                """\

                word
                """,
            ),
        ),
        parse_mock,
    )

    assert "".join([str(result) for result in results]) == textwrap.dedent(
        """\
        [Newline Statement, Lower Statement]
            Newline Statement
                Newline+
                    Newline+ <<0, 1>> ws:None [1, 1 -> 2, 1]
        [Newline Statement, Lower Statement]
            Lower Statement
                Lower
                    Lower <<Regex: <_sre.SRE_Match object; span=(1, 5), match='word'>>> ws:None [2, 1 -> 2, 5]
                Newline+
                    Newline+ <<5, 6>> ws:None [2, 5 -> 3, 1]
        """,
    )

# ----------------------------------------------------------------------
class TestPreventParentTraversal(object):
    _upper_statement                        = StatementEx("Upper Statement", _upper_token, NewlineToken())
    _lower_statement                        = StatementEx("Lower Statement", _lower_token, NewlineToken())
    _indent_statement                       = StatementEx("Indent Statement", IndentToken())
    _dedent_statement                       = StatementEx("Dedent Statement", DedentToken())

    _statements                             = DynamicStatementInfo(
        [_upper_statement, _indent_statement, _dedent_statement],
        [],
    )

    # ----------------------------------------------------------------------
    def test_Match(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=DynamicStatementInfo(
                [self._lower_statement, self._dedent_statement],
                [],
                False,
            ),
        )

        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                        two
                        three
                        four

                    FIVE
                    """,
                ),
            ),
            parse_mock,
        )

        assert "".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Upper Statement, Indent Statement, Dedent Statement]
                Upper Statement
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            [Upper Statement, Indent Statement, Dedent Statement]
                Indent Statement
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
            [Lower Statement, Dedent Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                    Newline+
                        Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
            [Lower Statement, Dedent Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 5 -> 3, 10]
                    Newline+
                        Newline+ <<21, 22>> ws:None [3, 10 -> 4, 1]
            [Lower Statement, Dedent Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(26, 30), match='four'>>> ws:None [4, 5 -> 4, 9]
                    Newline+
                        Newline+ <<30, 32>> ws:None [4, 9 -> 6, 1]
            [Lower Statement, Dedent Statement]
                Dedent Statement
                    Dedent
                        Dedent <<>> ws:None [6, 1 -> 6, 1]
            [Upper Statement, Indent Statement, Dedent Statement]
                Upper Statement
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(32, 36), match='FIVE'>>> ws:None [6, 1 -> 6, 5]
                    Newline+
                        Newline+ <<36, 37>> ws:None [6, 5 -> 7, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=DynamicStatementInfo(
                [self._lower_statement, self._dedent_statement],
                [],
                False,
            ),
        )

        with pytest.raises(SyntaxInvalidError) as ex:
            Parse(
                self._statements,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        ONE
                            two
                            three
                            four

                        five
                        """,
                    ),
                ),
                parse_mock,
            )

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 6
        assert ex.Column == 1

        assert ex.ToString() == textwrap.dedent(
            """\
            The syntax is not recognized [6, 1]

            [Upper Statement, Indent Statement, Dedent Statement]
                Upper Statement
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            [Upper Statement, Indent Statement, Dedent Statement]
                Indent Statement
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
            [Lower Statement, Dedent Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                    Newline+
                        Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
            [Lower Statement, Dedent Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 5 -> 3, 10]
                    Newline+
                        Newline+ <<21, 22>> ws:None [3, 10 -> 4, 1]
            [Lower Statement, Dedent Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(26, 30), match='four'>>> ws:None [4, 5 -> 4, 9]
                    Newline+
                        Newline+ <<30, 32>> ws:None [4, 9 -> 6, 1]
            [Lower Statement, Dedent Statement]
                Dedent Statement
                    Dedent
                        Dedent <<>> ws:None [6, 1 -> 6, 1]
            [Upper Statement, Indent Statement, Dedent Statement]
                Upper Statement
                    Upper
                        None
                Indent Statement
                    Indent
                        None
                Dedent Statement
                    Dedent
                        None
            """,
        )

# ----------------------------------------------------------------------
def test_InvalidDynamicTraversalError(parse_mock):
    parse_mock.OnStatementCompleteAsync = CoroutineMock(
        return_value=DynamicStatementInfo(
            [StatementEx("Newline", NewlineToken())],
            [],
            False,
        ),
    )

    with pytest.raises(InvalidDynamicTraversalError) as ex:
        Parse(
            DynamicStatementInfo(
                [StatementEx("Newline", NewlineToken())],
                [],
            ),
            CreateIterator(
                textwrap.dedent(
                    """\



                    """,
                ),
            ),
            parse_mock,
        )

    ex = ex.value

    assert str(ex) == "Dynamic statements that prohibit parent traversal should never be applied over other dynamic statements within the same lexical scope. You should make these dynamic statements the first ones applied in this lexical scope."
    assert ex.Line == 1
    assert ex.Column == 1

# ----------------------------------------------------------------------
def test_DynamicExpressions(parse_mock):
    results = Parse(
        DynamicStatementInfo(
            [
                StatementEx(
                    "Statement",
                    _upper_token,
                    DynamicStatements.Expressions,
                    _lower_token,
                    NewlineToken(),
                ),
            ],
            [
                StatementEx(
                    "Expression",
                    _number_token,
                ),
            ],
        ),
        CreateIterator("WORD 1234 lower"),
        parse_mock,
    )

    assert "".join([str(result) for result in results]) == textwrap.dedent(
        """\
        [Statement]
            Statement
                Upper
                    Upper <<Regex: <_sre.SRE_Match object; span=(0, 4), match='WORD'>>> ws:None [1, 1 -> 1, 5]
                DynamicStatements.Expressions
                    [Expression]
                        Expression
                            Number
                                Number <<Regex: <_sre.SRE_Match object; span=(5, 9), match='1234'>>> ws:(4, 5) [1, 6 -> 1, 10]
                Lower
                    Lower <<Regex: <_sre.SRE_Match object; span=(10, 15), match='lower'>>> ws:(9, 10) [1, 11 -> 1, 16]
                Newline+
                    Newline+ <<15, 16>> ws:None [1, 16 -> 2, 1]
        """,
    )
