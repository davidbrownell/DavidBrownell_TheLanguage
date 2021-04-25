# ----------------------------------------------------------------------
# |
# |  ParseGenerator_UnitTest.py
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
"""Unit test for ParseGenerator"""

import os
import re
import sys
import textwrap

from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import pytest

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

sys.path.insert(0, os.path.join(_script_dir, ".."))
with CallOnExit(lambda: sys.path.pop(0)):
    from Normalize import *
    from NormalizedIterator import NormalizedIterator
    from ParseGenerator import *
    from Statement import StandardStatement

    from Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken
    )

# ----------------------------------------------------------------------
class TestSimple(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number", re.compile(r"(?P<value>[0-9]+)"))

    _upper_statement                        = StandardStatement("Upper Statement", [_upper_token, NewlineToken()])
    _lower_statement                        = StandardStatement("Lower Statement", [_lower_token, NewlineToken()])
    _number_statement                       = StandardStatement("Number Statement", [_number_token, NewlineToken()])

    _statements                             = [_upper_statement, _lower_statement, _number_statement]

    # ----------------------------------------------------------------------
    def test_MatchStandard(self):
        with ThreadPoolExecutor() as executor:
            callback_mock = Mock(
                return_value=None,
            )

            results = list(
                Parse(
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
                    callback_mock,
                    executor,
                ),
            )

            # Verify the results
            assert len(results) == 1
            results = results[0]

            assert results.Parent is None
            assert len(results.Children) == 3

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._upper_statement

            assert len(results.Children[0].Children) == 2

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._upper_token
            assert results.Children[0].Children[0].Value.match.group("value") == "ONE"
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
            assert results.Children[1].Children[0].Value.match.group("value") == "two"
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
            assert results.Children[2].Children[0].Value.match.group("value") == "33333"
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
            assert callback_mock.call_count == 3

            assert callback_mock.call_args_list[0][0] == (self._upper_statement, results.Children[0], 2)
            assert callback_mock.call_args_list[1][0] == (self._lower_statement, results.Children[1], 3)
            assert callback_mock.call_args_list[2][0] == (self._number_statement, results.Children[2], 4)

    # ----------------------------------------------------------------------
    def test_MatchReverse(self):
        with ThreadPoolExecutor() as executor:
            callback_mock = Mock(
                return_value=None,
            )

            results = list(
                Parse(
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
                    callback_mock,
                    executor,
                ),
            )

            # Verify the results
            assert len(results) == 1
            results = results[0]

            assert results.Parent is None
            assert len(results.Children) == 3

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._number_statement

            assert len(results.Children[0].Children) == 2

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._number_token
            assert results.Children[0].Children[0].Value.match.group("value") == "33"
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
            assert results.Children[1].Children[0].Value.match.group("value") == "twoooooooo"
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
            assert results.Children[2].Children[0].Value.match.group("value") == "ONE"
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
            assert callback_mock.call_count == 3

            assert callback_mock.call_args_list[0][0] == (self._number_statement, results.Children[0], 2)
            assert callback_mock.call_args_list[1][0] == (self._lower_statement, results.Children[1], 3)
            assert callback_mock.call_args_list[2][0] == (self._upper_statement, results.Children[2], 4)

    # ----------------------------------------------------------------------
    def test_MatchSame(self):
        with ThreadPoolExecutor() as executor:
            callback_mock = Mock(
                return_value=None,
            )

            results = list(
                Parse(
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
                    callback_mock,
                    executor,
                ),
            )

            # Verify the results
            assert len(results) == 1
            results = results[0]

            assert results.Parent is None
            assert len(results.Children) == 3

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._number_statement

            assert len(results.Children[0].Children) == 2

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._number_token
            assert results.Children[0].Children[0].Value.match.group("value") == "1"
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
            assert results.Children[1].Children[0].Value.match.group("value") == "22"
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
            assert results.Children[2].Children[0].Value.match.group("value") == "333"
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
            assert callback_mock.call_count == 3

            assert callback_mock.call_args_list[0][0] == (self._number_statement, results.Children[0], 2)
            assert callback_mock.call_args_list[1][0] == (self._number_statement, results.Children[1], 3)
            assert callback_mock.call_args_list[2][0] == (self._number_statement, results.Children[2], 4)

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

    _statements                             = [ _statement ]

    # ----------------------------------------------------------------------
    def test_Match(self):
        with ThreadPoolExecutor() as executor:
            callback_mock = Mock(
                return_value=None,
            )

            results = list(
                Parse(
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
                    callback_mock,
                    executor,
                ),
            )

            # Verify the results
            assert len(results) == 1
            results = results[0]

            assert results.Parent is None
            assert len(results.Children) == 1

            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._statement

            assert len(results.Children[0].Children) == 7

            # Line 1
            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._upper_token
            assert results.Children[0].Children[0].Value.match.group("value") == "ONE"
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
            assert results.Children[0].Children[3].Value.match.group("value") == "TWO"
            assert results.Children[0].Children[3].Whitespace is None
            assert results.Children[0].Children[3].Iter.Line == 2
            assert results.Children[0].Children[3].Iter.Column == 8

            assert results.Children[0].Children[4].Parent == results.Children[0]
            assert results.Children[0].Children[4].Type == self._upper_token
            assert results.Children[0].Children[4].Value.match.group("value") == "THREE"
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
            assert callback_mock.call_count == 1

            assert callback_mock.call_args_list[0][0] == (self._statement, results.Children[0], 3)

# ----------------------------------------------------------------------
class TestNewStatements(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))

    _upper_statement                        = StandardStatement("Upper Statement", [_upper_token])
    _lower_statement                        = StandardStatement("Lower Statement", [_lower_token, NewlineToken()])

    _statements                             = [_upper_statement]
    _new_statements                         = [_lower_statement]

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        with ThreadPoolExecutor() as executor:
            # The callback isn't returning any new statements; therefore an
            # error will be generated when attempting to parse the lowercase
            # token.
            callback_mock = Mock(
                return_value=None,
            )

            with pytest.raises(SyntaxErrorException) as ex:
                results = list(
                    Parse(
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
                        callback_mock,
                        executor,
                    ),
                )

            ex = ex.value

            # Validate
            assert ex.Line == 1
            assert ex.Column == 4
            assert ex.Message == "The syntax is not recognized"
            assert not ex.Potentials

    # ----------------------------------------------------------------------
    def test_Match(self):
        with ThreadPoolExecutor() as executor:
            callback_mock = Mock()

            callback_mock.side_effect = [self._new_statements, None]

            results = list(
                Parse(
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
                    callback_mock,
                    executor,
                ),
            )

            # Verify the results
            assert len(results) == 1
            results = results[0]

            assert results.Parent is None
            assert len(results.Children) == 2

            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._upper_statement

            assert len(results.Children[0].Children) == 1

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._upper_token
            assert results.Children[0].Children[0].Value.match.group("value") == "ONE"
            assert results.Children[0].Children[0].Whitespace is None
            assert results.Children[0].Children[0].Iter.Line == 1
            assert results.Children[0].Children[0].Iter.Column == 4

            assert results.Children[1].Parent == results
            assert results.Children[1].Type == self._lower_statement

            assert len(results.Children[1].Children) == 2

            assert results.Children[1].Children[0].Parent == results.Children[1]
            assert results.Children[1].Children[0].Type == self._lower_token
            assert results.Children[1].Children[0].Value.match.group("value") == "two"
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
            assert callback_mock.call_count == 2

            assert callback_mock.call_args_list[0][0] == (self._upper_statement, results.Children[0], 1)
            assert callback_mock.call_args_list[1][0] == (self._lower_statement, results.Children[1], 2)

