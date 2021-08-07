# ----------------------------------------------------------------------
# |
# |  TupleExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-06 18:37:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for TupleExpression.py"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TupleExpression import *
    from ...Common.AutomatedTests import Execute


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
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Single
                                        '(' <<Regex: <_sre.SRE_Match object; span=(7, 8), match='('>>> ws:(6, 7) [1, 8 -> 1, 9]
                                        DynamicStatementsType.Expressions
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
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Single
                                        '(' <<Regex: <_sre.SRE_Match object; span=(19, 20), match='('>>> ws:(18, 19) [3, 7 -> 3, 8]
                                        DynamicStatementsType.Expressions
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
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(7, 8), match='('>>> ws:(6, 7) [1, 8 -> 1, 9]
                                        Delimited Elements
                                            DynamicStatementsType.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(8, 9), match='a'>>> ws:None [1, 9 -> 1, 10]
                                            Repeat: (Delimiter and Element, 1, None)
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(9, 10), match=','>>> ws:None [1, 10 -> 1, 11]
                                                    DynamicStatementsType.Expressions
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
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(21, 22), match='('>>> ws:(20, 21) [2, 8 -> 2, 9]
                                        Delimited Elements
                                            DynamicStatementsType.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='c'>>> ws:None [2, 9 -> 2, 10]
                                            Repeat: (Delimiter and Element, 1, None)
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [2, 10 -> 2, 11]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='d'>>> ws:(24, 25) [2, 12 -> 2, 13]
                                            Repeat: (Trailing Delimiter, 0, 1)
                                                ',' <<Regex: <_sre.SRE_Match object; span=(26, 27), match=','>>> ws:None [2, 13 -> 2, 14]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(28, 29), match=')'>>> ws:(27, 28) [2, 15 -> 2, 16]
                        Newline+ <<29, 31>> ws:None [2, 16 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(31, 35), match='val3'>>> ws:None [4, 1 -> 4, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(36, 37), match='='>>> ws:(35, 36) [4, 6 -> 4, 7]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(38, 39), match='('>>> ws:(37, 38) [4, 8 -> 4, 9]
                                        Delimited Elements
                                            DynamicStatementsType.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(39, 40), match='e'>>> ws:None [4, 9 -> 4, 10]
                                            Repeat: (Delimiter and Element, 1, None)
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(40, 41), match=','>>> ws:None [4, 10 -> 4, 11]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(42, 43), match='f'>>> ws:(41, 42) [4, 12 -> 4, 13]
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(43, 44), match=','>>> ws:None [4, 13 -> 4, 14]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(45, 46), match='g'>>> ws:(44, 45) [4, 15 -> 4, 16]
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(46, 47), match=','>>> ws:None [4, 16 -> 4, 17]
                                                    DynamicStatementsType.Expressions
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
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(58, 59), match='('>>> ws:(57, 58) [5, 8 -> 5, 9]
                                        Delimited Elements
                                            DynamicStatementsType.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(59, 60), match='i'>>> ws:None [5, 9 -> 5, 10]
                                            Repeat: (Delimiter and Element, 1, None)
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(60, 61), match=','>>> ws:None [5, 10 -> 5, 11]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(62, 63), match='j'>>> ws:(61, 62) [5, 12 -> 5, 13]
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(63, 64), match=','>>> ws:None [5, 13 -> 5, 14]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(65, 66), match='k'>>> ws:(64, 65) [5, 15 -> 5, 16]
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(66, 67), match=','>>> ws:None [5, 16 -> 5, 17]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(68, 69), match='l'>>> ws:(67, 68) [5, 18 -> 5, 19]
                                            Repeat: (Trailing Delimiter, 0, 1)
                                                ',' <<Regex: <_sre.SRE_Match object; span=(69, 70), match=','>>> ws:None [5, 19 -> 5, 20]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(71, 72), match=')'>>> ws:(70, 71) [5, 21 -> 5, 22]
                        Newline+ <<72, 74>> ws:None [5, 22 -> 7, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(74, 78), match='val5'>>> ws:None [7, 1 -> 7, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(79, 80), match='='>>> ws:(78, 79) [7, 6 -> 7, 7]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(81, 82), match='('>>> ws:(80, 81) [7, 8 -> 7, 9]
                                        Delimited Elements
                                            DynamicStatementsType.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(82, 83), match='m'>>> ws:None [7, 9 -> 7, 10]
                                            Repeat: (Delimiter and Element, 1, None)
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(83, 84), match=','>>> ws:None [7, 10 -> 7, 11]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(85, 86), match='n'>>> ws:(84, 85) [7, 12 -> 7, 13]
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(86, 87), match=','>>> ws:None [7, 13 -> 7, 14]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(92, 93), match='o'>>> ws:None [8, 5 -> 8, 6]
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(93, 94), match=','>>> ws:None [8, 6 -> 8, 7]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(95, 96), match='p'>>> ws:(94, 95) [8, 8 -> 8, 9]
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(96, 97), match=','>>> ws:None [8, 9 -> 8, 10]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(106, 107), match='q'>>> ws:None [9, 9 -> 9, 10]
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(107, 108), match=','>>> ws:None [9, 10 -> 9, 11]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(109, 110), match='r'>>> ws:None [10, 1 -> 10, 2]
                                            Repeat: (Trailing Delimiter, 0, 1)
                                                ',' <<Regex: <_sre.SRE_Match object; span=(110, 111), match=','>>> ws:None [10, 2 -> 10, 3]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(111, 112), match=')'>>> ws:None [10, 3 -> 10, 4]
                        Newline+ <<112, 114>> ws:None [10, 4 -> 12, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(114, 118), match='val5'>>> ws:None [12, 1 -> 12, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(119, 120), match='='>>> ws:(118, 119) [12, 6 -> 12, 7]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                Tuple Expression
                                    Multiple
                                        '(' <<Regex: <_sre.SRE_Match object; span=(121, 122), match='('>>> ws:(120, 121) [12, 8 -> 12, 9]
                                        Delimited Elements
                                            DynamicStatementsType.Expressions
                                                1.0.0 Grammar
                                                    Tuple Expression
                                                        Multiple
                                                            '(' <<Regex: <_sre.SRE_Match object; span=(122, 123), match='('>>> ws:None [12, 9 -> 12, 10]
                                                            Delimited Elements
                                                                DynamicStatementsType.Expressions
                                                                    1.0.0 Grammar
                                                                        Variable Name
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(123, 124), match='x'>>> ws:None [12, 10 -> 12, 11]
                                                                Repeat: (Delimiter and Element, 1, None)
                                                                    Delimiter and Element
                                                                        ',' <<Regex: <_sre.SRE_Match object; span=(124, 125), match=','>>> ws:None [12, 11 -> 12, 12]
                                                                        DynamicStatementsType.Expressions
                                                                            1.0.0 Grammar
                                                                                Variable Name
                                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(126, 127), match='y'>>> ws:(125, 126) [12, 13 -> 12, 14]
                                                            ')' <<Regex: <_sre.SRE_Match object; span=(127, 128), match=')'>>> ws:None [12, 14 -> 12, 15]
                                            Repeat: (Delimiter and Element, 1, None)
                                                Delimiter and Element
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(128, 129), match=','>>> ws:None [12, 15 -> 12, 16]
                                                    DynamicStatementsType.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(130, 131), match='z'>>> ws:(129, 130) [12, 17 -> 12, 18]
                                        ')' <<Regex: <_sre.SRE_Match object; span=(131, 132), match=')'>>> ws:None [12, 18 -> 12, 19]
                        Newline+ <<132, 133>> ws:None [12, 19 -> 13, 1]
        """,
    )
