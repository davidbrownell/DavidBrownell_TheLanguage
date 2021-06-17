# ----------------------------------------------------------------------
# |
# |  FuncDeclarationStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-13 12:58:11
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for FuncDeclarationStatement"""

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
    from ..FuncDeclarationStatement import *


# ----------------------------------------------------------------------
def test_NoArgs():
    assert Execute(
        textwrap.dedent(
            """\
            type val Func():
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='type'>>> ws:None [1, 1 -> 1, 5]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(5, 8), match='val'>>> ws:(4, 5) [1, 6 -> 1, 9]
                    <name> <<Regex: <_sre.SRE_Match object; span=(9, 13), match='Func'>>> ws:(8, 9) [1, 10 -> 1, 14]
                    '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [1, 14 -> 1, 15]
                    ')' <<Regex: <_sre.SRE_Match object; span=(14, 15), match=')'>>> ws:None [1, 15 -> 1, 16]
                    ':' <<Regex: <_sre.SRE_Match object; span=(15, 16), match=':'>>> ws:None [1, 16 -> 1, 17]
                    Newline+ <<16, 17>> ws:None [1, 17 -> 2, 1]
                    Indent <<17, 21, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(21, 25), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [3, 1 -> 3, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_MultipleStatements():
    assert Execute(
        textwrap.dedent(
            """\
            type val Func():
                pass
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='type'>>> ws:None [1, 1 -> 1, 5]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(5, 8), match='val'>>> ws:(4, 5) [1, 6 -> 1, 9]
                    <name> <<Regex: <_sre.SRE_Match object; span=(9, 13), match='Func'>>> ws:(8, 9) [1, 10 -> 1, 14]
                    '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [1, 14 -> 1, 15]
                    ')' <<Regex: <_sre.SRE_Match object; span=(14, 15), match=')'>>> ws:None [1, 15 -> 1, 16]
                    ':' <<Regex: <_sre.SRE_Match object; span=(15, 16), match=':'>>> ws:None [1, 16 -> 1, 17]
                    Newline+ <<16, 17>> ws:None [1, 17 -> 2, 1]
                    Indent <<17, 21, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(21, 25), match='pass'>>> ws:None [2, 5 -> 2, 9]
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(30, 34), match='pass'>>> ws:None [3, 5 -> 3, 9]
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_TraditionalSingleArg():
    assert Execute(
        textwrap.dedent(
            """\
            # No Trailing Comma
            type val Func1(int val a):
                pass

            # Trailing Comma
            type val Func2(int val a,):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(20, 24), match='type'>>> ws:None [2, 1 -> 2, 5]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(25, 28), match='val'>>> ws:(24, 25) [2, 6 -> 2, 9]
                    <name> <<Regex: <_sre.SRE_Match object; span=(29, 34), match='Func1'>>> ws:(28, 29) [2, 10 -> 2, 15]
                    '(' <<Regex: <_sre.SRE_Match object; span=(34, 35), match='('>>> ws:None [2, 15 -> 2, 16]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(35, 38), match='int'>>> ws:None [2, 16 -> 2, 19]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(39, 42), match='val'>>> ws:(38, 39) [2, 20 -> 2, 23]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(43, 44), match='a'>>> ws:(42, 43) [2, 24 -> 2, 25]
                    ')' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=')'>>> ws:None [2, 25 -> 2, 26]
                    ':' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=':'>>> ws:None [2, 26 -> 2, 27]
                    Newline+ <<46, 47>> ws:None [2, 27 -> 3, 1]
                    Indent <<47, 51, (4)>> ws:None [3, 1 -> 3, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(51, 55), match='pass'>>> ws:None [3, 5 -> 3, 9]
                    Dedent <<>> ws:None [5, 1 -> 5, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(74, 78), match='type'>>> ws:None [6, 1 -> 6, 5]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(79, 82), match='val'>>> ws:(78, 79) [6, 6 -> 6, 9]
                    <name> <<Regex: <_sre.SRE_Match object; span=(83, 88), match='Func2'>>> ws:(82, 83) [6, 10 -> 6, 15]
                    '(' <<Regex: <_sre.SRE_Match object; span=(88, 89), match='('>>> ws:None [6, 15 -> 6, 16]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(89, 92), match='int'>>> ws:None [6, 16 -> 6, 19]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(93, 96), match='val'>>> ws:(92, 93) [6, 20 -> 6, 23]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(97, 98), match='a'>>> ws:(96, 97) [6, 24 -> 6, 25]
                                Repeat: (',', 0, 1)
                                    ',' <<Regex: <_sre.SRE_Match object; span=(98, 99), match=','>>> ws:None [6, 25 -> 6, 26]
                    ')' <<Regex: <_sre.SRE_Match object; span=(99, 100), match=')'>>> ws:None [6, 26 -> 6, 27]
                    ':' <<Regex: <_sre.SRE_Match object; span=(100, 101), match=':'>>> ws:None [6, 27 -> 6, 28]
                    Newline+ <<101, 102>> ws:None [6, 28 -> 7, 1]
                    Indent <<102, 106, (4)>> ws:None [7, 1 -> 7, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(106, 110), match='pass'>>> ws:None [7, 5 -> 7, 9]
                    Dedent <<>> ws:None [8, 1 -> 8, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_TraditionalMultiArgs():
    assert Execute(
        textwrap.dedent(
            """\
            # No trailing comma
            string view Func1(int var a, bool val b, char ref c, double view dee):
                pass

            # Trailing comma
            string view Func2(int var a, bool val b, char ref c, double view dee,):
                pass

            # Multiline
            string view Func1(
                int var a,
                bool val b,
                    char ref c,
                double view dee,
            ):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(20, 26), match='string'>>> ws:None [2, 1 -> 2, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(27, 31), match='view'>>> ws:(26, 27) [2, 8 -> 2, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(32, 37), match='Func1'>>> ws:(31, 32) [2, 13 -> 2, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(37, 38), match='('>>> ws:None [2, 18 -> 2, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(38, 41), match='int'>>> ws:None [2, 19 -> 2, 22]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'var' <<Regex: <_sre.SRE_Match object; span=(42, 45), match='var'>>> ws:(41, 42) [2, 23 -> 2, 26]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(46, 47), match='a'>>> ws:(45, 46) [2, 27 -> 2, 28]
                                Repeat: (Comma and Parameter, 0, None)
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(47, 48), match=','>>> ws:None [2, 28 -> 2, 29]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(49, 53), match='bool'>>> ws:(48, 49) [2, 30 -> 2, 34]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(54, 57), match='val'>>> ws:(53, 54) [2, 35 -> 2, 38]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(58, 59), match='b'>>> ws:(57, 58) [2, 39 -> 2, 40]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(59, 60), match=','>>> ws:None [2, 40 -> 2, 41]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(61, 65), match='char'>>> ws:(60, 61) [2, 42 -> 2, 46]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'ref' <<Regex: <_sre.SRE_Match object; span=(66, 69), match='ref'>>> ws:(65, 66) [2, 47 -> 2, 50]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(70, 71), match='c'>>> ws:(69, 70) [2, 51 -> 2, 52]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(71, 72), match=','>>> ws:None [2, 52 -> 2, 53]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(73, 79), match='double'>>> ws:(72, 73) [2, 54 -> 2, 60]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'view' <<Regex: <_sre.SRE_Match object; span=(80, 84), match='view'>>> ws:(79, 80) [2, 61 -> 2, 65]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(85, 88), match='dee'>>> ws:(84, 85) [2, 66 -> 2, 69]
                    ')' <<Regex: <_sre.SRE_Match object; span=(88, 89), match=')'>>> ws:None [2, 69 -> 2, 70]
                    ':' <<Regex: <_sre.SRE_Match object; span=(89, 90), match=':'>>> ws:None [2, 70 -> 2, 71]
                    Newline+ <<90, 91>> ws:None [2, 71 -> 3, 1]
                    Indent <<91, 95, (4)>> ws:None [3, 1 -> 3, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(95, 99), match='pass'>>> ws:None [3, 5 -> 3, 9]
                    Dedent <<>> ws:None [5, 1 -> 5, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(118, 124), match='string'>>> ws:None [6, 1 -> 6, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(125, 129), match='view'>>> ws:(124, 125) [6, 8 -> 6, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(130, 135), match='Func2'>>> ws:(129, 130) [6, 13 -> 6, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(135, 136), match='('>>> ws:None [6, 18 -> 6, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(136, 139), match='int'>>> ws:None [6, 19 -> 6, 22]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'var' <<Regex: <_sre.SRE_Match object; span=(140, 143), match='var'>>> ws:(139, 140) [6, 23 -> 6, 26]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(144, 145), match='a'>>> ws:(143, 144) [6, 27 -> 6, 28]
                                Repeat: (Comma and Parameter, 0, None)
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(145, 146), match=','>>> ws:None [6, 28 -> 6, 29]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(147, 151), match='bool'>>> ws:(146, 147) [6, 30 -> 6, 34]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(152, 155), match='val'>>> ws:(151, 152) [6, 35 -> 6, 38]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(156, 157), match='b'>>> ws:(155, 156) [6, 39 -> 6, 40]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(157, 158), match=','>>> ws:None [6, 40 -> 6, 41]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(159, 163), match='char'>>> ws:(158, 159) [6, 42 -> 6, 46]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'ref' <<Regex: <_sre.SRE_Match object; span=(164, 167), match='ref'>>> ws:(163, 164) [6, 47 -> 6, 50]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(168, 169), match='c'>>> ws:(167, 168) [6, 51 -> 6, 52]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(169, 170), match=','>>> ws:None [6, 52 -> 6, 53]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(171, 177), match='double'>>> ws:(170, 171) [6, 54 -> 6, 60]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'view' <<Regex: <_sre.SRE_Match object; span=(178, 182), match='view'>>> ws:(177, 178) [6, 61 -> 6, 65]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(183, 186), match='dee'>>> ws:(182, 183) [6, 66 -> 6, 69]
                                Repeat: (',', 0, 1)
                                    ',' <<Regex: <_sre.SRE_Match object; span=(186, 187), match=','>>> ws:None [6, 69 -> 6, 70]
                    ')' <<Regex: <_sre.SRE_Match object; span=(187, 188), match=')'>>> ws:None [6, 70 -> 6, 71]
                    ':' <<Regex: <_sre.SRE_Match object; span=(188, 189), match=':'>>> ws:None [6, 71 -> 6, 72]
                    Newline+ <<189, 190>> ws:None [6, 72 -> 7, 1]
                    Indent <<190, 194, (4)>> ws:None [7, 1 -> 7, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(194, 198), match='pass'>>> ws:None [7, 5 -> 7, 9]
                    Dedent <<>> ws:None [9, 1 -> 9, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(212, 218), match='string'>>> ws:None [10, 1 -> 10, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(219, 223), match='view'>>> ws:(218, 219) [10, 8 -> 10, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(224, 229), match='Func1'>>> ws:(223, 224) [10, 13 -> 10, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(229, 230), match='('>>> ws:None [10, 18 -> 10, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(235, 238), match='int'>>> ws:None [11, 5 -> 11, 8]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'var' <<Regex: <_sre.SRE_Match object; span=(239, 242), match='var'>>> ws:(238, 239) [11, 9 -> 11, 12]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(243, 244), match='a'>>> ws:(242, 243) [11, 13 -> 11, 14]
                                Repeat: (Comma and Parameter, 0, None)
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(244, 245), match=','>>> ws:None [11, 14 -> 11, 15]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(250, 254), match='bool'>>> ws:None [12, 5 -> 12, 9]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(255, 258), match='val'>>> ws:(254, 255) [12, 10 -> 12, 13]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(259, 260), match='b'>>> ws:(258, 259) [12, 14 -> 12, 15]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(260, 261), match=','>>> ws:None [12, 15 -> 12, 16]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(270, 274), match='char'>>> ws:None [13, 9 -> 13, 13]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'ref' <<Regex: <_sre.SRE_Match object; span=(275, 278), match='ref'>>> ws:(274, 275) [13, 14 -> 13, 17]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(279, 280), match='c'>>> ws:(278, 279) [13, 18 -> 13, 19]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(280, 281), match=','>>> ws:None [13, 19 -> 13, 20]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(286, 292), match='double'>>> ws:None [14, 5 -> 14, 11]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'view' <<Regex: <_sre.SRE_Match object; span=(293, 297), match='view'>>> ws:(292, 293) [14, 12 -> 14, 16]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(298, 301), match='dee'>>> ws:(297, 298) [14, 17 -> 14, 20]
                                Repeat: (',', 0, 1)
                                    ',' <<Regex: <_sre.SRE_Match object; span=(301, 302), match=','>>> ws:None [14, 20 -> 14, 21]
                    ')' <<Regex: <_sre.SRE_Match object; span=(303, 304), match=')'>>> ws:None [15, 1 -> 15, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(304, 305), match=':'>>> ws:None [15, 2 -> 15, 3]
                    Newline+ <<305, 306>> ws:None [15, 3 -> 16, 1]
                    Indent <<306, 310, (4)>> ws:None [16, 1 -> 16, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(310, 314), match='pass'>>> ws:None [16, 5 -> 16, 9]
                    Dedent <<>> ws:None [17, 1 -> 17, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_TraditionalWithDefaults():
    assert Execute(
        textwrap.dedent(
            """\
            string val Func(int view a, bool var bee=true):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='string'>>> ws:None [1, 1 -> 1, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(7, 10), match='val'>>> ws:(6, 7) [1, 8 -> 1, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(11, 15), match='Func'>>> ws:(10, 11) [1, 12 -> 1, 16]
                    '(' <<Regex: <_sre.SRE_Match object; span=(15, 16), match='('>>> ws:None [1, 16 -> 1, 17]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(16, 19), match='int'>>> ws:None [1, 17 -> 1, 20]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(20, 24), match='view'>>> ws:(19, 20) [1, 21 -> 1, 25]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='a'>>> ws:(24, 25) [1, 26 -> 1, 27]
                                Repeat: (Comma and Parameter, 0, None)
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(26, 27), match=','>>> ws:None [1, 27 -> 1, 28]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(28, 32), match='bool'>>> ws:(27, 28) [1, 29 -> 1, 33]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(33, 36), match='var'>>> ws:(32, 33) [1, 34 -> 1, 37]
                                                Or: [With Default, <name>]
                                                    With Default
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(37, 40), match='bee'>>> ws:(36, 37) [1, 38 -> 1, 41]
                                                        '=' <<Regex: <_sre.SRE_Match object; span=(40, 41), match='='>>> ws:None [1, 41 -> 1, 42]
                                                        DynamicStatements.Expressions
                                                            1.0.0 Grammar
                                                                Variable Name
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(41, 45), match='true'>>> ws:None [1, 42 -> 1, 46]
                    ')' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=')'>>> ws:None [1, 46 -> 1, 47]
                    ':' <<Regex: <_sre.SRE_Match object; span=(46, 47), match=':'>>> ws:None [1, 47 -> 1, 48]
                    Newline+ <<47, 48>> ws:None [1, 48 -> 2, 1]
                    Indent <<48, 52, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(52, 56), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [3, 1 -> 3, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_TraditionalWithPositional():
    assert Execute(
        textwrap.dedent(
            """\
            int var Func1(int view a, /, bool var b):
                pass

            int var Func2(int view a, /):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 3), match='int'>>> ws:None [1, 1 -> 1, 4]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'var' <<Regex: <_sre.SRE_Match object; span=(4, 7), match='var'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    <name> <<Regex: <_sre.SRE_Match object; span=(8, 13), match='Func1'>>> ws:(7, 8) [1, 9 -> 1, 14]
                    '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [1, 14 -> 1, 15]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(14, 17), match='int'>>> ws:None [1, 15 -> 1, 18]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(18, 22), match='view'>>> ws:(17, 18) [1, 19 -> 1, 23]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(23, 24), match='a'>>> ws:(22, 23) [1, 24 -> 1, 25]
                                Repeat: (Comma and Parameter, 0, None)
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(24, 25), match=','>>> ws:None [1, 25 -> 1, 26]
                                        Or: [Parameter, '/', '*']
                                            '/' <<Regex: <_sre.SRE_Match object; span=(26, 27), match='/'>>> ws:(25, 26) [1, 27 -> 1, 28]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(27, 28), match=','>>> ws:None [1, 28 -> 1, 29]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(29, 33), match='bool'>>> ws:(28, 29) [1, 30 -> 1, 34]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(34, 37), match='var'>>> ws:(33, 34) [1, 35 -> 1, 38]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(38, 39), match='b'>>> ws:(37, 38) [1, 39 -> 1, 40]
                    ')' <<Regex: <_sre.SRE_Match object; span=(39, 40), match=')'>>> ws:None [1, 40 -> 1, 41]
                    ':' <<Regex: <_sre.SRE_Match object; span=(40, 41), match=':'>>> ws:None [1, 41 -> 1, 42]
                    Newline+ <<41, 42>> ws:None [1, 42 -> 2, 1]
                    Indent <<42, 46, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(46, 50), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(52, 55), match='int'>>> ws:None [4, 1 -> 4, 4]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'var' <<Regex: <_sre.SRE_Match object; span=(56, 59), match='var'>>> ws:(55, 56) [4, 5 -> 4, 8]
                    <name> <<Regex: <_sre.SRE_Match object; span=(60, 65), match='Func2'>>> ws:(59, 60) [4, 9 -> 4, 14]
                    '(' <<Regex: <_sre.SRE_Match object; span=(65, 66), match='('>>> ws:None [4, 14 -> 4, 15]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(66, 69), match='int'>>> ws:None [4, 15 -> 4, 18]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(70, 74), match='view'>>> ws:(69, 70) [4, 19 -> 4, 23]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(75, 76), match='a'>>> ws:(74, 75) [4, 24 -> 4, 25]
                                Repeat: (Comma and Parameter, 0, None)
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(76, 77), match=','>>> ws:None [4, 25 -> 4, 26]
                                        Or: [Parameter, '/', '*']
                                            '/' <<Regex: <_sre.SRE_Match object; span=(78, 79), match='/'>>> ws:(77, 78) [4, 27 -> 4, 28]
                    ')' <<Regex: <_sre.SRE_Match object; span=(79, 80), match=')'>>> ws:None [4, 28 -> 4, 29]
                    ':' <<Regex: <_sre.SRE_Match object; span=(80, 81), match=':'>>> ws:None [4, 29 -> 4, 30]
                    Newline+ <<81, 82>> ws:None [4, 30 -> 5, 1]
                    Indent <<82, 86, (4)>> ws:None [5, 1 -> 5, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(86, 90), match='pass'>>> ws:None [5, 5 -> 5, 9]
                    Dedent <<>> ws:None [6, 1 -> 6, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_TraditionalWithKeyword():
    assert Execute(
        textwrap.dedent(
            """\
            int var Func1(int view a, *, bool var b):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 3), match='int'>>> ws:None [1, 1 -> 1, 4]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'var' <<Regex: <_sre.SRE_Match object; span=(4, 7), match='var'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    <name> <<Regex: <_sre.SRE_Match object; span=(8, 13), match='Func1'>>> ws:(7, 8) [1, 9 -> 1, 14]
                    '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [1, 14 -> 1, 15]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(14, 17), match='int'>>> ws:None [1, 15 -> 1, 18]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(18, 22), match='view'>>> ws:(17, 18) [1, 19 -> 1, 23]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(23, 24), match='a'>>> ws:(22, 23) [1, 24 -> 1, 25]
                                Repeat: (Comma and Parameter, 0, None)
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(24, 25), match=','>>> ws:None [1, 25 -> 1, 26]
                                        Or: [Parameter, '/', '*']
                                            '*' <<Regex: <_sre.SRE_Match object; span=(26, 27), match='*'>>> ws:(25, 26) [1, 27 -> 1, 28]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(27, 28), match=','>>> ws:None [1, 28 -> 1, 29]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(29, 33), match='bool'>>> ws:(28, 29) [1, 30 -> 1, 34]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(34, 37), match='var'>>> ws:(33, 34) [1, 35 -> 1, 38]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(38, 39), match='b'>>> ws:(37, 38) [1, 39 -> 1, 40]
                    ')' <<Regex: <_sre.SRE_Match object; span=(39, 40), match=')'>>> ws:None [1, 40 -> 1, 41]
                    ':' <<Regex: <_sre.SRE_Match object; span=(40, 41), match=':'>>> ws:None [1, 41 -> 1, 42]
                    Newline+ <<41, 42>> ws:None [1, 42 -> 2, 1]
                    Indent <<42, 46, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(46, 50), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [3, 1 -> 3, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_TraditionalWithPositionalAndKeyword():
    assert Execute(
        textwrap.dedent(
            """\
            string view Func(int view a, /, int view b, *, int view c):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='string'>>> ws:None [1, 1 -> 1, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(7, 11), match='view'>>> ws:(6, 7) [1, 8 -> 1, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(12, 16), match='Func'>>> ws:(11, 12) [1, 13 -> 1, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(16, 17), match='('>>> ws:None [1, 17 -> 1, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(17, 20), match='int'>>> ws:None [1, 18 -> 1, 21]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(21, 25), match='view'>>> ws:(20, 21) [1, 22 -> 1, 26]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(26, 27), match='a'>>> ws:(25, 26) [1, 27 -> 1, 28]
                                Repeat: (Comma and Parameter, 0, None)
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(27, 28), match=','>>> ws:None [1, 28 -> 1, 29]
                                        Or: [Parameter, '/', '*']
                                            '/' <<Regex: <_sre.SRE_Match object; span=(29, 30), match='/'>>> ws:(28, 29) [1, 30 -> 1, 31]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(30, 31), match=','>>> ws:None [1, 31 -> 1, 32]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(32, 35), match='int'>>> ws:(31, 32) [1, 33 -> 1, 36]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'view' <<Regex: <_sre.SRE_Match object; span=(36, 40), match='view'>>> ws:(35, 36) [1, 37 -> 1, 41]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(41, 42), match='b'>>> ws:(40, 41) [1, 42 -> 1, 43]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(42, 43), match=','>>> ws:None [1, 43 -> 1, 44]
                                        Or: [Parameter, '/', '*']
                                            '*' <<Regex: <_sre.SRE_Match object; span=(44, 45), match='*'>>> ws:(43, 44) [1, 45 -> 1, 46]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=','>>> ws:None [1, 46 -> 1, 47]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(47, 50), match='int'>>> ws:(46, 47) [1, 48 -> 1, 51]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'view' <<Regex: <_sre.SRE_Match object; span=(51, 55), match='view'>>> ws:(50, 51) [1, 52 -> 1, 56]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(56, 57), match='c'>>> ws:(55, 56) [1, 57 -> 1, 58]
                    ')' <<Regex: <_sre.SRE_Match object; span=(57, 58), match=')'>>> ws:None [1, 58 -> 1, 59]
                    ':' <<Regex: <_sre.SRE_Match object; span=(58, 59), match=':'>>> ws:None [1, 59 -> 1, 60]
                    Newline+ <<59, 60>> ws:None [1, 60 -> 2, 1]
                    Indent <<60, 64, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(64, 68), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [3, 1 -> 3, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_NewPositional():
    assert Execute(
        textwrap.dedent(
            """\
            string ref Func1(pos: int view a, bool val b):
                pass

            string ref Func2(
                pos: int view a, bool val b
            ):
                pass

            string ref Func3(
                pos:
                    int view a,
                    bool val b,
            ):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='string'>>> ws:None [1, 1 -> 1, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'ref' <<Regex: <_sre.SRE_Match object; span=(7, 10), match='ref'>>> ws:(6, 7) [1, 8 -> 1, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(11, 16), match='Func1'>>> ws:(10, 11) [1, 12 -> 1, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(16, 17), match='('>>> ws:None [1, 17 -> 1, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(17, 20), match='pos'>>> ws:None [1, 18 -> 1, 21]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(20, 21), match=':'>>> ws:None [1, 21 -> 1, 22]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(22, 25), match='int'>>> ws:(21, 22) [1, 23 -> 1, 26]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(26, 30), match='view'>>> ws:(25, 26) [1, 27 -> 1, 31]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='a'>>> ws:(30, 31) [1, 32 -> 1, 33]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=','>>> ws:None [1, 33 -> 1, 34]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(34, 38), match='bool'>>> ws:(33, 34) [1, 35 -> 1, 39]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(39, 42), match='val'>>> ws:(38, 39) [1, 40 -> 1, 43]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(43, 44), match='b'>>> ws:(42, 43) [1, 44 -> 1, 45]
                    ')' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=')'>>> ws:None [1, 45 -> 1, 46]
                    ':' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=':'>>> ws:None [1, 46 -> 1, 47]
                    Newline+ <<46, 47>> ws:None [1, 47 -> 2, 1]
                    Indent <<47, 51, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(51, 55), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(57, 63), match='string'>>> ws:None [4, 1 -> 4, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'ref' <<Regex: <_sre.SRE_Match object; span=(64, 67), match='ref'>>> ws:(63, 64) [4, 8 -> 4, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(68, 73), match='Func2'>>> ws:(67, 68) [4, 12 -> 4, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(73, 74), match='('>>> ws:None [4, 17 -> 4, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(79, 82), match='pos'>>> ws:None [5, 5 -> 5, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(82, 83), match=':'>>> ws:None [5, 8 -> 5, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(84, 87), match='int'>>> ws:(83, 84) [5, 10 -> 5, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(88, 92), match='view'>>> ws:(87, 88) [5, 14 -> 5, 18]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(93, 94), match='a'>>> ws:(92, 93) [5, 19 -> 5, 20]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(94, 95), match=','>>> ws:None [5, 20 -> 5, 21]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(96, 100), match='bool'>>> ws:(95, 96) [5, 22 -> 5, 26]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(101, 104), match='val'>>> ws:(100, 101) [5, 27 -> 5, 30]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(105, 106), match='b'>>> ws:(104, 105) [5, 31 -> 5, 32]
                    ')' <<Regex: <_sre.SRE_Match object; span=(107, 108), match=')'>>> ws:None [6, 1 -> 6, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(108, 109), match=':'>>> ws:None [6, 2 -> 6, 3]
                    Newline+ <<109, 110>> ws:None [6, 3 -> 7, 1]
                    Indent <<110, 114, (4)>> ws:None [7, 1 -> 7, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(114, 118), match='pass'>>> ws:None [7, 5 -> 7, 9]
                    Dedent <<>> ws:None [9, 1 -> 9, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(120, 126), match='string'>>> ws:None [9, 1 -> 9, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'ref' <<Regex: <_sre.SRE_Match object; span=(127, 130), match='ref'>>> ws:(126, 127) [9, 8 -> 9, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(131, 136), match='Func3'>>> ws:(130, 131) [9, 12 -> 9, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(136, 137), match='('>>> ws:None [9, 17 -> 9, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(142, 145), match='pos'>>> ws:None [10, 5 -> 10, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(145, 146), match=':'>>> ws:None [10, 8 -> 10, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(155, 158), match='int'>>> ws:None [11, 9 -> 11, 12]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(159, 163), match='view'>>> ws:(158, 159) [11, 13 -> 11, 17]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(164, 165), match='a'>>> ws:(163, 164) [11, 18 -> 11, 19]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(165, 166), match=','>>> ws:None [11, 19 -> 11, 20]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(175, 179), match='bool'>>> ws:None [12, 9 -> 12, 13]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(180, 183), match='val'>>> ws:(179, 180) [12, 14 -> 12, 17]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(184, 185), match='b'>>> ws:(183, 184) [12, 18 -> 12, 19]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(185, 186), match=','>>> ws:None [12, 19 -> 12, 20]
                    ')' <<Regex: <_sre.SRE_Match object; span=(187, 188), match=')'>>> ws:None [13, 1 -> 13, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(188, 189), match=':'>>> ws:None [13, 2 -> 13, 3]
                    Newline+ <<189, 190>> ws:None [13, 3 -> 14, 1]
                    Indent <<190, 194, (4)>> ws:None [14, 1 -> 14, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(194, 198), match='pass'>>> ws:None [14, 5 -> 14, 9]
                    Dedent <<>> ws:None [15, 1 -> 15, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_NewAny():
    assert Execute(
        textwrap.dedent(
            """\
            string ref Func1(any: int view a, bool val b):
                pass

            string ref Func2(
                any: int view a, bool val b
            ):
                pass

            string ref Func3(
                any:
                    int view a,
                    bool val b,
            ):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='string'>>> ws:None [1, 1 -> 1, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'ref' <<Regex: <_sre.SRE_Match object; span=(7, 10), match='ref'>>> ws:(6, 7) [1, 8 -> 1, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(11, 16), match='Func1'>>> ws:(10, 11) [1, 12 -> 1, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(16, 17), match='('>>> ws:None [1, 17 -> 1, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(17, 20), match='any'>>> ws:None [1, 18 -> 1, 21]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(20, 21), match=':'>>> ws:None [1, 21 -> 1, 22]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(22, 25), match='int'>>> ws:(21, 22) [1, 23 -> 1, 26]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(26, 30), match='view'>>> ws:(25, 26) [1, 27 -> 1, 31]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='a'>>> ws:(30, 31) [1, 32 -> 1, 33]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=','>>> ws:None [1, 33 -> 1, 34]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(34, 38), match='bool'>>> ws:(33, 34) [1, 35 -> 1, 39]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(39, 42), match='val'>>> ws:(38, 39) [1, 40 -> 1, 43]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(43, 44), match='b'>>> ws:(42, 43) [1, 44 -> 1, 45]
                    ')' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=')'>>> ws:None [1, 45 -> 1, 46]
                    ':' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=':'>>> ws:None [1, 46 -> 1, 47]
                    Newline+ <<46, 47>> ws:None [1, 47 -> 2, 1]
                    Indent <<47, 51, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(51, 55), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(57, 63), match='string'>>> ws:None [4, 1 -> 4, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'ref' <<Regex: <_sre.SRE_Match object; span=(64, 67), match='ref'>>> ws:(63, 64) [4, 8 -> 4, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(68, 73), match='Func2'>>> ws:(67, 68) [4, 12 -> 4, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(73, 74), match='('>>> ws:None [4, 17 -> 4, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(79, 82), match='any'>>> ws:None [5, 5 -> 5, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(82, 83), match=':'>>> ws:None [5, 8 -> 5, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(84, 87), match='int'>>> ws:(83, 84) [5, 10 -> 5, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(88, 92), match='view'>>> ws:(87, 88) [5, 14 -> 5, 18]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(93, 94), match='a'>>> ws:(92, 93) [5, 19 -> 5, 20]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(94, 95), match=','>>> ws:None [5, 20 -> 5, 21]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(96, 100), match='bool'>>> ws:(95, 96) [5, 22 -> 5, 26]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(101, 104), match='val'>>> ws:(100, 101) [5, 27 -> 5, 30]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(105, 106), match='b'>>> ws:(104, 105) [5, 31 -> 5, 32]
                    ')' <<Regex: <_sre.SRE_Match object; span=(107, 108), match=')'>>> ws:None [6, 1 -> 6, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(108, 109), match=':'>>> ws:None [6, 2 -> 6, 3]
                    Newline+ <<109, 110>> ws:None [6, 3 -> 7, 1]
                    Indent <<110, 114, (4)>> ws:None [7, 1 -> 7, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(114, 118), match='pass'>>> ws:None [7, 5 -> 7, 9]
                    Dedent <<>> ws:None [9, 1 -> 9, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(120, 126), match='string'>>> ws:None [9, 1 -> 9, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'ref' <<Regex: <_sre.SRE_Match object; span=(127, 130), match='ref'>>> ws:(126, 127) [9, 8 -> 9, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(131, 136), match='Func3'>>> ws:(130, 131) [9, 12 -> 9, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(136, 137), match='('>>> ws:None [9, 17 -> 9, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(142, 145), match='any'>>> ws:None [10, 5 -> 10, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(145, 146), match=':'>>> ws:None [10, 8 -> 10, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(155, 158), match='int'>>> ws:None [11, 9 -> 11, 12]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(159, 163), match='view'>>> ws:(158, 159) [11, 13 -> 11, 17]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(164, 165), match='a'>>> ws:(163, 164) [11, 18 -> 11, 19]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(165, 166), match=','>>> ws:None [11, 19 -> 11, 20]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(175, 179), match='bool'>>> ws:None [12, 9 -> 12, 13]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(180, 183), match='val'>>> ws:(179, 180) [12, 14 -> 12, 17]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(184, 185), match='b'>>> ws:(183, 184) [12, 18 -> 12, 19]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(185, 186), match=','>>> ws:None [12, 19 -> 12, 20]
                    ')' <<Regex: <_sre.SRE_Match object; span=(187, 188), match=')'>>> ws:None [13, 1 -> 13, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(188, 189), match=':'>>> ws:None [13, 2 -> 13, 3]
                    Newline+ <<189, 190>> ws:None [13, 3 -> 14, 1]
                    Indent <<190, 194, (4)>> ws:None [14, 1 -> 14, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(194, 198), match='pass'>>> ws:None [14, 5 -> 14, 9]
                    Dedent <<>> ws:None [15, 1 -> 15, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_NewKey():
    assert Execute(
        textwrap.dedent(
            """\
            string ref Func1(key: int view a, bool val b):
                pass

            string ref Func2(
                key: int view a, bool val b
            ):
                pass

            string ref Func3(
                key:
                    int view a,
                    bool val b,
            ):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='string'>>> ws:None [1, 1 -> 1, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'ref' <<Regex: <_sre.SRE_Match object; span=(7, 10), match='ref'>>> ws:(6, 7) [1, 8 -> 1, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(11, 16), match='Func1'>>> ws:(10, 11) [1, 12 -> 1, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(16, 17), match='('>>> ws:None [1, 17 -> 1, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(17, 20), match='key'>>> ws:None [1, 18 -> 1, 21]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(20, 21), match=':'>>> ws:None [1, 21 -> 1, 22]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(22, 25), match='int'>>> ws:(21, 22) [1, 23 -> 1, 26]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(26, 30), match='view'>>> ws:(25, 26) [1, 27 -> 1, 31]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='a'>>> ws:(30, 31) [1, 32 -> 1, 33]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=','>>> ws:None [1, 33 -> 1, 34]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(34, 38), match='bool'>>> ws:(33, 34) [1, 35 -> 1, 39]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(39, 42), match='val'>>> ws:(38, 39) [1, 40 -> 1, 43]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(43, 44), match='b'>>> ws:(42, 43) [1, 44 -> 1, 45]
                    ')' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=')'>>> ws:None [1, 45 -> 1, 46]
                    ':' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=':'>>> ws:None [1, 46 -> 1, 47]
                    Newline+ <<46, 47>> ws:None [1, 47 -> 2, 1]
                    Indent <<47, 51, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(51, 55), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(57, 63), match='string'>>> ws:None [4, 1 -> 4, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'ref' <<Regex: <_sre.SRE_Match object; span=(64, 67), match='ref'>>> ws:(63, 64) [4, 8 -> 4, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(68, 73), match='Func2'>>> ws:(67, 68) [4, 12 -> 4, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(73, 74), match='('>>> ws:None [4, 17 -> 4, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(79, 82), match='key'>>> ws:None [5, 5 -> 5, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(82, 83), match=':'>>> ws:None [5, 8 -> 5, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(84, 87), match='int'>>> ws:(83, 84) [5, 10 -> 5, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(88, 92), match='view'>>> ws:(87, 88) [5, 14 -> 5, 18]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(93, 94), match='a'>>> ws:(92, 93) [5, 19 -> 5, 20]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(94, 95), match=','>>> ws:None [5, 20 -> 5, 21]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(96, 100), match='bool'>>> ws:(95, 96) [5, 22 -> 5, 26]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(101, 104), match='val'>>> ws:(100, 101) [5, 27 -> 5, 30]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(105, 106), match='b'>>> ws:(104, 105) [5, 31 -> 5, 32]
                    ')' <<Regex: <_sre.SRE_Match object; span=(107, 108), match=')'>>> ws:None [6, 1 -> 6, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(108, 109), match=':'>>> ws:None [6, 2 -> 6, 3]
                    Newline+ <<109, 110>> ws:None [6, 3 -> 7, 1]
                    Indent <<110, 114, (4)>> ws:None [7, 1 -> 7, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(114, 118), match='pass'>>> ws:None [7, 5 -> 7, 9]
                    Dedent <<>> ws:None [9, 1 -> 9, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(120, 126), match='string'>>> ws:None [9, 1 -> 9, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'ref' <<Regex: <_sre.SRE_Match object; span=(127, 130), match='ref'>>> ws:(126, 127) [9, 8 -> 9, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(131, 136), match='Func3'>>> ws:(130, 131) [9, 12 -> 9, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(136, 137), match='('>>> ws:None [9, 17 -> 9, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(142, 145), match='key'>>> ws:None [10, 5 -> 10, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(145, 146), match=':'>>> ws:None [10, 8 -> 10, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(155, 158), match='int'>>> ws:None [11, 9 -> 11, 12]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(159, 163), match='view'>>> ws:(158, 159) [11, 13 -> 11, 17]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(164, 165), match='a'>>> ws:(163, 164) [11, 18 -> 11, 19]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(165, 166), match=','>>> ws:None [11, 19 -> 11, 20]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(175, 179), match='bool'>>> ws:None [12, 9 -> 12, 13]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(180, 183), match='val'>>> ws:(179, 180) [12, 14 -> 12, 17]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(184, 185), match='b'>>> ws:(183, 184) [12, 18 -> 12, 19]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(185, 186), match=','>>> ws:None [12, 19 -> 12, 20]
                    ')' <<Regex: <_sre.SRE_Match object; span=(187, 188), match=')'>>> ws:None [13, 1 -> 13, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(188, 189), match=':'>>> ws:None [13, 2 -> 13, 3]
                    Newline+ <<189, 190>> ws:None [13, 3 -> 14, 1]
                    Indent <<190, 194, (4)>> ws:None [14, 1 -> 14, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(194, 198), match='pass'>>> ws:None [14, 5 -> 14, 9]
                    Dedent <<>> ws:None [15, 1 -> 15, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_NewPosAndAny():
    assert Execute(
        textwrap.dedent(
            """\
            string view Func1(pos: int val a, bool var b, any: char view c):
                pass

            string view Func2(
                pos: int val a, bool var b
                any: char view c
            ):
                pass

            string view Func3(
                pos:
                    int val a,
                    bool var b,
                any:
                    char view c,
            ):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='string'>>> ws:None [1, 1 -> 1, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(7, 11), match='view'>>> ws:(6, 7) [1, 8 -> 1, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(12, 17), match='Func1'>>> ws:(11, 12) [1, 13 -> 1, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(17, 18), match='('>>> ws:None [1, 18 -> 1, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(18, 21), match='pos'>>> ws:None [1, 19 -> 1, 22]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(21, 22), match=':'>>> ws:None [1, 22 -> 1, 23]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(23, 26), match='int'>>> ws:(22, 23) [1, 24 -> 1, 27]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(27, 30), match='val'>>> ws:(26, 27) [1, 28 -> 1, 31]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='a'>>> ws:(30, 31) [1, 32 -> 1, 33]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=','>>> ws:None [1, 33 -> 1, 34]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(34, 38), match='bool'>>> ws:(33, 34) [1, 35 -> 1, 39]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(39, 42), match='var'>>> ws:(38, 39) [1, 40 -> 1, 43]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(43, 44), match='b'>>> ws:(42, 43) [1, 44 -> 1, 45]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=','>>> ws:None [1, 45 -> 1, 46]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(46, 49), match='any'>>> ws:(45, 46) [1, 47 -> 1, 50]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(49, 50), match=':'>>> ws:None [1, 50 -> 1, 51]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(51, 55), match='char'>>> ws:(50, 51) [1, 52 -> 1, 56]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(56, 60), match='view'>>> ws:(55, 56) [1, 57 -> 1, 61]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(61, 62), match='c'>>> ws:(60, 61) [1, 62 -> 1, 63]
                    ')' <<Regex: <_sre.SRE_Match object; span=(62, 63), match=')'>>> ws:None [1, 63 -> 1, 64]
                    ':' <<Regex: <_sre.SRE_Match object; span=(63, 64), match=':'>>> ws:None [1, 64 -> 1, 65]
                    Newline+ <<64, 65>> ws:None [1, 65 -> 2, 1]
                    Indent <<65, 69, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(69, 73), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(75, 81), match='string'>>> ws:None [4, 1 -> 4, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(82, 86), match='view'>>> ws:(81, 82) [4, 8 -> 4, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(87, 92), match='Func2'>>> ws:(86, 87) [4, 13 -> 4, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(92, 93), match='('>>> ws:None [4, 18 -> 4, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(98, 101), match='pos'>>> ws:None [5, 5 -> 5, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(101, 102), match=':'>>> ws:None [5, 8 -> 5, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(103, 106), match='int'>>> ws:(102, 103) [5, 10 -> 5, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(107, 110), match='val'>>> ws:(106, 107) [5, 14 -> 5, 17]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(111, 112), match='a'>>> ws:(110, 111) [5, 18 -> 5, 19]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(112, 113), match=','>>> ws:None [5, 19 -> 5, 20]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(114, 118), match='bool'>>> ws:(113, 114) [5, 21 -> 5, 25]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(119, 122), match='var'>>> ws:(118, 119) [5, 26 -> 5, 29]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(123, 124), match='b'>>> ws:(122, 123) [5, 30 -> 5, 31]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(129, 132), match='any'>>> ws:None [6, 5 -> 6, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(132, 133), match=':'>>> ws:None [6, 8 -> 6, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(134, 138), match='char'>>> ws:(133, 134) [6, 10 -> 6, 14]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(139, 143), match='view'>>> ws:(138, 139) [6, 15 -> 6, 19]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(144, 145), match='c'>>> ws:(143, 144) [6, 20 -> 6, 21]
                    ')' <<Regex: <_sre.SRE_Match object; span=(146, 147), match=')'>>> ws:None [7, 1 -> 7, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(147, 148), match=':'>>> ws:None [7, 2 -> 7, 3]
                    Newline+ <<148, 149>> ws:None [7, 3 -> 8, 1]
                    Indent <<149, 153, (4)>> ws:None [8, 1 -> 8, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(153, 157), match='pass'>>> ws:None [8, 5 -> 8, 9]
                    Dedent <<>> ws:None [10, 1 -> 10, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(159, 165), match='string'>>> ws:None [10, 1 -> 10, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(166, 170), match='view'>>> ws:(165, 166) [10, 8 -> 10, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(171, 176), match='Func3'>>> ws:(170, 171) [10, 13 -> 10, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(176, 177), match='('>>> ws:None [10, 18 -> 10, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(182, 185), match='pos'>>> ws:None [11, 5 -> 11, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(185, 186), match=':'>>> ws:None [11, 8 -> 11, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(195, 198), match='int'>>> ws:None [12, 9 -> 12, 12]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(199, 202), match='val'>>> ws:(198, 199) [12, 13 -> 12, 16]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(203, 204), match='a'>>> ws:(202, 203) [12, 17 -> 12, 18]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(204, 205), match=','>>> ws:None [12, 18 -> 12, 19]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(214, 218), match='bool'>>> ws:None [13, 9 -> 13, 13]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(219, 222), match='var'>>> ws:(218, 219) [13, 14 -> 13, 17]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(223, 224), match='b'>>> ws:(222, 223) [13, 18 -> 13, 19]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(224, 225), match=','>>> ws:None [13, 19 -> 13, 20]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(230, 233), match='any'>>> ws:None [14, 5 -> 14, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(233, 234), match=':'>>> ws:None [14, 8 -> 14, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(243, 247), match='char'>>> ws:None [15, 9 -> 15, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(248, 252), match='view'>>> ws:(247, 248) [15, 14 -> 15, 18]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(253, 254), match='c'>>> ws:(252, 253) [15, 19 -> 15, 20]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(254, 255), match=','>>> ws:None [15, 20 -> 15, 21]
                    ')' <<Regex: <_sre.SRE_Match object; span=(256, 257), match=')'>>> ws:None [16, 1 -> 16, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(257, 258), match=':'>>> ws:None [16, 2 -> 16, 3]
                    Newline+ <<258, 259>> ws:None [16, 3 -> 17, 1]
                    Indent <<259, 263, (4)>> ws:None [17, 1 -> 17, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(263, 267), match='pass'>>> ws:None [17, 5 -> 17, 9]
                    Dedent <<>> ws:None [18, 1 -> 18, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_NewPosAndKey():
    assert Execute(
        textwrap.dedent(
            """\
            string view Func1(pos: int val a, bool var b, key: char view c):
                pass

            string view Func2(
                pos: int val a, bool var b
                key: char view c
            ):
                pass

            string view Func3(
                pos:
                    int val a,
                    bool var b,
                key:
                    char view c,
            ):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='string'>>> ws:None [1, 1 -> 1, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(7, 11), match='view'>>> ws:(6, 7) [1, 8 -> 1, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(12, 17), match='Func1'>>> ws:(11, 12) [1, 13 -> 1, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(17, 18), match='('>>> ws:None [1, 18 -> 1, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(18, 21), match='pos'>>> ws:None [1, 19 -> 1, 22]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(21, 22), match=':'>>> ws:None [1, 22 -> 1, 23]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(23, 26), match='int'>>> ws:(22, 23) [1, 24 -> 1, 27]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(27, 30), match='val'>>> ws:(26, 27) [1, 28 -> 1, 31]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='a'>>> ws:(30, 31) [1, 32 -> 1, 33]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=','>>> ws:None [1, 33 -> 1, 34]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(34, 38), match='bool'>>> ws:(33, 34) [1, 35 -> 1, 39]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(39, 42), match='var'>>> ws:(38, 39) [1, 40 -> 1, 43]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(43, 44), match='b'>>> ws:(42, 43) [1, 44 -> 1, 45]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=','>>> ws:None [1, 45 -> 1, 46]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(46, 49), match='key'>>> ws:(45, 46) [1, 47 -> 1, 50]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(49, 50), match=':'>>> ws:None [1, 50 -> 1, 51]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(51, 55), match='char'>>> ws:(50, 51) [1, 52 -> 1, 56]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(56, 60), match='view'>>> ws:(55, 56) [1, 57 -> 1, 61]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(61, 62), match='c'>>> ws:(60, 61) [1, 62 -> 1, 63]
                    ')' <<Regex: <_sre.SRE_Match object; span=(62, 63), match=')'>>> ws:None [1, 63 -> 1, 64]
                    ':' <<Regex: <_sre.SRE_Match object; span=(63, 64), match=':'>>> ws:None [1, 64 -> 1, 65]
                    Newline+ <<64, 65>> ws:None [1, 65 -> 2, 1]
                    Indent <<65, 69, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(69, 73), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(75, 81), match='string'>>> ws:None [4, 1 -> 4, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(82, 86), match='view'>>> ws:(81, 82) [4, 8 -> 4, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(87, 92), match='Func2'>>> ws:(86, 87) [4, 13 -> 4, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(92, 93), match='('>>> ws:None [4, 18 -> 4, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(98, 101), match='pos'>>> ws:None [5, 5 -> 5, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(101, 102), match=':'>>> ws:None [5, 8 -> 5, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(103, 106), match='int'>>> ws:(102, 103) [5, 10 -> 5, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(107, 110), match='val'>>> ws:(106, 107) [5, 14 -> 5, 17]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(111, 112), match='a'>>> ws:(110, 111) [5, 18 -> 5, 19]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(112, 113), match=','>>> ws:None [5, 19 -> 5, 20]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(114, 118), match='bool'>>> ws:(113, 114) [5, 21 -> 5, 25]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(119, 122), match='var'>>> ws:(118, 119) [5, 26 -> 5, 29]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(123, 124), match='b'>>> ws:(122, 123) [5, 30 -> 5, 31]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(129, 132), match='key'>>> ws:None [6, 5 -> 6, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(132, 133), match=':'>>> ws:None [6, 8 -> 6, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(134, 138), match='char'>>> ws:(133, 134) [6, 10 -> 6, 14]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(139, 143), match='view'>>> ws:(138, 139) [6, 15 -> 6, 19]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(144, 145), match='c'>>> ws:(143, 144) [6, 20 -> 6, 21]
                    ')' <<Regex: <_sre.SRE_Match object; span=(146, 147), match=')'>>> ws:None [7, 1 -> 7, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(147, 148), match=':'>>> ws:None [7, 2 -> 7, 3]
                    Newline+ <<148, 149>> ws:None [7, 3 -> 8, 1]
                    Indent <<149, 153, (4)>> ws:None [8, 1 -> 8, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(153, 157), match='pass'>>> ws:None [8, 5 -> 8, 9]
                    Dedent <<>> ws:None [10, 1 -> 10, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(159, 165), match='string'>>> ws:None [10, 1 -> 10, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(166, 170), match='view'>>> ws:(165, 166) [10, 8 -> 10, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(171, 176), match='Func3'>>> ws:(170, 171) [10, 13 -> 10, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(176, 177), match='('>>> ws:None [10, 18 -> 10, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(182, 185), match='pos'>>> ws:None [11, 5 -> 11, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(185, 186), match=':'>>> ws:None [11, 8 -> 11, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(195, 198), match='int'>>> ws:None [12, 9 -> 12, 12]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(199, 202), match='val'>>> ws:(198, 199) [12, 13 -> 12, 16]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(203, 204), match='a'>>> ws:(202, 203) [12, 17 -> 12, 18]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(204, 205), match=','>>> ws:None [12, 18 -> 12, 19]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(214, 218), match='bool'>>> ws:None [13, 9 -> 13, 13]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(219, 222), match='var'>>> ws:(218, 219) [13, 14 -> 13, 17]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(223, 224), match='b'>>> ws:(222, 223) [13, 18 -> 13, 19]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(224, 225), match=','>>> ws:None [13, 19 -> 13, 20]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(230, 233), match='key'>>> ws:None [14, 5 -> 14, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(233, 234), match=':'>>> ws:None [14, 8 -> 14, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(243, 247), match='char'>>> ws:None [15, 9 -> 15, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(248, 252), match='view'>>> ws:(247, 248) [15, 14 -> 15, 18]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(253, 254), match='c'>>> ws:(252, 253) [15, 19 -> 15, 20]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(254, 255), match=','>>> ws:None [15, 20 -> 15, 21]
                    ')' <<Regex: <_sre.SRE_Match object; span=(256, 257), match=')'>>> ws:None [16, 1 -> 16, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(257, 258), match=':'>>> ws:None [16, 2 -> 16, 3]
                    Newline+ <<258, 259>> ws:None [16, 3 -> 17, 1]
                    Indent <<259, 263, (4)>> ws:None [17, 1 -> 17, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(263, 267), match='pass'>>> ws:None [17, 5 -> 17, 9]
                    Dedent <<>> ws:None [18, 1 -> 18, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_NewAnyAndKey():
    assert Execute(
        textwrap.dedent(
            """\
            string view Func1(any: int val a, bool var b, key: char view c):
                pass

            string view Func2(
                any: int val a, bool var b
                key: char view c
            ):
                pass

            string view Func3(
                any:
                    int val a,
                    bool var b,
                key:
                    char view c,
            ):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='string'>>> ws:None [1, 1 -> 1, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(7, 11), match='view'>>> ws:(6, 7) [1, 8 -> 1, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(12, 17), match='Func1'>>> ws:(11, 12) [1, 13 -> 1, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(17, 18), match='('>>> ws:None [1, 18 -> 1, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(18, 21), match='any'>>> ws:None [1, 19 -> 1, 22]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(21, 22), match=':'>>> ws:None [1, 22 -> 1, 23]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(23, 26), match='int'>>> ws:(22, 23) [1, 24 -> 1, 27]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(27, 30), match='val'>>> ws:(26, 27) [1, 28 -> 1, 31]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='a'>>> ws:(30, 31) [1, 32 -> 1, 33]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=','>>> ws:None [1, 33 -> 1, 34]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(34, 38), match='bool'>>> ws:(33, 34) [1, 35 -> 1, 39]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(39, 42), match='var'>>> ws:(38, 39) [1, 40 -> 1, 43]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(43, 44), match='b'>>> ws:(42, 43) [1, 44 -> 1, 45]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=','>>> ws:None [1, 45 -> 1, 46]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(46, 49), match='key'>>> ws:(45, 46) [1, 47 -> 1, 50]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(49, 50), match=':'>>> ws:None [1, 50 -> 1, 51]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(51, 55), match='char'>>> ws:(50, 51) [1, 52 -> 1, 56]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(56, 60), match='view'>>> ws:(55, 56) [1, 57 -> 1, 61]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(61, 62), match='c'>>> ws:(60, 61) [1, 62 -> 1, 63]
                    ')' <<Regex: <_sre.SRE_Match object; span=(62, 63), match=')'>>> ws:None [1, 63 -> 1, 64]
                    ':' <<Regex: <_sre.SRE_Match object; span=(63, 64), match=':'>>> ws:None [1, 64 -> 1, 65]
                    Newline+ <<64, 65>> ws:None [1, 65 -> 2, 1]
                    Indent <<65, 69, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(69, 73), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(75, 81), match='string'>>> ws:None [4, 1 -> 4, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(82, 86), match='view'>>> ws:(81, 82) [4, 8 -> 4, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(87, 92), match='Func2'>>> ws:(86, 87) [4, 13 -> 4, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(92, 93), match='('>>> ws:None [4, 18 -> 4, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(98, 101), match='any'>>> ws:None [5, 5 -> 5, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(101, 102), match=':'>>> ws:None [5, 8 -> 5, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(103, 106), match='int'>>> ws:(102, 103) [5, 10 -> 5, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(107, 110), match='val'>>> ws:(106, 107) [5, 14 -> 5, 17]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(111, 112), match='a'>>> ws:(110, 111) [5, 18 -> 5, 19]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(112, 113), match=','>>> ws:None [5, 19 -> 5, 20]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(114, 118), match='bool'>>> ws:(113, 114) [5, 21 -> 5, 25]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(119, 122), match='var'>>> ws:(118, 119) [5, 26 -> 5, 29]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(123, 124), match='b'>>> ws:(122, 123) [5, 30 -> 5, 31]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(129, 132), match='key'>>> ws:None [6, 5 -> 6, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(132, 133), match=':'>>> ws:None [6, 8 -> 6, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(134, 138), match='char'>>> ws:(133, 134) [6, 10 -> 6, 14]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(139, 143), match='view'>>> ws:(138, 139) [6, 15 -> 6, 19]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(144, 145), match='c'>>> ws:(143, 144) [6, 20 -> 6, 21]
                    ')' <<Regex: <_sre.SRE_Match object; span=(146, 147), match=')'>>> ws:None [7, 1 -> 7, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(147, 148), match=':'>>> ws:None [7, 2 -> 7, 3]
                    Newline+ <<148, 149>> ws:None [7, 3 -> 8, 1]
                    Indent <<149, 153, (4)>> ws:None [8, 1 -> 8, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(153, 157), match='pass'>>> ws:None [8, 5 -> 8, 9]
                    Dedent <<>> ws:None [10, 1 -> 10, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(159, 165), match='string'>>> ws:None [10, 1 -> 10, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'view' <<Regex: <_sre.SRE_Match object; span=(166, 170), match='view'>>> ws:(165, 166) [10, 8 -> 10, 12]
                    <name> <<Regex: <_sre.SRE_Match object; span=(171, 176), match='Func3'>>> ws:(170, 171) [10, 13 -> 10, 18]
                    '(' <<Regex: <_sre.SRE_Match object; span=(176, 177), match='('>>> ws:None [10, 18 -> 10, 19]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(182, 185), match='any'>>> ws:None [11, 5 -> 11, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(185, 186), match=':'>>> ws:None [11, 8 -> 11, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(195, 198), match='int'>>> ws:None [12, 9 -> 12, 12]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(199, 202), match='val'>>> ws:(198, 199) [12, 13 -> 12, 16]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(203, 204), match='a'>>> ws:(202, 203) [12, 17 -> 12, 18]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(204, 205), match=','>>> ws:None [12, 18 -> 12, 19]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(214, 218), match='bool'>>> ws:None [13, 9 -> 13, 13]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'var' <<Regex: <_sre.SRE_Match object; span=(219, 222), match='var'>>> ws:(218, 219) [13, 14 -> 13, 17]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(223, 224), match='b'>>> ws:(222, 223) [13, 18 -> 13, 19]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(224, 225), match=','>>> ws:None [13, 19 -> 13, 20]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(230, 233), match='key'>>> ws:None [14, 5 -> 14, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(233, 234), match=':'>>> ws:None [14, 8 -> 14, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(243, 247), match='char'>>> ws:None [15, 9 -> 15, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'view' <<Regex: <_sre.SRE_Match object; span=(248, 252), match='view'>>> ws:(247, 248) [15, 14 -> 15, 18]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(253, 254), match='c'>>> ws:(252, 253) [15, 19 -> 15, 20]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(254, 255), match=','>>> ws:None [15, 20 -> 15, 21]
                    ')' <<Regex: <_sre.SRE_Match object; span=(256, 257), match=')'>>> ws:None [16, 1 -> 16, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(257, 258), match=':'>>> ws:None [16, 2 -> 16, 3]
                    Newline+ <<258, 259>> ws:None [16, 3 -> 17, 1]
                    Indent <<259, 263, (4)>> ws:None [17, 1 -> 17, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(263, 267), match='pass'>>> ws:None [17, 5 -> 17, 9]
                    Dedent <<>> ws:None [18, 1 -> 18, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_NewPosAnyAndKey():
    assert Execute(
        textwrap.dedent(
            """\
            string val Func1(pos: int val a, bool val b, any: char val c, double val d, enum val e, key: float val f, good val g):
                pass

            string val Func2(
                pos: int val a, bool val b,
                any: char val c, double val d, enum val e,
                key: float val f, good val g,
            ):
                pass

            string val Func3(
                pos:
                    int val a,
                    bool val b,
                any:
                    char val c,
                    double val d,
                    enum val e,
                key:
                    float val f,
                    good val g,
            ):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='string'>>> ws:None [1, 1 -> 1, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(7, 10), match='val'>>> ws:(6, 7) [1, 8 -> 1, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(11, 16), match='Func1'>>> ws:(10, 11) [1, 12 -> 1, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(16, 17), match='('>>> ws:None [1, 17 -> 1, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(17, 20), match='pos'>>> ws:None [1, 18 -> 1, 21]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(20, 21), match=':'>>> ws:None [1, 21 -> 1, 22]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(22, 25), match='int'>>> ws:(21, 22) [1, 23 -> 1, 26]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(26, 29), match='val'>>> ws:(25, 26) [1, 27 -> 1, 30]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(30, 31), match='a'>>> ws:(29, 30) [1, 31 -> 1, 32]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(31, 32), match=','>>> ws:None [1, 32 -> 1, 33]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(33, 37), match='bool'>>> ws:(32, 33) [1, 34 -> 1, 38]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(38, 41), match='val'>>> ws:(37, 38) [1, 39 -> 1, 42]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(42, 43), match='b'>>> ws:(41, 42) [1, 43 -> 1, 44]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(43, 44), match=','>>> ws:None [1, 44 -> 1, 45]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(45, 48), match='any'>>> ws:(44, 45) [1, 46 -> 1, 49]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(48, 49), match=':'>>> ws:None [1, 49 -> 1, 50]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(50, 54), match='char'>>> ws:(49, 50) [1, 51 -> 1, 55]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(55, 58), match='val'>>> ws:(54, 55) [1, 56 -> 1, 59]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(59, 60), match='c'>>> ws:(58, 59) [1, 60 -> 1, 61]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(60, 61), match=','>>> ws:None [1, 61 -> 1, 62]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(62, 68), match='double'>>> ws:(61, 62) [1, 63 -> 1, 69]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(69, 72), match='val'>>> ws:(68, 69) [1, 70 -> 1, 73]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(73, 74), match='d'>>> ws:(72, 73) [1, 74 -> 1, 75]
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(74, 75), match=','>>> ws:None [1, 75 -> 1, 76]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(76, 80), match='enum'>>> ws:(75, 76) [1, 77 -> 1, 81]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(81, 84), match='val'>>> ws:(80, 81) [1, 82 -> 1, 85]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(85, 86), match='e'>>> ws:(84, 85) [1, 86 -> 1, 87]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(86, 87), match=','>>> ws:None [1, 87 -> 1, 88]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(88, 91), match='key'>>> ws:(87, 88) [1, 89 -> 1, 92]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(91, 92), match=':'>>> ws:None [1, 92 -> 1, 93]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(93, 98), match='float'>>> ws:(92, 93) [1, 94 -> 1, 99]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(99, 102), match='val'>>> ws:(98, 99) [1, 100 -> 1, 103]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(103, 104), match='f'>>> ws:(102, 103) [1, 104 -> 1, 105]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(104, 105), match=','>>> ws:None [1, 105 -> 1, 106]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(106, 110), match='good'>>> ws:(105, 106) [1, 107 -> 1, 111]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(111, 114), match='val'>>> ws:(110, 111) [1, 112 -> 1, 115]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(115, 116), match='g'>>> ws:(114, 115) [1, 116 -> 1, 117]
                    ')' <<Regex: <_sre.SRE_Match object; span=(116, 117), match=')'>>> ws:None [1, 117 -> 1, 118]
                    ':' <<Regex: <_sre.SRE_Match object; span=(117, 118), match=':'>>> ws:None [1, 118 -> 1, 119]
                    Newline+ <<118, 119>> ws:None [1, 119 -> 2, 1]
                    Indent <<119, 123, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(123, 127), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(129, 135), match='string'>>> ws:None [4, 1 -> 4, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(136, 139), match='val'>>> ws:(135, 136) [4, 8 -> 4, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(140, 145), match='Func2'>>> ws:(139, 140) [4, 12 -> 4, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(145, 146), match='('>>> ws:None [4, 17 -> 4, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(151, 154), match='pos'>>> ws:None [5, 5 -> 5, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(154, 155), match=':'>>> ws:None [5, 8 -> 5, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(156, 159), match='int'>>> ws:(155, 156) [5, 10 -> 5, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(160, 163), match='val'>>> ws:(159, 160) [5, 14 -> 5, 17]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(164, 165), match='a'>>> ws:(163, 164) [5, 18 -> 5, 19]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(165, 166), match=','>>> ws:None [5, 19 -> 5, 20]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(167, 171), match='bool'>>> ws:(166, 167) [5, 21 -> 5, 25]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(172, 175), match='val'>>> ws:(171, 172) [5, 26 -> 5, 29]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(176, 177), match='b'>>> ws:(175, 176) [5, 30 -> 5, 31]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(177, 178), match=','>>> ws:None [5, 31 -> 5, 32]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(183, 186), match='any'>>> ws:None [6, 5 -> 6, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(186, 187), match=':'>>> ws:None [6, 8 -> 6, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(188, 192), match='char'>>> ws:(187, 188) [6, 10 -> 6, 14]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(193, 196), match='val'>>> ws:(192, 193) [6, 15 -> 6, 18]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(197, 198), match='c'>>> ws:(196, 197) [6, 19 -> 6, 20]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(198, 199), match=','>>> ws:None [6, 20 -> 6, 21]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(200, 206), match='double'>>> ws:(199, 200) [6, 22 -> 6, 28]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(207, 210), match='val'>>> ws:(206, 207) [6, 29 -> 6, 32]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(211, 212), match='d'>>> ws:(210, 211) [6, 33 -> 6, 34]
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(212, 213), match=','>>> ws:None [6, 34 -> 6, 35]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(214, 218), match='enum'>>> ws:(213, 214) [6, 36 -> 6, 40]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(219, 222), match='val'>>> ws:(218, 219) [6, 41 -> 6, 44]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(223, 224), match='e'>>> ws:(222, 223) [6, 45 -> 6, 46]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(224, 225), match=','>>> ws:None [6, 46 -> 6, 47]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(230, 233), match='key'>>> ws:None [7, 5 -> 7, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(233, 234), match=':'>>> ws:None [7, 8 -> 7, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(235, 240), match='float'>>> ws:(234, 235) [7, 10 -> 7, 15]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(241, 244), match='val'>>> ws:(240, 241) [7, 16 -> 7, 19]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(245, 246), match='f'>>> ws:(244, 245) [7, 20 -> 7, 21]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(246, 247), match=','>>> ws:None [7, 21 -> 7, 22]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(248, 252), match='good'>>> ws:(247, 248) [7, 23 -> 7, 27]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(253, 256), match='val'>>> ws:(252, 253) [7, 28 -> 7, 31]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(257, 258), match='g'>>> ws:(256, 257) [7, 32 -> 7, 33]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(258, 259), match=','>>> ws:None [7, 33 -> 7, 34]
                    ')' <<Regex: <_sre.SRE_Match object; span=(260, 261), match=')'>>> ws:None [8, 1 -> 8, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(261, 262), match=':'>>> ws:None [8, 2 -> 8, 3]
                    Newline+ <<262, 263>> ws:None [8, 3 -> 9, 1]
                    Indent <<263, 267, (4)>> ws:None [9, 1 -> 9, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(267, 271), match='pass'>>> ws:None [9, 5 -> 9, 9]
                    Dedent <<>> ws:None [11, 1 -> 11, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(273, 279), match='string'>>> ws:None [11, 1 -> 11, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(280, 283), match='val'>>> ws:(279, 280) [11, 8 -> 11, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(284, 289), match='Func3'>>> ws:(283, 284) [11, 12 -> 11, 17]
                    '(' <<Regex: <_sre.SRE_Match object; span=(289, 290), match='('>>> ws:None [11, 17 -> 11, 18]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(295, 298), match='pos'>>> ws:None [12, 5 -> 12, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(298, 299), match=':'>>> ws:None [12, 8 -> 12, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(308, 311), match='int'>>> ws:None [13, 9 -> 13, 12]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(312, 315), match='val'>>> ws:(311, 312) [13, 13 -> 13, 16]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(316, 317), match='a'>>> ws:(315, 316) [13, 17 -> 13, 18]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(317, 318), match=','>>> ws:None [13, 18 -> 13, 19]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(327, 331), match='bool'>>> ws:None [14, 9 -> 14, 13]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(332, 335), match='val'>>> ws:(331, 332) [14, 14 -> 14, 17]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(336, 337), match='b'>>> ws:(335, 336) [14, 18 -> 14, 19]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(337, 338), match=','>>> ws:None [14, 19 -> 14, 20]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'any' <<Regex: <_sre.SRE_Match object; span=(343, 346), match='any'>>> ws:None [15, 5 -> 15, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(346, 347), match=':'>>> ws:None [15, 8 -> 15, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(356, 360), match='char'>>> ws:None [16, 9 -> 16, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(361, 364), match='val'>>> ws:(360, 361) [16, 14 -> 16, 17]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(365, 366), match='c'>>> ws:(364, 365) [16, 18 -> 16, 19]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(366, 367), match=','>>> ws:None [16, 19 -> 16, 20]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(376, 382), match='double'>>> ws:None [17, 9 -> 17, 15]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(383, 386), match='val'>>> ws:(382, 383) [17, 16 -> 17, 19]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(387, 388), match='d'>>> ws:(386, 387) [17, 20 -> 17, 21]
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(388, 389), match=','>>> ws:None [17, 21 -> 17, 22]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(398, 402), match='enum'>>> ws:None [18, 9 -> 18, 13]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(403, 406), match='val'>>> ws:(402, 403) [18, 14 -> 18, 17]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(407, 408), match='e'>>> ws:(406, 407) [18, 18 -> 18, 19]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(408, 409), match=','>>> ws:None [18, 19 -> 18, 20]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(414, 417), match='key'>>> ws:None [19, 5 -> 19, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(417, 418), match=':'>>> ws:None [19, 8 -> 19, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(427, 432), match='float'>>> ws:None [20, 9 -> 20, 14]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(433, 436), match='val'>>> ws:(432, 433) [20, 15 -> 20, 18]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(437, 438), match='f'>>> ws:(436, 437) [20, 19 -> 20, 20]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(438, 439), match=','>>> ws:None [20, 20 -> 20, 21]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(448, 452), match='good'>>> ws:None [21, 9 -> 21, 13]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(453, 456), match='val'>>> ws:(452, 453) [21, 14 -> 21, 17]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(457, 458), match='g'>>> ws:(456, 457) [21, 18 -> 21, 19]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(458, 459), match=','>>> ws:None [21, 19 -> 21, 20]
                    ')' <<Regex: <_sre.SRE_Match object; span=(460, 461), match=')'>>> ws:None [22, 1 -> 22, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(461, 462), match=':'>>> ws:None [22, 2 -> 22, 3]
                    Newline+ <<462, 463>> ws:None [22, 3 -> 23, 1]
                    Indent <<463, 467, (4)>> ws:None [23, 1 -> 23, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(467, 471), match='pass'>>> ws:None [23, 5 -> 23, 9]
                    Dedent <<>> ws:None [24, 1 -> 24, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_Defaults():
    assert Execute(
        textwrap.dedent(
            """\
            string val Traditional(int val a, bool val b, char val c=c_default, double val d=d_default):
                pass

            string val TraditionalWithDelimiters(int val a, /, bool val b, *, char val c=c_default, double val d=d_default):
                pass

            string val NewStyle(
                pos: int val a, bool val b,
                key: char val c=c_default, double val d=d_default,
            ):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='string'>>> ws:None [1, 1 -> 1, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(7, 10), match='val'>>> ws:(6, 7) [1, 8 -> 1, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(11, 22), match='Traditional'>>> ws:(10, 11) [1, 12 -> 1, 23]
                    '(' <<Regex: <_sre.SRE_Match object; span=(22, 23), match='('>>> ws:None [1, 23 -> 1, 24]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(23, 26), match='int'>>> ws:None [1, 24 -> 1, 27]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(27, 30), match='val'>>> ws:(26, 27) [1, 28 -> 1, 31]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='a'>>> ws:(30, 31) [1, 32 -> 1, 33]
                                Repeat: (Comma and Parameter, 0, None)
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=','>>> ws:None [1, 33 -> 1, 34]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(34, 38), match='bool'>>> ws:(33, 34) [1, 35 -> 1, 39]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(39, 42), match='val'>>> ws:(38, 39) [1, 40 -> 1, 43]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(43, 44), match='b'>>> ws:(42, 43) [1, 44 -> 1, 45]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=','>>> ws:None [1, 45 -> 1, 46]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(46, 50), match='char'>>> ws:(45, 46) [1, 47 -> 1, 51]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(51, 54), match='val'>>> ws:(50, 51) [1, 52 -> 1, 55]
                                                Or: [With Default, <name>]
                                                    With Default
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(55, 56), match='c'>>> ws:(54, 55) [1, 56 -> 1, 57]
                                                        '=' <<Regex: <_sre.SRE_Match object; span=(56, 57), match='='>>> ws:None [1, 57 -> 1, 58]
                                                        DynamicStatements.Expressions
                                                            1.0.0 Grammar
                                                                Variable Name
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(57, 66), match='c_default'>>> ws:None [1, 58 -> 1, 67]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(66, 67), match=','>>> ws:None [1, 67 -> 1, 68]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(68, 74), match='double'>>> ws:(67, 68) [1, 69 -> 1, 75]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(75, 78), match='val'>>> ws:(74, 75) [1, 76 -> 1, 79]
                                                Or: [With Default, <name>]
                                                    With Default
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(79, 80), match='d'>>> ws:(78, 79) [1, 80 -> 1, 81]
                                                        '=' <<Regex: <_sre.SRE_Match object; span=(80, 81), match='='>>> ws:None [1, 81 -> 1, 82]
                                                        DynamicStatements.Expressions
                                                            1.0.0 Grammar
                                                                Variable Name
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(81, 90), match='d_default'>>> ws:None [1, 82 -> 1, 91]
                    ')' <<Regex: <_sre.SRE_Match object; span=(90, 91), match=')'>>> ws:None [1, 91 -> 1, 92]
                    ':' <<Regex: <_sre.SRE_Match object; span=(91, 92), match=':'>>> ws:None [1, 92 -> 1, 93]
                    Newline+ <<92, 93>> ws:None [1, 93 -> 2, 1]
                    Indent <<93, 97, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(97, 101), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(103, 109), match='string'>>> ws:None [4, 1 -> 4, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(110, 113), match='val'>>> ws:(109, 110) [4, 8 -> 4, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(114, 139), match='TraditionalWithDelimiters'>>> ws:(113, 114) [4, 12 -> 4, 37]
                    '(' <<Regex: <_sre.SRE_Match object; span=(139, 140), match='('>>> ws:None [4, 37 -> 4, 38]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(140, 143), match='int'>>> ws:None [4, 38 -> 4, 41]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(144, 147), match='val'>>> ws:(143, 144) [4, 42 -> 4, 45]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(148, 149), match='a'>>> ws:(147, 148) [4, 46 -> 4, 47]
                                Repeat: (Comma and Parameter, 0, None)
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(149, 150), match=','>>> ws:None [4, 47 -> 4, 48]
                                        Or: [Parameter, '/', '*']
                                            '/' <<Regex: <_sre.SRE_Match object; span=(151, 152), match='/'>>> ws:(150, 151) [4, 49 -> 4, 50]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(152, 153), match=','>>> ws:None [4, 50 -> 4, 51]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(154, 158), match='bool'>>> ws:(153, 154) [4, 52 -> 4, 56]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(159, 162), match='val'>>> ws:(158, 159) [4, 57 -> 4, 60]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(163, 164), match='b'>>> ws:(162, 163) [4, 61 -> 4, 62]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(164, 165), match=','>>> ws:None [4, 62 -> 4, 63]
                                        Or: [Parameter, '/', '*']
                                            '*' <<Regex: <_sre.SRE_Match object; span=(166, 167), match='*'>>> ws:(165, 166) [4, 64 -> 4, 65]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(167, 168), match=','>>> ws:None [4, 65 -> 4, 66]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(169, 173), match='char'>>> ws:(168, 169) [4, 67 -> 4, 71]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(174, 177), match='val'>>> ws:(173, 174) [4, 72 -> 4, 75]
                                                Or: [With Default, <name>]
                                                    With Default
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(178, 179), match='c'>>> ws:(177, 178) [4, 76 -> 4, 77]
                                                        '=' <<Regex: <_sre.SRE_Match object; span=(179, 180), match='='>>> ws:None [4, 77 -> 4, 78]
                                                        DynamicStatements.Expressions
                                                            1.0.0 Grammar
                                                                Variable Name
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(180, 189), match='c_default'>>> ws:None [4, 78 -> 4, 87]
                                    Comma and Parameter
                                        ',' <<Regex: <_sre.SRE_Match object; span=(189, 190), match=','>>> ws:None [4, 87 -> 4, 88]
                                        Or: [Parameter, '/', '*']
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(191, 197), match='double'>>> ws:(190, 191) [4, 89 -> 4, 95]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(198, 201), match='val'>>> ws:(197, 198) [4, 96 -> 4, 99]
                                                Or: [With Default, <name>]
                                                    With Default
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(202, 203), match='d'>>> ws:(201, 202) [4, 100 -> 4, 101]
                                                        '=' <<Regex: <_sre.SRE_Match object; span=(203, 204), match='='>>> ws:None [4, 101 -> 4, 102]
                                                        DynamicStatements.Expressions
                                                            1.0.0 Grammar
                                                                Variable Name
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(204, 213), match='d_default'>>> ws:None [4, 102 -> 4, 111]
                    ')' <<Regex: <_sre.SRE_Match object; span=(213, 214), match=')'>>> ws:None [4, 111 -> 4, 112]
                    ':' <<Regex: <_sre.SRE_Match object; span=(214, 215), match=':'>>> ws:None [4, 112 -> 4, 113]
                    Newline+ <<215, 216>> ws:None [4, 113 -> 5, 1]
                    Indent <<216, 220, (4)>> ws:None [5, 1 -> 5, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(220, 224), match='pass'>>> ws:None [5, 5 -> 5, 9]
                    Dedent <<>> ws:None [7, 1 -> 7, 1]
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(226, 232), match='string'>>> ws:None [7, 1 -> 7, 7]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(233, 236), match='val'>>> ws:(232, 233) [7, 8 -> 7, 11]
                    <name> <<Regex: <_sre.SRE_Match object; span=(237, 245), match='NewStyle'>>> ws:(236, 237) [7, 12 -> 7, 20]
                    '(' <<Regex: <_sre.SRE_Match object; span=(245, 246), match='('>>> ws:None [7, 20 -> 7, 21]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Repeat: (New Style, 1, 3)
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'pos' <<Regex: <_sre.SRE_Match object; span=(251, 254), match='pos'>>> ws:None [8, 5 -> 8, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(254, 255), match=':'>>> ws:None [8, 8 -> 8, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(256, 259), match='int'>>> ws:(255, 256) [8, 10 -> 8, 13]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(260, 263), match='val'>>> ws:(259, 260) [8, 14 -> 8, 17]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(264, 265), match='a'>>> ws:(263, 264) [8, 18 -> 8, 19]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(265, 266), match=','>>> ws:None [8, 19 -> 8, 20]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(267, 271), match='bool'>>> ws:(266, 267) [8, 21 -> 8, 25]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(272, 275), match='val'>>> ws:(271, 272) [8, 26 -> 8, 29]
                                                Or: [With Default, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(276, 277), match='b'>>> ws:(275, 276) [8, 30 -> 8, 31]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(277, 278), match=','>>> ws:None [8, 31 -> 8, 32]
                                New Style
                                    Or: ['pos', 'any', 'key']
                                        'key' <<Regex: <_sre.SRE_Match object; span=(283, 286), match='key'>>> ws:None [9, 5 -> 9, 8]
                                    ':' <<Regex: <_sre.SRE_Match object; span=(286, 287), match=':'>>> ws:None [9, 8 -> 9, 9]
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(288, 292), match='char'>>> ws:(287, 288) [9, 10 -> 9, 14]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(293, 296), match='val'>>> ws:(292, 293) [9, 15 -> 9, 18]
                                        Or: [With Default, <name>]
                                            With Default
                                                <name> <<Regex: <_sre.SRE_Match object; span=(297, 298), match='c'>>> ws:(296, 297) [9, 19 -> 9, 20]
                                                '=' <<Regex: <_sre.SRE_Match object; span=(298, 299), match='='>>> ws:None [9, 20 -> 9, 21]
                                                DynamicStatements.Expressions
                                                    1.0.0 Grammar
                                                        Variable Name
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(299, 308), match='c_default'>>> ws:None [9, 21 -> 9, 30]
                                    Repeat: (Comma and Parameter, 0, None)
                                        Comma and Parameter
                                            ',' <<Regex: <_sre.SRE_Match object; span=(308, 309), match=','>>> ws:None [9, 30 -> 9, 31]
                                            Parameter
                                                Type
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(310, 316), match='double'>>> ws:(309, 310) [9, 32 -> 9, 38]
                                                    Repeat: (Modifier, 0, 1)
                                                        Modifier
                                                            'val' <<Regex: <_sre.SRE_Match object; span=(317, 320), match='val'>>> ws:(316, 317) [9, 39 -> 9, 42]
                                                Or: [With Default, <name>]
                                                    With Default
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(321, 322), match='d'>>> ws:(320, 321) [9, 43 -> 9, 44]
                                                        '=' <<Regex: <_sre.SRE_Match object; span=(322, 323), match='='>>> ws:None [9, 44 -> 9, 45]
                                                        DynamicStatements.Expressions
                                                            1.0.0 Grammar
                                                                Variable Name
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(323, 332), match='d_default'>>> ws:None [9, 45 -> 9, 54]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(332, 333), match=','>>> ws:None [9, 54 -> 9, 55]
                    ')' <<Regex: <_sre.SRE_Match object; span=(334, 335), match=')'>>> ws:None [10, 1 -> 10, 2]
                    ':' <<Regex: <_sre.SRE_Match object; span=(335, 336), match=':'>>> ws:None [10, 2 -> 10, 3]
                    Newline+ <<336, 337>> ws:None [10, 3 -> 11, 1]
                    Indent <<337, 341, (4)>> ws:None [11, 1 -> 11, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(341, 345), match='pass'>>> ws:None [11, 5 -> 11, 9]
                    Dedent <<>> ws:None [12, 1 -> 12, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_PositionalParameterAfterDefaultValueParameterError():
    # Traditional
    with pytest.raises(PositionalParameterAfterDefaultValueParameterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                string val Func(int val a, bool val b=true, char val c):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Positional parameters may not appear after a parameter with a default value has been defined"
    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 54
    assert ex.ColumnEnd == 55

    # New style
    with pytest.raises(PositionalParameterAfterDefaultValueParameterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                string val Func(
                    pos:
                        int val a,
                    any:
                        bool val b=true,
                    key:
                        char val cee,
                ):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Positional parameters may not appear after a parameter with a default value has been defined"
    assert ex.Line == 7
    assert ex.LineEnd == 7
    assert ex.Column == 18
    assert ex.ColumnEnd == 21

# ----------------------------------------------------------------------
def test_InvalidNewStyleParameterGroupOrderingError():
    with pytest.raises(InvalidNewStyleParameterGroupOrderingError) as ex:
        Execute(
            textwrap.dedent(
                """\
                string val Func(
                    any:
                        int val a,
                    pos:
                        bool val b,
                ):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Parameter groups must appear in the order 'pos', 'any', 'key'"
    assert ex.Line == 4
    assert ex.LineEnd == 4
    assert ex.Column == 5
    assert ex.ColumnEnd == 8

    with pytest.raises(InvalidNewStyleParameterGroupOrderingError) as ex:
        Execute(
            textwrap.dedent(
                """\
                string val Func(
                    pos:
                        int val a,
                    key:
                        bool val b,
                    any:
                        char val c,
                ):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Parameter groups must appear in the order 'pos', 'any', 'key'"
    assert ex.Line == 6
    assert ex.LineEnd == 6
    assert ex.Column == 5
    assert ex.ColumnEnd == 8

# ----------------------------------------------------------------------
def test_InvalidTraditionalDelimiterOrderError():
    with pytest.raises(InvalidTraditionalDelimiterOrderError) as ex:
        Execute(
            textwrap.dedent(
                """\
                string val Func(int val a, *, bool val b, /, char val c):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "The positional delimiter ('/') must appear before the keyword delimiter ('*')"
    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 43
    assert ex.ColumnEnd == 44

# ----------------------------------------------------------------------
def test_InvalidTraditionalPositionalDelimiterError():
    with pytest.raises(InvalidTraditionalPositionalDelimiterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                string val Func(/, int val a):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "The positional delimiter ('/') must appear after at least 1 parameter"
    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 17
    assert ex.ColumnEnd == 18

# ----------------------------------------------------------------------
def test_InvalidTraditionalKeywordDelimiterError():
    with pytest.raises(InvalidTraditionalKeywordDelimiterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                string val Func(int val a, *):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "The keyword delimiter ('*') must appear before at least 1 parameter"
    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 28
    assert ex.ColumnEnd == 29

# ----------------------------------------------------------------------
def test_InvalidTraditionalDuplicatePositionalDelimiterError():
    with pytest.raises(InvalidTraditionalDuplicatePositionalDelimiterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                string val Func(int val a, /, bool val b, /, char val c):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "The positional delimiter ('/') may only appear once in a list of parameters"
    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 43
    assert ex.ColumnEnd == 44

# ----------------------------------------------------------------------
def test_InvalidTraditionalDuplicateKeywordDelimiterError():
    with pytest.raises(InvalidTraditionalDuplicateKeywordDelimiterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                string val Func(
                    int val a, bool val b,
                    *,
                    char val c,
                    *,
                    double val d,
                ):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "The keyword delimiter ('*') may only appear once in a list of parameters"
    assert ex.Line == 5
    assert ex.LineEnd == 5
    assert ex.Column == 5
    assert ex.ColumnEnd == 6

# ----------------------------------------------------------------------
def test_Export():
    assert Execute(
        textwrap.dedent(
            """\
            export string val Exported(int val a):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Repeat: ('export', 0, 1)
                        'export' <<Regex: <_sre.SRE_Match object; span=(0, 6), match='export'>>> ws:None [1, 1 -> 1, 7]
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 13), match='string'>>> ws:(6, 7) [1, 8 -> 1, 14]
                        Repeat: (Modifier, 0, 1)
                            Modifier
                                'val' <<Regex: <_sre.SRE_Match object; span=(14, 17), match='val'>>> ws:(13, 14) [1, 15 -> 1, 18]
                    <name> <<Regex: <_sre.SRE_Match object; span=(18, 26), match='Exported'>>> ws:(17, 18) [1, 19 -> 1, 27]
                    '(' <<Regex: <_sre.SRE_Match object; span=(26, 27), match='('>>> ws:None [1, 27 -> 1, 28]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(27, 30), match='int'>>> ws:None [1, 28 -> 1, 31]
                                            Repeat: (Modifier, 0, 1)
                                                Modifier
                                                    'val' <<Regex: <_sre.SRE_Match object; span=(31, 34), match='val'>>> ws:(30, 31) [1, 32 -> 1, 35]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(35, 36), match='a'>>> ws:(34, 35) [1, 36 -> 1, 37]
                    ')' <<Regex: <_sre.SRE_Match object; span=(36, 37), match=')'>>> ws:None [1, 37 -> 1, 38]
                    ':' <<Regex: <_sre.SRE_Match object; span=(37, 38), match=':'>>> ws:None [1, 38 -> 1, 39]
                    Newline+ <<38, 39>> ws:None [1, 39 -> 2, 1]
                    Indent <<39, 43, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(43, 47), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [3, 1 -> 3, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_NoModifierInType():
    assert Execute(
        textwrap.dedent(
            """\
            string Func(int value):
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Declaration
                    Type
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='string'>>> ws:None [1, 1 -> 1, 7]
                    <name> <<Regex: <_sre.SRE_Match object; span=(7, 11), match='Func'>>> ws:(6, 7) [1, 8 -> 1, 12]
                    '(' <<Regex: <_sre.SRE_Match object; span=(11, 12), match='('>>> ws:None [1, 12 -> 1, 13]
                    Repeat: (Or: [Repeat: (New Style, 1, 3), Traditional], 0, 1)
                        Or: [Repeat: (New Style, 1, 3), Traditional]
                            Traditional
                                Or: [Parameter, '/', '*']
                                    Parameter
                                        Type
                                            <name> <<Regex: <_sre.SRE_Match object; span=(12, 15), match='int'>>> ws:None [1, 13 -> 1, 16]
                                        Or: [With Default, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(16, 21), match='value'>>> ws:(15, 16) [1, 17 -> 1, 22]
                    ')' <<Regex: <_sre.SRE_Match object; span=(21, 22), match=')'>>> ws:None [1, 22 -> 1, 23]
                    ':' <<Regex: <_sre.SRE_Match object; span=(22, 23), match=':'>>> ws:None [1, 23 -> 1, 24]
                    Newline+ <<23, 24>> ws:None [1, 24 -> 2, 1]
                    Indent <<24, 28, (4)>> ws:None [2, 1 -> 2, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Pass
                                    'pass' <<Regex: <_sre.SRE_Match object; span=(28, 32), match='pass'>>> ws:None [2, 5 -> 2, 9]
                    Dedent <<>> ws:None [3, 1 -> 3, 1]
        """,
    )
