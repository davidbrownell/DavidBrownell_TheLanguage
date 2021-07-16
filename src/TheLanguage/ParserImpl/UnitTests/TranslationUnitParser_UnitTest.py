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
    from ..AST import Node
    from ..StatementDSL import CreateStatement, DynamicStatements, StatementItem

    from ..Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
    )

    from ..TranslationUnitParser import *

    from ..Statements.UnitTests import (
        CoroutineMock,
        CreateIterator,
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
    _upper_statement                        = CreateStatement(name="Upper Statement", item=[_upper_token, NewlineToken()])
    _lower_statement                        = CreateStatement(name="Lower Statement", item=[_lower_token, NewlineToken()])
    _number_statement                       = CreateStatement(name="Number Statement", item=[_number_token, NewlineToken()])

    _statements                             = DynamicStatementInfo(
        (_upper_statement, _lower_statement, _number_statement),
        (),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchStandard(self, parse_mock):
        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Upper Statement, Lower Statement, Number Statement}
                        Upper Statement
                            Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                Dynamic Statements
                    {Upper Statement, Lower Statement, Number Statement}
                        Lower Statement
                            Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                Dynamic Statements
                    {Upper Statement, Lower Statement, Number Statement}
                        Number Statement
                            Number <<Regex: <_sre.SRE_Match object; span=(8, 13), match='33333'>>> ws:None [3, 1 -> 3, 6]
                            Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) OnStatementCompleteAsync, Upper, 0, 3
                Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
            1) OnStatementCompleteAsync, Newline+, 3, 4
                Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            2) OnStatementCompleteAsync, Upper Statement, 0, 4
                Upper Statement
                    Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            3) OnStatementCompleteAsync, {Upper Statement, Lower Statement, Number Statement}, 0, 4
                {Upper Statement, Lower Statement, Number Statement}
                    Upper Statement
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            4) OnStatementCompleteAsync, Dynamic Statements, 0, 4
                Dynamic Statements
                    {Upper Statement, Lower Statement, Number Statement}
                        Upper Statement
                            Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            5) OnStatementCompleteAsync, Lower, 4, 7
                Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
            6) OnStatementCompleteAsync, Newline+, 7, 8
                Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            7) OnStatementCompleteAsync, Lower Statement, 4, 8
                Lower Statement
                    Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                    Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            8) OnStatementCompleteAsync, {Upper Statement, Lower Statement, Number Statement}, 4, 8
                {Upper Statement, Lower Statement, Number Statement}
                    Lower Statement
                        Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                        Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            9) OnStatementCompleteAsync, Dynamic Statements, 4, 8
                Dynamic Statements
                    {Upper Statement, Lower Statement, Number Statement}
                        Lower Statement
                            Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            10) OnStatementCompleteAsync, Number, 8, 13
                Number <<Regex: <_sre.SRE_Match object; span=(8, 13), match='33333'>>> ws:None [3, 1 -> 3, 6]
            11) OnStatementCompleteAsync, Newline+, 13, 14
                Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
            12) OnStatementCompleteAsync, Number Statement, 8, 14
                Number Statement
                    Number <<Regex: <_sre.SRE_Match object; span=(8, 13), match='33333'>>> ws:None [3, 1 -> 3, 6]
                    Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
            13) OnStatementCompleteAsync, {Upper Statement, Lower Statement, Number Statement}, 8, 14
                {Upper Statement, Lower Statement, Number Statement}
                    Number Statement
                        Number <<Regex: <_sre.SRE_Match object; span=(8, 13), match='33333'>>> ws:None [3, 1 -> 3, 6]
                        Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
            14) OnStatementCompleteAsync, Dynamic Statements, 8, 14
                Dynamic Statements
                    {Upper Statement, Lower Statement, Number Statement}
                        Number Statement
                            Number <<Regex: <_sre.SRE_Match object; span=(8, 13), match='33333'>>> ws:None [3, 1 -> 3, 6]
                            Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
            """,
        )


    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchReverse(self, parse_mock):
        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Upper Statement, Lower Statement, Number Statement}
                        Number Statement
                            Number <<Regex: <_sre.SRE_Match object; span=(0, 2), match='33'>>> ws:None [1, 1 -> 1, 3]
                            Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                Dynamic Statements
                    {Upper Statement, Lower Statement, Number Statement}
                        Lower Statement
                            Lower <<Regex: <_sre.SRE_Match object; span=(3, 14), match='twooooooooo'>>> ws:None [2, 1 -> 2, 12]
                            Newline+ <<14, 15>> ws:None [2, 12 -> 3, 1]
                Dynamic Statements
                    {Upper Statement, Lower Statement, Number Statement}
                        Upper Statement
                            Upper <<Regex: <_sre.SRE_Match object; span=(15, 18), match='ONE'>>> ws:None [3, 1 -> 3, 4]
                            Newline+ <<18, 19>> ws:None [3, 4 -> 4, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 15

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_EarlyTermination(self, parse_mock):
        parse_mock.OnStatementCompleteAsync = CoroutineMock(
            side_effect=[True, False],
        )

        result = await ParseAsync(
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

        assert result is None

# ----------------------------------------------------------------------
class TestIndentation(object):
    _statement                              = CreateStatement(
        name="Statement",
        item=[
            _upper_token,
            NewlineToken(),
            IndentToken(),
            _upper_token,
            _upper_token,
            NewlineToken(),
            DedentToken(),
        ],
    )

    _statements                             = DynamicStatementInfo(
        (_statement,),
        (),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Statement}
                        Statement
                            Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                            Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                            Upper <<Regex: <_sre.SRE_Match object; span=(8, 11), match='TWO'>>> ws:None [2, 5 -> 2, 8]
                            Upper <<Regex: <_sre.SRE_Match object; span=(17, 22), match='THREE'>>> ws:(11, 17) [2, 14 -> 2, 19]
                            Newline+ <<22, 23>> ws:None [2, 19 -> 3, 1]
                            Dedent <<>> ws:None [3, 1 -> 3, 1]
            """,
        )

