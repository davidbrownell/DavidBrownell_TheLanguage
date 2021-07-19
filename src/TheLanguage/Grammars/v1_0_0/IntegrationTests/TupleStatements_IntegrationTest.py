# ----------------------------------------------------------------------
# |
# |  TupleStatements_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 17:12:37
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

import pytest

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
def test_SingleDeclaration():
    assert Execute(
        textwrap.dedent(
            """\
            (a,) = var1

            ( # Comment 0
                # Comment 1
                a    # Comment 2
                ,    # Comment 3
                # Comment 4
            ) = var2
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Tuple Variable Declaration
                        Tuple Element
                            Single
                                '(' <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                                Or: {<name>, Tuple Element}
                                    <name> <<Regex: <_sre.SRE_Match object; span=(1, 2), match='a'>>> ws:None [1, 2 -> 1, 3]
                                ',' <<Regex: <_sre.SRE_Match object; span=(2, 3), match=','>>> ws:None [1, 3 -> 1, 4]
                                ')' <<Regex: <_sre.SRE_Match object; span=(3, 4), match=')'>>> ws:None [1, 4 -> 1, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='='>>> ws:(4, 5) [1, 6 -> 1, 7]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(7, 11), match='var1'>>> ws:(6, 7) [1, 8 -> 1, 12]
                        Newline+ <<11, 13>> ws:None [1, 12 -> 3, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Tuple Variable Declaration
                        Tuple Element
                            Single
                                '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [3, 1 -> 3, 2]
                                Or: {<name>, Tuple Element}
                                    <name> <<Regex: <_sre.SRE_Match object; span=(47, 48), match='a'>>> ws:None [5, 5 -> 5, 6]
                                ',' <<Regex: <_sre.SRE_Match object; span=(68, 69), match=','>>> ws:None [6, 5 -> 6, 6]
                                ')' <<Regex: <_sre.SRE_Match object; span=(101, 102), match=')'>>> ws:None [8, 1 -> 8, 2]
                        '=' <<Regex: <_sre.SRE_Match object; span=(103, 104), match='='>>> ws:(102, 103) [8, 3 -> 8, 4]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(105, 109), match='var2'>>> ws:(104, 105) [8, 5 -> 8, 9]
                        Newline+ <<109, 110>> ws:None [8, 9 -> 9, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_MultipleDeclaration():
    assert Execute(
        textwrap.dedent(
            """\
            (a, b) = var1
            (a, b,) = var2

            (a, b, c, d) = var3
            (a, b, c, d,) = var4

            (a, b,
                c, d,
                    e,
            ) = var5

            # Nested
            (a, (b, c), d) = var6
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Tuple Variable Declaration
                        Tuple Element
                            Multiple
                                '(' <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                                Or: {<name>, Tuple Element}
                                    <name> <<Regex: <_sre.SRE_Match object; span=(1, 2), match='a'>>> ws:None [1, 2 -> 1, 3]
                                Repeat: (Comma and Element, 1, None)
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(2, 3), match=','>>> ws:None [1, 3 -> 1, 4]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(4, 5), match='b'>>> ws:(3, 4) [1, 5 -> 1, 6]
                                ')' <<Regex: <_sre.SRE_Match object; span=(5, 6), match=')'>>> ws:None [1, 6 -> 1, 7]
                        '=' <<Regex: <_sre.SRE_Match object; span=(7, 8), match='='>>> ws:(6, 7) [1, 8 -> 1, 9]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(9, 13), match='var1'>>> ws:(8, 9) [1, 10 -> 1, 14]
                        Newline+ <<13, 14>> ws:None [1, 14 -> 2, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Tuple Variable Declaration
                        Tuple Element
                            Multiple
                                '(' <<Regex: <_sre.SRE_Match object; span=(14, 15), match='('>>> ws:None [2, 1 -> 2, 2]
                                Or: {<name>, Tuple Element}
                                    <name> <<Regex: <_sre.SRE_Match object; span=(15, 16), match='a'>>> ws:None [2, 2 -> 2, 3]
                                Repeat: (Comma and Element, 1, None)
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=','>>> ws:None [2, 3 -> 2, 4]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(18, 19), match='b'>>> ws:(17, 18) [2, 5 -> 2, 6]
                                Repeat: (',', 0, 1)
                                    ',' <<Regex: <_sre.SRE_Match object; span=(19, 20), match=','>>> ws:None [2, 6 -> 2, 7]
                                ')' <<Regex: <_sre.SRE_Match object; span=(20, 21), match=')'>>> ws:None [2, 7 -> 2, 8]
                        '=' <<Regex: <_sre.SRE_Match object; span=(22, 23), match='='>>> ws:(21, 22) [2, 9 -> 2, 10]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(24, 28), match='var2'>>> ws:(23, 24) [2, 11 -> 2, 15]
                        Newline+ <<28, 30>> ws:None [2, 15 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Tuple Variable Declaration
                        Tuple Element
                            Multiple
                                '(' <<Regex: <_sre.SRE_Match object; span=(30, 31), match='('>>> ws:None [4, 1 -> 4, 2]
                                Or: {<name>, Tuple Element}
                                    <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='a'>>> ws:None [4, 2 -> 4, 3]
                                Repeat: (Comma and Element, 1, None)
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=','>>> ws:None [4, 3 -> 4, 4]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(34, 35), match='b'>>> ws:(33, 34) [4, 5 -> 4, 6]
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(35, 36), match=','>>> ws:None [4, 6 -> 4, 7]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(37, 38), match='c'>>> ws:(36, 37) [4, 8 -> 4, 9]
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(38, 39), match=','>>> ws:None [4, 9 -> 4, 10]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(40, 41), match='d'>>> ws:(39, 40) [4, 11 -> 4, 12]
                                ')' <<Regex: <_sre.SRE_Match object; span=(41, 42), match=')'>>> ws:None [4, 12 -> 4, 13]
                        '=' <<Regex: <_sre.SRE_Match object; span=(43, 44), match='='>>> ws:(42, 43) [4, 14 -> 4, 15]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(45, 49), match='var3'>>> ws:(44, 45) [4, 16 -> 4, 20]
                        Newline+ <<49, 50>> ws:None [4, 20 -> 5, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Tuple Variable Declaration
                        Tuple Element
                            Multiple
                                '(' <<Regex: <_sre.SRE_Match object; span=(50, 51), match='('>>> ws:None [5, 1 -> 5, 2]
                                Or: {<name>, Tuple Element}
                                    <name> <<Regex: <_sre.SRE_Match object; span=(51, 52), match='a'>>> ws:None [5, 2 -> 5, 3]
                                Repeat: (Comma and Element, 1, None)
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(52, 53), match=','>>> ws:None [5, 3 -> 5, 4]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(54, 55), match='b'>>> ws:(53, 54) [5, 5 -> 5, 6]
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(55, 56), match=','>>> ws:None [5, 6 -> 5, 7]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(57, 58), match='c'>>> ws:(56, 57) [5, 8 -> 5, 9]
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(58, 59), match=','>>> ws:None [5, 9 -> 5, 10]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(60, 61), match='d'>>> ws:(59, 60) [5, 11 -> 5, 12]
                                Repeat: (',', 0, 1)
                                    ',' <<Regex: <_sre.SRE_Match object; span=(61, 62), match=','>>> ws:None [5, 12 -> 5, 13]
                                ')' <<Regex: <_sre.SRE_Match object; span=(62, 63), match=')'>>> ws:None [5, 13 -> 5, 14]
                        '=' <<Regex: <_sre.SRE_Match object; span=(64, 65), match='='>>> ws:(63, 64) [5, 15 -> 5, 16]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(66, 70), match='var4'>>> ws:(65, 66) [5, 17 -> 5, 21]
                        Newline+ <<70, 72>> ws:None [5, 21 -> 7, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Tuple Variable Declaration
                        Tuple Element
                            Multiple
                                '(' <<Regex: <_sre.SRE_Match object; span=(72, 73), match='('>>> ws:None [7, 1 -> 7, 2]
                                Or: {<name>, Tuple Element}
                                    <name> <<Regex: <_sre.SRE_Match object; span=(73, 74), match='a'>>> ws:None [7, 2 -> 7, 3]
                                Repeat: (Comma and Element, 1, None)
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(74, 75), match=','>>> ws:None [7, 3 -> 7, 4]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(76, 77), match='b'>>> ws:(75, 76) [7, 5 -> 7, 6]
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(77, 78), match=','>>> ws:None [7, 6 -> 7, 7]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(83, 84), match='c'>>> ws:None [8, 5 -> 8, 6]
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(84, 85), match=','>>> ws:None [8, 6 -> 8, 7]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(86, 87), match='d'>>> ws:(85, 86) [8, 8 -> 8, 9]
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(87, 88), match=','>>> ws:None [8, 9 -> 8, 10]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(97, 98), match='e'>>> ws:None [9, 9 -> 9, 10]
                                Repeat: (',', 0, 1)
                                    ',' <<Regex: <_sre.SRE_Match object; span=(98, 99), match=','>>> ws:None [9, 10 -> 9, 11]
                                ')' <<Regex: <_sre.SRE_Match object; span=(100, 101), match=')'>>> ws:None [10, 1 -> 10, 2]
                        '=' <<Regex: <_sre.SRE_Match object; span=(102, 103), match='='>>> ws:(101, 102) [10, 3 -> 10, 4]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(104, 108), match='var5'>>> ws:(103, 104) [10, 5 -> 10, 9]
                        Newline+ <<108, 110>> ws:None [10, 9 -> 12, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Tuple Variable Declaration
                        Tuple Element
                            Multiple
                                '(' <<Regex: <_sre.SRE_Match object; span=(119, 120), match='('>>> ws:None [13, 1 -> 13, 2]
                                Or: {<name>, Tuple Element}
                                    <name> <<Regex: <_sre.SRE_Match object; span=(120, 121), match='a'>>> ws:None [13, 2 -> 13, 3]
                                Repeat: (Comma and Element, 1, None)
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(121, 122), match=','>>> ws:None [13, 3 -> 13, 4]
                                        Or: {<name>, Tuple Element}
                                            Tuple Element
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(123, 124), match='('>>> ws:(122, 123) [13, 5 -> 13, 6]
                                                    Or: {<name>, Tuple Element}
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(124, 125), match='b'>>> ws:None [13, 6 -> 13, 7]
                                                    Repeat: (Comma and Element, 1, None)
                                                        Comma and Element
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(125, 126), match=','>>> ws:None [13, 7 -> 13, 8]
                                                            Or: {<name>, Tuple Element}
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(127, 128), match='c'>>> ws:(126, 127) [13, 9 -> 13, 10]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(128, 129), match=')'>>> ws:None [13, 10 -> 13, 11]
                                    Comma and Element
                                        ',' <<Regex: <_sre.SRE_Match object; span=(129, 130), match=','>>> ws:None [13, 11 -> 13, 12]
                                        Or: {<name>, Tuple Element}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(131, 132), match='d'>>> ws:(130, 131) [13, 13 -> 13, 14]
                                ')' <<Regex: <_sre.SRE_Match object; span=(132, 133), match=')'>>> ws:None [13, 14 -> 13, 15]
                        '=' <<Regex: <_sre.SRE_Match object; span=(134, 135), match='='>>> ws:(133, 134) [13, 16 -> 13, 17]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(136, 140), match='var6'>>> ws:(135, 136) [13, 18 -> 13, 22]
                        Newline+ <<140, 141>> ws:None [13, 22 -> 14, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_SingleExpression():
    assert Execute(
        textwrap.dedent(
            """\
            val1 = (a,)

            val = ( # Comment 0
                # Comment 1
                a # Comment 2
                , # Comment 3
                # Comment 4
            )
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='val1'>>> ws:None [1, 1 -> 1, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='='>>> ws:(4, 5) [1, 6 -> 1, 7]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Single
                                        '(' <<Regex: <_sre.SRE_Match object; span=(7, 8), match='('>>> ws:(6, 7) [1, 8 -> 1, 9]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(8, 9), match='a'>>> ws:None [1, 9 -> 1, 10]
                                        ',' <<Regex: <_sre.SRE_Match object; span=(9, 10), match=','>>> ws:None [1, 10 -> 1, 11]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(10, 11), match=')'>>> ws:None [1, 11 -> 1, 12]
                        Newline+ <<11, 13>> ws:None [1, 12 -> 3, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(13, 16), match='val'>>> ws:None [3, 1 -> 3, 4]
                        '=' <<Regex: <_sre.SRE_Match object; span=(17, 18), match='='>>> ws:(16, 17) [3, 5 -> 3, 6]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Single
                                        '(' <<Regex: <_sre.SRE_Match object; span=(19, 20), match='('>>> ws:(18, 19) [3, 7 -> 3, 8]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(53, 54), match='a'>>> ws:None [5, 5 -> 5, 6]
                                        ',' <<Regex: <_sre.SRE_Match object; span=(71, 72), match=','>>> ws:None [6, 5 -> 6, 6]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(101, 102), match=')'>>> ws:None [8, 1 -> 8, 2]
                        Newline+ <<102, 103>> ws:None [8, 2 -> 9, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_MultipleExpression():
    assert Execute(
        textwrap.dedent(
            """\
            val1 = (a, b)
            val2 = (c, d, )

            val3 = (e, f, g, h)
            val4 = (i, j, k, l, )

            val5 = (m, n,
                o, p,
                    q,
            r,)

            val5 = ((x, y), z)
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='val1'>>> ws:None [1, 1 -> 1, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='='>>> ws:(4, 5) [1, 6 -> 1, 7]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(7, 8), match='('>>> ws:(6, 7) [1, 8 -> 1, 9]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(8, 9), match='a'>>> ws:None [1, 9 -> 1, 10]
                                        Repeat: (Comma and Element, 1, None)
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(9, 10), match=','>>> ws:None [1, 10 -> 1, 11]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(11, 12), match='b'>>> ws:(10, 11) [1, 12 -> 1, 13]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(12, 13), match=')'>>> ws:None [1, 13 -> 1, 14]
                        Newline+ <<13, 14>> ws:None [1, 14 -> 2, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(14, 18), match='val2'>>> ws:None [2, 1 -> 2, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(19, 20), match='='>>> ws:(18, 19) [2, 6 -> 2, 7]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(21, 22), match='('>>> ws:(20, 21) [2, 8 -> 2, 9]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='c'>>> ws:None [2, 9 -> 2, 10]
                                        Repeat: (Comma and Element, 1, None)
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [2, 10 -> 2, 11]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='d'>>> ws:(24, 25) [2, 12 -> 2, 13]
                                        Repeat: (',', 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(26, 27), match=','>>> ws:None [2, 13 -> 2, 14]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(28, 29), match=')'>>> ws:(27, 28) [2, 15 -> 2, 16]
                        Newline+ <<29, 31>> ws:None [2, 16 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(31, 35), match='val3'>>> ws:None [4, 1 -> 4, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(36, 37), match='='>>> ws:(35, 36) [4, 6 -> 4, 7]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(38, 39), match='('>>> ws:(37, 38) [4, 8 -> 4, 9]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(39, 40), match='e'>>> ws:None [4, 9 -> 4, 10]
                                        Repeat: (Comma and Element, 1, None)
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(40, 41), match=','>>> ws:None [4, 10 -> 4, 11]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(42, 43), match='f'>>> ws:(41, 42) [4, 12 -> 4, 13]
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(43, 44), match=','>>> ws:None [4, 13 -> 4, 14]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(45, 46), match='g'>>> ws:(44, 45) [4, 15 -> 4, 16]
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(46, 47), match=','>>> ws:None [4, 16 -> 4, 17]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(48, 49), match='h'>>> ws:(47, 48) [4, 18 -> 4, 19]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(49, 50), match=')'>>> ws:None [4, 19 -> 4, 20]
                        Newline+ <<50, 51>> ws:None [4, 20 -> 5, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(51, 55), match='val4'>>> ws:None [5, 1 -> 5, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(56, 57), match='='>>> ws:(55, 56) [5, 6 -> 5, 7]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(58, 59), match='('>>> ws:(57, 58) [5, 8 -> 5, 9]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(59, 60), match='i'>>> ws:None [5, 9 -> 5, 10]
                                        Repeat: (Comma and Element, 1, None)
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(60, 61), match=','>>> ws:None [5, 10 -> 5, 11]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(62, 63), match='j'>>> ws:(61, 62) [5, 12 -> 5, 13]
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(63, 64), match=','>>> ws:None [5, 13 -> 5, 14]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(65, 66), match='k'>>> ws:(64, 65) [5, 15 -> 5, 16]
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(66, 67), match=','>>> ws:None [5, 16 -> 5, 17]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(68, 69), match='l'>>> ws:(67, 68) [5, 18 -> 5, 19]
                                        Repeat: (',', 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(69, 70), match=','>>> ws:None [5, 19 -> 5, 20]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(71, 72), match=')'>>> ws:(70, 71) [5, 21 -> 5, 22]
                        Newline+ <<72, 74>> ws:None [5, 22 -> 7, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(74, 78), match='val5'>>> ws:None [7, 1 -> 7, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(79, 80), match='='>>> ws:(78, 79) [7, 6 -> 7, 7]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(81, 82), match='('>>> ws:(80, 81) [7, 8 -> 7, 9]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(82, 83), match='m'>>> ws:None [7, 9 -> 7, 10]
                                        Repeat: (Comma and Element, 1, None)
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(83, 84), match=','>>> ws:None [7, 10 -> 7, 11]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(85, 86), match='n'>>> ws:(84, 85) [7, 12 -> 7, 13]
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(86, 87), match=','>>> ws:None [7, 13 -> 7, 14]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(92, 93), match='o'>>> ws:None [8, 5 -> 8, 6]
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(93, 94), match=','>>> ws:None [8, 6 -> 8, 7]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(95, 96), match='p'>>> ws:(94, 95) [8, 8 -> 8, 9]
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(96, 97), match=','>>> ws:None [8, 9 -> 8, 10]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(106, 107), match='q'>>> ws:None [9, 9 -> 9, 10]
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(107, 108), match=','>>> ws:None [9, 10 -> 9, 11]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(109, 110), match='r'>>> ws:None [10, 1 -> 10, 2]
                                        Repeat: (',', 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(110, 111), match=','>>> ws:None [10, 2 -> 10, 3]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(111, 112), match=')'>>> ws:None [10, 3 -> 10, 4]
                        Newline+ <<112, 114>> ws:None [10, 4 -> 12, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(114, 118), match='val5'>>> ws:None [12, 1 -> 12, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(119, 120), match='='>>> ws:(118, 119) [12, 6 -> 12, 7]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(121, 122), match='('>>> ws:(120, 121) [12, 8 -> 12, 9]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Tuple Expression
                                                    Multiple
                                                        '(' <<Regex: <_sre.SRE_Match object; span=(122, 123), match='('>>> ws:None [12, 9 -> 12, 10]
                                                        DynamicStatements.Expressions
                                                            1.0.0 Grammar
                                                                Variable Name
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(123, 124), match='x'>>> ws:None [12, 10 -> 12, 11]
                                                        Repeat: (Comma and Element, 1, None)
                                                            Comma and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(124, 125), match=','>>> ws:None [12, 11 -> 12, 12]
                                                                DynamicStatements.Expressions
                                                                    1.0.0 Grammar
                                                                        Variable Name
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(126, 127), match='y'>>> ws:(125, 126) [12, 13 -> 12, 14]
                                                        ')' <<Regex: <_sre.SRE_Match object; span=(127, 128), match=')'>>> ws:None [12, 14 -> 12, 15]
                                        Repeat: (Comma and Element, 1, None)
                                            Comma and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(128, 129), match=','>>> ws:None [12, 15 -> 12, 16]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(130, 131), match='z'>>> ws:(129, 130) [12, 17 -> 12, 18]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(131, 132), match=')'>>> ws:None [12, 18 -> 12, 19]
                        Newline+ <<132, 133>> ws:None [12, 19 -> 13, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_InvalidDeclarationSingle():
    for invalid_var in [
        "InvalidUppercase",
        "no.dots",
        "ends_with_double_under__",
    ]:
        with pytest.raises(NamingConventions.InvalidVariableNameError) as ex:
            Execute("({},) = value".format(invalid_var))

        ex = ex.value

        expected_value = textwrap.dedent(
            """\
            '{}' is not a valid variable name.

            Variable names must:
                Begin with a lowercase letter
                Contain upper-, lower-, numeric-, or underscore-characters
                Not end with double underscores
            """,
        ).format(
            invalid_var,
        )

        assert str(ex) == expected_value, invalid_var

# ----------------------------------------------------------------------
def test_InvalidDeclarationMultipleFirst():
    for invalid_var in [
        "InvalidUppercase",
        "no.dots",
        "ends_with_double_under__",
    ]:
        with pytest.raises(NamingConventions.InvalidVariableNameError) as ex:
            Execute("({}, valid1, valid2) = value".format(invalid_var))

        ex = ex.value

        expected_value = textwrap.dedent(
            """\
            '{}' is not a valid variable name.

            Variable names must:
                Begin with a lowercase letter
                Contain upper-, lower-, numeric-, or underscore-characters
                Not end with double underscores
            """,
        ).format(
            invalid_var,
        )

        assert str(ex) == expected_value, invalid_var

# ----------------------------------------------------------------------
def test_InvalidDeclarationMultipleSecond():
    for invalid_var in [
        "InvalidUppercase",
        "no.dots",
        "ends_with_double_under__",
    ]:
        with pytest.raises(NamingConventions.InvalidVariableNameError) as ex:
            Execute("(valid1, {},) = value".format(invalid_var))

        ex = ex.value

        expected_value = textwrap.dedent(
            """\
            '{}' is not a valid variable name.

            Variable names must:
                Begin with a lowercase letter
                Contain upper-, lower-, numeric-, or underscore-characters
                Not end with double underscores
            """,
        ).format(
            invalid_var,
        )

        assert str(ex) == expected_value, invalid_var

# ----------------------------------------------------------------------
def test_InvalidDeclarationMultipleNested():
    for invalid_var in [
        "InvalidUppercase",
        "no.dots",
        "ends_with_double_under__",
    ]:
        with pytest.raises(NamingConventions.InvalidVariableNameError) as ex:
            Execute("(valid1, (validA, {}), valid2) = value".format(invalid_var))

        ex = ex.value

        expected_value = textwrap.dedent(
            """\
            '{}' is not a valid variable name.

            Variable names must:
                Begin with a lowercase letter
                Contain upper-, lower-, numeric-, or underscore-characters
                Not end with double underscores
            """,
        ).format(
            invalid_var,
        )

        assert str(ex) == expected_value, invalid_var

# ----------------------------------------------------------------------
def test_TupleTypes():
    assert Execute(
        textwrap.dedent(
            """\
            # Using the 'as' statement: <expr> 'as' <type>

            single = value as (a,)

            multiple1 = value as (a, b)
            multiple2 = value as (a, b,)

            single_multiline = value as (
                a
                    ,
            )
            multiple_multiline = value as (
                a,
                    b
                        ,
                    c,
            d)
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(48, 54), match='single'>>> ws:None [3, 1 -> 3, 7]
                        '=' <<Regex: <_sre.SRE_Match object; span=(55, 56), match='='>>> ws:(54, 55) [3, 8 -> 3, 9]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(57, 62), match='value'>>> ws:(56, 57) [3, 10 -> 3, 15]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(63, 65), match='as'>>> ws:(62, 63) [3, 16 -> 3, 18]
                                    DynamicStatements.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Single
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(66, 67), match='('>>> ws:(65, 66) [3, 19 -> 3, 20]
                                                    DynamicStatements.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(67, 68), match='a'>>> ws:None [3, 20 -> 3, 21]
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(68, 69), match=','>>> ws:None [3, 21 -> 3, 22]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(69, 70), match=')'>>> ws:None [3, 22 -> 3, 23]
                        Newline+ <<70, 72>> ws:None [3, 23 -> 5, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(72, 81), match='multiple1'>>> ws:None [5, 1 -> 5, 10]
                        '=' <<Regex: <_sre.SRE_Match object; span=(82, 83), match='='>>> ws:(81, 82) [5, 11 -> 5, 12]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(84, 89), match='value'>>> ws:(83, 84) [5, 13 -> 5, 18]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(90, 92), match='as'>>> ws:(89, 90) [5, 19 -> 5, 21]
                                    DynamicStatements.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(93, 94), match='('>>> ws:(92, 93) [5, 22 -> 5, 23]
                                                    DynamicStatements.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(94, 95), match='a'>>> ws:None [5, 23 -> 5, 24]
                                                    Repeat: (Comma and Element, 1, None)
                                                        Comma and Element
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(95, 96), match=','>>> ws:None [5, 24 -> 5, 25]
                                                            DynamicStatements.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(97, 98), match='b'>>> ws:(96, 97) [5, 26 -> 5, 27]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(98, 99), match=')'>>> ws:None [5, 27 -> 5, 28]
                        Newline+ <<99, 100>> ws:None [5, 28 -> 6, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(100, 109), match='multiple2'>>> ws:None [6, 1 -> 6, 10]
                        '=' <<Regex: <_sre.SRE_Match object; span=(110, 111), match='='>>> ws:(109, 110) [6, 11 -> 6, 12]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(112, 117), match='value'>>> ws:(111, 112) [6, 13 -> 6, 18]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(118, 120), match='as'>>> ws:(117, 118) [6, 19 -> 6, 21]
                                    DynamicStatements.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(121, 122), match='('>>> ws:(120, 121) [6, 22 -> 6, 23]
                                                    DynamicStatements.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(122, 123), match='a'>>> ws:None [6, 23 -> 6, 24]
                                                    Repeat: (Comma and Element, 1, None)
                                                        Comma and Element
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(123, 124), match=','>>> ws:None [6, 24 -> 6, 25]
                                                            DynamicStatements.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(125, 126), match='b'>>> ws:(124, 125) [6, 26 -> 6, 27]
                                                    Repeat: (',', 0, 1)
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(126, 127), match=','>>> ws:None [6, 27 -> 6, 28]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(127, 128), match=')'>>> ws:None [6, 28 -> 6, 29]
                        Newline+ <<128, 130>> ws:None [6, 29 -> 8, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(130, 146), match='single_multiline'>>> ws:None [8, 1 -> 8, 17]
                        '=' <<Regex: <_sre.SRE_Match object; span=(147, 148), match='='>>> ws:(146, 147) [8, 18 -> 8, 19]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(149, 154), match='value'>>> ws:(148, 149) [8, 20 -> 8, 25]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(155, 157), match='as'>>> ws:(154, 155) [8, 26 -> 8, 28]
                                    DynamicStatements.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Single
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(158, 159), match='('>>> ws:(157, 158) [8, 29 -> 8, 30]
                                                    DynamicStatements.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(164, 165), match='a'>>> ws:None [9, 5 -> 9, 6]
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(174, 175), match=','>>> ws:None [10, 9 -> 10, 10]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(176, 177), match=')'>>> ws:None [11, 1 -> 11, 2]
                        Newline+ <<177, 178>> ws:None [11, 2 -> 12, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(178, 196), match='multiple_multiline'>>> ws:None [12, 1 -> 12, 19]
                        '=' <<Regex: <_sre.SRE_Match object; span=(197, 198), match='='>>> ws:(196, 197) [12, 20 -> 12, 21]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(199, 204), match='value'>>> ws:(198, 199) [12, 22 -> 12, 27]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(205, 207), match='as'>>> ws:(204, 205) [12, 28 -> 12, 30]
                                    DynamicStatements.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(208, 209), match='('>>> ws:(207, 208) [12, 31 -> 12, 32]
                                                    DynamicStatements.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(214, 215), match='a'>>> ws:None [13, 5 -> 13, 6]
                                                    Repeat: (Comma and Element, 1, None)
                                                        Comma and Element
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(215, 216), match=','>>> ws:None [13, 6 -> 13, 7]
                                                            DynamicStatements.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(225, 226), match='b'>>> ws:None [14, 9 -> 14, 10]
                                                        Comma and Element
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(239, 240), match=','>>> ws:None [15, 13 -> 15, 14]
                                                            DynamicStatements.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(249, 250), match='c'>>> ws:None [16, 9 -> 16, 10]
                                                        Comma and Element
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(250, 251), match=','>>> ws:None [16, 10 -> 16, 11]
                                                            DynamicStatements.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(252, 253), match='d'>>> ws:None [17, 1 -> 17, 2]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(253, 254), match=')'>>> ws:None [17, 2 -> 17, 3]
                        Newline+ <<254, 255>> ws:None [17, 3 -> 18, 1]
        """,
    )
