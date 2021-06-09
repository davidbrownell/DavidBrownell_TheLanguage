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
    from ..Statement import DynamicStatements, Statement
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

    _include_statement                      = Statement("Include", _include_token, _lower_token, NewlineToken())
    _upper_statement                        = Statement("Upper", _upper_token, NewlineToken())
    _lower_statement                        = Statement("Lower", _lower_token, NewlineToken())
    _number_statement                       = Statement("Number", _number_token, NewlineToken())

    _new_scope_statement                    = Statement(
        "New Scope",
        _upper_token,
        RegexToken("Colon Token", re.compile(r":")),
        NewlineToken(),
        IndentToken(),
        DynamicStatements.Statements,
        DynamicStatements.Statements,
        DedentToken(),
    )

    _dynamic_number_statement               = Statement("Dynamic Number", _number_token, _number_token, _number_token, NewlineToken())

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

                    assert callback_args[0].Type == statement
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
                    node,
                    iter_before,
                    iter_after,
                ):
                    if node.Type == cls._include_statement:
                        assert len(node.Children) == 3
                        value = node.Children[1].Value.Match.group("value")

                        return Observer.ImportInfo(value, value if value in cls._content_dict else None)

                    return self.mock(node, iter_before, iter_after)

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

            assert str(results) == textwrap.dedent(
                """\
                <Root>
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match='3'>>> ws:None [3, 1 -> 3, 2]
                            Newline+ <<9, 10>> ws:None [3, 2 -> 4, 1]
                """,
            )

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

            assert str(one_results) == textwrap.dedent(
                """\
                <Root>
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                            Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                    Or: [Include, Upper, Lower, Number, New Scope] / Or: [Dynamic Number]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                            Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                """,
            )

            # Verify the other
            number_results = all_results["number"]

            assert str(number_results) == textwrap.dedent(
                """\
                <Root>
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                            Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                            Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                            Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                """,
            )

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

            assert str(one_results) == textwrap.dedent(
                """\
                <Root>
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                            Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                    Or: [Include, Upper, Lower, Number, New Scope] / Or: [Dynamic Number]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                            Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                """,
            )

            # two
            two_results = results["two"]

            assert str(two_results) == textwrap.dedent(
                """\
                <Root>
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='aaa'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 8), match='BBBB'>>> ws:None [2, 1 -> 2, 5]
                            Newline+ <<8, 9>> ws:None [2, 5 -> 3, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(9, 16), match='include'>>> ws:None [3, 1 -> 3, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(17, 23), match='number'>>> ws:(16, 17) [3, 9 -> 3, 15]
                            Newline+ <<23, 24>> ws:None [3, 15 -> 4, 1]
                    Or: [Include, Upper, Lower, Number, New Scope] / Or: [Dynamic Number]
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(24, 30), match='cccccc'>>> ws:None [4, 1 -> 4, 7]
                            Newline+ <<30, 31>> ws:None [4, 7 -> 5, 1]
                """,
            )

            # number
            number_results = results["number"]

            assert str(number_results) == textwrap.dedent(
                """\
                <Root>
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                            Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                            Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                            Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                """,
            )

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

            assert str(one_results) == textwrap.dedent(
                """\
                <Root>
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(0, 7), match='include'>>> ws:None [1, 1 -> 1, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(8, 14), match='number'>>> ws:(7, 8) [1, 9 -> 1, 15]
                            Newline+ <<14, 15>> ws:None [1, 15 -> 2, 1]
                    Or: [Include, Upper, Lower, Number, New Scope] / Or: [Dynamic Number]
                        Dynamic Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(15, 16), match='4'>>> ws:None [2, 1 -> 2, 2]
                            Number Token <<Regex: <_sre.SRE_Match object; span=(17, 18), match='5'>>> ws:(16, 17) [2, 3 -> 2, 4]
                            Number Token <<Regex: <_sre.SRE_Match object; span=(19, 20), match='6'>>> ws:(18, 19) [2, 5 -> 2, 6]
                            Newline+ <<20, 21>> ws:None [2, 6 -> 3, 1]
                """,
            )

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
                single_threaded=True,
            )

            assert len(results) == 2
            assert "one" in results
            assert "number" in results

            one_results = results["one"]

            assert str(one_results) == textwrap.dedent(
                """\
                <Root>
                    Or: [Include, Upper, Lower, Number, New Scope]
                        New Scope
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(0, 8), match='NEWSCOPE'>>> ws:None [1, 1 -> 1, 9]
                            Colon Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match=':'>>> ws:None [1, 9 -> 1, 10]
                            Newline+ <<9, 10>> ws:None [1, 10 -> 2, 1]
                            Indent <<10, 14, (4)>> ws:None [2, 1 -> 2, 5]
                            DynamicStatements.Statements
                                Or: [Include, Upper, Lower, Number, New Scope]
                                    Include
                                        Include Token <<Regex: <_sre.SRE_Match object; span=(14, 21), match='include'>>> ws:None [2, 5 -> 2, 12]
                                        Lower Token <<Regex: <_sre.SRE_Match object; span=(22, 28), match='number'>>> ws:(21, 22) [2, 13 -> 2, 19]
                                        Newline+ <<28, 29>> ws:None [2, 19 -> 3, 1]
                            DynamicStatements.Statements
                                Or: [Include, Upper, Lower, Number, New Scope] / Or: [Dynamic Number]
                                    Dynamic Number
                                        Number Token <<Regex: <_sre.SRE_Match object; span=(33, 34), match='4'>>> ws:None [3, 5 -> 3, 6]
                                        Number Token <<Regex: <_sre.SRE_Match object; span=(35, 36), match='5'>>> ws:(34, 35) [3, 7 -> 3, 8]
                                        Number Token <<Regex: <_sre.SRE_Match object; span=(37, 38), match='6'>>> ws:(36, 37) [3, 9 -> 3, 10]
                                        Newline+ <<38, 39>> ws:None [3, 10 -> 4, 1]
                            Dedent <<>> ws:None [4, 1 -> 4, 1]
                """,
            )

            number_results = results["number"]

            assert str(number_results) == textwrap.dedent(
                """\
                <Root>
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                            Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                            Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                    Or: [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                            Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                """,
            )

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

            assert len(results[0].PotentialStatements) == 1
            key = tuple(self._statements.statements)
            assert key in results[0].PotentialStatements

            potentials = results[0].PotentialStatements[key]

            assert len(potentials) == 5

            assert str(potentials[0]) == textwrap.dedent(
                """\
                Include
                    <No results>
                """,
            )

            assert str(potentials[1]) == textwrap.dedent(
                """\
                Upper
                    <No results>
                """,
            )

            assert str(potentials[2]) == textwrap.dedent(
                """\
                Lower
                    <No results>
                """,
            )

            assert str(potentials[3]) == textwrap.dedent(
                """\
                Number
                    Number Token <<Regex: <_sre.SRE_Match object; span=(39, 40), match='7'>>> ws:None [4, 1 -> 4, 2]
                """,
            )

            assert str(potentials[4]) == textwrap.dedent(
                """\
                New Scope
                    <No results>
                """,
            )

# ----------------------------------------------------------------------
def test_NodeStrNoChildren():
    node = Node(Statement("Statement", NewlineToken()))

    assert str(node) == textwrap.dedent(
        """\
        Statement
            <No children>
        """,
    )

# TODO: Circular dependencies
