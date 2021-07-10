# ----------------------------------------------------------------------
# |
# |  TranslationUnitsParser_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-02 11:42:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for TranslationUnitsParser.py"""

import os
import re
import textwrap

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import Dict, Optional
from unittest.mock import Mock

import pytest

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
with InitRelativeImports():
    from ..StatementEx import DynamicStatements, StatementEx

    from ..Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
    )

    from ..TranslationUnitsParser import *


# ----------------------------------------------------------------------
class TestStandard(object):
    _content_dict                           = {
        "upper" : textwrap.dedent(
            """\
            FOUR
            Five
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

    _include_statement                      = StatementEx("Include", _include_token, _lower_token, NewlineToken())
    _upper_statement                        = StatementEx("Upper", _upper_token, NewlineToken())
    _lower_statement                        = StatementEx("Lower", _lower_token, NewlineToken())
    _number_statement                       = StatementEx("Number", _number_token, NewlineToken())

    _new_scope_statement                    = StatementEx(
        "New Scope",
        _upper_token,
        RegexToken("Colon Token", re.compile(r":")),
        NewlineToken(),
        IndentToken(),
        DynamicStatements.Statements,
        DynamicStatements.Statements,
        DedentToken(),
    )

    _dynamic_number_statement               = StatementEx("Dynamic Number", _number_token, _number_token, _number_token, NewlineToken())

    _statements                             = DynamicStatementInfo(
        [_include_statement, _upper_statement, _lower_statement, _number_statement, _new_scope_statement],
        [],
    )

    _or_statement_name                      = "[Include, Upper, Lower, Number, New Scope]"
    _dynamic_or_statement_name              = "[Include, Upper, Lower, Number, New Scope] / [Dynamic Number]"

    _dynamic_statements_name                = "Dynamic Statements"

    # ----------------------------------------------------------------------
    @classmethod
    @contextmanager
    def CreateObserver(
        cls,
        content_dict: Dict[str, str],
        num_threads: Optional[int]=None,
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
                    self.on_statement_compete_mock = Mock(
                        return_value=True,
                    )

                # ----------------------------------------------------------------------
                def OnStatementCompleteMethodCallToTuple(
                    self,
                    index,
                    use_statement_name=False,
                ):
                    callback_args = self.on_statement_compete_mock.call_args_list[index][0]

                    return (
                        callback_args[0].Type.Name if use_statement_name else callback_args[0].Type,
                        callback_args[1].Line,
                        callback_args[1].Column,
                        callback_args[2].Line,
                        callback_args[2].Column,
                    )

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
                def Enqueue(
                    funcs: List[Callable[[], None]],
                ) -> List[Future]:
                    return [executor.submit(func) for func in funcs]

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                def ExtractDynamicStatements(
                    fully_qualified_name: str,
                    node: RootNode,
                ) -> DynamicStatementInfo:
                    if fully_qualified_name == "number":
                        return DynamicStatementInfo([cls._dynamic_number_statement], [])

                    return DynamicStatementInfo([], [])

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                async def OnIndentAsync(
                    fully_qualified_name: str,
                    data: Statement.TokenParseResultData,
                    iter_before: NormalizedIterator,
                    iter_after: NormalizedIterator,
                ) -> Optional[DynamicStatementInfo]:
                    return None

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                async def OnDedentAsync(
                    fully_qualified_name: str,
                    data: Statement.TokenParseResultData,
                    iter_before: NormalizedIterator,
                    iter_after: NormalizedIterator,
                ) -> None:
                    return None

                # ----------------------------------------------------------------------
                @Interface.override
                async def OnStatementCompleteAsync(
                    self,
                    fully_qualified_name: str,
                    node: Node,
                    iter_before: NormalizedIterator,
                    iter_after: NormalizedIterator,
                ) -> Union[
                    bool,                               # True to continue processing, False to terminate
                    DynamicStatementInfo,               # DynamicStatementInfo generated by the statement
                    "Observer.ImportInfo",              # Import information generated by the statement
                ]:
                    if node.Type == cls._include_statement:
                        assert len(node.Children) == 3
                        value = node.Children[1].Value.Match.group("value")

                        return Observer.ImportInfo(value, value if value in cls._content_dict else None)

                    return self.on_statement_compete_mock(node, iter_before, iter_after)

            # ----------------------------------------------------------------------

            yield MyObserver()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoInclude(self):
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
            results = await ParseAsync(
                ["one"],
                self._statements,
                observer,
                single_threaded=True,
            )

            assert len(results) == 1
            assert "one" in results
            results = results["one"]

            assert results.ToString() == textwrap.dedent(
                """\
                <Root>
                    [Include, Upper, Lower, Number, New Scope]
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match='3'>>> ws:None [3, 1 -> 3, 2]
                            Newline+ <<9, 10>> ws:None [3, 2 -> 4, 1]
                """,
            )

            assert len(observer.on_statement_compete_mock.call_args_list) == 9

            assert observer.OnStatementCompleteMethodCallToTuple(0) == (self._lower_statement, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(1, use_statement_name=True) == (self._or_statement_name, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(2, use_statement_name=True) == (self._dynamic_statements_name, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(3) == (self._upper_statement, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(4, use_statement_name=True) == (self._or_statement_name, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(5, use_statement_name=True) == (self._dynamic_statements_name, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(6) == (self._number_statement, 3, 1, 4, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(7, use_statement_name=True) == (self._or_statement_name, 3, 1, 4, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(8, use_statement_name=True) == (self._dynamic_statements_name, 3, 1, 4, 1)

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleInclude(self):
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
        ) as observer:
            all_results = await ParseAsync(
                ["one"],
                self._statements,
                observer,
                single_threaded=True,
            )

            assert len(all_results) == 2
            assert "one" in all_results
            assert "number" in all_results

            one_results = all_results["one"]

            assert str(one_results) == textwrap.dedent(
                """\
                <Root>
                    [Include, Upper, Lower, Number, New Scope]
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                            Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                    [Include, Upper, Lower, Number, New Scope] / [Dynamic Number]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                            Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                """,
            )

            number_results = all_results["number"]

            assert str(number_results) == textwrap.dedent(
                """\
                <Root>
                    [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                            Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                            Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                            Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                """,
            )

            assert len(observer.on_statement_compete_mock.call_args_list) == 20

            # one (lines 1 - 3)
            assert observer.OnStatementCompleteMethodCallToTuple(0) == (self._lower_statement, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(1, use_statement_name=True) == (self._or_statement_name, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(2, use_statement_name=True) == (self._dynamic_statements_name, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(3) == (self._upper_statement, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(4, use_statement_name=True) == (self._or_statement_name, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(5, use_statement_name=True) == (self._dynamic_statements_name, 2, 1, 3, 1)

            # number
            assert observer.OnStatementCompleteMethodCallToTuple(6) == (self._number_statement, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(7, use_statement_name=True) == (self._or_statement_name, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(8, use_statement_name=True) == (self._dynamic_statements_name, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(9) == (self._number_statement, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(10, use_statement_name=True) == (self._or_statement_name, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(11, use_statement_name=True) == (self._dynamic_statements_name, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(12) == (self._number_statement, 3, 1, 4, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(13, use_statement_name=True) == (self._or_statement_name, 3, 1, 4, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(14, use_statement_name=True) == (self._dynamic_statements_name, 3, 1, 4, 1)

            # one (line 3, after include)
            assert observer.OnStatementCompleteMethodCallToTuple(15, use_statement_name=True) == (self._or_statement_name, 3, 1, 4, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(16, use_statement_name=True) == (self._dynamic_statements_name, 3, 1, 4, 1)

            # one (line 4)
            assert observer.OnStatementCompleteMethodCallToTuple(17) == (self._number_statement, 4, 1, 5, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(18, use_statement_name=True) == (self._dynamic_or_statement_name, 4, 1, 5, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(19, use_statement_name=True) == (self._dynamic_statements_name, 4, 1, 5, 1)

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_DoubleInclude(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    one
                    TWO
                    include number
                    3
                    include number
                    4
                    """,
                ),
            },
            num_threads=10,
        ) as observer:
            all_results = await ParseAsync(
                ["one"],
                self._statements,
                observer,
            )

            assert len(all_results) == 2
            assert "one" in all_results
            assert "number" in all_results

            one_results = all_results["one"]

            assert str(one_results) == textwrap.dedent(
                """\
                <Root>
                    [Include, Upper, Lower, Number, New Scope]
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                            Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                    [Include, Upper, Lower, Number, New Scope] / [Dynamic Number]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                            Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                    [Include, Upper, Lower, Number, New Scope] / [Dynamic Number]
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(25, 32), match='include'>>> ws:None [5, 1 -> 5, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(33, 39), match='number'>>> ws:(32, 33) [5, 9 -> 5, 15]
                            Newline+ <<39, 40>> ws:None [5, 15 -> 6, 1]
                    [Include, Upper, Lower, Number, New Scope] / [Dynamic Number]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(40, 41), match='4'>>> ws:None [6, 1 -> 6, 2]
                            Newline+ <<41, 42>> ws:None [6, 2 -> 7, 1]
                """,
            )

            assert len(observer.on_statement_compete_mock.call_args_list) == 25

            # one (lines 1 - 3)
            assert observer.OnStatementCompleteMethodCallToTuple(0) == (self._lower_statement, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(1, use_statement_name=True) == (self._or_statement_name, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(2, use_statement_name=True) == (self._dynamic_statements_name, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(3) == (self._upper_statement, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(4, use_statement_name=True) == (self._or_statement_name, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(5, use_statement_name=True) == (self._dynamic_statements_name, 2, 1, 3, 1)

            # number
            assert observer.OnStatementCompleteMethodCallToTuple(6) == (self._number_statement, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(7, use_statement_name=True) == (self._or_statement_name, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(8, use_statement_name=True) == (self._dynamic_statements_name, 1, 1, 2, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(9) == (self._number_statement, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(10, use_statement_name=True) == (self._or_statement_name, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(11, use_statement_name=True) == (self._dynamic_statements_name, 2, 1, 3, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(12) == (self._number_statement, 3, 1, 4, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(13, use_statement_name=True) == (self._or_statement_name, 3, 1, 4, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(14, use_statement_name=True) == (self._dynamic_statements_name, 3, 1, 4, 1)

            # one (line 3, after include)
            assert observer.OnStatementCompleteMethodCallToTuple(15, use_statement_name=True) == (self._or_statement_name, 3, 1, 4, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(16, use_statement_name=True) == (self._dynamic_statements_name, 3, 1, 4, 1)

            # one (line 4)
            assert observer.OnStatementCompleteMethodCallToTuple(17) == (self._number_statement, 4, 1, 5, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(18, use_statement_name=True) == (self._dynamic_or_statement_name, 4, 1, 5, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(19, use_statement_name=True) == (self._dynamic_statements_name, 4, 1, 5, 1)

            # one (line 5)
            assert observer.OnStatementCompleteMethodCallToTuple(20, use_statement_name=True) == (self._dynamic_or_statement_name, 5, 1, 6, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(21, use_statement_name=True) == (self._dynamic_statements_name, 5, 1, 6, 1)

            # one (line 6)
            assert observer.OnStatementCompleteMethodCallToTuple(22) == (self._number_statement, 6, 1, 7, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(23, use_statement_name=True) == (self._dynamic_or_statement_name, 6, 1, 7, 1)
            assert observer.OnStatementCompleteMethodCallToTuple(24, use_statement_name=True) == (self._dynamic_statements_name, 6, 1, 7, 1)

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InvalidInclude(self):
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
            results = await ParseAsync(
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
    @pytest.mark.asyncio
    async def test_MultipleFileSingleImport(self):
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
            results = await ParseAsync(
                ["one", "two"],
                self._statements,
                observer,
            )

            assert len(results) == 3
            assert "one" in results
            assert "two" in results
            assert "number" in results

            one_results = results["one"]

            assert str(one_results) == textwrap.dedent(
                """\
                <Root>
                    [Include, Upper, Lower, Number, New Scope]
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                            Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                    [Include, Upper, Lower, Number, New Scope] / [Dynamic Number]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                            Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                """,
            )

            two_results = results["two"]

            assert str(two_results) == textwrap.dedent(
                """\
                <Root>
                    [Include, Upper, Lower, Number, New Scope]
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='aaa'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 8), match='BBBB'>>> ws:None [2, 1 -> 2, 5]
                            Newline+ <<8, 9>> ws:None [2, 5 -> 3, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(9, 16), match='include'>>> ws:None [3, 1 -> 3, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(17, 23), match='number'>>> ws:(16, 17) [3, 9 -> 3, 15]
                            Newline+ <<23, 24>> ws:None [3, 15 -> 4, 1]
                    [Include, Upper, Lower, Number, New Scope] / [Dynamic Number]
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(24, 30), match='cccccc'>>> ws:None [4, 1 -> 4, 7]
                            Newline+ <<30, 31>> ws:None [4, 7 -> 5, 1]
                """,
            )

            number_results = results["number"]

            assert str(number_results) == textwrap.dedent(
                """\
                <Root>
                    [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                            Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                            Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                    [Include, Upper, Lower, Number, New Scope]
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                            Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                """,
            )

            assert len(observer.on_statement_compete_mock.call_args_list) == 31

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InsertedStatementsError(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    1 2 3
                    """,
                ),
            },
        ) as observer:
            results = await ParseAsync(
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
    @pytest.mark.asyncio
    async def test_InsertedStatementsSuccess(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    include number
                    1 2 3
                    """,
                ),
            },
        ) as observer:
            results = await ParseAsync(
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
                    [Include, Upper, Lower, Number, New Scope]
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(0, 7), match='include'>>> ws:None [1, 1 -> 1, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(8, 14), match='number'>>> ws:(7, 8) [1, 9 -> 1, 15]
                            Newline+ <<14, 15>> ws:None [1, 15 -> 2, 1]
                    [Include, Upper, Lower, Number, New Scope] / [Dynamic Number]
                        Dynamic Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(15, 16), match='1'>>> ws:None [2, 1 -> 2, 2]
                            Number Token <<Regex: <_sre.SRE_Match object; span=(17, 18), match='2'>>> ws:(16, 17) [2, 3 -> 2, 4]
                            Number Token <<Regex: <_sre.SRE_Match object; span=(19, 20), match='3'>>> ws:(18, 19) [2, 5 -> 2, 6]
                            Newline+ <<20, 21>> ws:None [2, 6 -> 3, 1]
                """,
            )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InsertedScopedStatementsError(self):
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
            results = await ParseAsync(
                ["one"],
                self._statements,
                observer,
            )

            assert len(results) == 1
            results = results[0]

            assert results.Line == 4
            assert results.Column == 2
            assert str(results) == "The syntax is not recognized"

            assert results.ToDebugString() == textwrap.dedent(
                """\
                The syntax is not recognized [4, 2]

                [Include, Upper, Lower, Number, New Scope]
                    New Scope
                        Upper Token
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(0, 8), match='NEWSCOPE'>>> ws:None [1, 1 -> 1, 9]
                        Colon Token
                            Colon Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match=':'>>> ws:None [1, 9 -> 1, 10]
                        Newline+
                            Newline+ <<9, 10>> ws:None [1, 10 -> 2, 1]
                        Indent
                            Indent <<10, 14, (4)>> ws:None [2, 1 -> 2, 5]
                        DynamicStatements.Statements
                            [Include, Upper, Lower, Number, New Scope]
                                Include
                                    Include Token
                                        Include Token <<Regex: <_sre.SRE_Match object; span=(14, 21), match='include'>>> ws:None [2, 5 -> 2, 12]
                                    Lower Token
                                        Lower Token <<Regex: <_sre.SRE_Match object; span=(22, 28), match='number'>>> ws:(21, 22) [2, 13 -> 2, 19]
                                    Newline+
                                        Newline+ <<28, 29>> ws:None [2, 19 -> 3, 1]
                        DynamicStatements.Statements
                            [Include, Upper, Lower, Number, New Scope] / [Dynamic Number]
                                Dynamic Number
                                    Number Token
                                        Number Token <<Regex: <_sre.SRE_Match object; span=(33, 34), match='4'>>> ws:None [3, 5 -> 3, 6]
                                    Number Token
                                        Number Token <<Regex: <_sre.SRE_Match object; span=(35, 36), match='5'>>> ws:(34, 35) [3, 7 -> 3, 8]
                                    Number Token
                                        Number Token <<Regex: <_sre.SRE_Match object; span=(37, 38), match='6'>>> ws:(36, 37) [3, 9 -> 3, 10]
                                    Newline+
                                        Newline+ <<38, 39>> ws:None [3, 10 -> 4, 1]
                        Dedent
                            Dedent <<>> ws:None [4, 1 -> 4, 1]
                [Include, Upper, Lower, Number, New Scope]
                    Include
                        Include Token
                            None
                    Upper
                        Upper Token
                            None
                    Lower
                        Lower Token
                            None
                    Number
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(39, 40), match='7'>>> ws:None [4, 1 -> 4, 2]
                        Newline+
                            None
                    New Scope
                        Upper Token
                            None
                """,
            )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InsertedScopedStatementsSuccess(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    NEWSCOPE:
                        include number
                        1 2 3
                    """,
                ),
            },
        ) as observer:
            results = await ParseAsync(
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
                    [Include, Upper, Lower, Number, New Scope]
                        New Scope
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(0, 8), match='NEWSCOPE'>>> ws:None [1, 1 -> 1, 9]
                            Colon Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match=':'>>> ws:None [1, 9 -> 1, 10]
                            Newline+ <<9, 10>> ws:None [1, 10 -> 2, 1]
                            Indent <<10, 14, (4)>> ws:None [2, 1 -> 2, 5]
                            DynamicStatements.Statements
                                [Include, Upper, Lower, Number, New Scope]
                                    Include
                                        Include Token <<Regex: <_sre.SRE_Match object; span=(14, 21), match='include'>>> ws:None [2, 5 -> 2, 12]
                                        Lower Token <<Regex: <_sre.SRE_Match object; span=(22, 28), match='number'>>> ws:(21, 22) [2, 13 -> 2, 19]
                                        Newline+ <<28, 29>> ws:None [2, 19 -> 3, 1]
                            DynamicStatements.Statements
                                [Include, Upper, Lower, Number, New Scope] / [Dynamic Number]
                                    Dynamic Number
                                        Number Token <<Regex: <_sre.SRE_Match object; span=(33, 34), match='1'>>> ws:None [3, 5 -> 3, 6]
                                        Number Token <<Regex: <_sre.SRE_Match object; span=(35, 36), match='2'>>> ws:(34, 35) [3, 7 -> 3, 8]
                                        Number Token <<Regex: <_sre.SRE_Match object; span=(37, 38), match='3'>>> ws:(36, 37) [3, 9 -> 3, 10]
                                        Newline+ <<38, 39>> ws:None [3, 10 -> 4, 1]
                            Dedent <<>> ws:None [4, 1 -> 4, 1]
                """,
            )

# ----------------------------------------------------------------------
def test_NodeStrNoChildren():
    node = Node(StatementEx("Statement", NewlineToken()))

    assert str(node) == textwrap.dedent(
        """\
        Statement
            <No Children>
        """,
    )

# TODO: Circular dependencies
