# ----------------------------------------------------------------------
# |
# |  FuncInvocationHybrid_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 00:30:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for FuncInvocationHybrid.py"""

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
    from . import Execute
    from ..FuncInvocationHybrid import *


# ----------------------------------------------------------------------
def test_NoArgs():
    assert Execute(
        textwrap.dedent(
            """\
            Func1()
            Func2(
            )
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='Func1'>>> ws:None [1, 1 -> 1, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='('>>> ws:None [1, 6 -> 1, 7]
                    ')' <<Regex: <_sre.SRE_Match object; span=(6, 7), match=')'>>> ws:None [1, 7 -> 1, 8]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(8, 13), match='Func2'>>> ws:None [2, 1 -> 2, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [2, 6 -> 2, 7]
                    ')' <<Regex: <_sre.SRE_Match object; span=(15, 16), match=')'>>> ws:None [3, 1 -> 3, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_SingleArg():
    assert Execute(
        textwrap.dedent(
            """\
            Func1(a)
            Func2(
                a
            )
            Func3(a=value)
            Func4(
                a=value,
            )
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='Func1'>>> ws:None [1, 1 -> 1, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='('>>> ws:None [1, 6 -> 1, 7]
                    Repeat: (Arguments, 0, 1)
                        Arguments
                            Or: [Keyword, DynamicStatements.Expressions]
                                DynamicStatements.Expressions
                                    1.0.0 Grammar
                                        Variable Name
                                            <name> <<Regex: <_sre.SRE_Match object; span=(6, 7), match='a'>>> ws:None [1, 7 -> 1, 8]
                    ')' <<Regex: <_sre.SRE_Match object; span=(7, 8), match=')'>>> ws:None [1, 8 -> 1, 9]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(9, 14), match='Func2'>>> ws:None [2, 1 -> 2, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(14, 15), match='('>>> ws:None [2, 6 -> 2, 7]
                    Repeat: (Arguments, 0, 1)
                        Arguments
                            Or: [Keyword, DynamicStatements.Expressions]
                                DynamicStatements.Expressions
                                    1.0.0 Grammar
                                        Variable Name
                                            <name> <<Regex: <_sre.SRE_Match object; span=(20, 21), match='a'>>> ws:None [3, 5 -> 3, 6]
                    ')' <<Regex: <_sre.SRE_Match object; span=(22, 23), match=')'>>> ws:None [4, 1 -> 4, 2]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(24, 29), match='Func3'>>> ws:None [5, 1 -> 5, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(29, 30), match='('>>> ws:None [5, 6 -> 5, 7]
                    Repeat: (Arguments, 0, 1)
                        Arguments
                            Or: [Keyword, DynamicStatements.Expressions]
                                Keyword
                                    <name> <<Regex: <_sre.SRE_Match object; span=(30, 31), match='a'>>> ws:None [5, 7 -> 5, 8]
                                    '=' <<Regex: <_sre.SRE_Match object; span=(31, 32), match='='>>> ws:None [5, 8 -> 5, 9]
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(32, 37), match='value'>>> ws:None [5, 9 -> 5, 14]
                    ')' <<Regex: <_sre.SRE_Match object; span=(37, 38), match=')'>>> ws:None [5, 14 -> 5, 15]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(39, 44), match='Func4'>>> ws:None [6, 1 -> 6, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(44, 45), match='('>>> ws:None [6, 6 -> 6, 7]
                    Repeat: (Arguments, 0, 1)
                        Arguments
                            Or: [Keyword, DynamicStatements.Expressions]
                                Keyword
                                    <name> <<Regex: <_sre.SRE_Match object; span=(50, 51), match='a'>>> ws:None [7, 5 -> 7, 6]
                                    '=' <<Regex: <_sre.SRE_Match object; span=(51, 52), match='='>>> ws:None [7, 6 -> 7, 7]
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(52, 57), match='value'>>> ws:None [7, 7 -> 7, 12]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(57, 58), match=','>>> ws:None [7, 12 -> 7, 13]
                    ')' <<Regex: <_sre.SRE_Match object; span=(59, 60), match=')'>>> ws:None [8, 1 -> 8, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_MultipleArgs():
    assert Execute(
        textwrap.dedent(
            """\
            Func1(a, b, c)

            Func2(a, b, c, d=one, e=two)

            Func3(
                a, b, c,
                d=one,
                e=two,
            )

            Func4(
                a,
                b,
                c,
                d=one,
                e=two,
            )
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='Func1'>>> ws:None [1, 1 -> 1, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='('>>> ws:None [1, 6 -> 1, 7]
                    Repeat: (Arguments, 0, 1)
                        Arguments
                            Or: [Keyword, DynamicStatements.Expressions]
                                DynamicStatements.Expressions
                                    1.0.0 Grammar
                                        Variable Name
                                            <name> <<Regex: <_sre.SRE_Match object; span=(6, 7), match='a'>>> ws:None [1, 7 -> 1, 8]
                            Repeat: (Comma and Argument, 0, None)
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(7, 8), match=','>>> ws:None [1, 8 -> 1, 9]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(9, 10), match='b'>>> ws:(8, 9) [1, 10 -> 1, 11]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(10, 11), match=','>>> ws:None [1, 11 -> 1, 12]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(12, 13), match='c'>>> ws:(11, 12) [1, 13 -> 1, 14]
                    ')' <<Regex: <_sre.SRE_Match object; span=(13, 14), match=')'>>> ws:None [1, 14 -> 1, 15]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(16, 21), match='Func2'>>> ws:None [3, 1 -> 3, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(21, 22), match='('>>> ws:None [3, 6 -> 3, 7]
                    Repeat: (Arguments, 0, 1)
                        Arguments
                            Or: [Keyword, DynamicStatements.Expressions]
                                DynamicStatements.Expressions
                                    1.0.0 Grammar
                                        Variable Name
                                            <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='a'>>> ws:None [3, 7 -> 3, 8]
                            Repeat: (Comma and Argument, 0, None)
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [3, 8 -> 3, 9]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='b'>>> ws:(24, 25) [3, 10 -> 3, 11]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(26, 27), match=','>>> ws:None [3, 11 -> 3, 12]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(28, 29), match='c'>>> ws:(27, 28) [3, 13 -> 3, 14]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=','>>> ws:None [3, 14 -> 3, 15]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        Keyword
                                            <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='d'>>> ws:(30, 31) [3, 16 -> 3, 17]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(32, 33), match='='>>> ws:None [3, 17 -> 3, 18]
                                            DynamicStatements.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(33, 36), match='one'>>> ws:None [3, 18 -> 3, 21]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(36, 37), match=','>>> ws:None [3, 21 -> 3, 22]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        Keyword
                                            <name> <<Regex: <_sre.SRE_Match object; span=(38, 39), match='e'>>> ws:(37, 38) [3, 23 -> 3, 24]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(39, 40), match='='>>> ws:None [3, 24 -> 3, 25]
                                            DynamicStatements.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(40, 43), match='two'>>> ws:None [3, 25 -> 3, 28]
                    ')' <<Regex: <_sre.SRE_Match object; span=(43, 44), match=')'>>> ws:None [3, 28 -> 3, 29]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(46, 51), match='Func3'>>> ws:None [5, 1 -> 5, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(51, 52), match='('>>> ws:None [5, 6 -> 5, 7]
                    Repeat: (Arguments, 0, 1)
                        Arguments
                            Or: [Keyword, DynamicStatements.Expressions]
                                DynamicStatements.Expressions
                                    1.0.0 Grammar
                                        Variable Name
                                            <name> <<Regex: <_sre.SRE_Match object; span=(57, 58), match='a'>>> ws:None [6, 5 -> 6, 6]
                            Repeat: (Comma and Argument, 0, None)
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(58, 59), match=','>>> ws:None [6, 6 -> 6, 7]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(60, 61), match='b'>>> ws:(59, 60) [6, 8 -> 6, 9]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(61, 62), match=','>>> ws:None [6, 9 -> 6, 10]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(63, 64), match='c'>>> ws:(62, 63) [6, 11 -> 6, 12]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(64, 65), match=','>>> ws:None [6, 12 -> 6, 13]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        Keyword
                                            <name> <<Regex: <_sre.SRE_Match object; span=(70, 71), match='d'>>> ws:None [7, 5 -> 7, 6]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(71, 72), match='='>>> ws:None [7, 6 -> 7, 7]
                                            DynamicStatements.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(72, 75), match='one'>>> ws:None [7, 7 -> 7, 10]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(75, 76), match=','>>> ws:None [7, 10 -> 7, 11]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        Keyword
                                            <name> <<Regex: <_sre.SRE_Match object; span=(81, 82), match='e'>>> ws:None [8, 5 -> 8, 6]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(82, 83), match='='>>> ws:None [8, 6 -> 8, 7]
                                            DynamicStatements.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(83, 86), match='two'>>> ws:None [8, 7 -> 8, 10]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(86, 87), match=','>>> ws:None [8, 10 -> 8, 11]
                    ')' <<Regex: <_sre.SRE_Match object; span=(88, 89), match=')'>>> ws:None [9, 1 -> 9, 2]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(91, 96), match='Func4'>>> ws:None [11, 1 -> 11, 6]
                    '(' <<Regex: <_sre.SRE_Match object; span=(96, 97), match='('>>> ws:None [11, 6 -> 11, 7]
                    Repeat: (Arguments, 0, 1)
                        Arguments
                            Or: [Keyword, DynamicStatements.Expressions]
                                DynamicStatements.Expressions
                                    1.0.0 Grammar
                                        Variable Name
                                            <name> <<Regex: <_sre.SRE_Match object; span=(102, 103), match='a'>>> ws:None [12, 5 -> 12, 6]
                            Repeat: (Comma and Argument, 0, None)
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(103, 104), match=','>>> ws:None [12, 6 -> 12, 7]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(109, 110), match='b'>>> ws:None [13, 5 -> 13, 6]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(110, 111), match=','>>> ws:None [13, 6 -> 13, 7]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(116, 117), match='c'>>> ws:None [14, 5 -> 14, 6]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(117, 118), match=','>>> ws:None [14, 6 -> 14, 7]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        Keyword
                                            <name> <<Regex: <_sre.SRE_Match object; span=(123, 124), match='d'>>> ws:None [15, 5 -> 15, 6]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(124, 125), match='='>>> ws:None [15, 6 -> 15, 7]
                                            DynamicStatements.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(125, 128), match='one'>>> ws:None [15, 7 -> 15, 10]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(128, 129), match=','>>> ws:None [15, 10 -> 15, 11]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        Keyword
                                            <name> <<Regex: <_sre.SRE_Match object; span=(134, 135), match='e'>>> ws:None [16, 5 -> 16, 6]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(135, 136), match='='>>> ws:None [16, 6 -> 16, 7]
                                            DynamicStatements.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(136, 139), match='two'>>> ws:None [16, 7 -> 16, 10]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(139, 140), match=','>>> ws:None [16, 10 -> 16, 11]
                    ')' <<Regex: <_sre.SRE_Match object; span=(141, 142), match=')'>>> ws:None [17, 1 -> 17, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_MethodName():
    assert Execute(
        textwrap.dedent(
            """\
            one.two.three(one, two, three)
            instance.method()
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 13), match='one.two.three'>>> ws:None [1, 1 -> 1, 14]
                    '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [1, 14 -> 1, 15]
                    Repeat: (Arguments, 0, 1)
                        Arguments
                            Or: [Keyword, DynamicStatements.Expressions]
                                DynamicStatements.Expressions
                                    1.0.0 Grammar
                                        Variable Name
                                            <name> <<Regex: <_sre.SRE_Match object; span=(14, 17), match='one'>>> ws:None [1, 15 -> 1, 18]
                            Repeat: (Comma and Argument, 0, None)
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(17, 18), match=','>>> ws:None [1, 18 -> 1, 19]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(19, 22), match='two'>>> ws:(18, 19) [1, 20 -> 1, 23]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(22, 23), match=','>>> ws:None [1, 23 -> 1, 24]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(24, 29), match='three'>>> ws:(23, 24) [1, 25 -> 1, 30]
                    ')' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=')'>>> ws:None [1, 30 -> 1, 31]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(31, 46), match='instance.method'>>> ws:None [2, 1 -> 2, 16]
                    '(' <<Regex: <_sre.SRE_Match object; span=(46, 47), match='('>>> ws:None [2, 16 -> 2, 17]
                    ')' <<Regex: <_sre.SRE_Match object; span=(47, 48), match=')'>>> ws:None [2, 17 -> 2, 18]
        """,
    )

# ----------------------------------------------------------------------
def test_FuncsAsArgs():
    assert Execute(
        textwrap.dedent(
            """\
            Func(
                Func1(),
                Func2(),
                Func3(one, Func4(two, three=value), four),
            )
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='Func'>>> ws:None [1, 1 -> 1, 5]
                    '(' <<Regex: <_sre.SRE_Match object; span=(4, 5), match='('>>> ws:None [1, 5 -> 1, 6]
                    Repeat: (Arguments, 0, 1)
                        Arguments
                            Or: [Keyword, DynamicStatements.Expressions]
                                DynamicStatements.Expressions
                                    1.0.0 Grammar
                                        Function Invocation
                                            <name> <<Regex: <_sre.SRE_Match object; span=(10, 15), match='Func1'>>> ws:None [2, 5 -> 2, 10]
                                            '(' <<Regex: <_sre.SRE_Match object; span=(15, 16), match='('>>> ws:None [2, 10 -> 2, 11]
                                            ')' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=')'>>> ws:None [2, 11 -> 2, 12]
                            Repeat: (Comma and Argument, 0, None)
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(17, 18), match=','>>> ws:None [2, 12 -> 2, 13]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Function Invocation
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(23, 28), match='Func2'>>> ws:None [3, 5 -> 3, 10]
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(28, 29), match='('>>> ws:None [3, 10 -> 3, 11]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=')'>>> ws:None [3, 11 -> 3, 12]
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(30, 31), match=','>>> ws:None [3, 12 -> 3, 13]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Function Invocation
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(36, 41), match='Func3'>>> ws:None [4, 5 -> 4, 10]
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(41, 42), match='('>>> ws:None [4, 10 -> 4, 11]
                                                    Repeat: (Arguments, 0, 1)
                                                        Arguments
                                                            Or: [Keyword, DynamicStatements.Expressions]
                                                                DynamicStatements.Expressions
                                                                    1.0.0 Grammar
                                                                        Variable Name
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(42, 45), match='one'>>> ws:None [4, 11 -> 4, 14]
                                                            Repeat: (Comma and Argument, 0, None)
                                                                Comma and Argument
                                                                    ',' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=','>>> ws:None [4, 14 -> 4, 15]
                                                                    Or: [Keyword, DynamicStatements.Expressions]
                                                                        DynamicStatements.Expressions
                                                                            1.0.0 Grammar
                                                                                Function Invocation
                                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(47, 52), match='Func4'>>> ws:(46, 47) [4, 16 -> 4, 21]
                                                                                    '(' <<Regex: <_sre.SRE_Match object; span=(52, 53), match='('>>> ws:None [4, 21 -> 4, 22]
                                                                                    Repeat: (Arguments, 0, 1)
                                                                                        Arguments
                                                                                            Or: [Keyword, DynamicStatements.Expressions]
                                                                                                DynamicStatements.Expressions
                                                                                                    1.0.0 Grammar
                                                                                                        Variable Name
                                                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(53, 56), match='two'>>> ws:None [4, 22 -> 4, 25]
                                                                                            Repeat: (Comma and Argument, 0, None)
                                                                                                Comma and Argument
                                                                                                    ',' <<Regex: <_sre.SRE_Match object; span=(56, 57), match=','>>> ws:None [4, 25 -> 4, 26]
                                                                                                    Or: [Keyword, DynamicStatements.Expressions]
                                                                                                        Keyword
                                                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(58, 63), match='three'>>> ws:(57, 58) [4, 27 -> 4, 32]
                                                                                                            '=' <<Regex: <_sre.SRE_Match object; span=(63, 64), match='='>>> ws:None [4, 32 -> 4, 33]
                                                                                                            DynamicStatements.Expressions
                                                                                                                1.0.0 Grammar
                                                                                                                    Variable Name
                                                                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(64, 69), match='value'>>> ws:None [4, 33 -> 4, 38]
                                                                                    ')' <<Regex: <_sre.SRE_Match object; span=(69, 70), match=')'>>> ws:None [4, 38 -> 4, 39]
                                                                Comma and Argument
                                                                    ',' <<Regex: <_sre.SRE_Match object; span=(70, 71), match=','>>> ws:None [4, 39 -> 4, 40]
                                                                    Or: [Keyword, DynamicStatements.Expressions]
                                                                        DynamicStatements.Expressions
                                                                            1.0.0 Grammar
                                                                                Variable Name
                                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(72, 76), match='four'>>> ws:(71, 72) [4, 41 -> 4, 45]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(76, 77), match=')'>>> ws:None [4, 45 -> 4, 46]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(77, 78), match=','>>> ws:None [4, 46 -> 4, 47]
                    ')' <<Regex: <_sre.SRE_Match object; span=(79, 80), match=')'>>> ws:None [5, 1 -> 5, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_PositionalAfterKeywordError():
    with pytest.raises(PositionalArgumentAfterKeywordArgumentError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Func(a, b=value, cool, d)
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Positional arguments may not appear after keyword arguments"
    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 18
    assert ex.ColumnEnd == 22
