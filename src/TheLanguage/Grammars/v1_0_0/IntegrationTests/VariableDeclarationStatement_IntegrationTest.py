# ----------------------------------------------------------------------
# |
# |  VariableDeclarationStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 14:34:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for VariableDeclarationStatement.py"""

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
    from ..VariableDeclarationStatement import *


# ----------------------------------------------------------------------
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            one = two
            three = Four()
            fix = Six(
                seven,
                eight,
                nine=value,
            )
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Variable Declaration
                    Or: [Tuple (Multiple), Tuple (Single), <name>]
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    '=' <<Regex: <_sre.SRE_Match object; span=(4, 5), match='='>>> ws:(3, 4) [1, 5 -> 1, 6]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 7 -> 1, 10]
            1.0.0 Grammar
                Variable Declaration
                    Or: [Tuple (Multiple), Tuple (Single), <name>]
                        <name> <<Regex: <_sre.SRE_Match object; span=(10, 15), match='three'>>> ws:None [2, 1 -> 2, 6]
                    '=' <<Regex: <_sre.SRE_Match object; span=(16, 17), match='='>>> ws:(15, 16) [2, 7 -> 2, 8]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Function Invocation
                                <name> <<Regex: <_sre.SRE_Match object; span=(18, 22), match='Four'>>> ws:(17, 18) [2, 9 -> 2, 13]
                                '(' <<Regex: <_sre.SRE_Match object; span=(22, 23), match='('>>> ws:None [2, 13 -> 2, 14]
                                ')' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=')'>>> ws:None [2, 14 -> 2, 15]
            1.0.0 Grammar
                Variable Declaration
                    Or: [Tuple (Multiple), Tuple (Single), <name>]
                        <name> <<Regex: <_sre.SRE_Match object; span=(25, 28), match='fix'>>> ws:None [3, 1 -> 3, 4]
                    '=' <<Regex: <_sre.SRE_Match object; span=(29, 30), match='='>>> ws:(28, 29) [3, 5 -> 3, 6]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Function Invocation
                                <name> <<Regex: <_sre.SRE_Match object; span=(31, 34), match='Six'>>> ws:(30, 31) [3, 7 -> 3, 10]
                                '(' <<Regex: <_sre.SRE_Match object; span=(34, 35), match='('>>> ws:None [3, 10 -> 3, 11]
                                Repeat: (Arguments, 0, 1)
                                    Arguments
                                        Or: [Keyword, DynamicStatements.Expressions]
                                            DynamicStatements.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(40, 45), match='seven'>>> ws:None [4, 5 -> 4, 10]
                                        Repeat: (Comma and Argument, 0, None)
                                            Comma and Argument
                                                ',' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=','>>> ws:None [4, 10 -> 4, 11]
                                                Or: [Keyword, DynamicStatements.Expressions]
                                                    DynamicStatements.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(51, 56), match='eight'>>> ws:None [5, 5 -> 5, 10]
                                            Comma and Argument
                                                ',' <<Regex: <_sre.SRE_Match object; span=(56, 57), match=','>>> ws:None [5, 10 -> 5, 11]
                                                Or: [Keyword, DynamicStatements.Expressions]
                                                    Keyword
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(62, 66), match='nine'>>> ws:None [6, 5 -> 6, 9]
                                                        '=' <<Regex: <_sre.SRE_Match object; span=(66, 67), match='='>>> ws:None [6, 9 -> 6, 10]
                                                        DynamicStatements.Expressions
                                                            1.0.0 Grammar
                                                                Variable Name
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(67, 72), match='value'>>> ws:None [6, 10 -> 6, 15]
                                        Repeat: (',', 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(72, 73), match=','>>> ws:None [6, 15 -> 6, 16]
                                ')' <<Regex: <_sre.SRE_Match object; span=(74, 75), match=')'>>> ws:None [7, 1 -> 7, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_TupleSingle():
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
                Variable Declaration
                    Or: [Tuple (Multiple), Tuple (Single), <name>]
                        Tuple (Single)
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
                Variable Declaration
                    Or: [Tuple (Multiple), Tuple (Single), <name>]
                        Tuple (Single)
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
def test_TupleMultiple():
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
                Variable Declaration
                    Or: [Tuple (Multiple), Tuple (Single), <name>]
                        Tuple (Multiple)
                            '(' <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                            <name> <<Regex: <_sre.SRE_Match object; span=(1, 2), match='a'>>> ws:None [1, 2 -> 1, 3]
                            Repeat: (Comma and Name, 1, None)
                                Comma and Name
                                    ',' <<Regex: <_sre.SRE_Match object; span=(2, 3), match=','>>> ws:None [1, 3 -> 1, 4]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(4, 5), match='b'>>> ws:(3, 4) [1, 5 -> 1, 6]
                            ')' <<Regex: <_sre.SRE_Match object; span=(5, 6), match=')'>>> ws:None [1, 6 -> 1, 7]
                    '=' <<Regex: <_sre.SRE_Match object; span=(7, 8), match='='>>> ws:(6, 7) [1, 8 -> 1, 9]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(9, 14), match='line1'>>> ws:(8, 9) [1, 10 -> 1, 15]
            1.0.0 Grammar
                Variable Declaration
                    Or: [Tuple (Multiple), Tuple (Single), <name>]
                        Tuple (Multiple)
                            '(' <<Regex: <_sre.SRE_Match object; span=(15, 16), match='('>>> ws:None [2, 1 -> 2, 2]
                            <name> <<Regex: <_sre.SRE_Match object; span=(16, 17), match='a'>>> ws:None [2, 2 -> 2, 3]
                            Repeat: (Comma and Name, 1, None)
                                Comma and Name
                                    ',' <<Regex: <_sre.SRE_Match object; span=(17, 18), match=','>>> ws:None [2, 3 -> 2, 4]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(19, 20), match='b'>>> ws:(18, 19) [2, 5 -> 2, 6]
                                Comma and Name
                                    ',' <<Regex: <_sre.SRE_Match object; span=(20, 21), match=','>>> ws:None [2, 6 -> 2, 7]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='c'>>> ws:(21, 22) [2, 8 -> 2, 9]
                                Comma and Name
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
                Variable Declaration
                    Or: [Tuple (Multiple), Tuple (Single), <name>]
                        Tuple (Multiple)
                            '(' <<Regex: <_sre.SRE_Match object; span=(40, 41), match='('>>> ws:None [4, 1 -> 4, 2]
                            <name> <<Regex: <_sre.SRE_Match object; span=(41, 42), match='a'>>> ws:None [4, 2 -> 4, 3]
                            Repeat: (Comma and Name, 1, None)
                                Comma and Name
                                    ',' <<Regex: <_sre.SRE_Match object; span=(42, 43), match=','>>> ws:None [4, 3 -> 4, 4]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(44, 45), match='b'>>> ws:(43, 44) [4, 5 -> 4, 6]
                                Comma and Name
                                    ',' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=','>>> ws:None [4, 6 -> 4, 7]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(51, 52), match='c'>>> ws:None [5, 5 -> 5, 6]
                                Comma and Name
                                    ',' <<Regex: <_sre.SRE_Match object; span=(52, 53), match=','>>> ws:None [5, 6 -> 5, 7]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(54, 55), match='d'>>> ws:(53, 54) [5, 8 -> 5, 9]
                                Comma and Name
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
