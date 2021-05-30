# ----------------------------------------------------------------------
# |
# |  StatementsParser_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-11 06:38:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for StatementsParser.py"""

import os
import re
import textwrap

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from unittest.mock import Mock

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..StatementsParser import *
    from ..Normalize import Normalize
    from ..NormalizedIterator import NormalizedIterator
    from ..Statement import Statement

    from ..Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
    )


# ----------------------------------------------------------------------
@contextmanager
def CreateObserver():
    with ThreadPoolExecutor() as executor:
        # ----------------------------------------------------------------------
        class MyObserver(Observer):
            # ----------------------------------------------------------------------
            def __init__(self):
                self.mock = Mock()

            # ----------------------------------------------------------------------
            def VerifyCallArgs(self, index, statement, results, before_line, before_col, after_line, after_col):
                callback_args = self.mock.call_args_list[index][0]

                assert callback_args[0] == results
                assert callback_args[0].Statement == statement
                assert callback_args[1].Line == before_line
                assert callback_args[1].Column == before_col
                assert callback_args[2].Line == after_line
                assert callback_args[2].Column == after_col

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def Enqueue(funcs):
                return [executor.submit(func) for func in funcs]

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def OnIndent(statement, results):
                pass

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def OnDedent(statement, results):
                pass

            # ----------------------------------------------------------------------
            @Interface.override
            def OnStatementComplete(self, result, iter_before, iter_after):
                return self.mock(result, iter_before, iter_after)

        # ----------------------------------------------------------------------

        yield MyObserver()

