# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatements_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-17 13:44:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for FuncInvocationStatements.py"""

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
    from . import ExecuteEx
    from ..FuncInvocationStatements import *


# ----------------------------------------------------------------------
def test_NoArgs():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            Func1()

            Func2(
            )
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='Func1'>>> ws:None [1, 1 -> 1, 6]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='('>>> ws:None [1, 6 -> 1, 7]
                            ')' <<Regex: <_sre.SRE_Match object; span=(6, 7), match=')'>>> ws:None [1, 7 -> 1, 8]
                        Newline+ <<7, 9>> ws:None [1, 8 -> 3, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(9, 14), match='Func2'>>> ws:None [3, 1 -> 3, 6]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(14, 15), match='('>>> ws:None [3, 6 -> 3, 7]
                            ')' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=')'>>> ws:None [4, 1 -> 4, 2]
                        Newline+ <<17, 18>> ws:None [4, 2 -> 5, 1]
        """,
    )

    assert len(node.Children) == 2

    assert node.Children[0].Children[0].Children[0].func_name == "Func1"
    assert node.Children[0].Children[0].Children[0].arguments == []

    assert node.Children[1].Children[0].Children[0].func_name == "Func2"
    assert node.Children[1].Children[0].Children[0].arguments == []

# ----------------------------------------------------------------------
def test_SingleArg():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            Func1(a)

            Func2(
                a
            )

            Func3(a=value)
            Func4(
                a=
                    value,
            )
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='Func1'>>> ws:None [1, 1 -> 1, 6]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='('>>> ws:None [1, 6 -> 1, 7]
                            Repeat: (Optional Arguments, 0, 1)
                                Optional Arguments
                                    Or: {Keyword, DynamicStatements.Expressions}
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(6, 7), match='a'>>> ws:None [1, 7 -> 1, 8]
                            ')' <<Regex: <_sre.SRE_Match object; span=(7, 8), match=')'>>> ws:None [1, 8 -> 1, 9]
                        Newline+ <<8, 10>> ws:None [1, 9 -> 3, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(10, 15), match='Func2'>>> ws:None [3, 1 -> 3, 6]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(15, 16), match='('>>> ws:None [3, 6 -> 3, 7]
                            Repeat: (Optional Arguments, 0, 1)
                                Optional Arguments
                                    Or: {Keyword, DynamicStatements.Expressions}
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(21, 22), match='a'>>> ws:None [4, 5 -> 4, 6]
                            ')' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=')'>>> ws:None [5, 1 -> 5, 2]
                        Newline+ <<24, 26>> ws:None [5, 2 -> 7, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(26, 31), match='Func3'>>> ws:None [7, 1 -> 7, 6]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(31, 32), match='('>>> ws:None [7, 6 -> 7, 7]
                            Repeat: (Optional Arguments, 0, 1)
                                Optional Arguments
                                    Or: {Keyword, DynamicStatements.Expressions}
                                        Keyword
                                            <name> <<Regex: <_sre.SRE_Match object; span=(32, 33), match='a'>>> ws:None [7, 7 -> 7, 8]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(33, 34), match='='>>> ws:None [7, 8 -> 7, 9]
                                            DynamicStatements.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(34, 39), match='value'>>> ws:None [7, 9 -> 7, 14]
                            ')' <<Regex: <_sre.SRE_Match object; span=(39, 40), match=')'>>> ws:None [7, 14 -> 7, 15]
                        Newline+ <<40, 41>> ws:None [7, 15 -> 8, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(41, 46), match='Func4'>>> ws:None [8, 1 -> 8, 6]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(46, 47), match='('>>> ws:None [8, 6 -> 8, 7]
                            Repeat: (Optional Arguments, 0, 1)
                                Optional Arguments
                                    Or: {Keyword, DynamicStatements.Expressions}
                                        Keyword
                                            <name> <<Regex: <_sre.SRE_Match object; span=(52, 53), match='a'>>> ws:None [9, 5 -> 9, 6]
                                            '=' <<Regex: <_sre.SRE_Match object; span=(53, 54), match='='>>> ws:None [9, 6 -> 9, 7]
                                            DynamicStatements.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(63, 68), match='value'>>> ws:None [10, 9 -> 10, 14]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(68, 69), match=','>>> ws:None [10, 14 -> 10, 15]
                            ')' <<Regex: <_sre.SRE_Match object; span=(70, 71), match=')'>>> ws:None [11, 1 -> 11, 2]
                        Newline+ <<71, 72>> ws:None [11, 2 -> 12, 1]
        """,
    )

    assert len(node.Children) == 4

    assert node.Children[0].Children[0].Children[0].func_name == "Func1"
    assert "".join([arg.ToString() for arg in node.Children[0].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(6, 7), match='a'>>> ws:None [1, 7 -> 1, 8]
        """,
    )

    assert node.Children[1].Children[0].Children[0].func_name == "Func2"
    assert "".join([arg.ToString() for arg in node.Children[1].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(21, 22), match='a'>>> ws:None [4, 5 -> 4, 6]
        """,
    )

    assert node.Children[2].Children[0].Children[0].func_name == "Func3"
    assert "".join([arg.ToString() for arg in node.Children[2].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        Keyword
            <name> <<Regex: <_sre.SRE_Match object; span=(32, 33), match='a'>>> ws:None [7, 7 -> 7, 8]
            '=' <<Regex: <_sre.SRE_Match object; span=(33, 34), match='='>>> ws:None [7, 8 -> 7, 9]
            DynamicStatements.Expressions
                1.0.0 Grammar
                    Variable Name
                        <name> <<Regex: <_sre.SRE_Match object; span=(34, 39), match='value'>>> ws:None [7, 9 -> 7, 14]
        """,
    )

    assert node.Children[3].Children[0].Children[0].func_name == "Func4"
    assert "".join([arg.ToString() for arg in node.Children[3].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        Keyword
            <name> <<Regex: <_sre.SRE_Match object; span=(52, 53), match='a'>>> ws:None [9, 5 -> 9, 6]
            '=' <<Regex: <_sre.SRE_Match object; span=(53, 54), match='='>>> ws:None [9, 6 -> 9, 7]
            DynamicStatements.Expressions
                1.0.0 Grammar
                    Variable Name
                        <name> <<Regex: <_sre.SRE_Match object; span=(63, 68), match='value'>>> ws:None [10, 9 -> 10, 14]
        """,
    )

# ----------------------------------------------------------------------
def test_MultipleArgs():
    result, node = ExecuteEx(
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
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='Func1'>>> ws:None [1, 1 -> 1, 6]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='('>>> ws:None [1, 6 -> 1, 7]
                            Repeat: (Optional Arguments, 0, 1)
                                Optional Arguments
                                    Or: {Keyword, DynamicStatements.Expressions}
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(6, 7), match='a'>>> ws:None [1, 7 -> 1, 8]
                                    Repeat: (Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}], 0, None)
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(7, 8), match=','>>> ws:None [1, 8 -> 1, 9]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(9, 10), match='b'>>> ws:(8, 9) [1, 10 -> 1, 11]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(10, 11), match=','>>> ws:None [1, 11 -> 1, 12]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(12, 13), match='c'>>> ws:(11, 12) [1, 13 -> 1, 14]
                            ')' <<Regex: <_sre.SRE_Match object; span=(13, 14), match=')'>>> ws:None [1, 14 -> 1, 15]
                        Newline+ <<14, 16>> ws:None [1, 15 -> 3, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(16, 21), match='Func2'>>> ws:None [3, 1 -> 3, 6]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(21, 22), match='('>>> ws:None [3, 6 -> 3, 7]
                            Repeat: (Optional Arguments, 0, 1)
                                Optional Arguments
                                    Or: {Keyword, DynamicStatements.Expressions}
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='a'>>> ws:None [3, 7 -> 3, 8]
                                    Repeat: (Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}], 0, None)
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [3, 8 -> 3, 9]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='b'>>> ws:(24, 25) [3, 10 -> 3, 11]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(26, 27), match=','>>> ws:None [3, 11 -> 3, 12]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(28, 29), match='c'>>> ws:(27, 28) [3, 13 -> 3, 14]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=','>>> ws:None [3, 14 -> 3, 15]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                Keyword
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='d'>>> ws:(30, 31) [3, 16 -> 3, 17]
                                                    '=' <<Regex: <_sre.SRE_Match object; span=(32, 33), match='='>>> ws:None [3, 17 -> 3, 18]
                                                    DynamicStatements.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(33, 36), match='one'>>> ws:None [3, 18 -> 3, 21]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(36, 37), match=','>>> ws:None [3, 21 -> 3, 22]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                Keyword
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(38, 39), match='e'>>> ws:(37, 38) [3, 23 -> 3, 24]
                                                    '=' <<Regex: <_sre.SRE_Match object; span=(39, 40), match='='>>> ws:None [3, 24 -> 3, 25]
                                                    DynamicStatements.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(40, 43), match='two'>>> ws:None [3, 25 -> 3, 28]
                            ')' <<Regex: <_sre.SRE_Match object; span=(43, 44), match=')'>>> ws:None [3, 28 -> 3, 29]
                        Newline+ <<44, 46>> ws:None [3, 29 -> 5, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(46, 51), match='Func3'>>> ws:None [5, 1 -> 5, 6]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(51, 52), match='('>>> ws:None [5, 6 -> 5, 7]
                            Repeat: (Optional Arguments, 0, 1)
                                Optional Arguments
                                    Or: {Keyword, DynamicStatements.Expressions}
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(57, 58), match='a'>>> ws:None [6, 5 -> 6, 6]
                                    Repeat: (Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}], 0, None)
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(58, 59), match=','>>> ws:None [6, 6 -> 6, 7]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(60, 61), match='b'>>> ws:(59, 60) [6, 8 -> 6, 9]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(61, 62), match=','>>> ws:None [6, 9 -> 6, 10]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(63, 64), match='c'>>> ws:(62, 63) [6, 11 -> 6, 12]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(64, 65), match=','>>> ws:None [6, 12 -> 6, 13]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                Keyword
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(70, 71), match='d'>>> ws:None [7, 5 -> 7, 6]
                                                    '=' <<Regex: <_sre.SRE_Match object; span=(71, 72), match='='>>> ws:None [7, 6 -> 7, 7]
                                                    DynamicStatements.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(72, 75), match='one'>>> ws:None [7, 7 -> 7, 10]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(75, 76), match=','>>> ws:None [7, 10 -> 7, 11]
                                            Or: {Keyword, DynamicStatements.Expressions}
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
                        Newline+ <<89, 91>> ws:None [9, 2 -> 11, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(91, 96), match='Func4'>>> ws:None [11, 1 -> 11, 6]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(96, 97), match='('>>> ws:None [11, 6 -> 11, 7]
                            Repeat: (Optional Arguments, 0, 1)
                                Optional Arguments
                                    Or: {Keyword, DynamicStatements.Expressions}
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(102, 103), match='a'>>> ws:None [12, 5 -> 12, 6]
                                    Repeat: (Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}], 0, None)
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(103, 104), match=','>>> ws:None [12, 6 -> 12, 7]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(109, 110), match='b'>>> ws:None [13, 5 -> 13, 6]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(110, 111), match=','>>> ws:None [13, 6 -> 13, 7]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(116, 117), match='c'>>> ws:None [14, 5 -> 14, 6]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(117, 118), match=','>>> ws:None [14, 6 -> 14, 7]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                Keyword
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(123, 124), match='d'>>> ws:None [15, 5 -> 15, 6]
                                                    '=' <<Regex: <_sre.SRE_Match object; span=(124, 125), match='='>>> ws:None [15, 6 -> 15, 7]
                                                    DynamicStatements.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(125, 128), match='one'>>> ws:None [15, 7 -> 15, 10]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(128, 129), match=','>>> ws:None [15, 10 -> 15, 11]
                                            Or: {Keyword, DynamicStatements.Expressions}
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
                        Newline+ <<142, 143>> ws:None [17, 2 -> 18, 1]
        """,
    )

    assert len(node.Children) == 4

    assert node.Children[0].Children[0].Children[0].func_name == "Func1"
    assert "".join([arg.ToString() for arg in node.Children[0].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(6, 7), match='a'>>> ws:None [1, 7 -> 1, 8]
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(9, 10), match='b'>>> ws:(8, 9) [1, 10 -> 1, 11]
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(12, 13), match='c'>>> ws:(11, 12) [1, 13 -> 1, 14]
        """,
    )

    assert node.Children[1].Children[0].Children[0].func_name == "Func2"
    assert "".join([arg.ToString() for arg in node.Children[1].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='a'>>> ws:None [3, 7 -> 3, 8]
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='b'>>> ws:(24, 25) [3, 10 -> 3, 11]
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(28, 29), match='c'>>> ws:(27, 28) [3, 13 -> 3, 14]
        Keyword
            <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='d'>>> ws:(30, 31) [3, 16 -> 3, 17]
            '=' <<Regex: <_sre.SRE_Match object; span=(32, 33), match='='>>> ws:None [3, 17 -> 3, 18]
            DynamicStatements.Expressions
                1.0.0 Grammar
                    Variable Name
                        <name> <<Regex: <_sre.SRE_Match object; span=(33, 36), match='one'>>> ws:None [3, 18 -> 3, 21]
        Keyword
            <name> <<Regex: <_sre.SRE_Match object; span=(38, 39), match='e'>>> ws:(37, 38) [3, 23 -> 3, 24]
            '=' <<Regex: <_sre.SRE_Match object; span=(39, 40), match='='>>> ws:None [3, 24 -> 3, 25]
            DynamicStatements.Expressions
                1.0.0 Grammar
                    Variable Name
                        <name> <<Regex: <_sre.SRE_Match object; span=(40, 43), match='two'>>> ws:None [3, 25 -> 3, 28]
        """,
    )

    assert node.Children[2].Children[0].Children[0].func_name == "Func3"
    assert "".join([arg.ToString() for arg in node.Children[2].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(57, 58), match='a'>>> ws:None [6, 5 -> 6, 6]
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(60, 61), match='b'>>> ws:(59, 60) [6, 8 -> 6, 9]
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(63, 64), match='c'>>> ws:(62, 63) [6, 11 -> 6, 12]
        Keyword
            <name> <<Regex: <_sre.SRE_Match object; span=(70, 71), match='d'>>> ws:None [7, 5 -> 7, 6]
            '=' <<Regex: <_sre.SRE_Match object; span=(71, 72), match='='>>> ws:None [7, 6 -> 7, 7]
            DynamicStatements.Expressions
                1.0.0 Grammar
                    Variable Name
                        <name> <<Regex: <_sre.SRE_Match object; span=(72, 75), match='one'>>> ws:None [7, 7 -> 7, 10]
        Keyword
            <name> <<Regex: <_sre.SRE_Match object; span=(81, 82), match='e'>>> ws:None [8, 5 -> 8, 6]
            '=' <<Regex: <_sre.SRE_Match object; span=(82, 83), match='='>>> ws:None [8, 6 -> 8, 7]
            DynamicStatements.Expressions
                1.0.0 Grammar
                    Variable Name
                        <name> <<Regex: <_sre.SRE_Match object; span=(83, 86), match='two'>>> ws:None [8, 7 -> 8, 10]
        """,
    )

    assert node.Children[3].Children[0].Children[0].func_name == "Func4"
    assert "".join([arg.ToString() for arg in node.Children[3].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(102, 103), match='a'>>> ws:None [12, 5 -> 12, 6]
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(109, 110), match='b'>>> ws:None [13, 5 -> 13, 6]
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(116, 117), match='c'>>> ws:None [14, 5 -> 14, 6]
        Keyword
            <name> <<Regex: <_sre.SRE_Match object; span=(123, 124), match='d'>>> ws:None [15, 5 -> 15, 6]
            '=' <<Regex: <_sre.SRE_Match object; span=(124, 125), match='='>>> ws:None [15, 6 -> 15, 7]
            DynamicStatements.Expressions
                1.0.0 Grammar
                    Variable Name
                        <name> <<Regex: <_sre.SRE_Match object; span=(125, 128), match='one'>>> ws:None [15, 7 -> 15, 10]
        Keyword
            <name> <<Regex: <_sre.SRE_Match object; span=(134, 135), match='e'>>> ws:None [16, 5 -> 16, 6]
            '=' <<Regex: <_sre.SRE_Match object; span=(135, 136), match='='>>> ws:None [16, 6 -> 16, 7]
            DynamicStatements.Expressions
                1.0.0 Grammar
                    Variable Name
                        <name> <<Regex: <_sre.SRE_Match object; span=(136, 139), match='two'>>> ws:None [16, 7 -> 16, 10]
        """,
    )

# ----------------------------------------------------------------------
def test_MethodName():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            one.two.three(arg1, arg2, arg3)
            instance.method()
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 13), match='one.two.three'>>> ws:None [1, 1 -> 1, 14]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [1, 14 -> 1, 15]
                            Repeat: (Optional Arguments, 0, 1)
                                Optional Arguments
                                    Or: {Keyword, DynamicStatements.Expressions}
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(14, 18), match='arg1'>>> ws:None [1, 15 -> 1, 19]
                                    Repeat: (Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}], 0, None)
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(18, 19), match=','>>> ws:None [1, 19 -> 1, 20]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(20, 24), match='arg2'>>> ws:(19, 20) [1, 21 -> 1, 25]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(24, 25), match=','>>> ws:None [1, 25 -> 1, 26]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(26, 30), match='arg3'>>> ws:(25, 26) [1, 27 -> 1, 31]
                            ')' <<Regex: <_sre.SRE_Match object; span=(30, 31), match=')'>>> ws:None [1, 31 -> 1, 32]
                        Newline+ <<31, 32>> ws:None [1, 32 -> 2, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(32, 47), match='instance.method'>>> ws:None [2, 1 -> 2, 16]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(47, 48), match='('>>> ws:None [2, 16 -> 2, 17]
                            ')' <<Regex: <_sre.SRE_Match object; span=(48, 49), match=')'>>> ws:None [2, 17 -> 2, 18]
                        Newline+ <<49, 50>> ws:None [2, 18 -> 3, 1]
        """,
    )

    assert len(node.Children) == 2

    assert node.Children[0].Children[0].Children[0].func_name == "one.two.three"
    assert "".join([arg.ToString() for arg in node.Children[0].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(14, 18), match='arg1'>>> ws:None [1, 15 -> 1, 19]
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(20, 24), match='arg2'>>> ws:(19, 20) [1, 21 -> 1, 25]
        Variable Name
            <name> <<Regex: <_sre.SRE_Match object; span=(26, 30), match='arg3'>>> ws:(25, 26) [1, 27 -> 1, 31]
        """,
    )

    assert node.Children[1].Children[0].Children[0].func_name == "instance.method"
    assert "".join([arg.ToString() for arg in node.Children[1].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        """,
    )

# ----------------------------------------------------------------------
def test_FuncsAsArgs():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            Func(
                Func1(),
                Func2(),
                Func3(one, Func4(two, three=value), four),
            )
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Invocation
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='Func'>>> ws:None [1, 1 -> 1, 5]
                        Arguments
                            '(' <<Regex: <_sre.SRE_Match object; span=(4, 5), match='('>>> ws:None [1, 5 -> 1, 6]
                            Repeat: (Optional Arguments, 0, 1)
                                Optional Arguments
                                    Or: {Keyword, DynamicStatements.Expressions}
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Function Invocation
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(10, 15), match='Func1'>>> ws:None [2, 5 -> 2, 10]
                                                    Arguments
                                                        '(' <<Regex: <_sre.SRE_Match object; span=(15, 16), match='('>>> ws:None [2, 10 -> 2, 11]
                                                        ')' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=')'>>> ws:None [2, 11 -> 2, 12]
                                    Repeat: (Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}], 0, None)
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(17, 18), match=','>>> ws:None [2, 12 -> 2, 13]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Function Invocation
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(23, 28), match='Func2'>>> ws:None [3, 5 -> 3, 10]
                                                            Arguments
                                                                '(' <<Regex: <_sre.SRE_Match object; span=(28, 29), match='('>>> ws:None [3, 10 -> 3, 11]
                                                                ')' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=')'>>> ws:None [3, 11 -> 3, 12]
                                        Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(30, 31), match=','>>> ws:None [3, 12 -> 3, 13]
                                            Or: {Keyword, DynamicStatements.Expressions}
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Function Invocation
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(36, 41), match='Func3'>>> ws:None [4, 5 -> 4, 10]
                                                            Arguments
                                                                '(' <<Regex: <_sre.SRE_Match object; span=(41, 42), match='('>>> ws:None [4, 10 -> 4, 11]
                                                                Repeat: (Optional Arguments, 0, 1)
                                                                    Optional Arguments
                                                                        Or: {Keyword, DynamicStatements.Expressions}
                                                                            DynamicStatements.Expressions
                                                                                1.0.0 Grammar
                                                                                    Variable Name
                                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(42, 45), match='one'>>> ws:None [4, 11 -> 4, 14]
                                                                        Repeat: (Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}], 0, None)
                                                                            Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                                                                ',' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=','>>> ws:None [4, 14 -> 4, 15]
                                                                                Or: {Keyword, DynamicStatements.Expressions}
                                                                                    DynamicStatements.Expressions
                                                                                        1.0.0 Grammar
                                                                                            Function Invocation
                                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(47, 52), match='Func4'>>> ws:(46, 47) [4, 16 -> 4, 21]
                                                                                                Arguments
                                                                                                    '(' <<Regex: <_sre.SRE_Match object; span=(52, 53), match='('>>> ws:None [4, 21 -> 4, 22]
                                                                                                    Repeat: (Optional Arguments, 0, 1)
                                                                                                        Optional Arguments
                                                                                                            Or: {Keyword, DynamicStatements.Expressions}
                                                                                                                DynamicStatements.Expressions
                                                                                                                    1.0.0 Grammar
                                                                                                                        Variable Name
                                                                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(53, 56), match='two'>>> ws:None [4, 22 -> 4, 25]
                                                                                                            Repeat: (Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}], 0, None)
                                                                                                                Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                                                                                                    ',' <<Regex: <_sre.SRE_Match object; span=(56, 57), match=','>>> ws:None [4, 25 -> 4, 26]
                                                                                                                    Or: {Keyword, DynamicStatements.Expressions}
                                                                                                                        Keyword
                                                                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(58, 63), match='three'>>> ws:(57, 58) [4, 27 -> 4, 32]
                                                                                                                            '=' <<Regex: <_sre.SRE_Match object; span=(63, 64), match='='>>> ws:None [4, 32 -> 4, 33]
                                                                                                                            DynamicStatements.Expressions
                                                                                                                                1.0.0 Grammar
                                                                                                                                    Variable Name
                                                                                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(64, 69), match='value'>>> ws:None [4, 33 -> 4, 38]
                                                                                                    ')' <<Regex: <_sre.SRE_Match object; span=(69, 70), match=')'>>> ws:None [4, 38 -> 4, 39]
                                                                            Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                                                                ',' <<Regex: <_sre.SRE_Match object; span=(70, 71), match=','>>> ws:None [4, 39 -> 4, 40]
                                                                                Or: {Keyword, DynamicStatements.Expressions}
                                                                                    DynamicStatements.Expressions
                                                                                        1.0.0 Grammar
                                                                                            Variable Name
                                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(72, 76), match='four'>>> ws:(71, 72) [4, 41 -> 4, 45]
                                                                ')' <<Regex: <_sre.SRE_Match object; span=(76, 77), match=')'>>> ws:None [4, 45 -> 4, 46]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(77, 78), match=','>>> ws:None [4, 46 -> 4, 47]
                            ')' <<Regex: <_sre.SRE_Match object; span=(79, 80), match=')'>>> ws:None [5, 1 -> 5, 2]
                        Newline+ <<80, 81>> ws:None [5, 2 -> 6, 1]
        """,
    )

    assert len(node.Children) == 1

    assert node.Children[0].Children[0].Children[0].func_name == "Func"
    assert "".join([arg.ToString() for arg in node.Children[0].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        Function Invocation
            <name> <<Regex: <_sre.SRE_Match object; span=(10, 15), match='Func1'>>> ws:None [2, 5 -> 2, 10]
            Arguments
                '(' <<Regex: <_sre.SRE_Match object; span=(15, 16), match='('>>> ws:None [2, 10 -> 2, 11]
                ')' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=')'>>> ws:None [2, 11 -> 2, 12]
        Function Invocation
            <name> <<Regex: <_sre.SRE_Match object; span=(23, 28), match='Func2'>>> ws:None [3, 5 -> 3, 10]
            Arguments
                '(' <<Regex: <_sre.SRE_Match object; span=(28, 29), match='('>>> ws:None [3, 10 -> 3, 11]
                ')' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=')'>>> ws:None [3, 11 -> 3, 12]
        Function Invocation
            <name> <<Regex: <_sre.SRE_Match object; span=(36, 41), match='Func3'>>> ws:None [4, 5 -> 4, 10]
            Arguments
                '(' <<Regex: <_sre.SRE_Match object; span=(41, 42), match='('>>> ws:None [4, 10 -> 4, 11]
                Repeat: (Optional Arguments, 0, 1)
                    Optional Arguments
                        Or: {Keyword, DynamicStatements.Expressions}
                            DynamicStatements.Expressions
                                1.0.0 Grammar
                                    Variable Name
                                        <name> <<Regex: <_sre.SRE_Match object; span=(42, 45), match='one'>>> ws:None [4, 11 -> 4, 14]
                        Repeat: (Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}], 0, None)
                            Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                ',' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=','>>> ws:None [4, 14 -> 4, 15]
                                Or: {Keyword, DynamicStatements.Expressions}
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Function Invocation
                                                <name> <<Regex: <_sre.SRE_Match object; span=(47, 52), match='Func4'>>> ws:(46, 47) [4, 16 -> 4, 21]
                                                Arguments
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(52, 53), match='('>>> ws:None [4, 21 -> 4, 22]
                                                    Repeat: (Optional Arguments, 0, 1)
                                                        Optional Arguments
                                                            Or: {Keyword, DynamicStatements.Expressions}
                                                                DynamicStatements.Expressions
                                                                    1.0.0 Grammar
                                                                        Variable Name
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(53, 56), match='two'>>> ws:None [4, 22 -> 4, 25]
                                                            Repeat: (Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}], 0, None)
                                                                Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                                                    ',' <<Regex: <_sre.SRE_Match object; span=(56, 57), match=','>>> ws:None [4, 25 -> 4, 26]
                                                                    Or: {Keyword, DynamicStatements.Expressions}
                                                                        Keyword
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(58, 63), match='three'>>> ws:(57, 58) [4, 27 -> 4, 32]
                                                                            '=' <<Regex: <_sre.SRE_Match object; span=(63, 64), match='='>>> ws:None [4, 32 -> 4, 33]
                                                                            DynamicStatements.Expressions
                                                                                1.0.0 Grammar
                                                                                    Variable Name
                                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(64, 69), match='value'>>> ws:None [4, 33 -> 4, 38]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(69, 70), match=')'>>> ws:None [4, 38 -> 4, 39]
                            Sequence: [',', Or: {Keyword, DynamicStatements.Expressions}]
                                ',' <<Regex: <_sre.SRE_Match object; span=(70, 71), match=','>>> ws:None [4, 39 -> 4, 40]
                                Or: {Keyword, DynamicStatements.Expressions}
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(72, 76), match='four'>>> ws:(71, 72) [4, 41 -> 4, 45]
                ')' <<Regex: <_sre.SRE_Match object; span=(76, 77), match=')'>>> ws:None [4, 45 -> 4, 46]
        """,
    )

# ----------------------------------------------------------------------
def test_PositionalAfterKeywordError():
    with pytest.raises(PositionalArgumentAfterKeywordArgumentError) as ex:
        ExecuteEx(
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

# ----------------------------------------------------------------------

def TODO_test_SuffixCalls():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            Func1().Func2()

            Func3()
                .Func4()
                .Func5()
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        """,
    )

    assert len(node.Children) == 1

    assert node.Children[0].Children[0].Children[0].func_name == "Func"
    assert "".join([arg.ToString() for arg in node.Children[0].Children[0].Children[0].arguments]) == textwrap.dedent(
        """\
        """,
    )
