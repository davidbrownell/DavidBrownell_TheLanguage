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
    from ..StandardStatement import StandardStatement

    from ..Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
        Token,
    )


# ----------------------------------------------------------------------
@contextmanager
def CreateObserver():
    with ThreadPoolExecutor() as executor:
        # ----------------------------------------------------------------------
        class MyObserver(Observer):
            # ----------------------------------------------------------------------
            def __init__(self):
                self.mock = Mock(
                    return_value=(True, None),
                )

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
            def OnIndent():
                pass

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def OnDedent():
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

    _upper_statement                        = StandardStatement([_upper_token, NewlineToken()])
    _lower_statement                        = StandardStatement([_lower_token, NewlineToken()])
    _number_statement                       = StandardStatement([_number_token, NewlineToken()])

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
            assert results[0].Statement == self._upper_statement
            assert len(results[0].Results) == 2

            assert results[0].Results[0].Token == self._upper_token
            assert results[0].Results[0].Value.Match.group("value") == "ONE"
            assert results[0].Results[0].Whitespace is None
            assert results[0].Results[0].Iter.Line == 1
            assert results[0].Results[0].Iter.Column == 4

            assert results[0].Results[1].Token == NewlineToken()
            assert results[0].Results[1].Value == Token.NewlineMatch(3, 4)
            assert results[0].Results[1].Whitespace is None
            assert results[0].Results[1].Iter.Line == 2
            assert results[0].Results[1].Iter.Column == 1

            # Line 2
            assert results[1].Statement == self._lower_statement

            assert len(results[1].Results) == 2

            assert results[1].Results[0].Token == self._lower_token
            assert results[1].Results[0].Value.Match.group("value") == "two"
            assert results[1].Results[0].Whitespace is None
            assert results[1].Results[0].Iter.Line == 2
            assert results[1].Results[0].Iter.Column == 4

            assert results[1].Results[1].Token == NewlineToken()
            assert results[1].Results[1].Value == Token.NewlineMatch(7, 8)
            assert results[1].Results[1].Whitespace is None
            assert results[1].Results[1].Iter.Line == 3
            assert results[1].Results[1].Iter.Column == 1

            # Line 3
            assert results[2].Statement == self._number_statement

            assert len(results[2].Results) == 2

            assert results[2].Results[0].Token == self._number_token
            assert results[2].Results[0].Value.Match.group("value") == "33333"
            assert results[2].Results[0].Whitespace is None
            assert results[2].Results[0].Iter.Line == 3
            assert results[2].Results[0].Iter.Column == 6

            assert results[2].Results[1].Token == NewlineToken()
            assert results[2].Results[1].Value == Token.NewlineMatch(13, 14)
            assert results[2].Results[1].Whitespace is None
            assert results[2].Results[1].Iter.Line == 4
            assert results[2].Results[1].Iter.Column == 1

            assert results[2].Results[1].Iter.AtEnd()

            # Verify the callback
            assert observer.mock.call_count == 3

            observer.VerifyCallArgs(0, self._upper_statement, results[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._lower_statement, results[1], 2, 1, 3, 1)
            observer.VerifyCallArgs(2, self._number_statement, results[2], 3, 1, 4, 1)

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
            assert results[0].Statement == self._number_statement

            assert len(results[0].Results) == 2

            assert results[0].Results[0].Token == self._number_token
            assert results[0].Results[0].Value.Match.group("value") == "33"
            assert results[0].Results[0].Whitespace is None
            assert results[0].Results[0].Iter.Line == 1
            assert results[0].Results[0].Iter.Column == 3

            assert results[0].Results[1].Token == NewlineToken()
            assert results[0].Results[1].Value == Token.NewlineMatch(2, 3)
            assert results[0].Results[1].Whitespace is None
            assert results[0].Results[1].Iter.Line == 2
            assert results[0].Results[1].Iter.Column == 1

            # Line 2
            assert results[1].Statement == self._lower_statement

            assert len(results[1].Results) == 2

            assert results[1].Results[0].Token == self._lower_token
            assert results[1].Results[0].Value.Match.group("value") == "twoooooooo"
            assert results[1].Results[0].Whitespace is None
            assert results[1].Results[0].Iter.Line == 2
            assert results[1].Results[0].Iter.Column == 11

            assert results[1].Results[1].Token == NewlineToken()
            assert results[1].Results[1].Value == Token.NewlineMatch(13, 14)
            assert results[1].Results[1].Whitespace is None
            assert results[1].Results[1].Iter.Line == 3
            assert results[1].Results[1].Iter.Column == 1

            # Line 3
            assert results[2].Statement == self._upper_statement

            assert len(results[2].Results) == 2

            assert results[2].Results[0].Token == self._upper_token
            assert results[2].Results[0].Value.Match.group("value") == "ONE"
            assert results[2].Results[0].Whitespace is None
            assert results[2].Results[0].Iter.Line == 3
            assert results[2].Results[0].Iter.Column == 4

            assert results[2].Results[1].Token == NewlineToken()
            assert results[2].Results[1].Value == Token.NewlineMatch(17, 18)
            assert results[2].Results[1].Whitespace is None
            assert results[2].Results[1].Iter.Line == 4
            assert results[2].Results[1].Iter.Column == 1

            assert results[2].Results[1].Iter.AtEnd()

            # Verify the callback
            assert observer.mock.call_count == 3

            observer.VerifyCallArgs(0, self._number_statement, results[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._lower_statement, results[1], 2, 1, 3, 1)
            observer.VerifyCallArgs(2, self._upper_statement, results[2],  3, 1, 4, 1)

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
            assert results[0].Statement == self._number_statement

            assert len(results[0].Results) == 2

            assert results[0].Results[0].Token == self._number_token
            assert results[0].Results[0].Value.Match.group("value") == "1"
            assert results[0].Results[0].Whitespace is None
            assert results[0].Results[0].Iter.Line == 1
            assert results[0].Results[0].Iter.Column == 2

            assert results[0].Results[1].Token == NewlineToken()
            assert results[0].Results[1].Value == Token.NewlineMatch(1, 2)
            assert results[0].Results[1].Whitespace is None
            assert results[0].Results[1].Iter.Line == 2
            assert results[0].Results[1].Iter.Column == 1

            # Line 2
            assert results[1].Statement == self._number_statement

            assert len(results[1].Results) == 2

            assert results[1].Results[0].Token == self._number_token
            assert results[1].Results[0].Value.Match.group("value") == "22"
            assert results[1].Results[0].Whitespace is None
            assert results[1].Results[0].Iter.Line == 2
            assert results[1].Results[0].Iter.Column == 3

            assert results[1].Results[1].Token == NewlineToken()
            assert results[1].Results[1].Value == Token.NewlineMatch(4, 5)
            assert results[1].Results[1].Whitespace is None
            assert results[1].Results[1].Iter.Line == 3
            assert results[1].Results[1].Iter.Column == 1

            # Line 3
            assert results[2].Statement == self._number_statement

            assert len(results[2].Results) == 2

            assert results[2].Results[0].Token == self._number_token
            assert results[2].Results[0].Value.Match.group("value") == "333"
            assert results[2].Results[0].Whitespace is None
            assert results[2].Results[0].Iter.Line == 3
            assert results[2].Results[0].Iter.Column == 4

            assert results[2].Results[1].Token == NewlineToken()
            assert results[2].Results[1].Value == Token.NewlineMatch(8, 9)
            assert results[2].Results[1].Whitespace is None
            assert results[2].Results[1].Iter.Line == 4
            assert results[2].Results[1].Iter.Column == 1

            assert results[2].Results[1].Iter.AtEnd()

            # Verify the callback
            assert observer.mock.call_count == 3

            observer.VerifyCallArgs(0, self._number_statement, results[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._number_statement, results[1], 2, 1, 3, 1)
            observer.VerifyCallArgs(2, self._number_statement, results[2], 3, 1, 4, 1)

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
    _statement                              = StandardStatement(
        [
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

            assert results[0].Statement == self._statement

            assert len(results[0].Results) == 7

            # Line 1
            assert results[0].Results[0].Token == self._upper_token
            assert results[0].Results[0].Value.Match.group("value") == "ONE"
            assert results[0].Results[0].Whitespace is None
            assert results[0].Results[0].Iter.Line == 1
            assert results[0].Results[0].Iter.Column == 4

            assert results[0].Results[1].Token == NewlineToken()
            assert results[0].Results[1].Value == Token.NewlineMatch(3, 4)
            assert results[0].Results[1].Whitespace is None
            assert results[0].Results[1].Iter.Line == 2
            assert results[0].Results[1].Iter.Column == 1

            # Line 2
            assert results[0].Results[2].Token == IndentToken()
            assert results[0].Results[2].Value == Token.IndentMatch(4, 8, 4)
            assert results[0].Results[2].Whitespace is None
            assert results[0].Results[2].Iter.Line == 2
            assert results[0].Results[2].Iter.Column == 5

            assert results[0].Results[3].Token == self._upper_token
            assert results[0].Results[3].Value.Match.group("value") == "TWO"
            assert results[0].Results[3].Whitespace is None
            assert results[0].Results[3].Iter.Line == 2
            assert results[0].Results[3].Iter.Column == 8

            assert results[0].Results[4].Token == self._upper_token
            assert results[0].Results[4].Value.Match.group("value") == "THREE"
            assert results[0].Results[4].Whitespace == (11, 16)
            assert results[0].Results[4].Iter.Line == 2
            assert results[0].Results[4].Iter.Column == 18

            assert results[0].Results[5].Token == NewlineToken()
            assert results[0].Results[5].Value == Token.NewlineMatch(21, 22)
            assert results[0].Results[5].Whitespace is None
            assert results[0].Results[5].Iter.Line == 3
            assert results[0].Results[5].Iter.Column == 1

            assert results[0].Results[6].Token == DedentToken()
            assert results[0].Results[6].Value == Token.DedentMatch()
            assert results[0].Results[6].Whitespace is None
            assert results[0].Results[6].Iter.Line == 3
            assert results[0].Results[6].Iter.Column == 1

            assert results[0].Results[6].Iter.AtEnd()

            # Verify the Callbacks
            assert observer.mock.call_count == 1

            observer.VerifyCallArgs(0, self._statement, results[0], 1, 1, 3, 1)

# ----------------------------------------------------------------------
class TestNewStatements(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))

    _upper_statement                        = StandardStatement([_upper_token])
    _lower_statement                        = StandardStatement([_lower_token, NewlineToken()])

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
            assert self._upper_statement in ex.PotentialStatements
            assert ex.PotentialStatements[self._upper_statement] == []

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

            assert results[0].Statement == self._upper_statement

            assert len(results[0].Results) == 1

            assert results[0].Results[0].Token == self._upper_token
            assert results[0].Results[0].Value.Match.group("value") == "ONE"
            assert results[0].Results[0].Whitespace is None
            assert results[0].Results[0].Iter.Line == 1
            assert results[0].Results[0].Iter.Column == 4

            assert results[1].Statement == self._lower_statement

            assert len(results[1].Results) == 2

            assert results[1].Results[0].Token == self._lower_token
            assert results[1].Results[0].Value.Match.group("value") == "two"
            assert results[1].Results[0].Whitespace == (3, 4)
            assert results[1].Results[0].Iter.Line == 1
            assert results[1].Results[0].Iter.Column == 8

            assert results[1].Results[1].Token == NewlineToken()
            assert results[1].Results[1].Value == Token.NewlineMatch(7, 8)
            assert results[1].Results[1].Whitespace is None
            assert results[1].Results[1].Iter.Line == 2
            assert results[1].Results[1].Iter.Column == 1

            # Verify the callbacks
            assert observer.mock.call_count == 2

            observer.VerifyCallArgs(0, self._upper_statement, results[0], 1, 1, 1, 4)
            observer.VerifyCallArgs(1, self._lower_statement, results[1], 1, 4, 2, 1)

# ----------------------------------------------------------------------
class TestNewScopedStatements(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))

    _upper_statement                        = StandardStatement([_upper_token])
    _lower_statement                        = StandardStatement([_lower_token])

    _newline_statement                      = StandardStatement([NewlineToken()])
    _indent_statement                       = StandardStatement([IndentToken()])
    _dedent_statement                       = StandardStatement([DedentToken()])

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

            # Line 1
            assert results[0].Statement == self._upper_statement

            assert len(results[0].Results) == 1

            assert results[0].Results[0].Token == self._upper_token
            assert results[0].Results[0].Value.Match.group("value") == "ONE"
            assert results[0].Results[0].Whitespace is None
            assert results[0].Results[0].Iter.Line == 1
            assert results[0].Results[0].Iter.Column == 4

            assert results[1].Statement == self._newline_statement

            assert len(results[1].Results) == 1

            assert results[1].Results[0].Token == NewlineToken()
            assert results[1].Results[0].Value == Token.NewlineMatch(3, 4)
            assert results[1].Results[0].Whitespace is None
            assert results[1].Results[0].Iter.Line == 2
            assert results[1].Results[0].Iter.Column == 1

            # Line 2
            assert results[2].Statement == self._indent_statement

            assert len(results[2].Results) == 1

            assert results[2].Results[0].Token == IndentToken()
            assert results[2].Results[0].Value == Token.IndentMatch(4, 8, 4)
            assert results[2].Results[0].Whitespace is None
            assert results[2].Results[0].Iter.Line == 2
            assert results[2].Results[0].Iter.Column == 5

            assert results[3].Statement == self._lower_statement

            assert len(results[3].Results) == 1

            assert results[3].Results[0].Token == self._lower_token
            assert results[3].Results[0].Value.Match.group("value") == "two"
            assert results[3].Results[0].Whitespace is None
            assert results[3].Results[0].Iter.Line == 2
            assert results[3].Results[0].Iter.Column == 8

            assert results[4].Statement == self._newline_statement

            assert len(results[4].Results) == 1

            assert results[4].Results[0].Token == NewlineToken()
            assert results[4].Results[0].Value == Token.NewlineMatch(11, 12)
            assert results[4].Results[0].Whitespace is None
            assert results[4].Results[0].Iter.Line == 3
            assert results[4].Results[0].Iter.Column == 1

            assert results[5].Statement == self._dedent_statement

            assert len(results[5].Results) == 1

            assert results[5].Results[0].Token == DedentToken()
            assert results[5].Results[0].Value == Token.DedentMatch()
            assert results[5].Results[0].Whitespace is None
            assert results[5].Results[0].Iter.Line == 3
            assert results[5].Results[0].Iter.Column == 1

            assert results[5].Results[0].Iter.AtEnd()

            # Verify the callbacks
            assert observer.mock.call_count == 6

            observer.VerifyCallArgs(0, self._upper_statement, results[0], 1, 1, 1, 4)
            observer.VerifyCallArgs(1, self._newline_statement, results[1], 1, 4, 2, 1)
            observer.VerifyCallArgs(2, self._indent_statement, results[2], 2, 1, 2, 5)
            observer.VerifyCallArgs(3, self._lower_statement, results[3], 2, 5, 2, 8)
            observer.VerifyCallArgs(4, self._newline_statement, results[4], 2, 8, 3, 1)
            observer.VerifyCallArgs(5, self._dedent_statement, results[5], 3, 1, 3, 1)

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

            assert len(ex.PotentialStatements) == 4

            assert self._upper_statement in ex.PotentialStatements
            assert ex.PotentialStatements[self._upper_statement] == []
            assert self._newline_statement in ex.PotentialStatements
            assert ex.PotentialStatements[self._newline_statement] == []
            assert self._indent_statement in ex.PotentialStatements
            assert ex.PotentialStatements[self._indent_statement] == []
            assert self._dedent_statement in ex.PotentialStatements
            assert ex.PotentialStatements[self._dedent_statement] == []

# ----------------------------------------------------------------------
class TestEmbeddedStatements(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Upper", re.compile(r"(?P<value>[a-z]+)"))

    _upper_lower_statement                  = StandardStatement([_upper_token, _lower_token, NewlineToken()])

    _uul_statement                          = StandardStatement([_upper_token, _upper_lower_statement])
    _lul_statement                          = StandardStatement([_lower_token, _upper_lower_statement])

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

            # Line 1
            assert results[0].Statement == self._uul_statement

            assert len(results[0].Results) == 2

            assert results[0].Results[0].Token == self._upper_token
            assert results[0].Results[0].Value.Match.group("value") == "ONE"
            assert results[0].Results[0].Whitespace is None
            assert results[0].Results[0].Iter.Line == 1
            assert results[0].Results[0].Iter.Column == 4

            assert results[0].Results[1].Statement == self._upper_lower_statement

            assert len(results[0].Results[1].Results) == 3

            assert results[0].Results[1].Results[0].Token == self._upper_token
            assert results[0].Results[1].Results[0].Value.Match.group("value") == "TWO"
            assert results[0].Results[1].Results[0].Whitespace == (3, 4)
            assert results[0].Results[1].Results[0].Iter.Line == 1
            assert results[0].Results[1].Results[0].Iter.Column == 8

            assert results[0].Results[1].Results[1].Token == self._lower_token
            assert results[0].Results[1].Results[1].Value.Match.group("value") == "three"
            assert results[0].Results[1].Results[1].Whitespace == (7, 9)
            assert results[0].Results[1].Results[1].Iter.Line == 1
            assert results[0].Results[1].Results[1].Iter.Column == 15

            assert results[0].Results[1].Results[2].Token == NewlineToken()
            assert results[0].Results[1].Results[2].Value == Token.NewlineMatch(14, 15)
            assert results[0].Results[1].Results[2].Whitespace is None
            assert results[0].Results[1].Results[2].Iter.Line == 2
            assert results[0].Results[1].Results[2].Iter.Column == 1

            # Line 2
            assert results[1].Statement == self._lul_statement

            assert len(results[1].Results) == 2

            assert results[1].Results[0].Token == self._lower_token
            assert results[1].Results[0].Value.Match.group("value") == "four"
            assert results[1].Results[0].Whitespace is None
            assert results[1].Results[0].Iter.Line == 2
            assert results[1].Results[0].Iter.Column == 5

            assert results[1].Results[1].Statement == self._upper_lower_statement

            assert len(results[1].Results[1].Results) == 3

            assert results[1].Results[1].Results[0].Token == self._upper_token
            assert results[1].Results[1].Results[0].Value.Match.group("value") == "FIVE"
            assert results[1].Results[1].Results[0].Whitespace == (19, 23)
            assert results[1].Results[1].Results[0].Iter.Line == 2
            assert results[1].Results[1].Results[0].Iter.Column == 13

            assert results[1].Results[1].Results[1].Token == self._lower_token
            assert results[1].Results[1].Results[1].Value.Match.group("value") == "six"
            assert results[1].Results[1].Results[1].Whitespace == (27, 28)
            assert results[1].Results[1].Results[1].Iter.Line == 2
            assert results[1].Results[1].Results[1].Iter.Column == 17

            assert results[1].Results[1].Results[2].Token == NewlineToken()
            assert results[1].Results[1].Results[2].Value == Token.NewlineMatch(31, 32)
            assert results[1].Results[1].Results[2].Whitespace is None
            assert results[1].Results[1].Results[2].Iter.Line == 3
            assert results[1].Results[1].Results[2].Iter.Column == 1

            # Verify the callbacks
            assert observer.mock.call_count == 4

            observer.VerifyCallArgs(0, self._upper_lower_statement, results[0].Results[1], 1, 4, 2, 1)
            observer.VerifyCallArgs(1, self._uul_statement, results[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(2, self._upper_lower_statement, results[1].Results[1], 2, 5, 3, 1)
            observer.VerifyCallArgs(3, self._lul_statement, results[1], 2, 1, 3, 1)

# ----------------------------------------------------------------------
class TestNoMatchError(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number", re.compile(r"(?P<value>[0-9]+)"))

    _upper_statement                        = StandardStatement([_upper_token, _number_token])
    _lower_statement                        = StandardStatement([_upper_token, _lower_token])

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
            assert ex.Column == 1
            assert str(ex) == "The syntax is not recognized"

            assert len(ex.PotentialStatements) == 2

            assert len(ex.PotentialStatements[self._upper_statement]) == 1
            assert ex.PotentialStatements[self._upper_statement][0].Token == self._upper_token
            assert ex.PotentialStatements[self._upper_statement][0].Iter.Line == 1
            assert ex.PotentialStatements[self._upper_statement][0].Iter.Column == 4

            assert len(ex.PotentialStatements[self._lower_statement]) == 1
            assert ex.PotentialStatements[self._lower_statement][0].Token == self._upper_token
            assert ex.PotentialStatements[self._lower_statement][0].Iter.Line == 1
            assert ex.PotentialStatements[self._lower_statement][0].Iter.Column == 4

# ----------------------------------------------------------------------
class TestVariedLengthMatches(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number", re.compile(r"(?P<value>[0-9]+)"))

    _upper_statement                        = StandardStatement([_upper_token, NewlineToken()])
    _lower_statement                        = StandardStatement([_lower_token, _lower_token, NewlineToken()])
    _number_statement                       = StandardStatement([_number_token, _number_token, _number_token, NewlineToken()])

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

            # Line 1
            assert results[0].Statement == self._lower_statement

            assert len(results[0].Results) == 3
            assert results[0].Results[0].Value.Match.group("value") == "one"
            assert results[0].Results[1].Value.Match.group("value") == "two"
            assert results[0].Results[2].Value == Token.NewlineMatch(7, 8)

            # Line 2
            assert results[1].Statement == self._number_statement

            assert len(results[1].Results) == 4
            assert results[1].Results[0].Value.Match.group("value") == "1"
            assert results[1].Results[1].Value.Match.group("value") == "2"
            assert results[1].Results[2].Value.Match.group("value") == "3"
            assert results[1].Results[3].Value == Token.NewlineMatch(13, 14)

            # Line 3
            assert results[2].Statement == self._upper_statement

            assert len(results[2].Results) == 2
            assert results[2].Results[0].Value.Match.group("value") == "WORD"
            assert results[2].Results[1].Value == Token.NewlineMatch(18, 19)

# ----------------------------------------------------------------------
class TestEmptyDynamicStatementInfo(object):
    with CreateObserver() as observer:
        observer.mock.side_effect = [
            DynamicStatementInfo([], []),
        ]

        results = Parse(
            DynamicStatementInfo(
                [StandardStatement([NewlineToken()])],
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
        assert len(results[0].Results) == 1
        assert results[0].Results[0].Value == Token.NewlineMatch(0, 1)

# ----------------------------------------------------------------------
class TestPreventParentTraversal(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))

    _upper_statement                        = StandardStatement([_upper_token, NewlineToken()])
    _lower_statement                        = StandardStatement([_lower_token, NewlineToken()])
    _indent_statement                       = StandardStatement([IndentToken()])
    _dedent_statement                       = StandardStatement([DedentToken()])

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

            # Line 1
            assert results[0].Statement == self._upper_statement

            assert len(results[0].Results) == 2
            assert results[0].Results[0].Value.Match.group("value") == "ONE"
            assert results[0].Results[1].Value == Token.NewlineMatch(3, 4)

            # Indent
            assert results[1].Statement == self._indent_statement

            assert len(results[1].Results) == 1
            assert results[1].Results[0].Value == Token.IndentMatch(4, 8, 4)

            # Line 2
            assert results[2].Statement == self._lower_statement

            assert len(results[2].Results) == 2
            assert results[2].Results[0].Value.Match.group("value") == "two"
            assert results[2].Results[1].Value == Token.NewlineMatch(11, 12)

            # Line 3
            assert results[3].Statement == self._lower_statement

            assert len(results[3].Results) == 2
            assert results[3].Results[0].Value.Match.group("value") == "three"
            assert results[3].Results[1].Value == Token.NewlineMatch(21, 22)

            # Line 4
            assert results[4].Statement == self._lower_statement

            assert len(results[4].Results) == 2
            assert results[4].Results[0].Value.Match.group("value") == "four"
            assert results[4].Results[1].Value == Token.NewlineMatch(30, 31)

            # Dedent
            assert results[5].Statement == self._dedent_statement

            assert len(results[5].Results) == 1
            assert results[5].Results[0].Value == Token.DedentMatch()

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
            DynamicStatementInfo([StandardStatement([NewlineToken()])], [], False),
        ]

        with pytest.raises(InvalidDynamicTraversalError) as ex:
            Parse(
                DynamicStatementInfo(
                    [StandardStatement([NewlineToken()])],
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
