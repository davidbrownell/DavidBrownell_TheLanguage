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
        InternalStatementMethodCallToTuple,
        MethodCallsToString,
        parse_mock as parse_mock_impl,
    )

# ----------------------------------------------------------------------
@pytest.fixture
def parse_mock(parse_mock_impl):
    parse_mock_impl.OnStatementCompleteAsync = CoroutineMock()

    return parse_mock_impl

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
            single_threaded=True,
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

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0, OnStatementCompleteAsync, Upper
            1, OnStatementCompleteAsync, Newline+
            2, OnStatementCompleteAsync, Upper Statement
            3, OnStatementCompleteAsync, [Upper Statement, Lower Statement, Number Statement]
            4, OnStatementCompleteAsync, Dynamic Statements
            5, OnStatementCompleteAsync, Lower
            6, OnStatementCompleteAsync, Newline+
            7, OnStatementCompleteAsync, Lower Statement
            8, OnStatementCompleteAsync, [Upper Statement, Lower Statement, Number Statement]
            9, OnStatementCompleteAsync, Dynamic Statements
            10, OnStatementCompleteAsync, Number
            11, OnStatementCompleteAsync, Newline+
            12, OnStatementCompleteAsync, Number Statement
            13, OnStatementCompleteAsync, [Upper Statement, Lower Statement, Number Statement]
            14, OnStatementCompleteAsync, Dynamic Statements
            """,
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

        assert len(parse_mock.method_calls) == 15

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
            side_effect=[self._new_statements, True, True, True, True, True, True, True, True],
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

        assert ex.ToDebugString() == textwrap.dedent(
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

        assert ex.ToDebugString() == textwrap.dedent(
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
class TestNewScopedStatementsComplex(object):
    _upper_statement                        = StatementEx("Upper Statement", _upper_token)
    _lower_statement                        = StatementEx("Lower Statement", _lower_token)

    _newline_statement                      = StatementEx("Newline Statement", NewlineToken())
    _dedent_statement                       = StatementEx("Dedent Statement", DedentToken())

    _new_scope_statement                    = StatementEx(
        "New Scope",
        _upper_token,
        RegexToken("Colon", re.compile(r":")),
        NewlineToken(),
        IndentToken(),
        DynamicStatements.Statements,
        DynamicStatements.Statements,
        DynamicStatements.Statements,
        DynamicStatements.Statements,
        DedentToken(),
    )

    _statements                             = DynamicStatementInfo([_newline_statement, _new_scope_statement], [])
    _new_statements                         = DynamicStatementInfo([_upper_statement, _lower_statement], [])

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
                    NEWSCOPE:
                        UPPER

                        lower
                    """,
                ),
            ),
            parse_mock,
        )

        assert "\n".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Newline Statement, New Scope]
                New Scope
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 8), match='NEWSCOPE'>>> ws:None [1, 1 -> 1, 9]
                    Colon
                        Colon <<Regex: <_sre.SRE_Match object; span=(8, 9), match=':'>>> ws:None [1, 9 -> 1, 10]
                    Newline+
                        Newline+ <<9, 10>> ws:None [1, 10 -> 2, 1]
                    Indent
                        Indent <<10, 14, (4)>> ws:None [2, 1 -> 2, 5]
                    DynamicStatements.Statements
                        [Newline Statement, New Scope] / [Upper Statement, Lower Statement]
                            Upper Statement
                                Upper
                                    Upper <<Regex: <_sre.SRE_Match object; span=(14, 19), match='UPPER'>>> ws:None [2, 5 -> 2, 10]
                    DynamicStatements.Statements
                        [Newline Statement, New Scope] / [Upper Statement, Lower Statement]
                            Newline Statement
                                Newline+
                                    Newline+ <<19, 21>> ws:None [2, 10 -> 4, 1]
                    DynamicStatements.Statements
                        [Newline Statement, New Scope] / [Upper Statement, Lower Statement]
                            Lower Statement
                                Lower
                                    Lower <<Regex: <_sre.SRE_Match object; span=(25, 30), match='lower'>>> ws:None [4, 5 -> 4, 10]
                    DynamicStatements.Statements
                        [Newline Statement, New Scope] / [Upper Statement, Lower Statement]
                            Newline Statement
                                Newline+
                                    Newline+ <<30, 31>> ws:None [4, 10 -> 5, 1]
                    Dedent
                        Dedent <<>> ws:None [5, 1 -> 5, 1]
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

        assert ex.ToDebugString() == textwrap.dedent(
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
    assert ex.Line == 4
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

# ----------------------------------------------------------------------
class TestCatastrophicInclude(object):
    _include_statement                      = StatementEx(
        "Include Statement",
        RegexToken("include", re.compile(r"include")),
        _upper_token,
        NewlineToken(),
    )

    # Both of these statements start with an include, but the
    # dynamic statements allowed will be based on the included
    # value.
    _lower_include_statement                = StatementEx(
        "Lower Include Statement",
        _include_statement,
        DynamicStatements.Statements,
        DynamicStatements.Statements,
    )

    _number_include_statement               = StatementEx(
        "Number Include Statement",
        _include_statement,
        DynamicStatements.Statements,
        DynamicStatements.Statements,
        DynamicStatements.Statements,
    )

    _lower_statement                        = StatementEx(
        "Lower Statement",
        _lower_token,
        NewlineToken(),
    )

    _number_statement                       = StatementEx(
        "Number Statement",
        _number_token,
        NewlineToken(),
    )

    _statements                             = DynamicStatementInfo(
        [_lower_include_statement, _number_include_statement],
        [],
    )

    _lower_dynamic_statements               = DynamicStatementInfo(
        [_lower_statement],
        [],
        True,
        # "Lower Dynamic Statements",
    )

    _number_dynamic_statements              = DynamicStatementInfo(
        [_number_statement],
        [],
        True,
        # "Number Dynamic Statements",
    )

    # ----------------------------------------------------------------------
    @classmethod
    @pytest.fixture
    def this_parse_mock(cls, parse_mock):
        # ----------------------------------------------------------------------
        async def OnStatementCompleteAsync(
            statement: Statement,
            data: Optional[Statement.ParseResultData],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ):
            if statement == cls._include_statement:
                value = data.DataItems[1].Data.Value.Match.group("value")

                if value == "LOWER":
                    return cls._lower_dynamic_statements
                elif value == "NUMBER":
                    return cls._number_dynamic_statements
                else:
                    assert False, value

            return True

        # ----------------------------------------------------------------------

        parse_mock.OnStatementCompleteAsync = OnStatementCompleteAsync

        return parse_mock

    # ----------------------------------------------------------------------
    def test_Lower(self, this_parse_mock):
        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include LOWER
                    one
                    two
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert "\n".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Lower Include Statement, Number Include Statement]
                Lower Include Statement
                    Include Statement
                        include
                            include <<Regex: <_sre.SRE_Match object; span=(0, 7), match='include'>>> ws:None [1, 1 -> 1, 8]
                        Upper
                            Upper <<Regex: <_sre.SRE_Match object; span=(8, 13), match='LOWER'>>> ws:(7, 8) [1, 9 -> 1, 14]
                        Newline+
                            Newline+ <<13, 14>> ws:None [1, 14 -> 2, 1]
                    DynamicStatements.Statements
                        [Lower Include Statement, Number Include Statement] / [Lower Statement]
                            Lower Statement
                                Lower
                                    Lower <<Regex: <_sre.SRE_Match object; span=(14, 17), match='one'>>> ws:None [2, 1 -> 2, 4]
                                Newline+
                                    Newline+ <<17, 18>> ws:None [2, 4 -> 3, 1]
                    DynamicStatements.Statements
                        [Lower Include Statement, Number Include Statement] / [Lower Statement]
                            Lower Statement
                                Lower
                                    Lower <<Regex: <_sre.SRE_Match object; span=(18, 21), match='two'>>> ws:None [3, 1 -> 3, 4]
                                Newline+
                                    Newline+ <<21, 22>> ws:None [3, 4 -> 4, 1]
            """,
        )

        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    def test_LowerAdditionalItem(self, this_parse_mock):
        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include LOWER
                    one
                    two

                    three
                    four
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert "\n".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Lower Include Statement, Number Include Statement]
                Number Include Statement
                    Include Statement
                        include
                            include <<Regex: <_sre.SRE_Match object; span=(0, 7), match='include'>>> ws:None [1, 1 -> 1, 8]
                        Upper
                            Upper <<Regex: <_sre.SRE_Match object; span=(8, 13), match='LOWER'>>> ws:(7, 8) [1, 9 -> 1, 14]
                        Newline+
                            Newline+ <<13, 14>> ws:None [1, 14 -> 2, 1]
                    DynamicStatements.Statements
                        [Lower Include Statement, Number Include Statement] / [Lower Statement]
                            Lower Statement
                                Lower
                                    Lower <<Regex: <_sre.SRE_Match object; span=(14, 17), match='one'>>> ws:None [2, 1 -> 2, 4]
                                Newline+
                                    Newline+ <<17, 18>> ws:None [2, 4 -> 3, 1]
                    DynamicStatements.Statements
                        [Lower Include Statement, Number Include Statement] / [Lower Statement]
                            Lower Statement
                                Lower
                                    Lower <<Regex: <_sre.SRE_Match object; span=(18, 21), match='two'>>> ws:None [3, 1 -> 3, 4]
                                Newline+
                                    Newline+ <<21, 23>> ws:None [3, 4 -> 5, 1]
                    DynamicStatements.Statements
                        [Lower Include Statement, Number Include Statement] / [Lower Statement]
                            Lower Statement
                                Lower
                                    Lower <<Regex: <_sre.SRE_Match object; span=(23, 28), match='three'>>> ws:None [5, 1 -> 5, 6]
                                Newline+
                                    Newline+ <<28, 29>> ws:None [5, 6 -> 6, 1]

            [Lower Include Statement, Number Include Statement] / [Lower Statement]
                Lower Statement
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(29, 33), match='four'>>> ws:None [6, 1 -> 6, 5]
                    Newline+
                        Newline+ <<33, 34>> ws:None [6, 5 -> 7, 1]
            """,
        )

        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    def test_Number(self, this_parse_mock):
        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include NUMBER
                    1
                    2
                    3
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert "\n".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Lower Include Statement, Number Include Statement]
                Number Include Statement
                    Include Statement
                        include
                            include <<Regex: <_sre.SRE_Match object; span=(0, 7), match='include'>>> ws:None [1, 1 -> 1, 8]
                        Upper
                            Upper <<Regex: <_sre.SRE_Match object; span=(8, 14), match='NUMBER'>>> ws:(7, 8) [1, 9 -> 1, 15]
                        Newline+
                            Newline+ <<14, 15>> ws:None [1, 15 -> 2, 1]
                    DynamicStatements.Statements
                        [Lower Include Statement, Number Include Statement] / [Number Statement]
                            Number Statement
                                Number
                                    Number <<Regex: <_sre.SRE_Match object; span=(15, 16), match='1'>>> ws:None [2, 1 -> 2, 2]
                                Newline+
                                    Newline+ <<16, 17>> ws:None [2, 2 -> 3, 1]
                    DynamicStatements.Statements
                        [Lower Include Statement, Number Include Statement] / [Number Statement]
                            Number Statement
                                Number
                                    Number <<Regex: <_sre.SRE_Match object; span=(17, 18), match='2'>>> ws:None [3, 1 -> 3, 2]
                                Newline+
                                    Newline+ <<18, 19>> ws:None [3, 2 -> 4, 1]
                    DynamicStatements.Statements
                        [Lower Include Statement, Number Include Statement] / [Number Statement]
                            Number Statement
                                Number
                                    Number <<Regex: <_sre.SRE_Match object; span=(19, 20), match='3'>>> ws:None [4, 1 -> 4, 2]
                                Newline+
                                    Newline+ <<20, 21>> ws:None [4, 2 -> 5, 1]
            """,
        )

        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    def test_NumberAdditionalItems(self, this_parse_mock):
        results = Parse(
            self._statements,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include NUMBER
                    1
                    2
                    3

                    4
                    5
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert "\n".join([str(result) for result in results]) == textwrap.dedent(
            """\
            [Lower Include Statement, Number Include Statement]
                Number Include Statement
                    Include Statement
                        include
                            include <<Regex: <_sre.SRE_Match object; span=(0, 7), match='include'>>> ws:None [1, 1 -> 1, 8]
                        Upper
                            Upper <<Regex: <_sre.SRE_Match object; span=(8, 14), match='NUMBER'>>> ws:(7, 8) [1, 9 -> 1, 15]
                        Newline+
                            Newline+ <<14, 15>> ws:None [1, 15 -> 2, 1]
                    DynamicStatements.Statements
                        [Lower Include Statement, Number Include Statement] / [Number Statement]
                            Number Statement
                                Number
                                    Number <<Regex: <_sre.SRE_Match object; span=(15, 16), match='1'>>> ws:None [2, 1 -> 2, 2]
                                Newline+
                                    Newline+ <<16, 17>> ws:None [2, 2 -> 3, 1]
                    DynamicStatements.Statements
                        [Lower Include Statement, Number Include Statement] / [Number Statement]
                            Number Statement
                                Number
                                    Number <<Regex: <_sre.SRE_Match object; span=(17, 18), match='2'>>> ws:None [3, 1 -> 3, 2]
                                Newline+
                                    Newline+ <<18, 19>> ws:None [3, 2 -> 4, 1]
                    DynamicStatements.Statements
                        [Lower Include Statement, Number Include Statement] / [Number Statement]
                            Number Statement
                                Number
                                    Number <<Regex: <_sre.SRE_Match object; span=(19, 20), match='3'>>> ws:None [4, 1 -> 4, 2]
                                Newline+
                                    Newline+ <<20, 22>> ws:None [4, 2 -> 6, 1]

            [Lower Include Statement, Number Include Statement] / [Number Statement]
                Number Statement
                    Number
                        Number <<Regex: <_sre.SRE_Match object; span=(22, 23), match='4'>>> ws:None [6, 1 -> 6, 2]
                    Newline+
                        Newline+ <<23, 24>> ws:None [6, 2 -> 7, 1]

            [Lower Include Statement, Number Include Statement] / [Number Statement]
                Number Statement
                    Number
                        Number <<Regex: <_sre.SRE_Match object; span=(24, 25), match='5'>>> ws:None [7, 1 -> 7, 2]
                    Newline+
                        Newline+ <<25, 26>> ws:None [7, 2 -> 8, 1]
            """,
        )

        assert this_parse_mock.method_calls == []