# ----------------------------------------------------------------------
class TestNewStatements(object):
    _upper_statement                        = CreateStatement(name="Upper Statement", item=_upper_token)
    _lower_statement                        = CreateStatement(name="Lower Statement", item=[_lower_token, NewlineToken()])

    _statements                             = DynamicStatementInfo((_upper_statement,), ())
    _new_statements                         = DynamicStatementInfo((_lower_statement,), ())

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnStatementCompleteAsync = CoroutineMock(
            side_effect=[self._new_statements, True, True, True, True, True, True, True, True],
        )

        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Upper Statement}
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                Dynamic Statements
                    {Upper Statement} / {Lower Statement}
                        Lower Statement
                            Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                            Newline+ <<7, 8>> ws:None [1, 8 -> 2, 1]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            result = await ParseAsync(
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

            assert result is None, result

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 1
        assert ex.Column == 4

        assert ex.ToDebugString() == textwrap.dedent(
            """\
            The syntax is not recognized [1, 4]

            <Root>
                Dynamic Statements
                    {Upper Statement}
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                Dynamic Statements
                    {Upper Statement}
                        Upper
                            <No Children>
            """,
        )

# ----------------------------------------------------------------------
class TestNewScopedStatements(object):
    _upper_statement                        = CreateStatement(name="Upper Statement", item=_upper_token)
    _lower_statement                        = CreateStatement(name="Lower Statement", item=_lower_token)

    _newline_statement                      = CreateStatement(name="Newline Statement", item=NewlineToken())
    _indent_statement                       = CreateStatement(name="Indent Statement", item=IndentToken())
    _dedent_statement                       = CreateStatement(name="Dedent Statement", item=DedentToken())

    _statements                             = DynamicStatementInfo((_upper_statement, _newline_statement, _indent_statement, _dedent_statement), ())
    _new_statements                         = DynamicStatementInfo((_lower_statement,), ())

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=self._new_statements,
        )

        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement}
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement}
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement}
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement} / {Lower Statement}
                        Lower <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement} / {Lower Statement}
                        Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement} / {Lower Statement}
                        Dedent <<>> ws:None [3, 1 -> 3, 1]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=self._new_statements,
        )

        with pytest.raises(SyntaxInvalidError) as ex:
            result = await ParseAsync(
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

            assert result is None, result

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 4
        assert ex.Column == 1

        assert ex.ToDebugString() == textwrap.dedent(
            """\
            The syntax is not recognized [4, 1]

            <Root>
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement}
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement}
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement}
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement} / {Lower Statement}
                        Lower <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement} / {Lower Statement}
                        Newline+ <<11, 13>> ws:None [2, 8 -> 4, 1]
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement} / {Lower Statement}
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
                Dynamic Statements
                    {Upper Statement, Newline Statement, Indent Statement, Dedent Statement}
                        Upper
                            <No Children>
                        Newline+
                            <No Children>
                        Indent
                            <No Children>
                        Dedent
                            <No Children>
            """,
        )

# ----------------------------------------------------------------------
class TestNewScopedStatementsComplex(object):
    _upper_statement                        = CreateStatement(name="Upper Statement", item=_upper_token)
    _lower_statement                        = CreateStatement(name="Lower Statement", item=_lower_token)

    _newline_statement                      = CreateStatement(name="Newline Statement", item=NewlineToken())
    _dedent_statement                       = CreateStatement(name="Dedent Statement", item=DedentToken())

    _new_scope_statement                    = CreateStatement(
        name="New Scope",
        item=[
            _upper_token,
            RegexToken("Colon", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            DynamicStatements.Statements,
            DynamicStatements.Statements,
            DynamicStatements.Statements,
            DynamicStatements.Statements,
            DedentToken(),
        ],
    )

    _statements                             = DynamicStatementInfo((_newline_statement, _new_scope_statement), ())
    _new_statements                         = DynamicStatementInfo((_upper_statement, _lower_statement), ())

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=self._new_statements,
        )

        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Newline Statement, New Scope}
                        New Scope
                            Upper <<Regex: <_sre.SRE_Match object; span=(0, 8), match='NEWSCOPE'>>> ws:None [1, 1 -> 1, 9]
                            Colon <<Regex: <_sre.SRE_Match object; span=(8, 9), match=':'>>> ws:None [1, 9 -> 1, 10]
                            Newline+ <<9, 10>> ws:None [1, 10 -> 2, 1]
                            Indent <<10, 14, (4)>> ws:None [2, 1 -> 2, 5]
                            DynamicStatements.Statements
                                {Newline Statement, New Scope} / {Upper Statement, Lower Statement}
                                    Upper <<Regex: <_sre.SRE_Match object; span=(14, 19), match='UPPER'>>> ws:None [2, 5 -> 2, 10]
                            DynamicStatements.Statements
                                {Newline Statement, New Scope} / {Upper Statement, Lower Statement}
                                    Newline+ <<19, 21>> ws:None [2, 10 -> 4, 1]
                            DynamicStatements.Statements
                                {Newline Statement, New Scope} / {Upper Statement, Lower Statement}
                                    Lower <<Regex: <_sre.SRE_Match object; span=(25, 30), match='lower'>>> ws:None [4, 5 -> 4, 10]
                            DynamicStatements.Statements
                                {Newline Statement, New Scope} / {Upper Statement, Lower Statement}
                                    Newline+ <<30, 31>> ws:None [4, 10 -> 5, 1]
                            Dedent <<>> ws:None [5, 1 -> 5, 1]
            """,
        )

# ----------------------------------------------------------------------
class TestEmbeddedStatements(object):
    _upper_lower_statement                  = CreateStatement(name="Upper Lower Statement", item=[_upper_token, _lower_token, NewlineToken()])

    _uul_statement                          = CreateStatement(name="uul", item=[_upper_token, _upper_lower_statement])
    _lul_statement                          = CreateStatement(name="lul", item=[_lower_token, _upper_lower_statement])

    _statements                             = DynamicStatementInfo((_uul_statement, _lul_statement), ())

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {uul, lul}
                        uul
                            Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                            Upper Lower Statement
                                Upper <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:(3, 4) [1, 5 -> 1, 8]
                                Lower <<Regex: <_sre.SRE_Match object; span=(9, 14), match='three'>>> ws:(7, 9) [1, 10 -> 1, 15]
                                Newline+ <<14, 15>> ws:None [1, 15 -> 2, 1]
                Dynamic Statements
                    {uul, lul}
                        lul
                            Lower <<Regex: <_sre.SRE_Match object; span=(15, 19), match='four'>>> ws:None [2, 1 -> 2, 5]
                            Upper Lower Statement
                                Upper <<Regex: <_sre.SRE_Match object; span=(23, 27), match='FIVE'>>> ws:(19, 23) [2, 9 -> 2, 13]
                                Lower <<Regex: <_sre.SRE_Match object; span=(28, 31), match='six'>>> ws:(27, 28) [2, 14 -> 2, 17]
                                Newline+ <<31, 32>> ws:None [2, 17 -> 3, 1]
            """,
        )