# ----------------------------------------------------------------------
class TestNewScopedStatements(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))

    _upper_statement                        = StandardStatement("Upper Statement", [_upper_token])
    _lower_statement                        = StandardStatement("Lower Statement", [_lower_token])

    _newline_statement                      = StandardStatement("Newline Statement", [NewlineToken()])
    _indent_statement                       = StandardStatement("Indent Statement", [IndentToken()])
    _dedent_statement                       = StandardStatement("Dedent Statement", [DedentToken()])

    _statements                             = [_upper_statement, _newline_statement, _indent_statement, _dedent_statement]
    _new_statements                         = [_lower_statement]

    # ----------------------------------------------------------------------
    def test_Match(self):
        with ThreadPoolExecutor() as executor:
            callback_mock = Mock()

            callback_mock.side_effect = [
                None,                       # ONE
                None,                       # Newline
                self._new_statements,       # Indent
                None,                       # two
                None,                       # Newline
                None,                       # Dedent
            ]

            results = list(
                Parse(
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
                    callback_mock,
                    executor,
                ),
            )

            # Verify the results
            assert len(results) == 1
            results = results[0]

            assert results.Parent is None
            assert len(results.Children) == 6

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._upper_statement

            assert len(results.Children[0].Children) == 1

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._upper_token
            assert results.Children[0].Children[0].Value.match.group("value") == "ONE"
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
            assert results.Children[3].Children[0].Value.match.group("value") == "two"
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
            assert callback_mock.call_count == 6

            assert callback_mock.call_args_list[0][0] == (self._upper_statement, results.Children[0], 1)
            assert callback_mock.call_args_list[1][0] == (self._newline_statement, results.Children[1], 2)
            assert callback_mock.call_args_list[2][0] == (self._indent_statement, results.Children[2], 2)
            assert callback_mock.call_args_list[3][0] == (self._lower_statement, results.Children[3], 2)
            assert callback_mock.call_args_list[4][0] == (self._newline_statement, results.Children[4], 3)
            assert callback_mock.call_args_list[5][0] == (self._dedent_statement, results.Children[5], 3)

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        with ThreadPoolExecutor() as executor:
            callback_mock = Mock()

            callback_mock.side_effect = [
                None,                       # ONE
                None,                       # Newline
                self._new_statements,       # Indent
                None,                       # two
                None,                       # Newline
                None,                       # Dedent
            ]

            with pytest.raises(SyntaxErrorException) as ex:
                results = list(
                    Parse(
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
                        callback_mock,
                        executor,
                    ),
                )

            ex = ex.value

            # Validate
            assert ex.Line == 4
            assert ex.Column == 1
            assert ex.Message == "The syntax is not recognized"
            assert not ex.Potentials


