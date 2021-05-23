# ----------------------------------------------------------------------
# |
# |  MultifileParser_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-11 14:25:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for MultifileParser.py"""

import os
import re
import textwrap

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import cast
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
    from ..MultifileParser import *
    from ..Normalize import Normalize
    from ..NormalizedIterator import NormalizedIterator
    from ..StandardStatement import StandardStatement
    from ..Statement import DynamicStatements
    from ..StatementsParser import SyntaxInvalidError

    from ..Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
        Token,
    )


# ----------------------------------------------------------------------
class TestStandard(object):
    _content_dict                           = {
        "upper" : textwrap.dedent(
            """\
            FOUR
            FIVE
            SIX
            """,
        ),
        "lower" : textwrap.dedent(
            """\
            four
            five
            six
            """,
        ),
        "number" : textwrap.dedent(
            """\
            4
            5
            6
            """,
        ),
    }

    _include_token                          = RegexToken("Include Token", re.compile(r"(?P<value>include)"))
    _upper_token                            = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower Token", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number Token", re.compile(r"(?P<value>[0-9]+)"))

    _include_statement                      = StandardStatement([_include_token, _lower_token, NewlineToken()])
    _upper_statement                        = StandardStatement([_upper_token, NewlineToken()])
    _lower_statement                        = StandardStatement([_lower_token, NewlineToken()])
    _number_statement                       = StandardStatement([_number_token, NewlineToken()])

    _new_scope_statement                    = StandardStatement(
        [
            _upper_token,
            RegexToken("Colon Token", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            DynamicStatements.Statements,
            DynamicStatements.Statements,
            DedentToken(),
        ],
    )

    _dynamic_number_statement               = StandardStatement([_number_token, _number_token, _number_token, NewlineToken()])

    _statements                             = DynamicStatementInfo(
        [_include_statement, _upper_statement, _lower_statement, _number_statement, _new_scope_statement],
        [],
    )

    # ----------------------------------------------------------------------
    @classmethod
    @contextmanager
    def CreateObserver(
        cls,
        content_dict,
        num_threads=None,
    ):
        for k, v in cls._content_dict.items():
            if k not in content_dict:
                content_dict[k] = v

        with ThreadPoolExecutor(
            max_workers=num_threads,
        ) as executor:
            # ----------------------------------------------------------------------
            class MyObserver(Observer):
                # ----------------------------------------------------------------------
                def __init__(self):
                    self.mock = Mock(
                        return_value=True,
                    )

                # ----------------------------------------------------------------------
                def VerifyCallArgs(self, index, statement, node, before_line, before_col, after_line, after_col):
                    callback_args = self.mock.call_args_list[index][0]

                    assert callback_args[0].Statement == statement
                    assert callback_args[1].Line == before_line
                    assert callback_args[1].Column == before_col
                    assert callback_args[2].Line == after_line
                    assert callback_args[2].Column == after_col

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                def LoadContent(
                    fully_qualified_name: str,
                ) -> str:
                    assert fully_qualified_name in content_dict
                    return content_dict[fully_qualified_name]

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                def ExtractDynamicStatementInfo(fully_qualified_name, node):
                    if fully_qualified_name == "number":
                        return DynamicStatementInfo([cls._dynamic_number_statement], [])

                    return DynamicStatementInfo([], [])

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                def Enqueue(funcs):
                    return [executor.submit(func) for func in funcs]

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                def OnIndent(
                    fully_qualified_name: str,
                    statement: Statement,
                    results: Statement.ParseResultItemsType,
                ):
                    pass

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                def OnDedent(
                    fully_qualified_name: str,
                    statement: Statement,
                    results: Statement.ParseResultItemsType,
                ):
                    pass

                # ----------------------------------------------------------------------
                @Interface.override
                def OnStatementComplete(
                    self,
                    fully_qualified_name,
                    result,
                    iter_before,
                    iter_after,
                ):
                    if result.Statement == cls._include_statement:
                        assert len(result.Results) == 3

                        value = result.Results[1].Value.Match.group("value")
                        return Observer.ImportInfo(value, value if value in cls._content_dict else None)

                    return self.mock(result, iter_before, iter_after)

            # ----------------------------------------------------------------------

            yield MyObserver()

    # ----------------------------------------------------------------------
    def test_NoInclude(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    one
                    TWO
                    3
                    """,
                ),
            },
            num_threads=5,
        ) as observer:
            results = Parse(
                ["one"],
                self._statements,
                observer,
            )

            # Verify the results
            assert len(results) == 1
            assert "one" in results
            results = results["one"]

            assert results.Parent is None
            assert results.Type is None
            assert len(results.Children) == 3

            # Line 1
            assert results.Children[0].Parent == results
            assert results.Children[0].Type == self._lower_statement

            assert len(results.Children[0].Children) == 2

            assert results.Children[0].Children[0].Parent == results.Children[0]
            assert results.Children[0].Children[0].Type == self._lower_token
            assert results.Children[0].Children[0].Value.Match.group("value") == "one"
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
            assert results.Children[1].Type == self._upper_statement

            assert len(results.Children[1].Children) == 2

            assert results.Children[1].Children[0].Parent == results.Children[1]
            assert results.Children[1].Children[0].Type == self._upper_token
            assert results.Children[1].Children[0].Value.Match.group("value") == "TWO"
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
            assert results.Children[2].Children[0].Value.Match.group("value") == "3"
            assert results.Children[2].Children[0].Whitespace is None
            assert results.Children[2].Children[0].Iter.Line == 3
            assert results.Children[2].Children[0].Iter.Column == 2

            assert results.Children[2].Children[1].Parent == results.Children[2]
            assert results.Children[2].Children[1].Type == NewlineToken()
            assert results.Children[2].Children[1].Value == Token.NewlineMatch(9, 10)
            assert results.Children[2].Children[1].Whitespace is None
            assert results.Children[2].Children[1].Iter.Line == 4
            assert results.Children[2].Children[1].Iter.Column == 1

            assert results.Children[2].Children[1].Iter.AtEnd()

            # Verify the callbacks
            assert observer.mock.call_count == 3

            observer.VerifyCallArgs(0, self._lower_statement, results.Children[0], 1, 1, 2, 1)
            observer.VerifyCallArgs(1, self._upper_statement, results.Children[1], 2, 1, 3, 1)
            observer.VerifyCallArgs(2, self._number_statement, results.Children[2], 3, 1, 4, 1)

    # ----------------------------------------------------------------------
    def test_SingleInclude(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    one
                    TWO
                    include number
                    3
                    """,
                ),
            },
            num_threads=5,
        ) as observer:
            all_results = Parse(
                ["one"],
                self._statements,
                observer,
            )

            # Verify the results
            assert len(all_results) == 2
            assert "one" in all_results
            assert "number" in all_results

            one_results = all_results["one"]

            assert one_results.Parent is None
            assert one_results.Type is None
            assert len(one_results.Children) == 4

            # Line 1
            assert one_results.Children[0].Parent == one_results
            assert one_results.Children[0].Type == self._lower_statement

            assert len(one_results.Children[0].Children) == 2

            assert one_results.Children[0].Children[0].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[0].Type == self._lower_token
            assert one_results.Children[0].Children[0].Value.Match.group("value") == "one"
            assert one_results.Children[0].Children[0].Whitespace is None
            assert one_results.Children[0].Children[0].Iter.Line == 1
            assert one_results.Children[0].Children[0].Iter.Column == 4

            assert one_results.Children[0].Children[1].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[1].Type == NewlineToken()
            assert one_results.Children[0].Children[1].Value == Token.NewlineMatch(3, 4)
            assert one_results.Children[0].Children[1].Whitespace is None
            assert one_results.Children[0].Children[1].Iter.Line == 2
            assert one_results.Children[0].Children[1].Iter.Column == 1

            # Line 2
            assert one_results.Children[1].Parent == one_results
            assert one_results.Children[1].Type == self._upper_statement

            assert len(one_results.Children[1].Children) == 2

            assert one_results.Children[1].Children[0].Parent == one_results.Children[1]
            assert one_results.Children[1].Children[0].Type == self._upper_token
            assert one_results.Children[1].Children[0].Value.Match.group("value") == "TWO"
            assert one_results.Children[1].Children[0].Whitespace is None
            assert one_results.Children[1].Children[0].Iter.Line == 2
            assert one_results.Children[1].Children[0].Iter.Column == 4

            assert one_results.Children[1].Children[1].Parent == one_results.Children[1]
            assert one_results.Children[1].Children[1].Type == NewlineToken()
            assert one_results.Children[1].Children[1].Value == Token.NewlineMatch(7, 8)
            assert one_results.Children[1].Children[1].Whitespace is None
            assert one_results.Children[1].Children[1].Iter.Line == 3
            assert one_results.Children[1].Children[1].Iter.Column == 1

            # Line 3
            assert one_results.Children[2].Parent == one_results
            assert one_results.Children[2].Type == self._include_statement

            assert len(one_results.Children[2].Children) == 3

            assert one_results.Children[2].Children[0].Parent == one_results.Children[2]
            assert one_results.Children[2].Children[0].Type == self._include_token
            assert one_results.Children[2].Children[0].Value.Match.group("value") == "include"
            assert one_results.Children[2].Children[0].Whitespace is None
            assert one_results.Children[2].Children[0].Iter.Line == 3
            assert one_results.Children[2].Children[0].Iter.Column == 8

            assert one_results.Children[2].Children[1].Parent == one_results.Children[2]
            assert one_results.Children[2].Children[1].Type == self._lower_token
            assert one_results.Children[2].Children[1].Value.Match.group("value") == "number"
            assert one_results.Children[2].Children[1].Whitespace == (15, 16)
            assert one_results.Children[2].Children[1].Iter.Line == 3
            assert one_results.Children[2].Children[1].Iter.Column == 15

            assert one_results.Children[2].Children[2].Parent == one_results.Children[2]
            assert one_results.Children[2].Children[2].Type == NewlineToken()
            assert one_results.Children[2].Children[2].Value == Token.NewlineMatch(22, 23)
            assert one_results.Children[2].Children[2].Whitespace is None
            assert one_results.Children[2].Children[2].Iter.Line == 4
            assert one_results.Children[2].Children[2].Iter.Column == 1

            # Line 4
            assert one_results.Children[3].Parent == one_results
            assert one_results.Children[3].Type == self._number_statement

            assert len(one_results.Children[3].Children) == 2

            assert one_results.Children[3].Children[0].Parent == one_results.Children[3]
            assert one_results.Children[3].Children[0].Type == self._number_token
            assert one_results.Children[3].Children[0].Value.Match.group("value") == "3"
            assert one_results.Children[3].Children[0].Whitespace is None
            assert one_results.Children[3].Children[0].Iter.Line == 4
            assert one_results.Children[3].Children[0].Iter.Column == 2

            assert one_results.Children[3].Children[1].Parent == one_results.Children[3]
            assert one_results.Children[3].Children[1].Type == NewlineToken()
            assert one_results.Children[3].Children[1].Value == Token.NewlineMatch(24, 25)
            assert one_results.Children[3].Children[1].Whitespace is None
            assert one_results.Children[3].Children[1].Iter.Line == 5
            assert one_results.Children[3].Children[1].Iter.Column == 1

            assert one_results.Children[3].Children[1].Iter.AtEnd()

            # Verify the other
            number_results = all_results["number"]

            assert number_results.Parent is None
            assert number_results.Type is None
            assert len(number_results.Children) == 3

            # Line 1
            assert number_results.Children[0].Parent == number_results
            assert number_results.Children[0].Type == self._number_statement

            assert len(number_results.Children[0].Children) == 2

            assert number_results.Children[0].Children[0].Parent == number_results.Children[0]
            assert number_results.Children[0].Children[0].Type == self._number_token
            assert number_results.Children[0].Children[0].Value.Match.group("value") == "4"
            assert number_results.Children[0].Children[0].Whitespace is None
            assert number_results.Children[0].Children[0].Iter.Line == 1
            assert number_results.Children[0].Children[0].Iter.Column == 2

            assert number_results.Children[0].Children[1].Parent == number_results.Children[0]
            assert number_results.Children[0].Children[1].Type == NewlineToken()
            assert number_results.Children[0].Children[1].Value == Token.NewlineMatch(1, 2)
            assert number_results.Children[0].Children[1].Whitespace is None
            assert number_results.Children[0].Children[1].Iter.Line == 2
            assert number_results.Children[0].Children[1].Iter.Column == 1

            # Line 2
            assert number_results.Children[1].Parent == number_results
            assert number_results.Children[1].Type == self._number_statement

            assert len(number_results.Children[1].Children) == 2

            assert number_results.Children[1].Children[0].Parent == number_results.Children[1]
            assert number_results.Children[1].Children[0].Type == self._number_token
            assert number_results.Children[1].Children[0].Value.Match.group("value") == "5"
            assert number_results.Children[1].Children[0].Whitespace is None
            assert number_results.Children[1].Children[0].Iter.Line == 2
            assert number_results.Children[1].Children[0].Iter.Column == 2

            assert number_results.Children[1].Children[1].Parent == number_results.Children[1]
            assert number_results.Children[1].Children[1].Type == NewlineToken()
            assert number_results.Children[1].Children[1].Value == Token.NewlineMatch(3, 4)
            assert number_results.Children[1].Children[1].Whitespace is None
            assert number_results.Children[1].Children[1].Iter.Line == 3
            assert number_results.Children[1].Children[1].Iter.Column == 1

            # Line 3
            assert number_results.Children[2].Parent == number_results
            assert number_results.Children[2].Type == self._number_statement

            assert len(number_results.Children[2].Children) == 2

            assert number_results.Children[2].Children[0].Parent == number_results.Children[2]
            assert number_results.Children[2].Children[0].Type == self._number_token
            assert number_results.Children[2].Children[0].Value.Match.group("value") == "6"
            assert number_results.Children[2].Children[0].Whitespace is None
            assert number_results.Children[2].Children[0].Iter.Line == 3
            assert number_results.Children[2].Children[0].Iter.Column == 2

            assert number_results.Children[2].Children[1].Parent == number_results.Children[2]
            assert number_results.Children[2].Children[1].Type == NewlineToken()
            assert number_results.Children[2].Children[1].Value == Token.NewlineMatch(5, 6)
            assert number_results.Children[2].Children[1].Whitespace is None
            assert number_results.Children[2].Children[1].Iter.Line == 4
            assert number_results.Children[2].Children[1].Iter.Column == 1

            assert number_results.Children[2].Children[1].Iter.AtEnd()

            # Verify the callbacks
            assert observer.mock.call_count == 6

            observer.VerifyCallArgs(0, self._lower_statement, one_results.Children[0], 1, 1, 2, 1)      # File 1, line 1
            observer.VerifyCallArgs(1, self._upper_statement, one_results.Children[1], 2, 1, 3, 1)      # File 1, line 2
            observer.VerifyCallArgs(2, self._number_statement, number_results.Children[0], 1, 1, 2, 1)  # File 2, line 1
            observer.VerifyCallArgs(3, self._number_statement, number_results.Children[1], 2, 1, 3, 1)  # File 2, line 2
            observer.VerifyCallArgs(4, self._number_statement, number_results.Children[2], 3, 1, 4, 1)  # File 2, line 3
            observer.VerifyCallArgs(5, self._number_statement, one_results.Children[3], 4, 1, 5, 1)     # File 1, line 4

    # ----------------------------------------------------------------------
    def test_DoubleImport(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    one
                    TWO
                    include number
                    3
                    include number
                    """,
                ),
            },
            num_threads=10,
        ) as observer:
            all_results = Parse(
                ["one"],
                self._statements,
                observer,
            )

            # Verify the results
            assert len(all_results) == 2
            assert "one" in all_results
            assert "number" in all_results

            one_results = all_results["one"]
            number_results = all_results["number"]

            # Verify the callbacks
            assert observer.mock.call_count == 6

            observer.VerifyCallArgs(0, self._lower_statement, one_results.Children[0], 1, 1, 2, 1)      # File 1, line 1
            observer.VerifyCallArgs(1, self._upper_statement, one_results.Children[1], 2, 1, 3, 1)      # File 1, line 2
            observer.VerifyCallArgs(2, self._number_statement, number_results.Children[0], 1, 1, 2, 1)  # File 2, line 1
            observer.VerifyCallArgs(3, self._number_statement, number_results.Children[1], 2, 1, 3, 1)  # File 2, line 2
            observer.VerifyCallArgs(4, self._number_statement, number_results.Children[2], 3, 1, 4, 1)  # File 2, line 3
            observer.VerifyCallArgs(5, self._number_statement, one_results.Children[3], 4, 1, 5, 1)     # File 1, line 4

    # ----------------------------------------------------------------------
    def test_InvalidImport(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    one
                    TWO
                    include invalid
                    3
                    """,
                ),
            },
            num_threads=10,
        ) as observer:
            results = Parse(
                ["one"],
                self._statements,
                observer,
            )

            assert len(results) == 1
            results = results[0]

            assert str(results) == "'invalid' could not be found"
            assert results.Line == 3
            assert results.Column == 1
            assert results.SourceName == "invalid"
            assert results.FullyQualifiedName == "one"

    # ----------------------------------------------------------------------
    def test_MultipleFilesSingleImport(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    one
                    TWO
                    include number
                    3
                    """,
                ),
                "two" : textwrap.dedent(
                    """\
                    aaa
                    BBBB
                    include number
                    cccccc
                    """,
                ),
            },
            num_threads=10,
        ) as observer:
            results = Parse(
                ["one", "two"],
                self._statements,
                observer,
            )

            # Verify the results
            assert len(results) == 3
            assert "number" in results
            assert "one" in results
            assert "two" in results

            # one
            one_results = results["one"]

            assert one_results.Parent is None
            assert one_results.Type is None
            assert len(one_results.Children) == 4

            # Line 1
            assert one_results.Children[0].Parent == one_results
            assert one_results.Children[0].Type == self._lower_statement

            assert len(one_results.Children[0].Children) == 2

            assert one_results.Children[0].Children[0].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[0].Type == self._lower_token
            assert one_results.Children[0].Children[0].Value.Match.group("value") == "one"
            assert one_results.Children[0].Children[0].Whitespace is None
            assert one_results.Children[0].Children[0].Iter.Line == 1
            assert one_results.Children[0].Children[0].Iter.Column == 4

            assert one_results.Children[0].Children[1].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[1].Type == NewlineToken()
            assert one_results.Children[0].Children[1].Value == Token.NewlineMatch(3, 4)
            assert one_results.Children[0].Children[1].Whitespace is None
            assert one_results.Children[0].Children[1].Iter.Line == 2
            assert one_results.Children[0].Children[1].Iter.Column == 1

            # Line 2
            assert one_results.Children[1].Parent == one_results
            assert one_results.Children[1].Type == self._upper_statement

            assert len(one_results.Children[1].Children) == 2

            assert one_results.Children[1].Children[0].Parent == one_results.Children[1]
            assert one_results.Children[1].Children[0].Type == self._upper_token
            assert one_results.Children[1].Children[0].Value.Match.group("value") == "TWO"
            assert one_results.Children[1].Children[0].Whitespace is None
            assert one_results.Children[1].Children[0].Iter.Line == 2
            assert one_results.Children[1].Children[0].Iter.Column == 4

            assert one_results.Children[1].Children[1].Parent == one_results.Children[1]
            assert one_results.Children[1].Children[1].Type == NewlineToken()
            assert one_results.Children[1].Children[1].Value == Token.NewlineMatch(7, 8)
            assert one_results.Children[1].Children[1].Whitespace is None
            assert one_results.Children[1].Children[1].Iter.Line == 3
            assert one_results.Children[1].Children[1].Iter.Column == 1

            # Line 3
            assert one_results.Children[2].Parent == one_results
            assert one_results.Children[2].Type == self._include_statement

            assert len(one_results.Children[2].Children) == 3

            assert one_results.Children[2].Children[0].Parent == one_results.Children[2]
            assert one_results.Children[2].Children[0].Type == self._include_token
            assert one_results.Children[2].Children[0].Value.Match.group("value") == "include"
            assert one_results.Children[2].Children[0].Whitespace is None
            assert one_results.Children[2].Children[0].Iter.Line == 3
            assert one_results.Children[2].Children[0].Iter.Column == 8

            assert one_results.Children[2].Children[1].Parent == one_results.Children[2]
            assert one_results.Children[2].Children[1].Type == self._lower_token
            assert one_results.Children[2].Children[1].Value.Match.group("value") == "number"
            assert one_results.Children[2].Children[1].Whitespace == (15, 16)
            assert one_results.Children[2].Children[1].Iter.Line == 3
            assert one_results.Children[2].Children[1].Iter.Column == 15

            assert one_results.Children[2].Children[2].Parent == one_results.Children[2]
            assert one_results.Children[2].Children[2].Type == NewlineToken()
            assert one_results.Children[2].Children[2].Value == Token.NewlineMatch(22, 23)
            assert one_results.Children[2].Children[2].Whitespace is None
            assert one_results.Children[2].Children[2].Iter.Line == 4
            assert one_results.Children[2].Children[2].Iter.Column == 1

            # Line 4
            assert one_results.Children[3].Parent == one_results
            assert one_results.Children[3].Type == self._number_statement

            assert len(one_results.Children[3].Children) == 2

            assert one_results.Children[3].Children[0].Parent == one_results.Children[3]
            assert one_results.Children[3].Children[0].Type == self._number_token
            assert one_results.Children[3].Children[0].Value.Match.group("value") == "3"
            assert one_results.Children[3].Children[0].Whitespace is None
            assert one_results.Children[3].Children[0].Iter.Line == 4
            assert one_results.Children[3].Children[0].Iter.Column == 2

            assert one_results.Children[3].Children[1].Parent == one_results.Children[3]
            assert one_results.Children[3].Children[1].Type == NewlineToken()
            assert one_results.Children[3].Children[1].Value == Token.NewlineMatch(24, 25)
            assert one_results.Children[3].Children[1].Whitespace is None
            assert one_results.Children[3].Children[1].Iter.Line == 5
            assert one_results.Children[3].Children[1].Iter.Column == 1

            assert one_results.Children[3].Children[1].Iter.AtEnd()

            # two
            two_results = results["two"]

            assert two_results.Parent is None
            assert two_results.Type is None
            assert len(two_results.Children) == 4

            # Line 1
            assert two_results.Children[0].Parent == two_results
            assert two_results.Children[0].Type == self._lower_statement

            assert len(two_results.Children[0].Children) == 2

            assert two_results.Children[0].Children[0].Parent == two_results.Children[0]
            assert two_results.Children[0].Children[0].Type == self._lower_token
            assert two_results.Children[0].Children[0].Value.Match.group("value") == "aaa"
            assert two_results.Children[0].Children[0].Whitespace is None
            assert two_results.Children[0].Children[0].Iter.Line == 1
            assert two_results.Children[0].Children[0].Iter.Column == 4

            assert two_results.Children[0].Children[1].Parent == two_results.Children[0]
            assert two_results.Children[0].Children[1].Type == NewlineToken()
            assert two_results.Children[0].Children[1].Value == Token.NewlineMatch(3, 4)
            assert two_results.Children[0].Children[1].Whitespace is None
            assert two_results.Children[0].Children[1].Iter.Line == 2
            assert two_results.Children[0].Children[1].Iter.Column == 1

            # Line 2
            assert two_results.Children[1].Parent == two_results
            assert two_results.Children[1].Type == self._upper_statement

            assert len(two_results.Children[1].Children) == 2

            assert two_results.Children[1].Children[0].Parent == two_results.Children[1]
            assert two_results.Children[1].Children[0].Type == self._upper_token
            assert two_results.Children[1].Children[0].Value.Match.group("value") == "BBBB"
            assert two_results.Children[1].Children[0].Whitespace is None
            assert two_results.Children[1].Children[0].Iter.Line == 2
            assert two_results.Children[1].Children[0].Iter.Column == 5

            assert two_results.Children[1].Children[1].Parent == two_results.Children[1]
            assert two_results.Children[1].Children[1].Type == NewlineToken()
            assert two_results.Children[1].Children[1].Value == Token.NewlineMatch(8, 9)
            assert two_results.Children[1].Children[1].Whitespace is None
            assert two_results.Children[1].Children[1].Iter.Line == 3
            assert two_results.Children[1].Children[1].Iter.Column == 1

            # Line 3
            assert two_results.Children[2].Parent == two_results
            assert two_results.Children[2].Type == self._include_statement

            assert len(two_results.Children[2].Children) == 3

            assert two_results.Children[2].Children[0].Parent == two_results.Children[2]
            assert two_results.Children[2].Children[0].Type == self._include_token
            assert two_results.Children[2].Children[0].Value.Match.group("value") == "include"
            assert two_results.Children[2].Children[0].Whitespace is None
            assert two_results.Children[2].Children[0].Iter.Line == 3
            assert two_results.Children[2].Children[0].Iter.Column == 8

            assert two_results.Children[2].Children[1].Parent == two_results.Children[2]
            assert two_results.Children[2].Children[1].Type == self._lower_token
            assert two_results.Children[2].Children[1].Value.Match.group("value") == "number"
            assert two_results.Children[2].Children[1].Whitespace == (16, 17)
            assert two_results.Children[2].Children[1].Iter.Line == 3
            assert two_results.Children[2].Children[1].Iter.Column == 15

            assert two_results.Children[2].Children[2].Parent == two_results.Children[2]
            assert two_results.Children[2].Children[2].Type == NewlineToken()
            assert two_results.Children[2].Children[2].Value == Token.NewlineMatch(23, 24)
            assert two_results.Children[2].Children[2].Whitespace is None
            assert two_results.Children[2].Children[2].Iter.Line == 4
            assert two_results.Children[2].Children[2].Iter.Column == 1

            # Line 4
            assert two_results.Children[3].Parent == two_results
            assert two_results.Children[3].Type == self._lower_statement

            assert len(two_results.Children[3].Children) == 2

            assert two_results.Children[3].Children[0].Parent == two_results.Children[3]
            assert two_results.Children[3].Children[0].Type == self._lower_token
            assert two_results.Children[3].Children[0].Value.Match.group("value") == "cccccc"
            assert two_results.Children[3].Children[0].Whitespace is None
            assert two_results.Children[3].Children[0].Iter.Line == 4
            assert two_results.Children[3].Children[0].Iter.Column == 7

            assert two_results.Children[3].Children[1].Parent == two_results.Children[3]
            assert two_results.Children[3].Children[1].Type == NewlineToken()
            assert two_results.Children[3].Children[1].Value == Token.NewlineMatch(30, 31)
            assert two_results.Children[3].Children[1].Whitespace is None
            assert two_results.Children[3].Children[1].Iter.Line == 5
            assert two_results.Children[3].Children[1].Iter.Column == 1

            assert two_results.Children[3].Children[1].Iter.AtEnd()

            # number
            number_results = results["number"]

            assert number_results.Parent is None
            assert number_results.Type is None
            assert len(number_results.Children) == 3

            # Line 1
            assert number_results.Children[0].Parent == number_results
            assert number_results.Children[0].Type == self._number_statement

            assert len(number_results.Children[0].Children) == 2

            assert number_results.Children[0].Children[0].Parent == number_results.Children[0]
            assert number_results.Children[0].Children[0].Type == self._number_token
            assert number_results.Children[0].Children[0].Value.Match.group("value") == "4"
            assert number_results.Children[0].Children[0].Whitespace is None
            assert number_results.Children[0].Children[0].Iter.Line == 1
            assert number_results.Children[0].Children[0].Iter.Column == 2

            assert number_results.Children[0].Children[1].Parent == number_results.Children[0]
            assert number_results.Children[0].Children[1].Type == NewlineToken()
            assert number_results.Children[0].Children[1].Value == Token.NewlineMatch(1, 2)
            assert number_results.Children[0].Children[1].Whitespace is None
            assert number_results.Children[0].Children[1].Iter.Line == 2
            assert number_results.Children[0].Children[1].Iter.Column == 1

            # Line 2
            assert number_results.Children[1].Parent == number_results
            assert number_results.Children[1].Type == self._number_statement

            assert len(number_results.Children[1].Children) == 2

            assert number_results.Children[1].Children[0].Parent == number_results.Children[1]
            assert number_results.Children[1].Children[0].Type == self._number_token
            assert number_results.Children[1].Children[0].Value.Match.group("value") == "5"
            assert number_results.Children[1].Children[0].Whitespace is None
            assert number_results.Children[1].Children[0].Iter.Line == 2
            assert number_results.Children[1].Children[0].Iter.Column == 2

            assert number_results.Children[1].Children[1].Parent == number_results.Children[1]
            assert number_results.Children[1].Children[1].Type == NewlineToken()
            assert number_results.Children[1].Children[1].Value == Token.NewlineMatch(3, 4)
            assert number_results.Children[1].Children[1].Whitespace is None
            assert number_results.Children[1].Children[1].Iter.Line == 3
            assert number_results.Children[1].Children[1].Iter.Column == 1

            # Line 3
            assert number_results.Children[2].Parent == number_results
            assert number_results.Children[2].Type == self._number_statement

            assert len(number_results.Children[2].Children) == 2

            assert number_results.Children[2].Children[0].Parent == number_results.Children[2]
            assert number_results.Children[2].Children[0].Type == self._number_token
            assert number_results.Children[2].Children[0].Value.Match.group("value") == "6"
            assert number_results.Children[2].Children[0].Whitespace is None
            assert number_results.Children[2].Children[0].Iter.Line == 3
            assert number_results.Children[2].Children[0].Iter.Column == 2

            assert number_results.Children[2].Children[1].Parent == number_results.Children[2]
            assert number_results.Children[2].Children[1].Type == NewlineToken()
            assert number_results.Children[2].Children[1].Value == Token.NewlineMatch(5, 6)
            assert number_results.Children[2].Children[1].Whitespace is None
            assert number_results.Children[2].Children[1].Iter.Line == 4
            assert number_results.Children[2].Children[1].Iter.Column == 1

            assert number_results.Children[2].Children[1].Iter.AtEnd()

            # Verify the callbacks
            assert observer.mock.call_count == 9

            # observer.VerifyCallArgs(0, self._lower_statement, one_results.Children[0], 1, 1, 2, 1)      # File 'one', line 1
            # observer.VerifyCallArgs(1, self._upper_statement, one_results.Children[1], 2, 1, 3, 1)      # File 'one', line 2
            # observer.VerifyCallArgs(2, self._lower_statement, two_results.Children[0], 1, 1, 2, 1)      # File 'two', line 1
            # observer.VerifyCallArgs(3, self._upper_statement, two_results.Children[1], 2, 1, 3, 1)      # File 'two', line 2
            # observer.VerifyCallArgs(4, self._number_statement, number_results.Children[0], 1, 1, 2, 1)  # File 'number', line 1
            # observer.VerifyCallArgs(5, self._number_statement, number_results.Children[1], 2, 1, 3, 1)  # File 'number', line 2
            # observer.VerifyCallArgs(6, self._number_statement, number_results.Children[2], 3, 1, 4, 1)  # File 'number', line 3
            # observer.VerifyCallArgs(7, self._number_statement, one_results.Children[3], 4, 1, 5, 1)     # File 'one', line 4
            # observer.VerifyCallArgs(8, self._lower_statement, two_results.Children[3], 4, 1, 5, 1)      # File 'two', line 4

    # ----------------------------------------------------------------------
    def test_InsertedStatementsError(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    1 2 3
                    include number
                    4 5 6
                    """,
                ),
            },
            num_threads=10,
        ) as observer:
            results = Parse(
                ["one"],
                self._statements,
                observer,
            )

            assert len(results) == 1
            results = results[0]

            assert str(results) == "The syntax is not recognized"
            assert results.Line == 1
            assert results.Column == 2
            assert results.FullyQualifiedName == "one"

    # ----------------------------------------------------------------------
    def test_InsertedStatementsSimple(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    include number
                    4 5 6
                    """,
                ),
            },
            num_threads=10,
        ) as observer:
            results = Parse(
                ["one"],
                self._statements,
                observer,
            )

            assert len(results) == 2
            assert "one" in results
            assert "number" in results

            one_results = results["one"]

            assert one_results.Parent is None
            assert one_results.Type is None
            assert len(one_results.Children) == 2

            assert one_results.Children[0].Parent == one_results
            assert one_results.Children[0].Type == self._include_statement

            assert len(one_results.Children[0].Children) == 3

            assert one_results.Children[0].Children[0].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[0].Type == self._include_token
            assert one_results.Children[0].Children[0].Value.Match.group("value") == "include"
            assert one_results.Children[0].Children[0].Whitespace is None
            assert one_results.Children[0].Children[0].Iter.Line == 1
            assert one_results.Children[0].Children[0].Iter.Column == 8

            assert one_results.Children[0].Children[1].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[1].Type == self._lower_token
            assert one_results.Children[0].Children[1].Value.Match.group("value") == "number"
            assert one_results.Children[0].Children[1].Whitespace == (7, 8)
            assert one_results.Children[0].Children[1].Iter.Line == 1
            assert one_results.Children[0].Children[1].Iter.Column == 15

            assert one_results.Children[0].Children[2].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[2].Type == NewlineToken()
            assert one_results.Children[0].Children[2].Value == Token.NewlineMatch(14, 15)
            assert one_results.Children[0].Children[2].Whitespace is None
            assert one_results.Children[0].Children[2].Iter.Line == 2
            assert one_results.Children[0].Children[2].Iter.Column == 1

            assert one_results.Children[1].Parent == one_results
            assert one_results.Children[1].Type == self._dynamic_number_statement

            assert len(one_results.Children[1].Children) == 4

            assert one_results.Children[1].Children[0].Parent == one_results.Children[1]
            assert one_results.Children[1].Children[0].Type == self._number_token
            assert one_results.Children[1].Children[0].Value.Match.group("value") == "4"
            assert one_results.Children[1].Children[0].Whitespace is None
            assert one_results.Children[1].Children[0].Iter.Line == 2
            assert one_results.Children[1].Children[0].Iter.Column == 2

            assert one_results.Children[1].Children[1].Parent == one_results.Children[1]
            assert one_results.Children[1].Children[1].Type == self._number_token
            assert one_results.Children[1].Children[1].Value.Match.group("value") == "5"
            assert one_results.Children[1].Children[1].Whitespace == (16, 17)
            assert one_results.Children[1].Children[1].Iter.Line == 2
            assert one_results.Children[1].Children[1].Iter.Column == 4

            assert one_results.Children[1].Children[2].Parent == one_results.Children[1]
            assert one_results.Children[1].Children[2].Type == self._number_token
            assert one_results.Children[1].Children[2].Value.Match.group("value") == "6"
            assert one_results.Children[1].Children[2].Whitespace == (18, 19)
            assert one_results.Children[1].Children[2].Iter.Line == 2
            assert one_results.Children[1].Children[2].Iter.Column == 6

            assert one_results.Children[1].Children[3].Parent == one_results.Children[1]
            assert one_results.Children[1].Children[3].Type == NewlineToken()
            assert one_results.Children[1].Children[3].Value == Token.NewlineMatch(20, 21)
            assert one_results.Children[1].Children[3].Whitespace is None
            assert one_results.Children[1].Children[3].Iter.Line == 3
            assert one_results.Children[1].Children[3].Iter.Column == 1

    # ----------------------------------------------------------------------
    def test_InsertedStatementsScoped(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    NEWSCOPE:
                        include number
                        4 5 6
                    """,
                ),
            },
            num_threads=10,
        ) as observer:
            results = Parse(
                ["one"],
                self._statements,
                observer,
            )

            assert len(results) == 2
            assert "one" in results
            assert "number" in results

            one_results = results["one"]

            assert one_results.Parent is None
            assert one_results.Type is None
            assert len(one_results.Children) == 1

            assert one_results.Children[0].Parent == one_results
            assert one_results.Children[0].Type == self._new_scope_statement

            assert len(one_results.Children[0].Children) == 7

            assert one_results.Children[0].Children[0].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[0].Type == self._upper_token
            assert one_results.Children[0].Children[0].Value.Match.group("value") == "NEWSCOPE"
            assert one_results.Children[0].Children[0].Whitespace is None
            assert one_results.Children[0].Children[0].Iter.Line == 1
            assert one_results.Children[0].Children[0].Iter.Column == 9

            assert one_results.Children[0].Children[1].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[1].Type.Name == "Colon Token"
            assert one_results.Children[0].Children[1].Whitespace is None
            assert one_results.Children[0].Children[1].Iter.Line == 1
            assert one_results.Children[0].Children[1].Iter.Column == 10

            assert one_results.Children[0].Children[2].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[2].Type == NewlineToken()
            assert one_results.Children[0].Children[2].Value == Token.NewlineMatch(9, 10)
            assert one_results.Children[0].Children[2].Whitespace is None
            assert one_results.Children[0].Children[2].Iter.Line == 2
            assert one_results.Children[0].Children[2].Iter.Column == 1

            assert one_results.Children[0].Children[3].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[3].Type == IndentToken()
            assert one_results.Children[0].Children[3].Value == Token.IndentMatch(10, 14, 4)
            assert one_results.Children[0].Children[3].Whitespace is None
            assert one_results.Children[0].Children[3].Iter.Line == 2
            assert one_results.Children[0].Children[3].Iter.Column == 5

            assert one_results.Children[0].Children[4].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[4].Type == DynamicStatements.Statements

            assert len(one_results.Children[0].Children[4].Children) == 1

            assert one_results.Children[0].Children[4].Children[0].Parent == one_results.Children[0].Children[4]
            assert one_results.Children[0].Children[4].Children[0].Type == self._include_statement

            assert len(one_results.Children[0].Children[4].Children[0].Children) == 3

            assert one_results.Children[0].Children[4].Children[0].Children[0].Type == self._include_token
            assert one_results.Children[0].Children[4].Children[0].Children[1].Value.Match.group("value") == "number"
            assert one_results.Children[0].Children[4].Children[0].Children[2].Type == NewlineToken()

            assert one_results.Children[0].Children[5].Parent == one_results.Children[0]
            assert one_results.Children[0].Children[5].Type == DynamicStatements.Statements

            assert len(one_results.Children[0].Children[5].Children) == 1

            assert one_results.Children[0].Children[5].Children[0].Type == self._dynamic_number_statement

            assert len(one_results.Children[0].Children[5].Children[0].Children) == 4

            assert one_results.Children[0].Children[5].Children[0].Children[0].Value.Match.group("value") == "4"
            assert one_results.Children[0].Children[5].Children[0].Children[1].Value.Match.group("value") == "5"
            assert one_results.Children[0].Children[5].Children[0].Children[2].Value.Match.group("value") == "6"
            assert one_results.Children[0].Children[5].Children[0].Children[3].Type == NewlineToken()

            assert one_results.Children[0].Children[6].Type == DedentToken()

    # ----------------------------------------------------------------------
    def test_InsertedStatementsAfterScope(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    NEWSCOPE:
                        include number
                        4 5 6
                    7 8 9
                    """,
                ),
            },
            num_threads=10,
        ) as observer:
            results = Parse(
                ["one"],
                self._statements,
                observer,
            )

            assert len(results) == 1

            assert results[0].Line == 4
            assert results[0].Column == 2
            assert str(results[0]) == "The syntax is not recognized"

            assert len(results[0].PotentialStatements) == 5
            assert results[0].PotentialStatements[self._include_statement] == []
            assert results[0].PotentialStatements[self._upper_statement] == []
            assert results[0].PotentialStatements[self._lower_statement] == []
            assert results[0].PotentialStatements[self._new_scope_statement] == []

            assert len(results[0].PotentialStatements[self._number_statement]) == 1
            assert results[0].PotentialStatements[self._number_statement][0].Token == self._number_token
            assert results[0].PotentialStatements[self._number_statement][0].Iter.Line == 4
            assert results[0].PotentialStatements[self._number_statement][0].Iter.Column == 2


# TODO: Circular dependencies