# ----------------------------------------------------------------------
class TestSimple(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number", re.compile(r"(?P<value>[0-9]+)"))

    _upper_statement                        = Statement("Upper Statement", _upper_token, NewlineToken())
    _lower_statement                        = Statement("Lower Statement", _lower_token, NewlineToken())
    _number_statement                       = Statement("Number Statement", _number_token, NewlineToken())

    _statements                             = DynamicStatementInfo(
        [_upper_statement, _lower_statement, _number_statement],
        [],
    )

    # ----------------------------------------------------------------------
    def test_MatchStandard(self):
        with CreateObserver() as observer:
            results = Parse(
                self._statements,
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            ONE
                            two
                            33333
                            """,
                        ),
                    ),
                ),
                observer,
            )

            # Verify the results
            assert len(results) == 3

            # Line 1
            assert str(results[0]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Lower Statement, Number Statement]
                    Upper Statement
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 4]
                        Newline+ <<3, 4>> ws:None [2, 1]
                """,
            )

            # Line 2
            assert str(results[1]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Lower Statement, Number Statement]
                    Lower Statement
                        Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 4]
                        Newline+ <<7, 8>> ws:None [3, 1]
                """,
            )

            # Line 3
            assert str(results[2]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Lower Statement, Number Statement]
                    Number Statement
                        Number <<Regex: <_sre.SRE_Match object; span=(8, 13), match='33333'>>> ws:None [3, 6]
                        Newline+ <<13, 14>> ws:None [4, 1]
                """,
            )

            # Verify the callback
            assert observer.mock.call_count == 3

            observer.VerifyCallArgs(0, self._upper_statement, results[0].Results[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._lower_statement, results[1].Results[0], 2, 1, 3, 1)
            observer.VerifyCallArgs(2, self._number_statement, results[2].Results[0], 3, 1, 4, 1)

    # ----------------------------------------------------------------------
    def test_MatchReverse(self):
        with CreateObserver() as observer:
            results = Parse(
                self._statements,
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            33
                            twoooooooo
                            ONE
                            """,
                        ),
                    ),
                ),
                observer,
            )

            # Verify the results
            assert len(results) == 3

            # Line 1
            assert str(results[0]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Lower Statement, Number Statement]
                    Number Statement
                        Number <<Regex: <_sre.SRE_Match object; span=(0, 2), match='33'>>> ws:None [1, 3]
                        Newline+ <<2, 3>> ws:None [2, 1]
                """,
            )

            # Line 2
            assert str(results[1]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Lower Statement, Number Statement]
                    Lower Statement
                        Lower <<Regex: <_sre.SRE_Match object; span=(3, 13), match='twoooooooo'>>> ws:None [2, 11]
                        Newline+ <<13, 14>> ws:None [3, 1]
                """,
            )

            # Line 3
            assert str(results[2]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Lower Statement, Number Statement]
                    Upper Statement
                        Upper <<Regex: <_sre.SRE_Match object; span=(14, 17), match='ONE'>>> ws:None [3, 4]
                        Newline+ <<17, 18>> ws:None [4, 1]
                """,
            )

            # Verify the callback
            assert observer.mock.call_count == 3

            observer.VerifyCallArgs(0, self._number_statement, results[0].Results[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._lower_statement, results[1].Results[0], 2, 1, 3, 1)
            observer.VerifyCallArgs(2, self._upper_statement, results[2].Results[0],  3, 1, 4, 1)

    # ----------------------------------------------------------------------
    def test_MatchSame(self):
        with CreateObserver() as observer:
            results = Parse(
                self._statements,
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            1
                            22
                            333
                            """,
                        ),
                    ),
                ),
                observer,
            )

            # Verify the results
            assert len(results) == 3

            # Line 1
            assert str(results[0]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Lower Statement, Number Statement]
                    Number Statement
                        Number <<Regex: <_sre.SRE_Match object; span=(0, 1), match='1'>>> ws:None [1, 2]
                        Newline+ <<1, 2>> ws:None [2, 1]
                """,
            )

            # Line 2
            assert str(results[1]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Lower Statement, Number Statement]
                    Number Statement
                        Number <<Regex: <_sre.SRE_Match object; span=(2, 4), match='22'>>> ws:None [2, 3]
                        Newline+ <<4, 5>> ws:None [3, 1]
                """,
            )

            # Line 3
            assert str(results[2]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Lower Statement, Number Statement]
                    Number Statement
                        Number <<Regex: <_sre.SRE_Match object; span=(5, 8), match='333'>>> ws:None [3, 4]
                        Newline+ <<8, 9>> ws:None [4, 1]
                """,
            )

            # Verify the callback
            assert observer.mock.call_count == 3

            observer.VerifyCallArgs(0, self._number_statement, results[0].Results[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._number_statement, results[1].Results[0], 2, 1, 3, 1)
            observer.VerifyCallArgs(2, self._number_statement, results[2].Results[0], 3, 1, 4, 1)

    # ----------------------------------------------------------------------
    def test_EarlyTermination(self):
        with CreateObserver() as observer:
            observer.mock.side_effect = [
                True,
                False,
            ]

            results = Parse(
                self._statements,
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            1
                            22
                            333
                            """,
                        ),
                    ),
                ),
                observer,
            )

            assert results is None

            # Verify the callback
            assert observer.mock.call_count == 2

            # Note that we can't compare the 2nd arg, as we don't have easy access to the Node
            # to compare it with
            assert observer.mock.call_args_list[0][0][0].Statement == self._number_statement
            assert observer.mock.call_args_list[0][0][1].Line == 1
            assert observer.mock.call_args_list[0][0][1].Column == 1
            assert observer.mock.call_args_list[0][0][2].Line == 2
            assert observer.mock.call_args_list[0][0][2].Column == 1

            assert observer.mock.call_args_list[1][0][0].Statement == self._number_statement
            assert observer.mock.call_args_list[1][0][1].Line == 2
            assert observer.mock.call_args_list[1][0][1].Column == 1
            assert observer.mock.call_args_list[1][0][2].Line == 3
            assert observer.mock.call_args_list[1][0][2].Column == 1

# ----------------------------------------------------------------------
class TestIndentation(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _statement                              = Statement(
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
        [ _statement ],
        [],
    )

    # ----------------------------------------------------------------------
    def test_Match(self):
        with CreateObserver() as observer:
            results = Parse(
                self._statements,
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            ONE
                                TWO     THREE
                            """,
                        ),
                    ),
                ),
                observer,
            )

            # Verify the results
            assert len(results) == 1

            assert str(results[0]) == textwrap.dedent(
                """\
                Or: [Statement]
                    Statement
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 4]
                        Newline+ <<3, 4>> ws:None [2, 1]
                        Indent <<4, 8, (4)>> ws:None [2, 5]
                        Upper <<Regex: <_sre.SRE_Match object; span=(8, 11), match='TWO'>>> ws:None [2, 8]
                        Upper <<Regex: <_sre.SRE_Match object; span=(16, 21), match='THREE'>>> ws:(11, 16) [2, 18]
                        Newline+ <<21, 22>> ws:None [3, 1]
                        Dedent <<>> ws:None [3, 1]
                """,
            )

            # Verify the Callbacks
            assert observer.mock.call_count == 1

            observer.VerifyCallArgs(0, self._statement, results[0].Results[0], 1, 1, 3, 1)