# ----------------------------------------------------------------------
class TestCallable(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _upper_statement                        = StandardStatement("Upper Statement", [_upper_token, NewlineToken()])

    _statements                             = [_upper_statement]

    # ----------------------------------------------------------------------
    def test_Standard(self):
        with ThreadPoolExecutor() as executor:
            callback_mock = Mock(
                return_value=None,
            )

            callback_mock.side_effect = [
                None,
                lambda: None,
                None,
                lambda: None,
                None,
            ]

            results = list(
                Parse(
                    NormalizedIterator(
                        Normalize(
                            textwrap.dedent(
                                """\
                                ONE
                                TWO
                                THREE
                                FOUR
                                FIVE
                                """,
                            ),
                        ),
                    ),
                    self._statements,
                    callback_mock,
                    executor,
                ),
            )

            # Verify the results
            assert len(results) == 3

            assert callable(results[0])
            assert results[0]() is None

            assert callable(results[1])
            assert results[1]() is None

            results = results[2]

            assert results.Parent is None
            assert len(results.Children) == 5

            # Line 1
            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._upper_token
            assert results.Children[0].Children[0].Value.match.group("value") == "ONE"
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
            assert results.Children[1].Children[0].Parent == results.Children[1]
            assert results.Children[1].Children[0].Type == self._upper_token
            assert results.Children[1].Children[0].Value.match.group("value") == "TWO"
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
            assert results.Children[2].Children[0].Parent == results.Children[2]
            assert results.Children[2].Children[0].Type == self._upper_token
            assert results.Children[2].Children[0].Value.match.group("value") == "THREE"
            assert results.Children[2].Children[0].Whitespace is None
            assert results.Children[2].Children[0].Iter.Line == 3
            assert results.Children[2].Children[0].Iter.Column == 6

            assert results.Children[2].Children[1].Parent == results.Children[2]
            assert results.Children[2].Children[1].Type == NewlineToken()
            assert results.Children[2].Children[1].Value == Token.NewlineMatch(13, 14)
            assert results.Children[2].Children[1].Whitespace is None
            assert results.Children[2].Children[1].Iter.Line == 4
            assert results.Children[2].Children[1].Iter.Column == 1

            # Line 4
            assert results.Children[3].Children[0].Parent == results.Children[3]
            assert results.Children[3].Children[0].Type == self._upper_token
            assert results.Children[3].Children[0].Value.match.group("value") == "FOUR"
            assert results.Children[3].Children[0].Whitespace is None
            assert results.Children[3].Children[0].Iter.Line == 4
            assert results.Children[3].Children[0].Iter.Column == 5

            assert results.Children[3].Children[1].Parent == results.Children[3]
            assert results.Children[3].Children[1].Type == NewlineToken()
            assert results.Children[3].Children[1].Value == Token.NewlineMatch(18, 19)
            assert results.Children[3].Children[1].Whitespace is None
            assert results.Children[3].Children[1].Iter.Line == 5
            assert results.Children[3].Children[1].Iter.Column == 1

            # Line 5
            assert results.Children[4].Children[0].Parent == results.Children[4]
            assert results.Children[4].Children[0].Type == self._upper_token
            assert results.Children[4].Children[0].Value.match.group("value") == "FIVE"
            assert results.Children[4].Children[0].Whitespace is None
            assert results.Children[4].Children[0].Iter.Line == 5
            assert results.Children[4].Children[0].Iter.Column == 5

            assert results.Children[4].Children[1].Parent == results.Children[4]
            assert results.Children[4].Children[1].Type == NewlineToken()
            assert results.Children[4].Children[1].Value == Token.NewlineMatch(23, 24)
            assert results.Children[4].Children[1].Whitespace is None
            assert results.Children[4].Children[1].Iter.Line == 6
            assert results.Children[4].Children[1].Iter.Column == 1

            # Verify the callbacks
            assert callback_mock.call_count == 5

            assert callback_mock.call_args_list[0][0] == (self._upper_statement, results.Children[0], 2)
            assert callback_mock.call_args_list[1][0] == (self._upper_statement, results.Children[1], 3)
            assert callback_mock.call_args_list[2][0] == (self._upper_statement, results.Children[2], 4)
            assert callback_mock.call_args_list[3][0] == (self._upper_statement, results.Children[3], 5)
            assert callback_mock.call_args_list[4][0] == (self._upper_statement, results.Children[4], 6)

# ----------------------------------------------------------------------
class TestEmbeddedStatements(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Upper", re.compile(r"(?P<value>[a-z]+)"))

    _upper_lower_statement                  = StandardStatement("Upper Lower Statement", [_upper_token, _lower_token, NewlineToken()])

    _uul_statement                          = StandardStatement("UUL", [_upper_token, _upper_lower_statement])
    _lul_statement                          = StandardStatement("LUL", [_lower_token, _upper_lower_statement])

    _statements                             = [_uul_statement, _lul_statement]

    # ----------------------------------------------------------------------
    def test_Match(self):
        with ThreadPoolExecutor() as executor:
            callback_mock = Mock(
                return_value=None,
            )

            results = list(
                Parse(
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
                    callback_mock,
                    executor,
                ),
            )

            # Verify the results
            assert len(results) == 1
            results = results[0]

            assert results.Parent is None
            assert len(results.Children) == 2

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._uul_statement

            assert len(results.Children[0].Children) == 2

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._upper_token
            assert results.Children[0].Children[0].Value.match.group("value") == "ONE"
            assert results.Children[0].Children[0].Whitespace is None
            assert results.Children[0].Children[0].Iter.Line == 1
            assert results.Children[0].Children[0].Iter.Column == 4

            assert results.Children[0].Children[1].Parent == results.Children[0]
            assert results.Children[0].Children[1].Type == self._upper_lower_statement

            assert len(results.Children[0].Children[1].Children) == 3

            assert results.Children[0].Children[1].Children[0].Parent == results.Children[0].Children[1]
            assert results.Children[0].Children[1].Children[0].Type == self._upper_token
            assert results.Children[0].Children[1].Children[0].Value.match.group("value") == "TWO"
            assert results.Children[0].Children[1].Children[0].Whitespace == (3, 4)
            assert results.Children[0].Children[1].Children[0].Iter.Line == 1
            assert results.Children[0].Children[1].Children[0].Iter.Column == 8

            assert results.Children[0].Children[1].Children[1].Parent == results.Children[0].Children[1]
            assert results.Children[0].Children[1].Children[1].Type == self._lower_token
            assert results.Children[0].Children[1].Children[1].Value.match.group("value") == "three"
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
            assert results.Children[1].Children[0].Value.match.group("value") == "four"
            assert results.Children[1].Children[0].Whitespace is None
            assert results.Children[1].Children[0].Iter.Line == 2
            assert results.Children[1].Children[0].Iter.Column == 5

            assert results.Children[1].Children[1].Parent == results.Children[1]
            assert results.Children[1].Children[1].Type == self._upper_lower_statement

            assert len(results.Children[1].Children[1].Children) == 3

            assert results.Children[1].Children[1].Children[0].Parent == results.Children[1].Children[1]
            assert results.Children[1].Children[1].Children[0].Type == self._upper_token
            assert results.Children[1].Children[1].Children[0].Value.match.group("value") == "FIVE"
            assert results.Children[1].Children[1].Children[0].Whitespace == (19, 23)
            assert results.Children[1].Children[1].Children[0].Iter.Line == 2
            assert results.Children[1].Children[1].Children[0].Iter.Column == 13

            assert results.Children[1].Children[1].Children[1].Parent == results.Children[1].Children[1]
            assert results.Children[1].Children[1].Children[1].Type == self._lower_token
            assert results.Children[1].Children[1].Children[1].Value.match.group("value") == "six"
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
            assert callback_mock.call_count == 2

            assert callback_mock.call_args_list[0][0] == (self._uul_statement, results.Children[0], 2)
            assert callback_mock.call_args_list[1][0] == (self._lul_statement, results.Children[1], 3)

# ----------------------------------------------------------------------
class TestNoMatchError(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number", re.compile(r"(?P<value>[0-9]+)"))

    _upper_statement                        = StandardStatement("Upper Number", [_upper_token, _number_token])
    _lower_statement                        = StandardStatement("Upper Lower", [_upper_token, _lower_token])

    _statements                             = [_upper_statement, _lower_statement]

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        with ThreadPoolExecutor() as executor:
            callback_mock = Mock(
                return_value=None,
            )

            with pytest.raises(SyntaxErrorException) as ex:
                list(
                    Parse(
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
                        callback_mock,
                        executor,
                    ),
                )

            ex = ex.value

            # Validate
            assert ex.Line == 1
            assert ex.Column == 1
            assert ex.Message == "The syntax is not recognized"

            assert len(ex.Potentials) == 2

            assert len(ex.Potentials[self._upper_statement].results) == 1
            assert ex.Potentials[self._upper_statement].results[0].token == self._upper_token
            assert ex.Potentials[self._upper_statement].results[0].iter.Line == 1
            assert ex.Potentials[self._upper_statement].results[0].iter.Column == 4

            assert len(ex.Potentials[self._lower_statement].results) == 1
            assert ex.Potentials[self._lower_statement].results[0].token == self._upper_token
            assert ex.Potentials[self._lower_statement].results[0].iter.Line == 1
            assert ex.Potentials[self._lower_statement].results[0].iter.Column == 4

# ----------------------------------------------------------------------
class TestAmbiguousError(object):
    _upper_token                            = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
    _upper_statement1                       = StandardStatement("Upper1", [_upper_token])
    _upper_statement2                       = StandardStatement("Upper2", [_upper_token])

    _statements                             = [_upper_statement1, _upper_statement2]

    # ----------------------------------------------------------------------
    def test_NoMatch(self):
        with ThreadPoolExecutor() as executor:
            callback_mock = Mock(
                return_value=None,
            )

            with pytest.raises(SyntaxAmbiguousException) as ex:
                list(
                    Parse(
                        NormalizedIterator(
                            Normalize(
                                textwrap.dedent(
                                    """\
                                    ONE
                                    """,
                                ),
                            ),
                        ),
                        self._statements,
                        callback_mock,
                        executor,
                    ),
                )

            ex = ex.value

            # Validate
            assert ex.Line == 1
            assert ex.Column == 1
            assert ex.Message == "The syntax is ambiguous"

            assert len(ex.Potentials) == 2

            assert len(ex.Potentials[self._upper_statement1].results) == 1
            assert ex.Potentials[self._upper_statement1].results[0].token == self._upper_token
            assert ex.Potentials[self._upper_statement1].results[0].iter.Line == 1
            assert ex.Potentials[self._upper_statement1].results[0].iter.Column == 4

            assert len(ex.Potentials[self._upper_statement2].results) == 1
            assert ex.Potentials[self._upper_statement2].results[0].token == self._upper_token
            assert ex.Potentials[self._upper_statement2].results[0].iter.Line == 1
            assert ex.Potentials[self._upper_statement2].results[0].iter.Column == 4
