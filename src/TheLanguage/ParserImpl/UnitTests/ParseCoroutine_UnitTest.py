# ----------------------------------------------------------------------
# |
# |  ParseCoroutine_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-24 14:23:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for ParseCoroutine"""

import os
import re
import textwrap

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from unittest.mock import Mock

import pytest

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Normalize import *
    from ..NormalizedIterator import NormalizedIterator
    from ..ParseCoroutine import *
    from ..StandardStatement import StandardStatement

    from ..Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken
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
                    return_value=Coroutine.Status.Continue,
                )

            # ----------------------------------------------------------------------
            def VerifyCallArgs(self, index, statement, node, before_line, before_col, after_line, after_col):
                callback_args = self.mock.call_args_list[index][0]

                assert callback_args[0] == node
                assert callback_args[0].Type == statement
                assert callback_args[1].Line == before_line
                assert callback_args[1].Column == before_col
                assert callback_args[2].Line == after_line
                assert callback_args[2].Column == after_col

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
            def OnStatementComplete(self, node, iter_before, iter_after):
                return self.mock(node, iter_before, iter_after)

        # ----------------------------------------------------------------------

        yield MyObserver()


# ----------------------------------------------------------------------
class TestSimple(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number", re.compile(r"(?P<value>[0-9]+)"))

    _upper_statement                        = StandardStatement("Upper Statement", [_upper_token, NewlineToken()])
    _lower_statement                        = StandardStatement("Lower Statement", [_lower_token, NewlineToken()])
    _number_statement                       = StandardStatement("Number Statement", [_number_token, NewlineToken()])

    _statements                             = DynamicStatementInfo(
        [_upper_statement, _lower_statement, _number_statement],
        [],
    )

    # ----------------------------------------------------------------------
    def test_MatchStandard(self):
        with CreateObserver() as observer:
            results = Coroutine.Execute(
                ParseCoroutine(
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
                    self._statements,
                    observer,
                ),
            )[0]

            # Verify the results
            assert results.Parent is None
            assert len(results.Children) == 3

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._upper_statement

            assert len(results.Children[0].Children) == 2

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._upper_token
            assert results.Children[0].Children[0].Value.Match.group("value") == "ONE"
            assert results.Children[0].Children[0].Whitespace is None
            assert results.Children[0].Children[0].Iter.Line == 1
            assert results.Children[0].Children[0].Iter.Column == 4

            assert results.Children[0].Children[1].Parent == results.Children[0]
            assert results.Children[0].Children[1].Type == NewlineToken()
            assert results.Children[0].Children[1].Value == Token.NewlineMatch(3, 4)
            assert results.Children[0].Children[1].Whitespace is None
            assert results.Children[0].Children[1].Iter.Line == 2
            assert results.Children[0].Children[1].Iter.Column == 1

            # Line 2
            assert results.Children[1].Parent == results
            assert results.Children[1].Type == self._lower_statement

            assert len(results.Children[1].Children) == 2

            assert results.Children[1].Children[0].Parent == results.Children[1]
            assert results.Children[1].Children[0].Type == self._lower_token
            assert results.Children[1].Children[0].Value.Match.group("value") == "two"
            assert results.Children[1].Children[0].Whitespace is None
            assert results.Children[1].Children[0].Iter.Line == 2
            assert results.Children[1].Children[0].Iter.Column == 4

            assert results.Children[1].Children[1].Parent == results.Children[1]
            assert results.Children[1].Children[1].Type == NewlineToken()
            assert results.Children[1].Children[1].Value == Token.NewlineMatch(7, 8)
            assert results.Children[1].Children[1].Whitespace is None
            assert results.Children[1].Children[1].Iter.Line == 3
            assert results.Children[1].Children[1].Iter.Column == 1

            # Line 3
            assert results.Children[2].Parent == results
            assert results.Children[2].Type == self._number_statement

            assert len(results.Children[2].Children) == 2

            assert results.Children[2].Children[0].Parent == results.Children[2]
            assert results.Children[2].Children[0].Type == self._number_token
            assert results.Children[2].Children[0].Value.Match.group("value") == "33333"
            assert results.Children[2].Children[0].Whitespace is None
            assert results.Children[2].Children[0].Iter.Line == 3
            assert results.Children[2].Children[0].Iter.Column == 6

            assert results.Children[2].Children[1].Parent == results.Children[2]
            assert results.Children[2].Children[1].Type == NewlineToken()
            assert results.Children[2].Children[1].Value == Token.NewlineMatch(13, 14)
            assert results.Children[2].Children[1].Whitespace is None
            assert results.Children[2].Children[1].Iter.Line == 4
            assert results.Children[2].Children[1].Iter.Column == 1

            assert results.Children[2].Children[1].Iter.AtEnd()

            # Verify the callback
            assert observer.mock.call_count == 3

            observer.VerifyCallArgs(0, self._upper_statement, results.Children[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._lower_statement, results.Children[1], 2, 1, 3, 1)
            observer.VerifyCallArgs(2, self._number_statement, results.Children[2], 3, 1, 4, 1)

    # ----------------------------------------------------------------------
    def test_MatchReverse(self):
        with CreateObserver() as observer:
            results = Coroutine.Execute(
                ParseCoroutine(
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
                    self._statements,
                    observer,
                ),
            )[0]

            # Verify the results
            assert results.Parent is None
            assert len(results.Children) == 3

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._number_statement

            assert len(results.Children[0].Children) == 2

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._number_token
            assert results.Children[0].Children[0].Value.Match.group("value") == "33"
            assert results.Children[0].Children[0].Whitespace is None
            assert results.Children[0].Children[0].Iter.Line == 1
            assert results.Children[0].Children[0].Iter.Column == 3

            assert results.Children[0].Children[1].Parent == results.Children[0]
            assert results.Children[0].Children[1].Type == NewlineToken()
            assert results.Children[0].Children[1].Value == Token.NewlineMatch(2, 3)
            assert results.Children[0].Children[1].Whitespace is None
            assert results.Children[0].Children[1].Iter.Line == 2
            assert results.Children[0].Children[1].Iter.Column == 1

            # Line 2
            assert results.Children[1].Parent == results
            assert results.Children[1].Type == self._lower_statement

            assert len(results.Children[1].Children) == 2

            assert results.Children[1].Children[0].Parent == results.Children[1]
            assert results.Children[1].Children[0].Type == self._lower_token
            assert results.Children[1].Children[0].Value.Match.group("value") == "twoooooooo"
            assert results.Children[1].Children[0].Whitespace is None
            assert results.Children[1].Children[0].Iter.Line == 2
            assert results.Children[1].Children[0].Iter.Column == 11

            assert results.Children[1].Children[1].Parent == results.Children[1]
            assert results.Children[1].Children[1].Type == NewlineToken()
            assert results.Children[1].Children[1].Value == Token.NewlineMatch(13, 14)
            assert results.Children[1].Children[1].Whitespace is None
            assert results.Children[1].Children[1].Iter.Line == 3
            assert results.Children[1].Children[1].Iter.Column == 1

            # Line 3
            assert results.Children[2].Parent == results
            assert results.Children[2].Type == self._upper_statement

            assert len(results.Children[2].Children) == 2

            assert results.Children[2].Children[0].Parent == results.Children[2]
            assert results.Children[2].Children[0].Type == self._upper_token
            assert results.Children[2].Children[0].Value.Match.group("value") == "ONE"
            assert results.Children[2].Children[0].Whitespace is None
            assert results.Children[2].Children[0].Iter.Line == 3
            assert results.Children[2].Children[0].Iter.Column == 4

            assert results.Children[2].Children[1].Parent == results.Children[2]
            assert results.Children[2].Children[1].Type == NewlineToken()
            assert results.Children[2].Children[1].Value == Token.NewlineMatch(17, 18)
            assert results.Children[2].Children[1].Whitespace is None
            assert results.Children[2].Children[1].Iter.Line == 4
            assert results.Children[2].Children[1].Iter.Column == 1

            assert results.Children[2].Children[1].Iter.AtEnd()

            # Verify the callback
            assert observer.mock.call_count == 3

            observer.VerifyCallArgs(0, self._number_statement, results.Children[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._lower_statement, results.Children[1], 2, 1, 3, 1)
            observer.VerifyCallArgs(2, self._upper_statement, results.Children[2],  3, 1, 4, 1)

    # ----------------------------------------------------------------------
    def test_MatchSame(self):
        with CreateObserver() as observer:
            results = Coroutine.Execute(
                ParseCoroutine(
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
                    self._statements,
                    observer,
                ),
            )[0]

            # Verify the results
            assert results.Parent is None
            assert len(results.Children) == 3

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._number_statement

            assert len(results.Children[0].Children) == 2

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._number_token
            assert results.Children[0].Children[0].Value.Match.group("value") == "1"
            assert results.Children[0].Children[0].Whitespace is None
            assert results.Children[0].Children[0].Iter.Line == 1
            assert results.Children[0].Children[0].Iter.Column == 2

            assert results.Children[0].Children[1].Parent == results.Children[0]
            assert results.Children[0].Children[1].Type == NewlineToken()
            assert results.Children[0].Children[1].Value == Token.NewlineMatch(1, 2)
            assert results.Children[0].Children[1].Whitespace is None
            assert results.Children[0].Children[1].Iter.Line == 2
            assert results.Children[0].Children[1].Iter.Column == 1

            # Line 2
            assert results.Children[1].Parent == results
            assert results.Children[1].Type == self._number_statement

            assert len(results.Children[1].Children) == 2

            assert results.Children[1].Children[0].Parent == results.Children[1]
            assert results.Children[1].Children[0].Type == self._number_token
            assert results.Children[1].Children[0].Value.Match.group("value") == "22"
            assert results.Children[1].Children[0].Whitespace is None
            assert results.Children[1].Children[0].Iter.Line == 2
            assert results.Children[1].Children[0].Iter.Column == 3

            assert results.Children[1].Children[1].Parent == results.Children[1]
            assert results.Children[1].Children[1].Type == NewlineToken()
            assert results.Children[1].Children[1].Value == Token.NewlineMatch(4, 5)
            assert results.Children[1].Children[1].Whitespace is None
            assert results.Children[1].Children[1].Iter.Line == 3
            assert results.Children[1].Children[1].Iter.Column == 1

            # Line 3
            assert results.Children[2].Parent == results
            assert results.Children[2].Type == self._number_statement

            assert len(results.Children[2].Children) == 2

            assert results.Children[2].Children[0].Parent == results.Children[2]
            assert results.Children[2].Children[0].Type == self._number_token
            assert results.Children[2].Children[0].Value.Match.group("value") == "333"
            assert results.Children[2].Children[0].Whitespace is None
            assert results.Children[2].Children[0].Iter.Line == 3
            assert results.Children[2].Children[0].Iter.Column == 4

            assert results.Children[2].Children[1].Parent == results.Children[2]
            assert results.Children[2].Children[1].Type == NewlineToken()
            assert results.Children[2].Children[1].Value == Token.NewlineMatch(8, 9)
            assert results.Children[2].Children[1].Whitespace is None
            assert results.Children[2].Children[1].Iter.Line == 4
            assert results.Children[2].Children[1].Iter.Column == 1

            assert results.Children[2].Children[1].Iter.AtEnd()

            # Verify the callback
            assert observer.mock.call_count == 3

            observer.VerifyCallArgs(0, self._number_statement, results.Children[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._number_statement, results.Children[1], 2, 1, 3, 1)
            observer.VerifyCallArgs(2, self._number_statement, results.Children[2], 3, 1, 4, 1)

    # ----------------------------------------------------------------------
    def test_EarlyTermination(self):
        with CreateObserver() as observer:
            observer.mock.side_effect = [
                Coroutine.Status.Continue,
                Coroutine.Status.Terminate,
            ]

            results = Coroutine.Execute(
                ParseCoroutine(
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
                    self._statements,
                    observer,
                ),
            )[0]

            # Verify the callback
            assert observer.mock.call_count == 2

            # Note that we can't compare the 2nd arg, as we don't have easy access to the Node
            # to compare it with
            assert observer.mock.call_args_list[0][0][0].Type == self._number_statement
            assert observer.mock.call_args_list[0][0][1].Line == 1
            assert observer.mock.call_args_list[0][0][1].Column == 1
            assert observer.mock.call_args_list[0][0][2].Line == 2
            assert observer.mock.call_args_list[0][0][2].Column == 1

            assert observer.mock.call_args_list[1][0][0].Type == self._number_statement
            assert observer.mock.call_args_list[1][0][1].Line == 2
            assert observer.mock.call_args_list[1][0][1].Column == 1
            assert observer.mock.call_args_list[1][0][2].Line == 3
            assert observer.mock.call_args_list[1][0][2].Column == 1

    # ----------------------------------------------------------------------
    # BugBug: Need more of these tests to ensure that the information is being combined correctly
    def test_Yield(self):
        with CreateObserver() as observer:
            observer.mock.side_effect = [
                Coroutine.Status.Yield,
                Coroutine.Status.Yield,
                Coroutine.Status.Continue,
            ]

            iterator = ParseCoroutine(
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
                self._statements,
                observer,
            )

            next(iterator)
            iterator.send(DynamicStatementInfo([], []))

            next(iterator)
            iterator.send(DynamicStatementInfo([], []))

            try:
                next(iterator)
            except StopIteration as ex:
                results = ex.value

            # Verify the results
            assert results.Parent is None
            assert len(results.Children) == 3

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._number_statement

            assert len(results.Children[0].Children) == 2

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._number_token
            assert results.Children[0].Children[0].Value.Match.group("value") == "1"
            assert results.Children[0].Children[0].Whitespace is None
            assert results.Children[0].Children[0].Iter.Line == 1
            assert results.Children[0].Children[0].Iter.Column == 2

            assert results.Children[0].Children[1].Parent == results.Children[0]
            assert results.Children[0].Children[1].Type == NewlineToken()
            assert results.Children[0].Children[1].Value == Token.NewlineMatch(1, 2)
            assert results.Children[0].Children[1].Whitespace is None
            assert results.Children[0].Children[1].Iter.Line == 2
            assert results.Children[0].Children[1].Iter.Column == 1

            # Line 2
            assert results.Children[1].Parent == results
            assert results.Children[1].Type == self._number_statement

            assert len(results.Children[1].Children) == 2

            assert results.Children[1].Children[0].Parent == results.Children[1]
            assert results.Children[1].Children[0].Type == self._number_token
            assert results.Children[1].Children[0].Value.Match.group("value") == "22"
            assert results.Children[1].Children[0].Whitespace is None
            assert results.Children[1].Children[0].Iter.Line == 2
            assert results.Children[1].Children[0].Iter.Column == 3

            assert results.Children[1].Children[1].Parent == results.Children[1]
            assert results.Children[1].Children[1].Type == NewlineToken()
            assert results.Children[1].Children[1].Value == Token.NewlineMatch(4, 5)
            assert results.Children[1].Children[1].Whitespace is None
            assert results.Children[1].Children[1].Iter.Line == 3
            assert results.Children[1].Children[1].Iter.Column == 1

            # Line 3
            assert results.Children[2].Parent == results
            assert results.Children[2].Type == self._number_statement

            assert len(results.Children[2].Children) == 2

            assert results.Children[2].Children[0].Parent == results.Children[2]
            assert results.Children[2].Children[0].Type == self._number_token
            assert results.Children[2].Children[0].Value.Match.group("value") == "333"
            assert results.Children[2].Children[0].Whitespace is None
            assert results.Children[2].Children[0].Iter.Line == 3
            assert results.Children[2].Children[0].Iter.Column == 4

            assert results.Children[2].Children[1].Parent == results.Children[2]
            assert results.Children[2].Children[1].Type == NewlineToken()
            assert results.Children[2].Children[1].Value == Token.NewlineMatch(8, 9)
            assert results.Children[2].Children[1].Whitespace is None
            assert results.Children[2].Children[1].Iter.Line == 4
            assert results.Children[2].Children[1].Iter.Column == 1

            assert results.Children[2].Children[1].Iter.AtEnd()

            # Verify the callback
            assert observer.mock.call_count == 3

            observer.VerifyCallArgs(0, self._number_statement, results.Children[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._number_statement, results.Children[1], 2, 1, 3, 1)
            observer.VerifyCallArgs(2, self._number_statement, results.Children[2], 3, 1, 4, 1)

# ----------------------------------------------------------------------
class TestIndentation(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _statement                              = StandardStatement(
        "Statement",
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
            results = Coroutine.Execute(
                ParseCoroutine(
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
                    self._statements,
                    observer,
                ),
            )[0]

            # Verify the results
            assert results.Parent is None
            assert len(results.Children) == 1

            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._statement

            assert len(results.Children[0].Children) == 7

            # Line 1
            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._upper_token
            assert results.Children[0].Children[0].Value.Match.group("value") == "ONE"
            assert results.Children[0].Children[0].Whitespace is None
            assert results.Children[0].Children[0].Iter.Line == 1
            assert results.Children[0].Children[0].Iter.Column == 4

            assert results.Children[0].Children[1].Parent == results.Children[0]
            assert results.Children[0].Children[1].Type == NewlineToken()
            assert results.Children[0].Children[1].Value == Token.NewlineMatch(3, 4)
            assert results.Children[0].Children[1].Whitespace is None
            assert results.Children[0].Children[1].Iter.Line == 2
            assert results.Children[0].Children[1].Iter.Column == 1

            # Line 2
            assert results.Children[0].Children[2].Parent == results.Children[0]
            assert results.Children[0].Children[2].Type == IndentToken()
            assert results.Children[0].Children[2].Value == Token.IndentMatch(4, 8, 4)
            assert results.Children[0].Children[2].Whitespace is None
            assert results.Children[0].Children[2].Iter.Line == 2
            assert results.Children[0].Children[2].Iter.Column == 5

            assert results.Children[0].Children[3].Parent == results.Children[0]
            assert results.Children[0].Children[3].Type == self._upper_token
            assert results.Children[0].Children[3].Value.Match.group("value") == "TWO"
            assert results.Children[0].Children[3].Whitespace is None
            assert results.Children[0].Children[3].Iter.Line == 2
            assert results.Children[0].Children[3].Iter.Column == 8

            assert results.Children[0].Children[4].Parent == results.Children[0]
            assert results.Children[0].Children[4].Type == self._upper_token
            assert results.Children[0].Children[4].Value.Match.group("value") == "THREE"
            assert results.Children[0].Children[4].Whitespace == (11, 16)
            assert results.Children[0].Children[4].Iter.Line == 2
            assert results.Children[0].Children[4].Iter.Column == 18

            assert results.Children[0].Children[5].Parent == results.Children[0]
            assert results.Children[0].Children[5].Type == NewlineToken()
            assert results.Children[0].Children[5].Value == Token.NewlineMatch(21, 22)
            assert results.Children[0].Children[5].Whitespace is None
            assert results.Children[0].Children[5].Iter.Line == 3
            assert results.Children[0].Children[5].Iter.Column == 1

            assert results.Children[0].Children[6].Parent == results.Children[0]
            assert results.Children[0].Children[6].Type == DedentToken()
            assert results.Children[0].Children[6].Value == Token.DedentMatch()
            assert results.Children[0].Children[6].Whitespace is None
            assert results.Children[0].Children[6].Iter.Line == 3
            assert results.Children[0].Children[6].Iter.Column == 1

            assert results.Children[0].Children[6].Iter.AtEnd()

            # Verify the Callbacks
            assert observer.mock.call_count == 1

            observer.VerifyCallArgs(0, self._statement, results.Children[0], 1, 1, 3, 1)

# ----------------------------------------------------------------------
class TestNewStatements(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))

    _upper_statement                        = StandardStatement("Upper Statement", [_upper_token])
    _lower_statement                        = StandardStatement("Lower Statement", [_lower_token, NewlineToken()])

    _statements                             = DynamicStatementInfo([_upper_statement], [])
    _new_statements                         = DynamicStatementInfo([_lower_statement], [])

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        with CreateObserver() as observer:
            # The callback isn't returning any new statements; therefore an
            # error will be generated when attempting to parse the lowercase
            # token.
            with pytest.raises(SyntaxInvalidError) as ex:
                results = Coroutine.Execute(
                    ParseCoroutine(
                        NormalizedIterator(
                            Normalize(
                                textwrap.dedent(
                                    """\
                                    ONE two
                                    """,
                                ),
                            ),
                        ),
                        self._statements,
                        observer,
                    ),
                )[0]

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
                Coroutine.Status.Continue,
            ]

            results = Coroutine.Execute(
                ParseCoroutine(
                    NormalizedIterator(
                        Normalize(
                            textwrap.dedent(
                                """\
                                ONE two
                                """,
                            ),
                        ),
                    ),
                    self._statements,
                    observer,
                ),
            )[0]

            # Verify the results
            assert results.Parent is None
            assert len(results.Children) == 2

            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._upper_statement

            assert len(results.Children[0].Children) == 1

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._upper_token
            assert results.Children[0].Children[0].Value.Match.group("value") == "ONE"
            assert results.Children[0].Children[0].Whitespace is None
            assert results.Children[0].Children[0].Iter.Line == 1
            assert results.Children[0].Children[0].Iter.Column == 4

            assert results.Children[1].Parent == results
            assert results.Children[1].Type == self._lower_statement

            assert len(results.Children[1].Children) == 2

            assert results.Children[1].Children[0].Parent == results.Children[1]
            assert results.Children[1].Children[0].Type == self._lower_token
            assert results.Children[1].Children[0].Value.Match.group("value") == "two"
            assert results.Children[1].Children[0].Whitespace == (3, 4)
            assert results.Children[1].Children[0].Iter.Line == 1
            assert results.Children[1].Children[0].Iter.Column == 8

            assert results.Children[1].Children[1].Parent == results.Children[1]
            assert results.Children[1].Children[1].Type == NewlineToken()
            assert results.Children[1].Children[1].Value == Token.NewlineMatch(7, 8)
            assert results.Children[1].Children[1].Whitespace is None
            assert results.Children[1].Children[1].Iter.Line == 2
            assert results.Children[1].Children[1].Iter.Column == 1

            # Verify the callbacks
            assert observer.mock.call_count == 2

            observer.VerifyCallArgs(0, self._upper_statement, results.Children[0], 1, 1, 1, 4)
            observer.VerifyCallArgs(1, self._lower_statement, results.Children[1], 1, 4, 2, 1)

# ----------------------------------------------------------------------
class TestNewScopedStatements(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))

    _upper_statement                        = StandardStatement("Upper Statement", [_upper_token])
    _lower_statement                        = StandardStatement("Lower Statement", [_lower_token])

    _newline_statement                      = StandardStatement("Newline Statement", [NewlineToken()])
    _indent_statement                       = StandardStatement("Indent Statement", [IndentToken()])
    _dedent_statement                       = StandardStatement("Dedent Statement", [DedentToken()])

    _statements                             = DynamicStatementInfo([_upper_statement, _newline_statement, _indent_statement, _dedent_statement], [])
    _new_statements                         = DynamicStatementInfo([_lower_statement], [])

    # ----------------------------------------------------------------------
    def test_Match(self):
        with CreateObserver() as observer:
            observer.mock.side_effect = [
                Coroutine.Status.Continue,  # ONE
                Coroutine.Status.Continue,  # Newline
                self._new_statements,       # Indent
                Coroutine.Status.Continue,  # two
                Coroutine.Status.Continue,  # Newline
                Coroutine.Status.Continue,  # Dedent
            ]

            results = Coroutine.Execute(
                ParseCoroutine(
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
                    self._statements,
                    observer,
                ),
            )[0]

            # Verify the results
            assert results.Parent is None
            assert len(results.Children) == 6

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._upper_statement

            assert len(results.Children[0].Children) == 1

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._upper_token
            assert results.Children[0].Children[0].Value.Match.group("value") == "ONE"
            assert results.Children[0].Children[0].Whitespace is None
            assert results.Children[0].Children[0].Iter.Line == 1
            assert results.Children[0].Children[0].Iter.Column == 4

            assert results.Children[1].Parent == results
            assert results.Children[1].Type == self._newline_statement

            assert len(results.Children[1].Children) == 1

            assert results.Children[1].Children[0].Parent == results.Children[1]
            assert results.Children[1].Children[0].Type == NewlineToken()
            assert results.Children[1].Children[0].Value == Token.NewlineMatch(3, 4)
            assert results.Children[1].Children[0].Whitespace is None
            assert results.Children[1].Children[0].Iter.Line == 2
            assert results.Children[1].Children[0].Iter.Column == 1

            # Line 2
            assert results.Children[2].Parent == results
            assert results.Children[2].Type == self._indent_statement

            assert len(results.Children[2].Children) == 1

            assert results.Children[2].Children[0].Parent == results.Children[2]
            assert results.Children[2].Children[0].Type == IndentToken()
            assert results.Children[2].Children[0].Value == Token.IndentMatch(4, 8, 4)
            assert results.Children[2].Children[0].Whitespace is None
            assert results.Children[2].Children[0].Iter.Line == 2
            assert results.Children[2].Children[0].Iter.Column == 5

            assert results.Children[3].Parent == results
            assert results.Children[3].Type == self._lower_statement

            assert len(results.Children[3].Children) == 1

            assert results.Children[3].Children[0].Parent == results.Children[3]
            assert results.Children[3].Children[0].Type == self._lower_token
            assert results.Children[3].Children[0].Value.Match.group("value") == "two"
            assert results.Children[3].Children[0].Whitespace is None
            assert results.Children[3].Children[0].Iter.Line == 2
            assert results.Children[3].Children[0].Iter.Column == 8

            assert results.Children[4].Parent == results
            assert results.Children[4].Type == self._newline_statement

            assert len(results.Children[4].Children) == 1

            assert results.Children[4].Children[0].Parent == results.Children[4]
            assert results.Children[4].Children[0].Type == NewlineToken()
            assert results.Children[4].Children[0].Value == Token.NewlineMatch(11, 12)
            assert results.Children[4].Children[0].Whitespace is None
            assert results.Children[4].Children[0].Iter.Line == 3
            assert results.Children[4].Children[0].Iter.Column == 1

            assert results.Children[5].Parent == results
            assert results.Children[5].Type == self._dedent_statement

            assert len(results.Children[5].Children) == 1

            assert results.Children[5].Children[0].Parent == results.Children[5]
            assert results.Children[5].Children[0].Type == DedentToken()
            assert results.Children[5].Children[0].Value == Token.DedentMatch()
            assert results.Children[5].Children[0].Whitespace is None
            assert results.Children[5].Children[0].Iter.Line == 3
            assert results.Children[5].Children[0].Iter.Column == 1

            assert results.Children[5].Children[0].Iter.AtEnd()

            # Verify the callbacks
            assert observer.mock.call_count == 6

            observer.VerifyCallArgs(0, self._upper_statement, results.Children[0], 1, 1, 1, 4)
            observer.VerifyCallArgs(1, self._newline_statement, results.Children[1], 1, 4, 2, 1)
            observer.VerifyCallArgs(2, self._indent_statement, results.Children[2], 2, 1, 2, 5)
            observer.VerifyCallArgs(3, self._lower_statement, results.Children[3], 2, 5, 2, 8)
            observer.VerifyCallArgs(4, self._newline_statement, results.Children[4], 2, 8, 3, 1)
            observer.VerifyCallArgs(5, self._dedent_statement, results.Children[5], 3, 1, 3, 1)

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        with CreateObserver() as observer:
            observer.mock.side_effect = [
                Coroutine.Status.Continue,                  # ONE
                Coroutine.Status.Continue,                  # Newline
                self._new_statements,                       # Indent
                Coroutine.Status.Continue,                  # two
                Coroutine.Status.Continue,                  # Newline
                Coroutine.Status.Continue,                  # Dedent
            ]

            with pytest.raises(SyntaxInvalidError) as ex:
                results = Coroutine.Execute(
                    ParseCoroutine(
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
                        self._statements,
                        observer,
                    ),
                )[0]

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

    _upper_lower_statement                  = StandardStatement("Upper Lower Statement", [_upper_token, _lower_token, NewlineToken()])

    _uul_statement                          = StandardStatement("UUL", [_upper_token, _upper_lower_statement])
    _lul_statement                          = StandardStatement("LUL", [_lower_token, _upper_lower_statement])

    _statements                             = DynamicStatementInfo([_uul_statement, _lul_statement], [])

    # ----------------------------------------------------------------------
    def test_Match(self):
        with CreateObserver() as observer:
            results = Coroutine.Execute(
                ParseCoroutine(
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
                    self._statements,
                    observer,
                ),
            )[0]

            # Verify the results
            assert results.Parent is None
            assert len(results.Children) == 2

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._uul_statement

            assert len(results.Children[0].Children) == 2

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._upper_token
            assert results.Children[0].Children[0].Value.Match.group("value") == "ONE"
            assert results.Children[0].Children[0].Whitespace is None
            assert results.Children[0].Children[0].Iter.Line == 1
            assert results.Children[0].Children[0].Iter.Column == 4

            assert results.Children[0].Children[1].Parent == results.Children[0]
            assert results.Children[0].Children[1].Type == self._upper_lower_statement

            assert len(results.Children[0].Children[1].Children) == 3

            assert results.Children[0].Children[1].Children[0].Parent == results.Children[0].Children[1]
            assert results.Children[0].Children[1].Children[0].Type == self._upper_token
            assert results.Children[0].Children[1].Children[0].Value.Match.group("value") == "TWO"
            assert results.Children[0].Children[1].Children[0].Whitespace == (3, 4)
            assert results.Children[0].Children[1].Children[0].Iter.Line == 1
            assert results.Children[0].Children[1].Children[0].Iter.Column == 8

            assert results.Children[0].Children[1].Children[1].Parent == results.Children[0].Children[1]
            assert results.Children[0].Children[1].Children[1].Type == self._lower_token
            assert results.Children[0].Children[1].Children[1].Value.Match.group("value") == "three"
            assert results.Children[0].Children[1].Children[1].Whitespace == (7, 9)
            assert results.Children[0].Children[1].Children[1].Iter.Line == 1
            assert results.Children[0].Children[1].Children[1].Iter.Column == 15

            assert results.Children[0].Children[1].Children[2].Parent == results.Children[0].Children[1]
            assert results.Children[0].Children[1].Children[2].Type == NewlineToken()
            assert results.Children[0].Children[1].Children[2].Value == Token.NewlineMatch(14, 15)
            assert results.Children[0].Children[1].Children[2].Whitespace is None
            assert results.Children[0].Children[1].Children[2].Iter.Line == 2
            assert results.Children[0].Children[1].Children[2].Iter.Column == 1

            # Line 2
            assert results.Children[1].Parent == results
            assert results.Children[1].Type == self._lul_statement

            assert len(results.Children[1].Children) == 2

            assert results.Children[1].Children[0].Parent == results.Children[1]
            assert results.Children[1].Children[0].Type == self._lower_token
            assert results.Children[1].Children[0].Value.Match.group("value") == "four"
            assert results.Children[1].Children[0].Whitespace is None
            assert results.Children[1].Children[0].Iter.Line == 2
            assert results.Children[1].Children[0].Iter.Column == 5

            assert results.Children[1].Children[1].Parent == results.Children[1]
            assert results.Children[1].Children[1].Type == self._upper_lower_statement

            assert len(results.Children[1].Children[1].Children) == 3

            assert results.Children[1].Children[1].Children[0].Parent == results.Children[1].Children[1]
            assert results.Children[1].Children[1].Children[0].Type == self._upper_token
            assert results.Children[1].Children[1].Children[0].Value.Match.group("value") == "FIVE"
            assert results.Children[1].Children[1].Children[0].Whitespace == (19, 23)
            assert results.Children[1].Children[1].Children[0].Iter.Line == 2
            assert results.Children[1].Children[1].Children[0].Iter.Column == 13

            assert results.Children[1].Children[1].Children[1].Parent == results.Children[1].Children[1]
            assert results.Children[1].Children[1].Children[1].Type == self._lower_token
            assert results.Children[1].Children[1].Children[1].Value.Match.group("value") == "six"
            assert results.Children[1].Children[1].Children[1].Whitespace == (27, 28)
            assert results.Children[1].Children[1].Children[1].Iter.Line == 2
            assert results.Children[1].Children[1].Children[1].Iter.Column == 17

            assert results.Children[1].Children[1].Children[2].Parent == results.Children[1].Children[1]
            assert results.Children[1].Children[1].Children[2].Type == NewlineToken()
            assert results.Children[1].Children[1].Children[2].Value == Token.NewlineMatch(31, 32)
            assert results.Children[1].Children[1].Children[2].Whitespace is None
            assert results.Children[1].Children[1].Children[2].Iter.Line == 3
            assert results.Children[1].Children[1].Children[2].Iter.Column == 1

            # Verify the callbacks
            assert observer.mock.call_count == 2

            observer.VerifyCallArgs(0, self._uul_statement, results.Children[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._lul_statement, results.Children[1], 2, 1, 3, 1)

# ----------------------------------------------------------------------
class TestNoMatchError(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number", re.compile(r"(?P<value>[0-9]+)"))

    _upper_statement                        = StandardStatement("Upper Number", [_upper_token, _number_token])
    _lower_statement                        = StandardStatement("Upper Lower", [_upper_token, _lower_token])

    _statements                             = DynamicStatementInfo([_upper_statement, _lower_statement], [])

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        with CreateObserver() as observer:
            with pytest.raises(SyntaxInvalidError) as ex:
                list(
                    ParseCoroutine(
                        NormalizedIterator(
                            Normalize(
                                textwrap.dedent(
                                    """\
                                    ONE INVALID
                                    """,
                                ),
                            ),
                        ),
                        self._statements,
                        observer,
                    ),
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