# ----------------------------------------------------------------------
class TestNewStatements(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))

    _upper_statement                        = Statement("Upper Statement", _upper_token)
    _lower_statement                        = Statement("Lower Statement", _lower_token, NewlineToken())

    _statements                             = DynamicStatementInfo([_upper_statement], [])
    _new_statements                         = DynamicStatementInfo([_lower_statement], [])

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        with CreateObserver() as observer:
            # The callback isn't returning any new statements; therefore an
            # error will be generated when attempting to parse the lowercase
            # token.
            with pytest.raises(SyntaxInvalidError) as ex:
                results = Parse(
                        self._statements,
                        NormalizedIterator(
                            Normalize(
                                textwrap.dedent(
                                    """\
                                    ONE two
                                    """,
                                ),
                            ),
                        ),
                        observer,
                    )

            ex = ex.value

            # Validate
            assert ex.Line == 1
            assert ex.Column == 4
            assert str(ex) == "The syntax is not recognized"

            assert len(ex.PotentialStatements) == 1
            key = tuple(self._statements.statements)
            assert key in ex.PotentialStatements

            assert len(ex.PotentialStatements[key]) == 1
            assert ex.PotentialStatements[key][0].Results == []

    # ----------------------------------------------------------------------
    def test_Match(self):
        with CreateObserver() as observer:
            observer.mock.side_effect = [
                self._new_statements,
                True,
            ]

            results = Parse(
                self._statements,
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            ONE two
                            """,
                        ),
                    ),
                ),
                observer,
            )

            # Verify the results
            assert len(results) == 2

            assert str(results[0]) == textwrap.dedent(
                """\
                Or: [Upper Statement]
                    Upper Statement
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 4]
                """,
            )

            assert str(results[1]) == textwrap.dedent(
                """\
                Or: [Lower Statement, Upper Statement]
                    Lower Statement
                        Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
                        Newline+ <<7, 8>> ws:None [2, 1]
                """,
            )

            # Verify the callbacks
            assert observer.mock.call_count == 2

            observer.VerifyCallArgs(0, self._upper_statement, results[0].Results[0], 1, 1, 1, 4)
            observer.VerifyCallArgs(1, self._lower_statement, results[1].Results[0], 1, 4, 2, 1)

# ----------------------------------------------------------------------
class TestNewScopedStatements(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))

    _upper_statement                        = Statement("Upper Statement", _upper_token)
    _lower_statement                        = Statement("Lower Statement", _lower_token)

    _newline_statement                      = Statement("Newline Statement", NewlineToken())
    _indent_statement                       = Statement("Indent Statement", IndentToken())
    _dedent_statement                       = Statement("Dedent Statement", DedentToken())

    _statements                             = DynamicStatementInfo([_upper_statement, _newline_statement, _indent_statement, _dedent_statement], [])
    _new_statements                         = DynamicStatementInfo([_lower_statement], [])

    # ----------------------------------------------------------------------
    def test_Match(self):
        with CreateObserver() as observer:
            observer.mock.side_effect = [
                True,                       # ONE
                True,                       # Newline
                self._new_statements,       # Indent
                True,                       # two
                True,                       # Newline
                True,                       # Dedent
            ]

            results = Parse(
                self._statements,
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            ONE
                                two
                            """,
                        ),
                    ),
                ),
                observer,
            )

            # Verify the results
            assert len(results) == 6

            assert str(results[0]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                    Upper Statement
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 4]
                """,
            )

            assert str(results[1]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                    Newline Statement
                        Newline+ <<3, 4>> ws:None [2, 1]
                """,
            )

            assert str(results[2]) == textwrap.dedent(
                """\
                Or: [Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                    Indent Statement
                        Indent <<4, 8, (4)>> ws:None [2, 5]
                """,
            )

            assert str(results[3]) == textwrap.dedent(
                """\
                Or: [Lower Statement, Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                    Lower Statement
                        Lower <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 8]
                """,
            )

            assert str(results[4]) == textwrap.dedent(
                """\
                Or: [Lower Statement, Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                    Newline Statement
                        Newline+ <<11, 12>> ws:None [3, 1]
                """,
            )

            assert str(results[5]) == textwrap.dedent(
                """\
                Or: [Lower Statement, Upper Statement, Newline Statement, Indent Statement, Dedent Statement]
                    Dedent Statement
                        Dedent <<>> ws:None [3, 1]
                """,
            )

            # Verify the callbacks
            assert observer.mock.call_count == 6

            observer.VerifyCallArgs(0, self._upper_statement, results[0].Results[0], 1, 1, 1, 4)
            observer.VerifyCallArgs(1, self._newline_statement, results[1].Results[0], 1, 4, 2, 1)
            observer.VerifyCallArgs(2, self._indent_statement, results[2].Results[0], 2, 1, 2, 5)
            observer.VerifyCallArgs(3, self._lower_statement, results[3].Results[0], 2, 5, 2, 8)
            observer.VerifyCallArgs(4, self._newline_statement, results[4].Results[0], 2, 8, 3, 1)
            observer.VerifyCallArgs(5, self._dedent_statement, results[5].Results[0], 3, 1, 3, 1)

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        with CreateObserver() as observer:
            observer.mock.side_effect = [
                True,                       # ONE
                True,                       # Newline
                self._new_statements,       # Indent
                True,                       # two
                True,                       # Newline
                True,                       # Dedent
            ]

            with pytest.raises(SyntaxInvalidError) as ex:
                results = Parse(
                    self._statements,
                    NormalizedIterator(
                        Normalize(
                            textwrap.dedent(
                                """\
                                ONE
                                    two

                                no_match_as_lower_is_out_of_scope
                                """,
                            ),
                        ),
                    ),
                    observer,
                )

            ex = ex.value

            # Validate
            assert ex.Line == 4
            assert ex.Column == 1
            assert str(ex) == "The syntax is not recognized"

            assert len(ex.PotentialStatements) == 1
            key = tuple(self._statements.statements)
            assert key in ex.PotentialStatements

            potentials = ex.PotentialStatements[key]

            assert len(potentials) == 4

            assert str(potentials[0]) == textwrap.dedent(
                """\
                Upper Statement
                    <No results>
                """,
            )

            assert str(potentials[1]) == textwrap.dedent(
                """\
                Newline Statement
                    <No results>
                """,
            )

            assert str(potentials[2]) == textwrap.dedent(
                """\
                Indent Statement
                    <No results>
                """,
            )

            assert str(potentials[3]) == textwrap.dedent(
                """\
                Dedent Statement
                    <No results>
                """,
            )

