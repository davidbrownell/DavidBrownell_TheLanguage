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
    from ..AST import Node
    from ..StatementDSL import CreateStatement, DynamicStatements

    from ..Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
    )

    from ..TranslationUnitsParser import *

    from ..Statements.UnitTests import MethodCallsToString


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

    _include_statement                      = CreateStatement(name="Include", item=[_include_token, _lower_token, NewlineToken()])
    _upper_statement                        = CreateStatement(name="Upper", item=[_upper_token, NewlineToken()])
    _lower_statement                        = CreateStatement(name="Lower", item=[_lower_token, NewlineToken()])
    _number_statement                       = CreateStatement(name="Number", item=[_number_token, NewlineToken()])

    _new_scope_statement                    = CreateStatement(
        name="New Scope",
        item=[
            _upper_token,
            RegexToken("Colon Token", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            DynamicStatements.Statements,
            DynamicStatements.Statements,
            DedentToken(),
        ],
    )

    _dynamic_number_statement               = CreateStatement(
        name="Dynamic Number",
        item=[
            _number_token,
            _number_token,
            _number_token,
            NewlineToken(),
        ],
    )

    _statements                             = DynamicStatementInfo(
        (_include_statement, _upper_statement, _lower_statement, _number_statement, _new_scope_statement),
        (),
    )

    _or_statement_name                      = "{Include, Upper, Lower, Number, New Scope}"
    _dynamic_or_statement_name              = "{Include, Upper, Lower, Number, New Scope} / {Dynamic Number}"

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
                    self.on_statement_complete_mock = Mock(
                        return_value=True,
                    )

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
                def LoadContent(
                    fully_qualified_name: str,
                ) -> str:
                    assert fully_qualified_name in content_dict
                    return content_dict[fully_qualified_name]

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                def ExtractDynamicStatements(
                    fully_qualified_name: str,
                    node: RootNode,
                ) -> DynamicStatementInfo:
                    if fully_qualified_name == "number":
                        return DynamicStatementInfo((cls._dynamic_number_statement,), ())

                    return DynamicStatementInfo((), ())

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                def StartStatement(
                    fully_qualified_name: str,
                    statement_stack: List[Statement],
                ) -> None:
                    return

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                def EndStatement(
                    fully_qualified_name: str,
                    statement_info_stack: List[
                        Tuple[
                            Statement,
                            Optional[bool],
                        ],
                    ],
                ) -> None:
                    return

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                async def OnIndentAsync(
                    fully_qualified_name: str,
                    data_stack: List[Statement.StandardParseResultData],
                    iter_before: NormalizedIterator,
                    iter_after: NormalizedIterator,
                ) -> Optional[DynamicStatementInfo]:
                    return None

                # ----------------------------------------------------------------------
                @staticmethod
                @Interface.override
                async def OnDedentAsync(
                    fully_qualified_name: str,
                    data_stack: List[Statement.StandardParseResultData],
                    iter_before: NormalizedIterator,
                    iter_after: NormalizedIterator,
                ) -> None:
                    return None

                # ----------------------------------------------------------------------
                @Interface.override
                async def OnStatementCompleteAsync(
                    self,
                    fully_qualified_name: str,
                    statement: Statement,
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

                    return self.on_statement_complete_mock(node, iter_before, iter_after)

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
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Lower
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                                Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Upper
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                                Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match='3'>>> ws:None [3, 1 -> 3, 2]
                                Newline+ <<9, 10>> ws:None [3, 2 -> 4, 1]
                """,
            )

            assert MethodCallsToString(
                observer.on_statement_complete_mock,
                attribute_name="call_args_list",
            ) == textwrap.dedent(
                """\
                0) 0, 3
                    Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                1) 3, 4
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                2) 0, 4
                    Lower
                        Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                3) 0, 4
                    {Include, Upper, Lower, Number, New Scope}
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                4) 0, 4
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Lower
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                                Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                5) 4, 7
                    Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                6) 7, 8
                    Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                7) 4, 8
                    Upper
                        Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                        Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                8) 4, 7
                    Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                9) 4, 8
                    {Include, Upper, Lower, Number, New Scope}
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                10) 4, 8
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Upper
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                                Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                11) 8, 9
                    Number Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match='3'>>> ws:None [3, 1 -> 3, 2]
                12) 9, 10
                    Newline+ <<9, 10>> ws:None [3, 2 -> 4, 1]
                13) 8, 10
                    Number
                        Number Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match='3'>>> ws:None [3, 1 -> 3, 2]
                        Newline+ <<9, 10>> ws:None [3, 2 -> 4, 1]
                14) 8, 10
                    {Include, Upper, Lower, Number, New Scope}
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match='3'>>> ws:None [3, 1 -> 3, 2]
                            Newline+ <<9, 10>> ws:None [3, 2 -> 4, 1]
                15) 8, 10
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match='3'>>> ws:None [3, 1 -> 3, 2]
                                Newline+ <<9, 10>> ws:None [3, 2 -> 4, 1]
                """,
            )

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
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Lower
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                                Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Upper
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                                Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Include
                                Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                                Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                                Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                """,
            )

            number_results = all_results["number"]

            assert str(number_results) == textwrap.dedent(
                """\
                <Root>
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                                Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                                Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                                Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                """,
            )

            assert MethodCallsToString(
                observer.on_statement_complete_mock,
                attribute_name="call_args_list",
            ) == textwrap.dedent(
                """\
                0) 0, 3
                    Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                1) 3, 4
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                2) 0, 4
                    Lower
                        Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                3) 0, 4
                    {Include, Upper, Lower, Number, New Scope}
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                4) 0, 4
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Lower
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                                Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                5) 4, 7
                    Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                6) 7, 8
                    Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                7) 4, 8
                    Upper
                        Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                        Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                8) 4, 7
                    Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                9) 4, 8
                    {Include, Upper, Lower, Number, New Scope}
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                10) 4, 8
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Upper
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                                Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                11) 8, 15
                    Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                12) 16, 22
                    Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                13) 22, 23
                    Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                14) 0, 1
                    Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                15) 1, 2
                    Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                16) 0, 2
                    Number
                        Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                        Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                17) 0, 2
                    {Include, Upper, Lower, Number, New Scope}
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                            Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                18) 0, 2
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                                Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                19) 2, 3
                    Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                20) 3, 4
                    Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                21) 2, 4
                    Number
                        Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                        Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                22) 2, 4
                    {Include, Upper, Lower, Number, New Scope}
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                            Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                23) 2, 4
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                                Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                24) 4, 5
                    Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                25) 5, 6
                    Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                26) 4, 6
                    Number
                        Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                        Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                27) 4, 6
                    {Include, Upper, Lower, Number, New Scope}
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                            Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                28) 4, 6
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                                Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                29) 8, 15
                    Lower Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                30) 8, 23
                    {Include, Upper, Lower, Number, New Scope}
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                            Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                31) 8, 23
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Include
                                Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                                Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                32) 23, 24
                    Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                33) 24, 25
                    Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                34) 23, 25
                    Number
                        Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                        Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                35) 23, 24
                    Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                36) 23, 25
                    {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                            Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                37) 23, 25
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                                Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                """,
            )

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
                single_threaded=True,
            )

            assert len(all_results) == 2
            assert "one" in all_results
            assert "number" in all_results

            one_results = all_results["one"]

            assert str(one_results) == textwrap.dedent(
                """\
                <Root>
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Lower
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                                Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Upper
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                                Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Include
                                Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                                Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                                Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                            Include
                                Include Token <<Regex: <_sre.SRE_Match object; span=(25, 32), match='include'>>> ws:None [5, 1 -> 5, 8]
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(33, 39), match='number'>>> ws:(32, 33) [5, 9 -> 5, 15]
                                Newline+ <<39, 40>> ws:None [5, 15 -> 6, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(40, 41), match='4'>>> ws:None [6, 1 -> 6, 2]
                                Newline+ <<41, 42>> ws:None [6, 2 -> 7, 1]
                """,
            )

            assert MethodCallsToString(
                observer.on_statement_complete_mock,
                attribute_name="call_args_list",
            ) == textwrap.dedent(
                """\
                0) 0, 3
                    Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                1) 3, 4
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                2) 0, 4
                    Lower
                        Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                3) 0, 4
                    {Include, Upper, Lower, Number, New Scope}
                        Lower
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                4) 0, 4
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Lower
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                                Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                5) 4, 7
                    Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                6) 7, 8
                    Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                7) 4, 8
                    Upper
                        Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                        Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                8) 4, 7
                    Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                9) 4, 8
                    {Include, Upper, Lower, Number, New Scope}
                        Upper
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                10) 4, 8
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Upper
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                                Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                11) 8, 15
                    Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                12) 16, 22
                    Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                13) 22, 23
                    Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                14) 0, 1
                    Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                15) 1, 2
                    Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                16) 0, 2
                    Number
                        Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                        Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                17) 0, 2
                    {Include, Upper, Lower, Number, New Scope}
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                            Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                18) 0, 2
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                                Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                19) 2, 3
                    Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                20) 3, 4
                    Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                21) 2, 4
                    Number
                        Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                        Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                22) 2, 4
                    {Include, Upper, Lower, Number, New Scope}
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                            Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                23) 2, 4
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                                Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                24) 4, 5
                    Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                25) 5, 6
                    Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                26) 4, 6
                    Number
                        Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                        Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                27) 4, 6
                    {Include, Upper, Lower, Number, New Scope}
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                            Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                28) 4, 6
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                                Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                29) 8, 15
                    Lower Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                30) 8, 23
                    {Include, Upper, Lower, Number, New Scope}
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                            Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                31) 8, 23
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Include
                                Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                                Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                32) 23, 24
                    Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                33) 24, 25
                    Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                34) 23, 25
                    Number
                        Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                        Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                35) 23, 24
                    Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                36) 23, 25
                    {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                            Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                37) 23, 25
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                                Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                38) 25, 32
                    Include Token <<Regex: <_sre.SRE_Match object; span=(25, 32), match='include'>>> ws:None [5, 1 -> 5, 8]
                39) 33, 39
                    Lower Token <<Regex: <_sre.SRE_Match object; span=(33, 39), match='number'>>> ws:(32, 33) [5, 9 -> 5, 15]
                40) 39, 40
                    Newline+ <<39, 40>> ws:None [5, 15 -> 6, 1]
                41) 25, 32
                    Lower Token <<Regex: <_sre.SRE_Match object; span=(25, 32), match='include'>>> ws:None [5, 1 -> 5, 8]
                42) 25, 40
                    {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                        Include
                            Include Token <<Regex: <_sre.SRE_Match object; span=(25, 32), match='include'>>> ws:None [5, 1 -> 5, 8]
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(33, 39), match='number'>>> ws:(32, 33) [5, 9 -> 5, 15]
                            Newline+ <<39, 40>> ws:None [5, 15 -> 6, 1]
                43) 25, 40
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                            Include
                                Include Token <<Regex: <_sre.SRE_Match object; span=(25, 32), match='include'>>> ws:None [5, 1 -> 5, 8]
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(33, 39), match='number'>>> ws:(32, 33) [5, 9 -> 5, 15]
                                Newline+ <<39, 40>> ws:None [5, 15 -> 6, 1]
                44) 40, 41
                    Number Token <<Regex: <_sre.SRE_Match object; span=(40, 41), match='4'>>> ws:None [6, 1 -> 6, 2]
                45) 41, 42
                    Newline+ <<41, 42>> ws:None [6, 2 -> 7, 1]
                46) 40, 42
                    Number
                        Number Token <<Regex: <_sre.SRE_Match object; span=(40, 41), match='4'>>> ws:None [6, 1 -> 6, 2]
                        Newline+ <<41, 42>> ws:None [6, 2 -> 7, 1]
                47) 40, 41
                    Number Token <<Regex: <_sre.SRE_Match object; span=(40, 41), match='4'>>> ws:None [6, 1 -> 6, 2]
                48) 40, 42
                    {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                        Number
                            Number Token <<Regex: <_sre.SRE_Match object; span=(40, 41), match='4'>>> ws:None [6, 1 -> 6, 2]
                            Newline+ <<41, 42>> ws:None [6, 2 -> 7, 1]
                49) 40, 42
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(40, 41), match='4'>>> ws:None [6, 1 -> 6, 2]
                                Newline+ <<41, 42>> ws:None [6, 2 -> 7, 1]
                """,
            )

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
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Lower
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                                Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Upper
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                                Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Include
                                Include Token <<Regex: <_sre.SRE_Match object; span=(8, 15), match='include'>>> ws:None [3, 1 -> 3, 8]
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(16, 22), match='number'>>> ws:(15, 16) [3, 9 -> 3, 15]
                                Newline+ <<22, 23>> ws:None [3, 15 -> 4, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(23, 24), match='3'>>> ws:None [4, 1 -> 4, 2]
                                Newline+ <<24, 25>> ws:None [4, 2 -> 5, 1]
                """,
            )

            two_results = results["two"]

            assert str(two_results) == textwrap.dedent(
                """\
                <Root>
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Lower
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='aaa'>>> ws:None [1, 1 -> 1, 4]
                                Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Upper
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 8), match='BBBB'>>> ws:None [2, 1 -> 2, 5]
                                Newline+ <<8, 9>> ws:None [2, 5 -> 3, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Include
                                Include Token <<Regex: <_sre.SRE_Match object; span=(9, 16), match='include'>>> ws:None [3, 1 -> 3, 8]
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(17, 23), match='number'>>> ws:(16, 17) [3, 9 -> 3, 15]
                                Newline+ <<23, 24>> ws:None [3, 15 -> 4, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                            Lower
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(24, 30), match='cccccc'>>> ws:None [4, 1 -> 4, 7]
                                Newline+ <<30, 31>> ws:None [4, 7 -> 5, 1]
                """,
            )

            number_results = results["number"]

            assert str(number_results) == textwrap.dedent(
                """\
                <Root>
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 1), match='4'>>> ws:None [1, 1 -> 1, 2]
                                Newline+ <<1, 2>> ws:None [1, 2 -> 2, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(2, 3), match='5'>>> ws:None [2, 1 -> 2, 2]
                                Newline+ <<3, 4>> ws:None [2, 2 -> 3, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Number
                                Number Token <<Regex: <_sre.SRE_Match object; span=(4, 5), match='6'>>> ws:None [3, 1 -> 3, 2]
                                Newline+ <<5, 6>> ws:None [3, 2 -> 4, 1]
                """,
            )

            assert len(observer.on_statement_complete_mock.call_args_list) == 60

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
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Include
                                Include Token <<Regex: <_sre.SRE_Match object; span=(0, 7), match='include'>>> ws:None [1, 1 -> 1, 8]
                                Lower Token <<Regex: <_sre.SRE_Match object; span=(8, 14), match='number'>>> ws:(7, 8) [1, 9 -> 1, 15]
                                Newline+ <<14, 15>> ws:None [1, 15 -> 2, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
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

                <Root>
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            New Scope
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(0, 8), match='NEWSCOPE'>>> ws:None [1, 1 -> 1, 9]
                                Colon Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match=':'>>> ws:None [1, 9 -> 1, 10]
                                Newline+ <<9, 10>> ws:None [1, 10 -> 2, 1]
                                Indent <<10, 14, (4)>> ws:None [2, 1 -> 2, 5]
                                DynamicStatements.Statements
                                    {Include, Upper, Lower, Number, New Scope}
                                        Include
                                            Include Token <<Regex: <_sre.SRE_Match object; span=(14, 21), match='include'>>> ws:None [2, 5 -> 2, 12]
                                            Lower Token <<Regex: <_sre.SRE_Match object; span=(22, 28), match='number'>>> ws:(21, 22) [2, 13 -> 2, 19]
                                            Newline+ <<28, 29>> ws:None [2, 19 -> 3, 1]
                                DynamicStatements.Statements
                                    {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
                                        Dynamic Number
                                            Number Token <<Regex: <_sre.SRE_Match object; span=(33, 34), match='4'>>> ws:None [3, 5 -> 3, 6]
                                            Number Token <<Regex: <_sre.SRE_Match object; span=(35, 36), match='5'>>> ws:(34, 35) [3, 7 -> 3, 8]
                                            Number Token <<Regex: <_sre.SRE_Match object; span=(37, 38), match='6'>>> ws:(36, 37) [3, 9 -> 3, 10]
                                            Newline+ <<38, 39>> ws:None [3, 10 -> 4, 1]
                                Dedent <<>> ws:None [4, 1 -> 4, 1]
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            Include
                                Include
                                    <No Children>
                            Upper
                                Upper
                                    <No Children>
                            Lower
                                Lower
                                    <No Children>
                            Number
                                Number
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(39, 40), match='7'>>> ws:None [4, 1 -> 4, 2]
                            New Scope
                                New Scope
                                    <No Children>
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
                    Dynamic Statements
                        {Include, Upper, Lower, Number, New Scope}
                            New Scope
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(0, 8), match='NEWSCOPE'>>> ws:None [1, 1 -> 1, 9]
                                Colon Token <<Regex: <_sre.SRE_Match object; span=(8, 9), match=':'>>> ws:None [1, 9 -> 1, 10]
                                Newline+ <<9, 10>> ws:None [1, 10 -> 2, 1]
                                Indent <<10, 14, (4)>> ws:None [2, 1 -> 2, 5]
                                DynamicStatements.Statements
                                    {Include, Upper, Lower, Number, New Scope}
                                        Include
                                            Include Token <<Regex: <_sre.SRE_Match object; span=(14, 21), match='include'>>> ws:None [2, 5 -> 2, 12]
                                            Lower Token <<Regex: <_sre.SRE_Match object; span=(22, 28), match='number'>>> ws:(21, 22) [2, 13 -> 2, 19]
                                            Newline+ <<28, 29>> ws:None [2, 19 -> 3, 1]
                                DynamicStatements.Statements
                                    {Include, Upper, Lower, Number, New Scope} / {Dynamic Number}
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
    node = Node(CreateStatement(name="Statement", item=NewlineToken()))

    assert str(node) == textwrap.dedent(
        """\
        Statement
            <No Children>
        """,
    )

# TODO: Circular dependencies