# ----------------------------------------------------------------------
class TestVariedLengthMatches(object):
    _upper_statement                        = CreateStatement(name="Upper", item=[_upper_token, NewlineToken()])
    _lower_statement                        = CreateStatement(name="Lower", item=[_lower_token, _lower_token, NewlineToken()])
    _number_statement                       = CreateStatement(name="Number", item=[_number_token, _number_token, _number_token, NewlineToken()])

    _statements                             = DynamicStatementInfo(
        (_upper_statement, _lower_statement, _number_statement),
        (),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Upper, Lower, Number}
                        Lower
                            Lower <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                            Newline+ <<7, 8>> ws:None [1, 8 -> 2, 1]
                Dynamic Statements
                    {Upper, Lower, Number}
                        Number
                            Number <<Regex: <_sre.SRE_Match object; span=(8, 9), match='1'>>> ws:None [2, 1 -> 2, 2]
                            Number <<Regex: <_sre.SRE_Match object; span=(10, 11), match='2'>>> ws:(9, 10) [2, 3 -> 2, 4]
                            Number <<Regex: <_sre.SRE_Match object; span=(12, 13), match='3'>>> ws:(11, 12) [2, 5 -> 2, 6]
                            Newline+ <<13, 14>> ws:None [2, 6 -> 3, 1]
                Dynamic Statements
                    {Upper, Lower, Number}
                        Upper
                            Upper <<Regex: <_sre.SRE_Match object; span=(14, 18), match='WORD'>>> ws:None [3, 1 -> 3, 5]
                            Newline+ <<18, 19>> ws:None [3, 5 -> 4, 1]
            """,
        )

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_EmptyDynamicStatementInfo(parse_mock):
    parse_mock.OnStatementCompleteAsync = CoroutineMock(
        return_value=DynamicStatementInfo((), ()),
    )

    result = await ParseAsync(
        DynamicStatementInfo(
            (
                CreateStatement(name="Newline Statement", item=NewlineToken()),
                CreateStatement(name="Lower Statement", item=[_lower_token, NewlineToken()]),
            ),
            (),
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

    assert str(result) == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                {Newline Statement, Lower Statement}
                    Newline+ <<0, 1>> ws:None [1, 1 -> 2, 1]
            Dynamic Statements
                {Newline Statement, Lower Statement}
                    Lower Statement
                        Lower <<Regex: <_sre.SRE_Match object; span=(1, 5), match='word'>>> ws:None [2, 1 -> 2, 5]
                        Newline+ <<5, 6>> ws:None [2, 5 -> 3, 1]
        """,
    )