# ----------------------------------------------------------------------
class TestEmbeddedStatements(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))

    _upper_lower_statement                  = Statement("Upper Lower Statement", _upper_token, _lower_token, NewlineToken())

    _uul_statement                          = Statement("uul", _upper_token, _upper_lower_statement)
    _lul_statement                          = Statement("lul", _lower_token, _upper_lower_statement)

    _statements                             = DynamicStatementInfo([_uul_statement, _lul_statement], [])

    # ----------------------------------------------------------------------
    def test_Match(self):
        with CreateObserver() as observer:
            results = Parse(
                self._statements,
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            ONE TWO  three
                            four    FIVE six
                            """,
                        ),
                    ),
                ),
                observer,
            )

            # Verify the results
            assert len(results) == 2

            assert str(results[0]) == textwrap.dedent(
                """\
                Or: [uul, lul]
                    uul
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 4]
                        Upper Lower Statement
                            Upper <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:(3, 4) [1, 8]
                            Lower <<Regex: <_sre.SRE_Match object; span=(9, 14), match='three'>>> ws:(7, 9) [1, 15]
                            Newline+ <<14, 15>> ws:None [2, 1]
                """,
            )

            assert str(results[1]) == textwrap.dedent(
                """\
                Or: [uul, lul]
                    lul
                        Lower <<Regex: <_sre.SRE_Match object; span=(15, 19), match='four'>>> ws:None [2, 5]
                        Upper Lower Statement
                            Upper <<Regex: <_sre.SRE_Match object; span=(23, 27), match='FIVE'>>> ws:(19, 23) [2, 13]
                            Lower <<Regex: <_sre.SRE_Match object; span=(28, 31), match='six'>>> ws:(27, 28) [2, 17]
                            Newline+ <<31, 32>> ws:None [3, 1]
                """,
            )

            # Verify the callbacks
            assert observer.mock.call_count == 4

            observer.VerifyCallArgs(0, self._upper_lower_statement, results[0].Results[0].Results[1], 1, 4, 2, 1)
            observer.VerifyCallArgs(1, self._uul_statement, results[0].Results[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(2, self._upper_lower_statement, results[1].Results[0].Results[1], 2, 5, 3, 1)
            observer.VerifyCallArgs(3, self._lul_statement, results[1].Results[0], 2, 1, 3, 1)

# ----------------------------------------------------------------------
class TestNoMatchError(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number", re.compile(r"(?P<value>[0-9]+)"))

    _upper_statement                        = Statement("Upper", _upper_token, _number_token)
    _lower_statement                        = Statement("Lower", _upper_token, _lower_token)

    _statements                             = DynamicStatementInfo([_upper_statement, _lower_statement], [])

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        with CreateObserver() as observer:
            with pytest.raises(SyntaxInvalidError) as ex:
                Parse(
                    self._statements,
                    NormalizedIterator(
                        Normalize(
                            textwrap.dedent(
                                """\
                                ONE INVALID
                                """,
                            ),
                        ),
                    ),
                    observer,
                )

            ex = ex.value

            # Validate
            assert ex.Line == 1
            assert ex.Column == 4
            assert str(ex) == "The syntax is not recognized"

            assert len(ex.PotentialStatements) == 1
            key = tuple(self._statements.statements)
            assert key in ex.PotentialStatements

            potentials = ex.PotentialStatements[key]

            assert len(potentials) == 2

            assert str(potentials[0]) == textwrap.dedent(
                """\
                Upper
                    Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 4]
                """,
            )

            assert str(potentials[1]) == textwrap.dedent(
                """\
                Lower
                    Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 4]
                """,
            )

# ----------------------------------------------------------------------
class TestVariedLengthMatches(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number", re.compile(r"(?P<value>[0-9]+)"))

    _upper_statement                        = Statement("Upper", _upper_token, NewlineToken())
    _lower_statement                        = Statement("Lower", _lower_token, _lower_token, NewlineToken())
    _number_statement                       = Statement("Number", _number_token, _number_token, _number_token, NewlineToken())

    _statements                             = DynamicStatementInfo(
        [_upper_statement, _lower_statement, _number_statement],
        [],
    )

    # ----------------------------------------------------------------------
    def test_Match(self):
        with CreateObserver() as observer:
            results = Parse(
                self._statements,
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            one two
                            1 2 3
                            WORD
                            """,
                        ),
                    ),
                ),
                observer,
            )

            assert len(results) == 3

            assert str(results[0]) == textwrap.dedent(
                """\
                Or: [Upper, Lower, Number]
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 4]
                        Lower <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 8]
                        Newline+ <<7, 8>> ws:None [2, 1]
                """,
            )

            assert str(results[1]) == textwrap.dedent(
                """\
                Or: [Upper, Lower, Number]
                    Number
                        Number <<Regex: <_sre.SRE_Match object; span=(8, 9), match='1'>>> ws:None [2, 2]
                        Number <<Regex: <_sre.SRE_Match object; span=(10, 11), match='2'>>> ws:(9, 10) [2, 4]
                        Number <<Regex: <_sre.SRE_Match object; span=(12, 13), match='3'>>> ws:(11, 12) [2, 6]
                        Newline+ <<13, 14>> ws:None [3, 1]
                """,
            )

            assert str(results[2]) == textwrap.dedent(
                """\
                Or: [Upper, Lower, Number]
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(14, 18), match='WORD'>>> ws:None [3, 5]
                        Newline+ <<18, 19>> ws:None [4, 1]
                """,
            )

