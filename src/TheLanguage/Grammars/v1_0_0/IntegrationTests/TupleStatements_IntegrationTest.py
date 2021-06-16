# ----------------------------------------------------------------------
# |
# |  TupleStatements_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 14:52:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for TupleStatements.py"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Execute
    from ..TupleStatements import *


# ----------------------------------------------------------------------
def test_SingleExpression():
    assert Execute(
        textwrap.dedent(
            """\
            assignment1 = (a,)
            assignment2 = (Func(),)
            assignment3 = (
                (value,),
            )
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Variable Declaration
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 11), match='assignment1'>>> ws:None [1, 1 -> 1, 12]
                    '=' <<Regex: <_sre.SRE_Match object; span=(12, 13), match='='>>> ws:(11, 12) [1, 13 -> 1, 14]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Tuple Expression
                                Or: [Multiple, Single]
                                    Single
                                        '(' <<Regex: <_sre.SRE_Match object; span=(14, 15), match='('>>> ws:(13, 14) [1, 15 -> 1, 16]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(15, 16), match='a'>>> ws:None [1, 16 -> 1, 17]
                                        ',' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=','>>> ws:None [1, 17 -> 1, 18]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(17, 18), match=')'>>> ws:None [1, 18 -> 1, 19]
            1.0.0 Grammar
                Variable Declaration
                    <name> <<Regex: <_sre.SRE_Match object; span=(19, 30), match='assignment2'>>> ws:None [2, 1 -> 2, 12]
                    '=' <<Regex: <_sre.SRE_Match object; span=(31, 32), match='='>>> ws:(30, 31) [2, 13 -> 2, 14]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Tuple Expression
                                Or: [Multiple, Single]
                                    Single
                                        '(' <<Regex: <_sre.SRE_Match object; span=(33, 34), match='('>>> ws:(32, 33) [2, 15 -> 2, 16]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Function Invocation
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(34, 38), match='Func'>>> ws:None [2, 16 -> 2, 20]
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(38, 39), match='('>>> ws:None [2, 20 -> 2, 21]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(39, 40), match=')'>>> ws:None [2, 21 -> 2, 22]
                                        ',' <<Regex: <_sre.SRE_Match object; span=(40, 41), match=','>>> ws:None [2, 22 -> 2, 23]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(41, 42), match=')'>>> ws:None [2, 23 -> 2, 24]
            1.0.0 Grammar
                Variable Declaration
                    <name> <<Regex: <_sre.SRE_Match object; span=(43, 54), match='assignment3'>>> ws:None [3, 1 -> 3, 12]
                    '=' <<Regex: <_sre.SRE_Match object; span=(55, 56), match='='>>> ws:(54, 55) [3, 13 -> 3, 14]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Tuple Expression
                                Or: [Multiple, Single]
                                    Single
                                        '(' <<Regex: <_sre.SRE_Match object; span=(57, 58), match='('>>> ws:(56, 57) [3, 15 -> 3, 16]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Tuple Expression
                                                    Or: [Multiple, Single]
                                                        Single
                                                            '(' <<Regex: <_sre.SRE_Match object; span=(63, 64), match='('>>> ws:None [4, 5 -> 4, 6]
                                                            DynamicStatements.Expressions
                                                                1.0.0 Grammar
                                                                    Variable Name
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(64, 69), match='value'>>> ws:None [4, 6 -> 4, 11]
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(69, 70), match=','>>> ws:None [4, 11 -> 4, 12]
                                                            ')' <<Regex: <_sre.SRE_Match object; span=(70, 71), match=')'>>> ws:None [4, 12 -> 4, 13]
                                        ',' <<Regex: <_sre.SRE_Match object; span=(71, 72), match=','>>> ws:None [4, 13 -> 4, 14]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(73, 74), match=')'>>> ws:None [5, 1 -> 5, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_MultipleExpression():
    assert Execute(
        textwrap.dedent(
            """\
            assignment1 = (a, b, c)
            assignment2 = (a, b, c, )
            assignment3 = (
                a, b,
                    c,
            )

            assignment4 = (
                Func1(),
                (x, y),
                z,
            )
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Variable Declaration
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 11), match='assignment1'>>> ws:None [1, 1 -> 1, 12]
                    '=' <<Regex: <_sre.SRE_Match object; span=(12, 13), match='='>>> ws:(11, 12) [1, 13 -> 1, 14]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Tuple Expression
                                Or: [Multiple, Single]
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(14, 15), match='('>>> ws:(13, 14) [1, 15 -> 1, 16]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(15, 16), match='a'>>> ws:None [1, 16 -> 1, 17]
                                        Repeat: (Comma and Expression, 1, None)
                                            Comma and Expression
                                                ',' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=','>>> ws:None [1, 17 -> 1, 18]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(18, 19), match='b'>>> ws:(17, 18) [1, 19 -> 1, 20]
                                            Comma and Expression
                                                ',' <<Regex: <_sre.SRE_Match object; span=(19, 20), match=','>>> ws:None [1, 20 -> 1, 21]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(21, 22), match='c'>>> ws:(20, 21) [1, 22 -> 1, 23]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(22, 23), match=')'>>> ws:None [1, 23 -> 1, 24]
            1.0.0 Grammar
                Variable Declaration
                    <name> <<Regex: <_sre.SRE_Match object; span=(24, 35), match='assignment2'>>> ws:None [2, 1 -> 2, 12]
                    '=' <<Regex: <_sre.SRE_Match object; span=(36, 37), match='='>>> ws:(35, 36) [2, 13 -> 2, 14]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Tuple Expression
                                Or: [Multiple, Single]
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(38, 39), match='('>>> ws:(37, 38) [2, 15 -> 2, 16]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(39, 40), match='a'>>> ws:None [2, 16 -> 2, 17]
                                        Repeat: (Comma and Expression, 1, None)
                                            Comma and Expression
                                                ',' <<Regex: <_sre.SRE_Match object; span=(40, 41), match=','>>> ws:None [2, 17 -> 2, 18]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(42, 43), match='b'>>> ws:(41, 42) [2, 19 -> 2, 20]
                                            Comma and Expression
                                                ',' <<Regex: <_sre.SRE_Match object; span=(43, 44), match=','>>> ws:None [2, 20 -> 2, 21]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(45, 46), match='c'>>> ws:(44, 45) [2, 22 -> 2, 23]
                                        Repeat: (',', 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(46, 47), match=','>>> ws:None [2, 23 -> 2, 24]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(48, 49), match=')'>>> ws:(47, 48) [2, 25 -> 2, 26]
            1.0.0 Grammar
                Variable Declaration
                    <name> <<Regex: <_sre.SRE_Match object; span=(50, 61), match='assignment3'>>> ws:None [3, 1 -> 3, 12]
                    '=' <<Regex: <_sre.SRE_Match object; span=(62, 63), match='='>>> ws:(61, 62) [3, 13 -> 3, 14]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Tuple Expression
                                Or: [Multiple, Single]
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(64, 65), match='('>>> ws:(63, 64) [3, 15 -> 3, 16]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(70, 71), match='a'>>> ws:None [4, 5 -> 4, 6]
                                        Repeat: (Comma and Expression, 1, None)
                                            Comma and Expression
                                                ',' <<Regex: <_sre.SRE_Match object; span=(71, 72), match=','>>> ws:None [4, 6 -> 4, 7]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(73, 74), match='b'>>> ws:(72, 73) [4, 8 -> 4, 9]
                                            Comma and Expression
                                                ',' <<Regex: <_sre.SRE_Match object; span=(74, 75), match=','>>> ws:None [4, 9 -> 4, 10]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(84, 85), match='c'>>> ws:None [5, 9 -> 5, 10]
                                        Repeat: (',', 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(85, 86), match=','>>> ws:None [5, 10 -> 5, 11]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(87, 88), match=')'>>> ws:None [6, 1 -> 6, 2]
            1.0.0 Grammar
                Variable Declaration
                    <name> <<Regex: <_sre.SRE_Match object; span=(90, 101), match='assignment4'>>> ws:None [8, 1 -> 8, 12]
                    '=' <<Regex: <_sre.SRE_Match object; span=(102, 103), match='='>>> ws:(101, 102) [8, 13 -> 8, 14]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Tuple Expression
                                Or: [Multiple, Single]
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(104, 105), match='('>>> ws:(103, 104) [8, 15 -> 8, 16]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Function Invocation
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(110, 115), match='Func1'>>> ws:None [9, 5 -> 9, 10]
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(115, 116), match='('>>> ws:None [9, 10 -> 9, 11]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(116, 117), match=')'>>> ws:None [9, 11 -> 9, 12]
                                        Repeat: (Comma and Expression, 1, None)
                                            Comma and Expression
                                                ',' <<Regex: <_sre.SRE_Match object; span=(117, 118), match=','>>> ws:None [9, 12 -> 9, 13]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Tuple Expression
                                                            Or: [Multiple, Single]
                                                                Multiple
                                                                    '(' <<Regex: <_sre.SRE_Match object; span=(123, 124), match='('>>> ws:None [10, 5 -> 10, 6]
                                                                    DynamicStatements.Expressions
                                                                        1.0.0 Grammar
                                                                            Variable Name
                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(124, 125), match='x'>>> ws:None [10, 6 -> 10, 7]
                                                                    Repeat: (Comma and Expression, 1, None)
                                                                        Comma and Expression
                                                                            ',' <<Regex: <_sre.SRE_Match object; span=(125, 126), match=','>>> ws:None [10, 7 -> 10, 8]
                                                                            DynamicStatements.Expressions
                                                                                1.0.0 Grammar
                                                                                    Variable Name
                                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(127, 128), match='y'>>> ws:(126, 127) [10, 9 -> 10, 10]
                                                                    ')' <<Regex: <_sre.SRE_Match object; span=(128, 129), match=')'>>> ws:None [10, 10 -> 10, 11]
                                            Comma and Expression
                                                ',' <<Regex: <_sre.SRE_Match object; span=(129, 130), match=','>>> ws:None [10, 11 -> 10, 12]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(135, 136), match='z'>>> ws:None [11, 5 -> 11, 6]
                                        Repeat: (',', 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(136, 137), match=','>>> ws:None [11, 6 -> 11, 7]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(138, 139), match=')'>>> ws:None [12, 1 -> 12, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_SingleAssignment():
    assert Execute(
        textwrap.dedent(
            """\
            (a,) = line1
            (
                a
                ,
            ) = Func()
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Tuple Variable Declaration
                    Or: [Multiple, Single]
                        Single
                            '(' <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                            <name> <<Regex: <_sre.SRE_Match object; span=(1, 2), match='a'>>> ws:None [1, 2 -> 1, 3]
                            ',' <<Regex: <_sre.SRE_Match object; span=(2, 3), match=','>>> ws:None [1, 3 -> 1, 4]
                            ')' <<Regex: <_sre.SRE_Match object; span=(3, 4), match=')'>>> ws:None [1, 4 -> 1, 5]
                    '=' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='='>>> ws:(4, 5) [1, 6 -> 1, 7]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(7, 12), match='line1'>>> ws:(6, 7) [1, 8 -> 1, 13]
            1.0.0 Grammar
                Tuple Variable Declaration
                    Or: [Multiple, Single]
                        Single
                            '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [2, 1 -> 2, 2]
                            <name> <<Regex: <_sre.SRE_Match object; span=(19, 20), match='a'>>> ws:None [3, 5 -> 3, 6]
                            ',' <<Regex: <_sre.SRE_Match object; span=(25, 26), match=','>>> ws:None [4, 5 -> 4, 6]
                            ')' <<Regex: <_sre.SRE_Match object; span=(27, 28), match=')'>>> ws:None [5, 1 -> 5, 2]
                    '=' <<Regex: <_sre.SRE_Match object; span=(29, 30), match='='>>> ws:(28, 29) [5, 3 -> 5, 4]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Function Invocation
                                <name> <<Regex: <_sre.SRE_Match object; span=(31, 35), match='Func'>>> ws:(30, 31) [5, 5 -> 5, 9]
                                '(' <<Regex: <_sre.SRE_Match object; span=(35, 36), match='('>>> ws:None [5, 9 -> 5, 10]
                                ')' <<Regex: <_sre.SRE_Match object; span=(36, 37), match=')'>>> ws:None [5, 10 -> 5, 11]
        """,
    )

# ----------------------------------------------------------------------
def test_MultipleAssignment():
    assert Execute(
        textwrap.dedent(
            """\
            (a, b) = line1
            (a, b, c, d, ) = Func()

            (a, b,
                c, d,
                    e,
            ) = Another
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Tuple Variable Declaration
                    Or: [Multiple, Single]
                        Multiple
                            '(' <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                            <name> <<Regex: <_sre.SRE_Match object; span=(1, 2), match='a'>>> ws:None [1, 2 -> 1, 3]
                            Repeat: (Comma and Variable Declaration, 1, None)
                                Comma and Variable Declaration
                                    ',' <<Regex: <_sre.SRE_Match object; span=(2, 3), match=','>>> ws:None [1, 3 -> 1, 4]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(4, 5), match='b'>>> ws:(3, 4) [1, 5 -> 1, 6]
                            ')' <<Regex: <_sre.SRE_Match object; span=(5, 6), match=')'>>> ws:None [1, 6 -> 1, 7]
                    '=' <<Regex: <_sre.SRE_Match object; span=(7, 8), match='='>>> ws:(6, 7) [1, 8 -> 1, 9]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(9, 14), match='line1'>>> ws:(8, 9) [1, 10 -> 1, 15]
            1.0.0 Grammar
                Tuple Variable Declaration
                    Or: [Multiple, Single]
                        Multiple
                            '(' <<Regex: <_sre.SRE_Match object; span=(15, 16), match='('>>> ws:None [2, 1 -> 2, 2]
                            <name> <<Regex: <_sre.SRE_Match object; span=(16, 17), match='a'>>> ws:None [2, 2 -> 2, 3]
                            Repeat: (Comma and Variable Declaration, 1, None)
                                Comma and Variable Declaration
                                    ',' <<Regex: <_sre.SRE_Match object; span=(17, 18), match=','>>> ws:None [2, 3 -> 2, 4]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(19, 20), match='b'>>> ws:(18, 19) [2, 5 -> 2, 6]
                                Comma and Variable Declaration
                                    ',' <<Regex: <_sre.SRE_Match object; span=(20, 21), match=','>>> ws:None [2, 6 -> 2, 7]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='c'>>> ws:(21, 22) [2, 8 -> 2, 9]
                                Comma and Variable Declaration
                                    ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [2, 9 -> 2, 10]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='d'>>> ws:(24, 25) [2, 11 -> 2, 12]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(26, 27), match=','>>> ws:None [2, 12 -> 2, 13]
                            ')' <<Regex: <_sre.SRE_Match object; span=(28, 29), match=')'>>> ws:(27, 28) [2, 14 -> 2, 15]
                    '=' <<Regex: <_sre.SRE_Match object; span=(30, 31), match='='>>> ws:(29, 30) [2, 16 -> 2, 17]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Function Invocation
                                <name> <<Regex: <_sre.SRE_Match object; span=(32, 36), match='Func'>>> ws:(31, 32) [2, 18 -> 2, 22]
                                '(' <<Regex: <_sre.SRE_Match object; span=(36, 37), match='('>>> ws:None [2, 22 -> 2, 23]
                                ')' <<Regex: <_sre.SRE_Match object; span=(37, 38), match=')'>>> ws:None [2, 23 -> 2, 24]
            1.0.0 Grammar
                Tuple Variable Declaration
                    Or: [Multiple, Single]
                        Multiple
                            '(' <<Regex: <_sre.SRE_Match object; span=(40, 41), match='('>>> ws:None [4, 1 -> 4, 2]
                            <name> <<Regex: <_sre.SRE_Match object; span=(41, 42), match='a'>>> ws:None [4, 2 -> 4, 3]
                            Repeat: (Comma and Variable Declaration, 1, None)
                                Comma and Variable Declaration
                                    ',' <<Regex: <_sre.SRE_Match object; span=(42, 43), match=','>>> ws:None [4, 3 -> 4, 4]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(44, 45), match='b'>>> ws:(43, 44) [4, 5 -> 4, 6]
                                Comma and Variable Declaration
                                    ',' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=','>>> ws:None [4, 6 -> 4, 7]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(51, 52), match='c'>>> ws:None [5, 5 -> 5, 6]
                                Comma and Variable Declaration
                                    ',' <<Regex: <_sre.SRE_Match object; span=(52, 53), match=','>>> ws:None [5, 6 -> 5, 7]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(54, 55), match='d'>>> ws:(53, 54) [5, 8 -> 5, 9]
                                Comma and Variable Declaration
                                    ',' <<Regex: <_sre.SRE_Match object; span=(55, 56), match=','>>> ws:None [5, 9 -> 5, 10]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(65, 66), match='e'>>> ws:None [6, 9 -> 6, 10]
                            Repeat: (',', 0, 1)
                                ',' <<Regex: <_sre.SRE_Match object; span=(66, 67), match=','>>> ws:None [6, 10 -> 6, 11]
                            ')' <<Regex: <_sre.SRE_Match object; span=(68, 69), match=')'>>> ws:None [7, 1 -> 7, 2]
                    '=' <<Regex: <_sre.SRE_Match object; span=(70, 71), match='='>>> ws:(69, 70) [7, 3 -> 7, 4]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(72, 79), match='Another'>>> ws:(71, 72) [7, 5 -> 7, 12]
        """,
    )