# ----------------------------------------------------------------------
class TestPreventParentTraversal(object):
    _upper_statement                        = CreateStatement(name="Upper Statement", item=[_upper_token, NewlineToken()])
    _lower_statement                        = CreateStatement(name="Lower Statement", item=[_lower_token, NewlineToken()])
    _indent_statement                       = CreateStatement(name="Indent Statement", item=IndentToken())
    _dedent_statement                       = CreateStatement(name="Dedent Statement", item=DedentToken())

    _statements                             = DynamicStatementInfo(
        (_upper_statement, _indent_statement, _dedent_statement),
        (),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async  def test_Match(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=DynamicStatementInfo(
                (self._lower_statement, self._dedent_statement),
                (),
                False,
            ),
        )

        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Upper Statement, Indent Statement, Dedent Statement}
                        Upper Statement
                            Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                Dynamic Statements
                    {Upper Statement, Indent Statement, Dedent Statement}
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                Dynamic Statements
                    {Lower Statement, Dedent Statement}
                        Lower Statement
                            Lower <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                            Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
                Dynamic Statements
                    {Lower Statement, Dedent Statement}
                        Lower Statement
                            Lower <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 5 -> 3, 10]
                            Newline+ <<21, 22>> ws:None [3, 10 -> 4, 1]
                Dynamic Statements
                    {Lower Statement, Dedent Statement}
                        Lower Statement
                            Lower <<Regex: <_sre.SRE_Match object; span=(26, 30), match='four'>>> ws:None [4, 5 -> 4, 9]
                            Newline+ <<30, 32>> ws:None [4, 9 -> 6, 1]
                Dynamic Statements
                    {Lower Statement, Dedent Statement}
                        Dedent <<>> ws:None [6, 1 -> 6, 1]
                Dynamic Statements
                    {Upper Statement, Indent Statement, Dedent Statement}
                        Upper Statement
                            Upper <<Regex: <_sre.SRE_Match object; span=(32, 36), match='FIVE'>>> ws:None [6, 1 -> 6, 5]
                            Newline+ <<36, 37>> ws:None [6, 5 -> 7, 1]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=DynamicStatementInfo(
                (self._lower_statement, self._dedent_statement),
                (),
                False,
            ),
        )

        with pytest.raises(SyntaxInvalidError) as ex:
            result = await ParseAsync(
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

            assert result is None, result

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 6
        assert ex.Column == 1

        assert ex.ToDebugString() == textwrap.dedent(
            """\
            The syntax is not recognized [6, 1]

            <Root>
                Dynamic Statements
                    {Upper Statement, Indent Statement, Dedent Statement}
                        Upper Statement
                            Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                Dynamic Statements
                    {Upper Statement, Indent Statement, Dedent Statement}
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                Dynamic Statements
                    {Lower Statement, Dedent Statement}
                        Lower Statement
                            Lower <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                            Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
                Dynamic Statements
                    {Lower Statement, Dedent Statement}
                        Lower Statement
                            Lower <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 5 -> 3, 10]
                            Newline+ <<21, 22>> ws:None [3, 10 -> 4, 1]
                Dynamic Statements
                    {Lower Statement, Dedent Statement}
                        Lower Statement
                            Lower <<Regex: <_sre.SRE_Match object; span=(26, 30), match='four'>>> ws:None [4, 5 -> 4, 9]
                            Newline+ <<30, 32>> ws:None [4, 9 -> 6, 1]
                Dynamic Statements
                    {Lower Statement, Dedent Statement}
                        Dedent <<>> ws:None [6, 1 -> 6, 1]
                Dynamic Statements
                    {Upper Statement, Indent Statement, Dedent Statement}
                        Upper Statement
                            Upper
                                <No Children>
                        Indent
                            <No Children>
                        Dedent
                            <No Children>
            """,
        )

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_InvalidDynamicTraversalError(parse_mock):
    parse_mock.OnStatementCompleteAsync = CoroutineMock(
        return_value=DynamicStatementInfo(
            (CreateStatement(name="Newline", item=NewlineToken()),),
            (),
            False,
        ),
    )

    with pytest.raises(InvalidDynamicTraversalError) as ex:
        result = await ParseAsync(
            DynamicStatementInfo(
                (CreateStatement(name="Newline", item=NewlineToken()),),
                (),
            ),
            CreateIterator(
                textwrap.dedent(
                    """\



                    """,
                ),
            ),
            parse_mock,
        )

        assert result is None, result

    ex = ex.value

    assert str(ex) == "Dynamic statements that prohibit parent traversal should never be applied over other dynamic statements within the same lexical scope. You should make these dynamic statements the first ones applied in this lexical scope."
    assert ex.Line == 4
    assert ex.Column == 1

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_DynamicExpressions(parse_mock):
    result = await ParseAsync(
        DynamicStatementInfo(
            (
                CreateStatement(
                    name="Statement",
                    item=[
                        _upper_token,
                        DynamicStatements.Expressions,
                        _lower_token,
                        NewlineToken(),
                    ],
                ),
            ),
            (
                CreateStatement(
                    name="Expression",
                    item=_number_token,
                ),
            ),
        ),
        CreateIterator("WORD 1234 lower"),
        parse_mock,
    )

    assert str(result) == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                {Statement}
                    Statement
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 4), match='WORD'>>> ws:None [1, 1 -> 1, 5]
                        DynamicStatements.Expressions
                            {Expression}
                                Number <<Regex: <_sre.SRE_Match object; span=(5, 9), match='1234'>>> ws:(4, 5) [1, 6 -> 1, 10]
                        Lower <<Regex: <_sre.SRE_Match object; span=(10, 15), match='lower'>>> ws:(9, 10) [1, 11 -> 1, 16]
                        Newline+ <<15, 16>> ws:None [1, 16 -> 2, 1]
        """,
    )

# ----------------------------------------------------------------------
class TestCatastrophicInclude(object):
    _include_statement                      = CreateStatement(
        name="Include Statement",
        item=[
            RegexToken("include", re.compile(r"include")),
            _upper_token,
            NewlineToken(),
        ],
    )

    # Both of these statements start with an include, but the
    # dynamic statements allowed will be based on the included
    # value.
    _lower_include_statement                = CreateStatement(
        name="Lower Include Statement",
        item=[
            _include_statement,
            DynamicStatements.Statements,
            DynamicStatements.Statements,
        ],
    )

    _number_include_statement               = CreateStatement(
        name="Number Include Statement",
        item=[
            _include_statement,
            DynamicStatements.Statements,
            DynamicStatements.Statements,
            DynamicStatements.Statements,
        ],
    )

    _lower_statement                        = CreateStatement(
        name="Lower Statement",
        item=[
            _lower_token,
            NewlineToken(),
        ],
    )

    _number_statement                       = CreateStatement(
        name="Number Statement",
        item=[
            _number_token,
            NewlineToken(),
        ],
    )

    _statements                             = DynamicStatementInfo(
        (_lower_include_statement, _number_include_statement),
        (),
    )

    _lower_dynamic_statements               = DynamicStatementInfo(
        (_lower_statement,),
        (),
        True,
        # "Lower Dynamic Statements",
    )

    _number_dynamic_statements              = DynamicStatementInfo(
        (_number_statement,),
        (),
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
            node: Node,
            iter_before: Statement.NormalizedIterator,
            iter_after: Statement.NormalizedIterator,
        ):
            if statement == cls._include_statement:
                value = node.Children[1].Value.Match.group("value")

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
    @pytest.mark.asyncio
    async def test_Lower(self, this_parse_mock):
        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Lower Include Statement, Number Include Statement}
                        Lower Include Statement
                            Include Statement
                                include <<Regex: <_sre.SRE_Match object; span=(0, 7), match='include'>>> ws:None [1, 1 -> 1, 8]
                                Upper <<Regex: <_sre.SRE_Match object; span=(8, 13), match='LOWER'>>> ws:(7, 8) [1, 9 -> 1, 14]
                                Newline+ <<13, 14>> ws:None [1, 14 -> 2, 1]
                            DynamicStatements.Statements
                                {Lower Include Statement, Number Include Statement} / {Lower Statement}
                                    Lower Statement
                                        Lower <<Regex: <_sre.SRE_Match object; span=(14, 17), match='one'>>> ws:None [2, 1 -> 2, 4]
                                        Newline+ <<17, 18>> ws:None [2, 4 -> 3, 1]
                            DynamicStatements.Statements
                                {Lower Include Statement, Number Include Statement} / {Lower Statement}
                                    Lower Statement
                                        Lower <<Regex: <_sre.SRE_Match object; span=(18, 21), match='two'>>> ws:None [3, 1 -> 3, 4]
                                        Newline+ <<21, 22>> ws:None [3, 4 -> 4, 1]
            """,
        )

        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_LowerAdditionalItem(self, this_parse_mock):
        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Lower Include Statement, Number Include Statement}
                        Number Include Statement
                            Include Statement
                                include <<Regex: <_sre.SRE_Match object; span=(0, 7), match='include'>>> ws:None [1, 1 -> 1, 8]
                                Upper <<Regex: <_sre.SRE_Match object; span=(8, 13), match='LOWER'>>> ws:(7, 8) [1, 9 -> 1, 14]
                                Newline+ <<13, 14>> ws:None [1, 14 -> 2, 1]
                            DynamicStatements.Statements
                                {Lower Include Statement, Number Include Statement} / {Lower Statement}
                                    Lower Statement
                                        Lower <<Regex: <_sre.SRE_Match object; span=(14, 17), match='one'>>> ws:None [2, 1 -> 2, 4]
                                        Newline+ <<17, 18>> ws:None [2, 4 -> 3, 1]
                            DynamicStatements.Statements
                                {Lower Include Statement, Number Include Statement} / {Lower Statement}
                                    Lower Statement
                                        Lower <<Regex: <_sre.SRE_Match object; span=(18, 21), match='two'>>> ws:None [3, 1 -> 3, 4]
                                        Newline+ <<21, 23>> ws:None [3, 4 -> 5, 1]
                            DynamicStatements.Statements
                                {Lower Include Statement, Number Include Statement} / {Lower Statement}
                                    Lower Statement
                                        Lower <<Regex: <_sre.SRE_Match object; span=(23, 28), match='three'>>> ws:None [5, 1 -> 5, 6]
                                        Newline+ <<28, 29>> ws:None [5, 6 -> 6, 1]
                Dynamic Statements
                    {Lower Include Statement, Number Include Statement} / {Lower Statement}
                        Lower Statement
                            Lower <<Regex: <_sre.SRE_Match object; span=(29, 33), match='four'>>> ws:None [6, 1 -> 6, 5]
                            Newline+ <<33, 34>> ws:None [6, 5 -> 7, 1]
            """,
        )

        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Number(self, this_parse_mock):
        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Lower Include Statement, Number Include Statement}
                        Number Include Statement
                            Include Statement
                                include <<Regex: <_sre.SRE_Match object; span=(0, 7), match='include'>>> ws:None [1, 1 -> 1, 8]
                                Upper <<Regex: <_sre.SRE_Match object; span=(8, 14), match='NUMBER'>>> ws:(7, 8) [1, 9 -> 1, 15]
                                Newline+ <<14, 15>> ws:None [1, 15 -> 2, 1]
                            DynamicStatements.Statements
                                {Lower Include Statement, Number Include Statement} / {Number Statement}
                                    Number Statement
                                        Number <<Regex: <_sre.SRE_Match object; span=(15, 16), match='1'>>> ws:None [2, 1 -> 2, 2]
                                        Newline+ <<16, 17>> ws:None [2, 2 -> 3, 1]
                            DynamicStatements.Statements
                                {Lower Include Statement, Number Include Statement} / {Number Statement}
                                    Number Statement
                                        Number <<Regex: <_sre.SRE_Match object; span=(17, 18), match='2'>>> ws:None [3, 1 -> 3, 2]
                                        Newline+ <<18, 19>> ws:None [3, 2 -> 4, 1]
                            DynamicStatements.Statements
                                {Lower Include Statement, Number Include Statement} / {Number Statement}
                                    Number Statement
                                        Number <<Regex: <_sre.SRE_Match object; span=(19, 20), match='3'>>> ws:None [4, 1 -> 4, 2]
                                        Newline+ <<20, 21>> ws:None [4, 2 -> 5, 1]
            """,
        )

        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NumberAdditionalItems(self, this_parse_mock):
        result = await ParseAsync(
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

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    {Lower Include Statement, Number Include Statement}
                        Number Include Statement
                            Include Statement
                                include <<Regex: <_sre.SRE_Match object; span=(0, 7), match='include'>>> ws:None [1, 1 -> 1, 8]
                                Upper <<Regex: <_sre.SRE_Match object; span=(8, 14), match='NUMBER'>>> ws:(7, 8) [1, 9 -> 1, 15]
                                Newline+ <<14, 15>> ws:None [1, 15 -> 2, 1]
                            DynamicStatements.Statements
                                {Lower Include Statement, Number Include Statement} / {Number Statement}
                                    Number Statement
                                        Number <<Regex: <_sre.SRE_Match object; span=(15, 16), match='1'>>> ws:None [2, 1 -> 2, 2]
                                        Newline+ <<16, 17>> ws:None [2, 2 -> 3, 1]
                            DynamicStatements.Statements
                                {Lower Include Statement, Number Include Statement} / {Number Statement}
                                    Number Statement
                                        Number <<Regex: <_sre.SRE_Match object; span=(17, 18), match='2'>>> ws:None [3, 1 -> 3, 2]
                                        Newline+ <<18, 19>> ws:None [3, 2 -> 4, 1]
                            DynamicStatements.Statements
                                {Lower Include Statement, Number Include Statement} / {Number Statement}
                                    Number Statement
                                        Number <<Regex: <_sre.SRE_Match object; span=(19, 20), match='3'>>> ws:None [4, 1 -> 4, 2]
                                        Newline+ <<20, 22>> ws:None [4, 2 -> 6, 1]
                Dynamic Statements
                    {Lower Include Statement, Number Include Statement} / {Number Statement}
                        Number Statement
                            Number <<Regex: <_sre.SRE_Match object; span=(22, 23), match='4'>>> ws:None [6, 1 -> 6, 2]
                            Newline+ <<23, 24>> ws:None [6, 2 -> 7, 1]
                Dynamic Statements
                    {Lower Include Statement, Number Include Statement} / {Number Statement}
                        Number Statement
                            Number <<Regex: <_sre.SRE_Match object; span=(24, 25), match='5'>>> ws:None [7, 1 -> 7, 2]
                            Newline+ <<25, 26>> ws:None [7, 2 -> 8, 1]
            """,
        )

        assert this_parse_mock.method_calls == []