# ----------------------------------------------------------------------
def test_EmptyDynamicStatementInfo():
    with CreateObserver() as observer:
        observer.mock.side_effect = [
            DynamicStatementInfo([], []),
        ]

        results = Parse(
            DynamicStatementInfo(
                [Statement("Newline", NewlineToken())],
                [],
            ),
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\

                        """,
                    ),
                ),
            ),
            observer,
        )

        assert len(results) == 1

        assert str(results[0]) == textwrap.dedent(
            """\
            Or: [Newline]
                Newline
                    Newline+ <<0, 1>> ws:None [2, 1]
            """,
        )

# ----------------------------------------------------------------------
class TestPreventParentTraversal(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))

    _upper_statement                        = Statement("Upper", _upper_token, NewlineToken())
    _lower_statement                        = Statement("Lower", _lower_token, NewlineToken())
    _indent_statement                       = Statement("Indent", IndentToken())
    _dedent_statement                       = Statement("Dedent", DedentToken())

    _statements                             = DynamicStatementInfo(
        [_upper_statement, _indent_statement, _dedent_statement],
        [],
    )

    # ----------------------------------------------------------------------
    def test_First(self):
        with CreateObserver() as observer:
            observer.mock.side_effect = [
                True,                       # ONE\n
                DynamicStatementInfo([self._lower_statement, self._dedent_statement], [], False),   # Indent
                True,                       # two
                True,                       # three
                True,                       # four
                True,                       # Dedent
            ]

            results = Parse(
                self._statements,
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\
                            ONE
                                two
                                three
                                four
                            """,
                        ),
                    ),
                ),
                observer,
            )

            assert len(results) == 6

            assert str(results[0]) == textwrap.dedent(
                """\
                Or: [Upper, Indent, Dedent]
                    Upper
                        Upper <<Regex: <_sre.SRE_Match object; span=(0, 3), match='ONE'>>> ws:None [1, 4]
                        Newline+ <<3, 4>> ws:None [2, 1]
                """,
            )

            assert str(results[1]) == textwrap.dedent(
                """\
                Or: [Upper, Indent, Dedent]
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 5]
                """,
            )

            assert str(results[2]) == textwrap.dedent(
                """\
                Or: [Lower, Dedent]
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 8]
                        Newline+ <<11, 12>> ws:None [3, 1]
                """,
            )

            assert str(results[3]) == textwrap.dedent(
                """\
                Or: [Lower, Dedent]
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 10]
                        Newline+ <<21, 22>> ws:None [4, 1]
                """,
            )

            assert str(results[4]) == textwrap.dedent(
                """\
                Or: [Lower, Dedent]
                    Lower
                        Lower <<Regex: <_sre.SRE_Match object; span=(26, 30), match='four'>>> ws:None [4, 9]
                        Newline+ <<30, 31>> ws:None [5, 1]
                """,
            )

            assert str(results[5]) == textwrap.dedent(
                """\
                Or: [Lower, Dedent]
                    Dedent
                        Dedent <<>> ws:None [5, 1]
                """,
            )

    # ----------------------------------------------------------------------
    def test_Error(self):
        with CreateObserver() as observer:
            observer.mock.side_effect = [
                True,                       # ONE\n
                DynamicStatementInfo([self._lower_statement, self._dedent_statement], [], False),   # Indent
                True,                       # two
                True,                       # three
                True,                       # four
                True,                       # Dedent
            ]

            with pytest.raises(SyntaxInvalidError) as ex:
                results = Parse(
                    self._statements,
                    NormalizedIterator(
                        Normalize(
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
                    ),
                    observer,
                )

            ex = ex.value

            assert ex.Line == 5
            assert ex.Column == 1
            assert str(ex) == "The syntax is not recognized"

# ----------------------------------------------------------------------
def test_InvalidDynamicTraversalError():
    with CreateObserver() as observer:
        observer.mock.side_effect = [
            DynamicStatementInfo([Statement("Newline", NewlineToken())], [], False),
        ]

        with pytest.raises(InvalidDynamicTraversalError) as ex:
            Parse(
                DynamicStatementInfo(
                    [Statement("Newline", NewlineToken())],
                    [],
                ),
                NormalizedIterator(
                    Normalize(
                        textwrap.dedent(
                            """\


                            """,
                        ),
                    ),
                ),
                observer,
            )

        ex = ex.value

        assert ex.Line == 1
        assert ex.Column == 1
        assert str(ex) == "Dynamic statements that prohibit parent traversal should never be applied over other dynamic statements within the same lexical scope. You should make these dynamic statements the first ones applied in this lexical scope."
