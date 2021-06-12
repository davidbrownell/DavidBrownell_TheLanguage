# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-11 15:23:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for FuncInvocationStatement.py"""

import os
import textwrap

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import PatchAndExecute, PatchAndExecuteFlag
    from ..FuncInvocationStatement import *


# ----------------------------------------------------------------------
def Execute(content: str):
    result = PatchAndExecute(
        {
            "filename" : content,
        },
        ["filename"],
        [],
        flag=PatchAndExecuteFlag.Validate,
        max_num_threads=1,
    )

    return result["filename"]

# ----------------------------------------------------------------------
def test_PositionalArgs():
    result = Execute(
        textwrap.dedent(
            """\
            func1()
            func2(a2)
            func3(a3,)
            func4(a4, b4, c4)
            func5(a5, b5, c5, )

            func6(
                a6
            )

            func7(
                a7,
                    b7,
                c7,
            )
            """,
        ),
    )

    assert str(result) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='func1'>>> ws:None [1, 1 -> 1, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='('>>> ws:None [1, 6 -> 1, 7]
                    ')' <<Regex: <_sre.SRE_Match object; span=(6, 7), match=')'>>> ws:None [1, 7 -> 1, 8]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(8, 13), match='func2'>>> ws:None [2, 1 -> 2, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [2, 6 -> 2, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                <name> <<Regex: <_sre.SRE_Match object; span=(14, 16), match='a2'>>> ws:None [2, 7 -> 2, 9]
                    ')' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=')'>>> ws:None [2, 9 -> 2, 10]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(18, 23), match='func3'>>> ws:None [3, 1 -> 3, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(23, 24), match='('>>> ws:None [3, 6 -> 3, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                <name> <<Regex: <_sre.SRE_Match object; span=(24, 26), match='a3'>>> ws:None [3, 7 -> 3, 9]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(26, 27), match=','>>> ws:None [3, 9 -> 3, 10]
                    ')' <<Regex: <_sre.SRE_Match object; span=(27, 28), match=')'>>> ws:None [3, 10 -> 3, 11]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(29, 34), match='func4'>>> ws:None [4, 1 -> 4, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(34, 35), match='('>>> ws:None [4, 6 -> 4, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                <name> <<Regex: <_sre.SRE_Match object; span=(35, 37), match='a4'>>> ws:None [4, 7 -> 4, 9]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(37, 38), match=','>>> ws:None [4, 9 -> 4, 10]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(39, 41), match='b4'>>> ws:(38, 39) [4, 11 -> 4, 13]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(41, 42), match=','>>> ws:None [4, 13 -> 4, 14]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(43, 45), match='c4'>>> ws:(42, 43) [4, 15 -> 4, 17]
                    ')' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=')'>>> ws:None [4, 17 -> 4, 18]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(47, 52), match='func5'>>> ws:None [5, 1 -> 5, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(52, 53), match='('>>> ws:None [5, 6 -> 5, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                <name> <<Regex: <_sre.SRE_Match object; span=(53, 55), match='a5'>>> ws:None [5, 7 -> 5, 9]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(55, 56), match=','>>> ws:None [5, 9 -> 5, 10]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(57, 59), match='b5'>>> ws:(56, 57) [5, 11 -> 5, 13]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(59, 60), match=','>>> ws:None [5, 13 -> 5, 14]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(61, 63), match='c5'>>> ws:(60, 61) [5, 15 -> 5, 17]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(63, 64), match=','>>> ws:None [5, 17 -> 5, 18]
                    ')' <<Regex: <_sre.SRE_Match object; span=(65, 66), match=')'>>> ws:(64, 65) [5, 19 -> 5, 20]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(68, 73), match='func6'>>> ws:None [7, 1 -> 7, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(73, 74), match='('>>> ws:None [7, 6 -> 7, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                <name> <<Regex: <_sre.SRE_Match object; span=(79, 81), match='a6'>>> ws:None [8, 5 -> 8, 7]
                    ')' <<Regex: <_sre.SRE_Match object; span=(82, 83), match=')'>>> ws:None [9, 1 -> 9, 2]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(85, 90), match='func7'>>> ws:None [11, 1 -> 11, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(90, 91), match='('>>> ws:None [11, 6 -> 11, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                <name> <<Regex: <_sre.SRE_Match object; span=(96, 98), match='a7'>>> ws:None [12, 5 -> 12, 7]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(98, 99), match=','>>> ws:None [12, 7 -> 12, 8]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(108, 110), match='b7'>>> ws:None [13, 9 -> 13, 11]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(110, 111), match=','>>> ws:None [13, 11 -> 13, 12]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(116, 118), match='c7'>>> ws:None [14, 5 -> 14, 7]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(118, 119), match=','>>> ws:None [14, 7 -> 14, 8]
                    ')' <<Regex: <_sre.SRE_Match object; span=(120, 121), match=')'>>> ws:None [15, 1 -> 15, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_KeywordArgs():
    result = Execute(
        textwrap.dedent(
            """\
            func1()
            func2(a=a2)
            func3(a=a3, )
            func4(a=a4, b=b4, c=c4)
            func5(aa=a5, bee=b5, cee=c5, )

            func6(
                six=a6
            )

            func7(
                seven=a7,
                    b=b7,
                        c=c7,
            )
            """,
        ),
    )

    assert str(result) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='func1'>>> ws:None [1, 1 -> 1, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='('>>> ws:None [1, 6 -> 1, 7]
                    ')' <<Regex: <_sre.SRE_Match object; span=(6, 7), match=')'>>> ws:None [1, 7 -> 1, 8]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(8, 13), match='func2'>>> ws:None [2, 1 -> 2, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [2, 6 -> 2, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                Named
                                    <name> <<Regex: <_sre.SRE_Match object; span=(14, 15), match='a'>>> ws:None [2, 7 -> 2, 8]
                                    '=' <<Regex: <_sre.SRE_Match object; span=(15, 16), match='='>>> ws:None [2, 8 -> 2, 9]
                                    Or: [DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(16, 18), match='a2'>>> ws:None [2, 9 -> 2, 11]
                    ')' <<Regex: <_sre.SRE_Match object; span=(18, 19), match=')'>>> ws:None [2, 11 -> 2, 12]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(20, 25), match='func3'>>> ws:None [3, 1 -> 3, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(25, 26), match='('>>> ws:None [3, 6 -> 3, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                Named
                                    <name> <<Regex: <_sre.SRE_Match object; span=(26, 27), match='a'>>> ws:None [3, 7 -> 3, 8]
                                    '=' <<Regex: <_sre.SRE_Match object; span=(27, 28), match='='>>> ws:None [3, 8 -> 3, 9]
                                    Or: [DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(28, 30), match='a3'>>> ws:None [3, 9 -> 3, 11]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(30, 31), match=','>>> ws:None [3, 11 -> 3, 12]
                    ')' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=')'>>> ws:(31, 32) [3, 13 -> 3, 14]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(34, 39), match='func4'>>> ws:None [4, 1 -> 4, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(39, 40), match='('>>> ws:None [4, 6 -> 4, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                Named
                                    <name> <<Regex: <_sre.SRE_Match object; span=(40, 41), match='a'>>> ws:None [4, 7 -> 4, 8]
                                    '=' <<Regex: <_sre.SRE_Match object; span=(41, 42), match='='>>> ws:None [4, 8 -> 4, 9]
                                    Or: [DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(42, 44), match='a4'>>> ws:None [4, 9 -> 4, 11]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=','>>> ws:None [4, 11 -> 4, 12]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        Named
                                            <name> <<Regex: <_sre.SRE_Match object; span=(46, 47), match='b'>>> ws:(45, 46) [4, 13 -> 4, 14]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(47, 48), match='='>>> ws:None [4, 14 -> 4, 15]
                                            Or: [DynamicStatements.Expressions, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(48, 50), match='b4'>>> ws:None [4, 15 -> 4, 17]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(50, 51), match=','>>> ws:None [4, 17 -> 4, 18]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        Named
                                            <name> <<Regex: <_sre.SRE_Match object; span=(52, 53), match='c'>>> ws:(51, 52) [4, 19 -> 4, 20]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(53, 54), match='='>>> ws:None [4, 20 -> 4, 21]
                                            Or: [DynamicStatements.Expressions, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(54, 56), match='c4'>>> ws:None [4, 21 -> 4, 23]
                    ')' <<Regex: <_sre.SRE_Match object; span=(56, 57), match=')'>>> ws:None [4, 23 -> 4, 24]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(58, 63), match='func5'>>> ws:None [5, 1 -> 5, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(63, 64), match='('>>> ws:None [5, 6 -> 5, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                Named
                                    <name> <<Regex: <_sre.SRE_Match object; span=(64, 66), match='aa'>>> ws:None [5, 7 -> 5, 9]
                                    '=' <<Regex: <_sre.SRE_Match object; span=(66, 67), match='='>>> ws:None [5, 9 -> 5, 10]
                                    Or: [DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(67, 69), match='a5'>>> ws:None [5, 10 -> 5, 12]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(69, 70), match=','>>> ws:None [5, 12 -> 5, 13]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        Named
                                            <name> <<Regex: <_sre.SRE_Match object; span=(71, 74), match='bee'>>> ws:(70, 71) [5, 14 -> 5, 17]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(74, 75), match='='>>> ws:None [5, 17 -> 5, 18]
                                            Or: [DynamicStatements.Expressions, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(75, 77), match='b5'>>> ws:None [5, 18 -> 5, 20]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(77, 78), match=','>>> ws:None [5, 20 -> 5, 21]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        Named
                                            <name> <<Regex: <_sre.SRE_Match object; span=(79, 82), match='cee'>>> ws:(78, 79) [5, 22 -> 5, 25]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(82, 83), match='='>>> ws:None [5, 25 -> 5, 26]
                                            Or: [DynamicStatements.Expressions, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(83, 85), match='c5'>>> ws:None [5, 26 -> 5, 28]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(85, 86), match=','>>> ws:None [5, 28 -> 5, 29]
                    ')' <<Regex: <_sre.SRE_Match object; span=(87, 88), match=')'>>> ws:(86, 87) [5, 30 -> 5, 31]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(90, 95), match='func6'>>> ws:None [7, 1 -> 7, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(95, 96), match='('>>> ws:None [7, 6 -> 7, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                Named
                                    <name> <<Regex: <_sre.SRE_Match object; span=(101, 104), match='six'>>> ws:None [8, 5 -> 8, 8]
                                    '=' <<Regex: <_sre.SRE_Match object; span=(104, 105), match='='>>> ws:None [8, 8 -> 8, 9]
                                    Or: [DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(105, 107), match='a6'>>> ws:None [8, 9 -> 8, 11]
                    ')' <<Regex: <_sre.SRE_Match object; span=(108, 109), match=')'>>> ws:None [9, 1 -> 9, 2]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(111, 116), match='func7'>>> ws:None [11, 1 -> 11, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(116, 117), match='('>>> ws:None [11, 6 -> 11, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                Named
                                    <name> <<Regex: <_sre.SRE_Match object; span=(122, 127), match='seven'>>> ws:None [12, 5 -> 12, 10]
                                    '=' <<Regex: <_sre.SRE_Match object; span=(127, 128), match='='>>> ws:None [12, 10 -> 12, 11]
                                    Or: [DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(128, 130), match='a7'>>> ws:None [12, 11 -> 12, 13]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(130, 131), match=','>>> ws:None [12, 13 -> 12, 14]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        Named
                                            <name> <<Regex: <_sre.SRE_Match object; span=(140, 141), match='b'>>> ws:None [13, 9 -> 13, 10]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(141, 142), match='='>>> ws:None [13, 10 -> 13, 11]
                                            Or: [DynamicStatements.Expressions, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(142, 144), match='b7'>>> ws:None [13, 11 -> 13, 13]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(144, 145), match=','>>> ws:None [13, 13 -> 13, 14]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        Named
                                            <name> <<Regex: <_sre.SRE_Match object; span=(158, 159), match='c'>>> ws:None [14, 13 -> 14, 14]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(159, 160), match='='>>> ws:None [14, 14 -> 14, 15]
                                            Or: [DynamicStatements.Expressions, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(160, 162), match='c7'>>> ws:None [14, 15 -> 14, 17]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(162, 163), match=','>>> ws:None [14, 17 -> 14, 18]
                    ')' <<Regex: <_sre.SRE_Match object; span=(164, 165), match=')'>>> ws:None [15, 1 -> 15, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_PositionalAndKeywordArgs():
    result = Execute(
        textwrap.dedent(
            """\
            func1(a1, b=b1)
            func2(a2, bee=b2,)
            func3(a3, b3, c=c3)
            func4(
                a4, b4, c4,
                dee4=4, eee4=4
            )
            """,
        ),
    )

    assert str(result) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='func1'>>> ws:None [1, 1 -> 1, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='('>>> ws:None [1, 6 -> 1, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                <name> <<Regex: <_sre.SRE_Match object; span=(6, 8), match='a1'>>> ws:None [1, 7 -> 1, 9]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(8, 9), match=','>>> ws:None [1, 9 -> 1, 10]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        Named
                                            <name> <<Regex: <_sre.SRE_Match object; span=(10, 11), match='b'>>> ws:(9, 10) [1, 11 -> 1, 12]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(11, 12), match='='>>> ws:None [1, 12 -> 1, 13]
                                            Or: [DynamicStatements.Expressions, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(12, 14), match='b1'>>> ws:None [1, 13 -> 1, 15]
                    ')' <<Regex: <_sre.SRE_Match object; span=(14, 15), match=')'>>> ws:None [1, 15 -> 1, 16]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(16, 21), match='func2'>>> ws:None [2, 1 -> 2, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(21, 22), match='('>>> ws:None [2, 6 -> 2, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                <name> <<Regex: <_sre.SRE_Match object; span=(22, 24), match='a2'>>> ws:None [2, 7 -> 2, 9]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(24, 25), match=','>>> ws:None [2, 9 -> 2, 10]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        Named
                                            <name> <<Regex: <_sre.SRE_Match object; span=(26, 29), match='bee'>>> ws:(25, 26) [2, 11 -> 2, 14]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(29, 30), match='='>>> ws:None [2, 14 -> 2, 15]
                                            Or: [DynamicStatements.Expressions, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(30, 32), match='b2'>>> ws:None [2, 15 -> 2, 17]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=','>>> ws:None [2, 17 -> 2, 18]
                    ')' <<Regex: <_sre.SRE_Match object; span=(33, 34), match=')'>>> ws:None [2, 18 -> 2, 19]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(35, 40), match='func3'>>> ws:None [3, 1 -> 3, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(40, 41), match='('>>> ws:None [3, 6 -> 3, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                <name> <<Regex: <_sre.SRE_Match object; span=(41, 43), match='a3'>>> ws:None [3, 7 -> 3, 9]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(43, 44), match=','>>> ws:None [3, 9 -> 3, 10]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(45, 47), match='b3'>>> ws:(44, 45) [3, 11 -> 3, 13]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(47, 48), match=','>>> ws:None [3, 13 -> 3, 14]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        Named
                                            <name> <<Regex: <_sre.SRE_Match object; span=(49, 50), match='c'>>> ws:(48, 49) [3, 15 -> 3, 16]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(50, 51), match='='>>> ws:None [3, 16 -> 3, 17]
                                            Or: [DynamicStatements.Expressions, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(51, 53), match='c3'>>> ws:None [3, 17 -> 3, 19]
                    ')' <<Regex: <_sre.SRE_Match object; span=(53, 54), match=')'>>> ws:None [3, 19 -> 3, 20]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(55, 60), match='func4'>>> ws:None [4, 1 -> 4, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(60, 61), match='('>>> ws:None [4, 6 -> 4, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                <name> <<Regex: <_sre.SRE_Match object; span=(66, 68), match='a4'>>> ws:None [5, 5 -> 5, 7]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(68, 69), match=','>>> ws:None [5, 7 -> 5, 8]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(70, 72), match='b4'>>> ws:(69, 70) [5, 9 -> 5, 11]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(72, 73), match=','>>> ws:None [5, 11 -> 5, 12]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(74, 76), match='c4'>>> ws:(73, 74) [5, 13 -> 5, 15]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(76, 77), match=','>>> ws:None [5, 15 -> 5, 16]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        Named
                                            <name> <<Regex: <_sre.SRE_Match object; span=(82, 86), match='dee4'>>> ws:None [6, 5 -> 6, 9]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(86, 87), match='='>>> ws:None [6, 9 -> 6, 10]
                                            Or: [DynamicStatements.Expressions, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(87, 88), match='4'>>> ws:None [6, 10 -> 6, 11]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(88, 89), match=','>>> ws:None [6, 11 -> 6, 12]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        Named
                                            <name> <<Regex: <_sre.SRE_Match object; span=(90, 94), match='eee4'>>> ws:(89, 90) [6, 13 -> 6, 17]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(94, 95), match='='>>> ws:None [6, 17 -> 6, 18]
                                            Or: [DynamicStatements.Expressions, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(95, 96), match='4'>>> ws:None [6, 18 -> 6, 19]
                    ')' <<Regex: <_sre.SRE_Match object; span=(97, 98), match=')'>>> ws:None [7, 1 -> 7, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_MethodName():
    result = Execute(
        textwrap.dedent(
            """\
            one.two.three(1, 2, 3)
            instance.method()
            """,
        ),
    )

    assert str(result) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 13), match='one.two.three'>>> ws:None [1, 1 -> 1, 14]
                    '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [1, 14 -> 1, 15]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                <name> <<Regex: <_sre.SRE_Match object; span=(14, 15), match='1'>>> ws:None [1, 15 -> 1, 16]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(15, 16), match=','>>> ws:None [1, 16 -> 1, 17]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(17, 18), match='2'>>> ws:(16, 17) [1, 18 -> 1, 19]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(18, 19), match=','>>> ws:None [1, 19 -> 1, 20]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(20, 21), match='3'>>> ws:(19, 20) [1, 21 -> 1, 22]
                    ')' <<Regex: <_sre.SRE_Match object; span=(21, 22), match=')'>>> ws:None [1, 22 -> 1, 23]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(23, 38), match='instance.method'>>> ws:None [2, 1 -> 2, 16]
                    '(' <<Regex: <_sre.SRE_Match object; span=(38, 39), match='('>>> ws:None [2, 16 -> 2, 17]
                    ')' <<Regex: <_sre.SRE_Match object; span=(39, 40), match=')'>>> ws:None [2, 17 -> 2, 18]
        """,
    )

# ----------------------------------------------------------------------
def test_Fractcal():
    result = Execute(
        textwrap.dedent(
            """\
            func8(
                func9(),
                func10(),
                func11(a11, func12(1, key=2), c11),
            )
            """,
        ),
    )

    assert str(result) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='func8'>>> ws:None [1, 1 -> 1, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='('>>> ws:None [1, 6 -> 1, 7]
                    Repeat: (Parameters, 0, 1)
                        Parameters
                            Or: [Named, DynamicStatements.Expressions, <name>]
                                DynamicStatements.Expressions
                                    1.0.0 Grammar
                                        Function Invocation
                                            <name> <<Regex: <_sre.SRE_Match object; span=(11, 16), match='func9'>>> ws:None [2, 5 -> 2, 10]
                                            '(' <<Regex: <_sre.SRE_Match object; span=(16, 17), match='('>>> ws:None [2, 10 -> 2, 11]
                                            ')' <<Regex: <_sre.SRE_Match object; span=(17, 18), match=')'>>> ws:None [2, 11 -> 2, 12]
                            Repeat: (Comma and Statement, 0, None)
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(18, 19), match=','>>> ws:None [2, 12 -> 2, 13]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Function Invocation
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(24, 30), match='func10'>>> ws:None [3, 5 -> 3, 11]
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(30, 31), match='('>>> ws:None [3, 11 -> 3, 12]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(31, 32), match=')'>>> ws:None [3, 12 -> 3, 13]
                                Comma and Statement
                                    ',' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=','>>> ws:None [3, 13 -> 3, 14]
                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Function Invocation
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(38, 44), match='func11'>>> ws:None [4, 5 -> 4, 11]
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(44, 45), match='('>>> ws:None [4, 11 -> 4, 12]
                                                    Repeat: (Parameters, 0, 1)
                                                        Parameters
                                                            Or: [Named, DynamicStatements.Expressions, <name>]
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(45, 48), match='a11'>>> ws:None [4, 12 -> 4, 15]
                                                            Repeat: (Comma and Statement, 0, None)
                                                                Comma and Statement
                                                                    ',' <<Regex: <_sre.SRE_Match object; span=(48, 49), match=','>>> ws:None [4, 15 -> 4, 16]
                                                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                                                        DynamicStatements.Expressions
                                                                            1.0.0 Grammar
                                                                                Function Invocation
                                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(50, 56), match='func12'>>> ws:(49, 50) [4, 17 -> 4, 23]
                                                                                    '(' <<Regex: <_sre.SRE_Match object; span=(56, 57), match='('>>> ws:None [4, 23 -> 4, 24]
                                                                                    Repeat: (Parameters, 0, 1)
                                                                                        Parameters
                                                                                            Or: [Named, DynamicStatements.Expressions, <name>]
                                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(57, 58), match='1'>>> ws:None [4, 24 -> 4, 25]
                                                                                            Repeat: (Comma and Statement, 0, None)
                                                                                                Comma and Statement
                                                                                                    ',' <<Regex: <_sre.SRE_Match object; span=(58, 59), match=','>>> ws:None [4, 25 -> 4, 26]
                                                                                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                                                                                        Named
                                                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(60, 63), match='key'>>> ws:(59, 60) [4, 27 -> 4, 30]
                                                                                                            '=' <<Regex: <_sre.SRE_Match object; span=(63, 64), match='='>>> ws:None [4, 30 -> 4, 31]
                                                                                                            Or: [DynamicStatements.Expressions, <name>]
                                                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(64, 65), match='2'>>> ws:None [4, 31 -> 4, 32]
                                                                                    ')' <<Regex: <_sre.SRE_Match object; span=(65, 66), match=')'>>> ws:None [4, 32 -> 4, 33]
                                                                Comma and Statement
                                                                    ',' <<Regex: <_sre.SRE_Match object; span=(66, 67), match=','>>> ws:None [4, 33 -> 4, 34]
                                                                    Or: [Named, DynamicStatements.Expressions, <name>]
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(68, 71), match='c11'>>> ws:(67, 68) [4, 35 -> 4, 38]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(71, 72), match=')'>>> ws:None [4, 38 -> 4, 39]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(72, 73), match=','>>> ws:None [4, 39 -> 4, 40]
                    ')' <<Regex: <_sre.SRE_Match object; span=(74, 75), match=')'>>> ws:None [5, 1 -> 5, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_PositionalAfterKeywordError():
    with pytest.raises(PositionalParamAfterKeywordParamError) as ex:
        Execute(
            textwrap.dedent(
                """\
                func(a, b, c, d=d, bad_arg)
                """,
            ),
        )

    result = ex.value

    assert str(result) == "Positional arguments may not appear after keyword arguments"
    assert result.FullyQualifiedName == "filename"
    assert result.Line == 1
    assert result.LineEnd == 1
    assert result.Column == 20
    assert result.ColumnEnd == 27
