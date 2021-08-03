# ----------------------------------------------------------------------
# |
# |  FuncDeclarationStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-27 00:47:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for FuncDeclarationStatement.py"""

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
    from . import Execute, ExecuteEx
    from ..FuncDeclarationStatement import *
    from ..Common import FuncParameters

# ----------------------------------------------------------------------
def test_NoArgs():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            Type Func():
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='Type'>>> ws:None [1, 1 -> 1, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(5, 9), match='Func'>>> ws:(4, 5) [1, 6 -> 1, 10]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(9, 10), match='('>>> ws:None [1, 10 -> 1, 11]
                            ')' <<Regex: <_sre.SRE_Match object; span=(10, 11), match=')'>>> ws:None [1, 11 -> 1, 12]
                        ':' <<Regex: <_sre.SRE_Match object; span=(11, 12), match=':'>>> ws:None [1, 12 -> 1, 13]
                        Newline+ <<12, 13>> ws:None [1, 13 -> 2, 1]
                        Indent <<13, 17, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(17, 21), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<21, 22>> ws:None [2, 9 -> 3, 1]
                        Dedent <<>> ws:None [3, 1 -> 3, 1]
        """,
    )

    assert str(node.Children[0].Children[0].Children[0].Info) == textwrap.dedent(
        """\
        Func
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='Type'>>> ws:None [1, 1 -> 1, 5]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    <No Parameters>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_MultipleNoArgStatementsAndFuncs():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            Type1 Func1():
                vara = varb
                pass

            Type2 Func2():
                pass
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='Type1'>>> ws:None [1, 1 -> 1, 6]
                        <name> <<Regex: <_sre.SRE_Match object; span=(6, 11), match='Func1'>>> ws:(5, 6) [1, 7 -> 1, 12]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(11, 12), match='('>>> ws:None [1, 12 -> 1, 13]
                            ')' <<Regex: <_sre.SRE_Match object; span=(12, 13), match=')'>>> ws:None [1, 13 -> 1, 14]
                        ':' <<Regex: <_sre.SRE_Match object; span=(13, 14), match=':'>>> ws:None [1, 14 -> 1, 15]
                        Newline+ <<14, 15>> ws:None [1, 15 -> 2, 1]
                        Indent <<15, 19, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Variable Declaration
                                        <name> <<Regex: <_sre.SRE_Match object; span=(19, 23), match='vara'>>> ws:None [2, 5 -> 2, 9]
                                        '=' <<Regex: <_sre.SRE_Match object; span=(24, 25), match='='>>> ws:(23, 24) [2, 10 -> 2, 11]
                                        DynamicStatementsType.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(26, 30), match='varb'>>> ws:(25, 26) [2, 12 -> 2, 16]
                                        Newline+ <<30, 31>> ws:None [2, 16 -> 3, 1]
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(35, 39), match='pass'>>> ws:None [3, 5 -> 3, 9]
                                        Newline+ <<39, 41>> ws:None [3, 9 -> 5, 1]
                        Dedent <<>> ws:None [5, 1 -> 5, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(41, 46), match='Type2'>>> ws:None [5, 1 -> 5, 6]
                        <name> <<Regex: <_sre.SRE_Match object; span=(47, 52), match='Func2'>>> ws:(46, 47) [5, 7 -> 5, 12]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(52, 53), match='('>>> ws:None [5, 12 -> 5, 13]
                            ')' <<Regex: <_sre.SRE_Match object; span=(53, 54), match=')'>>> ws:None [5, 13 -> 5, 14]
                        ':' <<Regex: <_sre.SRE_Match object; span=(54, 55), match=':'>>> ws:None [5, 14 -> 5, 15]
                        Newline+ <<55, 56>> ws:None [5, 15 -> 6, 1]
                        Indent <<56, 60, (4)>> ws:None [6, 1 -> 6, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(60, 64), match='pass'>>> ws:None [6, 5 -> 6, 9]
                                        Newline+ <<64, 65>> ws:None [6, 9 -> 7, 1]
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(69, 73), match='pass'>>> ws:None [7, 5 -> 7, 9]
                                        Newline+ <<73, 74>> ws:None [7, 9 -> 8, 1]
                        Dedent <<>> ws:None [8, 1 -> 8, 1]
        """,
    )

    assert str(node.Children[0].Children[0].Children[0].Info) == textwrap.dedent(
        """\
        Func1
            Export: False
            Statements: 2
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 5), match='Type1'>>> ws:None [1, 1 -> 1, 6]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    <No Parameters>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    assert str(node.Children[1].Children[0].Children[0].Info) == textwrap.dedent(
        """\
        Func2
            Export: False
            Statements: 2
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(41, 46), match='Type2'>>> ws:None [5, 1 -> 5, 6]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    <No Parameters>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_Export():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            String NoExport(Int a):
                pass

            export String WithExport(Int a):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 15), match='NoExport'>>> ws:(6, 7) [1, 8 -> 1, 16]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(15, 16), match='('>>> ws:None [1, 16 -> 1, 17]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(16, 19), match='Int'>>> ws:None [1, 17 -> 1, 20]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(20, 21), match='a'>>> ws:(19, 20) [1, 21 -> 1, 22]
                            ')' <<Regex: <_sre.SRE_Match object; span=(21, 22), match=')'>>> ws:None [1, 22 -> 1, 23]
                        ':' <<Regex: <_sre.SRE_Match object; span=(22, 23), match=':'>>> ws:None [1, 23 -> 1, 24]
                        Newline+ <<23, 24>> ws:None [1, 24 -> 2, 1]
                        Indent <<24, 28, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(28, 32), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<32, 34>> ws:None [2, 9 -> 4, 1]
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        Repeat: ('export', 0, 1)
                            'export' <<Regex: <_sre.SRE_Match object; span=(34, 40), match='export'>>> ws:None [4, 1 -> 4, 7]
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(41, 47), match='String'>>> ws:(40, 41) [4, 8 -> 4, 14]
                        <name> <<Regex: <_sre.SRE_Match object; span=(48, 58), match='WithExport'>>> ws:(47, 48) [4, 15 -> 4, 25]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(58, 59), match='('>>> ws:None [4, 25 -> 4, 26]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(59, 62), match='Int'>>> ws:None [4, 26 -> 4, 29]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(63, 64), match='a'>>> ws:(62, 63) [4, 30 -> 4, 31]
                            ')' <<Regex: <_sre.SRE_Match object; span=(64, 65), match=')'>>> ws:None [4, 31 -> 4, 32]
                        ':' <<Regex: <_sre.SRE_Match object; span=(65, 66), match=':'>>> ws:None [4, 32 -> 4, 33]
                        Newline+ <<66, 67>> ws:None [4, 33 -> 5, 1]
                        Indent <<67, 71, (4)>> ws:None [5, 1 -> 5, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(71, 75), match='pass'>>> ws:None [5, 5 -> 5, 9]
                                        Newline+ <<75, 76>> ws:None [5, 9 -> 6, 1]
                        Dedent <<>> ws:None [6, 1 -> 6, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        NoExport
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [1, 17 -> 1, 22]
                        Type: [1, 17 -> 1, 20]
                        Name: [1, 21 -> 1, 22]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        WithExport
            Export: True
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(41, 47), match='String'>>> ws:(40, 41) [4, 8 -> 4, 14]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [4, 26 -> 4, 31]
                        Type: [4, 26 -> 4, 29]
                        Name: [4, 30 -> 4, 31]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_DocString():
    result, node = ExecuteEx(
        textwrap.dedent(
            '''\
            Bool SingleStatement(Int a):
                """
                This is the
                doc string
                """
                pass

            String DoubleStatement(Int a):
                """
                This is the doc string
                """
                pass
                pass

            export Int WithExport(Int a, Bool b, Char c):
                """
                A
                    doc
                string
                """
                pass
                pass
                pass
            ''',
        ),
    )

    assert result == textwrap.dedent(
        '''\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='Bool'>>> ws:None [1, 1 -> 1, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(5, 20), match='SingleStatement'>>> ws:(4, 5) [1, 6 -> 1, 21]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(20, 21), match='('>>> ws:None [1, 21 -> 1, 22]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(21, 24), match='Int'>>> ws:None [1, 22 -> 1, 25]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='a'>>> ws:(24, 25) [1, 26 -> 1, 27]
                            ')' <<Regex: <_sre.SRE_Match object; span=(26, 27), match=')'>>> ws:None [1, 27 -> 1, 28]
                        ':' <<Regex: <_sre.SRE_Match object; span=(27, 28), match=':'>>> ws:None [1, 28 -> 1, 29]
                        Newline+ <<28, 29>> ws:None [1, 29 -> 2, 1]
                        Indent <<29, 33, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (Docstring, 0, 1)
                            Docstring
                                <docstring> <<Regex: <_sre.SRE_Match object; span=(33, 75), match='"""\\n    This is the\\n    doc string\\n    """'>>> ws:None [2, 5 -> 5, 8]
                                Newline+ <<75, 76>> ws:None [5, 8 -> 6, 1]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(80, 84), match='pass'>>> ws:None [6, 5 -> 6, 9]
                                        Newline+ <<84, 86>> ws:None [6, 9 -> 8, 1]
                        Dedent <<>> ws:None [8, 1 -> 8, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(86, 92), match='String'>>> ws:None [8, 1 -> 8, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(93, 108), match='DoubleStatement'>>> ws:(92, 93) [8, 8 -> 8, 23]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(108, 109), match='('>>> ws:None [8, 23 -> 8, 24]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(109, 112), match='Int'>>> ws:None [8, 24 -> 8, 27]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(113, 114), match='a'>>> ws:(112, 113) [8, 28 -> 8, 29]
                            ')' <<Regex: <_sre.SRE_Match object; span=(114, 115), match=')'>>> ws:None [8, 29 -> 8, 30]
                        ':' <<Regex: <_sre.SRE_Match object; span=(115, 116), match=':'>>> ws:None [8, 30 -> 8, 31]
                        Newline+ <<116, 117>> ws:None [8, 31 -> 9, 1]
                        Indent <<117, 121, (4)>> ws:None [9, 1 -> 9, 5]
                        Repeat: (Docstring, 0, 1)
                            Docstring
                                <docstring> <<Regex: <_sre.SRE_Match object; span=(121, 159), match='"""\\n    This is the doc string\\n    """'>>> ws:None [9, 5 -> 11, 8]
                                Newline+ <<159, 160>> ws:None [11, 8 -> 12, 1]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(164, 168), match='pass'>>> ws:None [12, 5 -> 12, 9]
                                        Newline+ <<168, 169>> ws:None [12, 9 -> 13, 1]
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(173, 177), match='pass'>>> ws:None [13, 5 -> 13, 9]
                                        Newline+ <<177, 179>> ws:None [13, 9 -> 15, 1]
                        Dedent <<>> ws:None [15, 1 -> 15, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        Repeat: ('export', 0, 1)
                            'export' <<Regex: <_sre.SRE_Match object; span=(179, 185), match='export'>>> ws:None [15, 1 -> 15, 7]
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(186, 189), match='Int'>>> ws:(185, 186) [15, 8 -> 15, 11]
                        <name> <<Regex: <_sre.SRE_Match object; span=(190, 200), match='WithExport'>>> ws:(189, 190) [15, 12 -> 15, 22]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(200, 201), match='('>>> ws:None [15, 22 -> 15, 23]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(201, 204), match='Int'>>> ws:None [15, 23 -> 15, 26]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(205, 206), match='a'>>> ws:(204, 205) [15, 27 -> 15, 28]
                                        Repeat: (Delimiter and Element, 0, None)
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(206, 207), match=','>>> ws:None [15, 28 -> 15, 29]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(208, 212), match='Bool'>>> ws:(207, 208) [15, 30 -> 15, 34]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(213, 214), match='b'>>> ws:(212, 213) [15, 35 -> 15, 36]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(214, 215), match=','>>> ws:None [15, 36 -> 15, 37]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(216, 220), match='Char'>>> ws:(215, 216) [15, 38 -> 15, 42]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(221, 222), match='c'>>> ws:(220, 221) [15, 43 -> 15, 44]
                            ')' <<Regex: <_sre.SRE_Match object; span=(222, 223), match=')'>>> ws:None [15, 44 -> 15, 45]
                        ':' <<Regex: <_sre.SRE_Match object; span=(223, 224), match=':'>>> ws:None [15, 45 -> 15, 46]
                        Newline+ <<224, 225>> ws:None [15, 46 -> 16, 1]
                        Indent <<225, 229, (4)>> ws:None [16, 1 -> 16, 5]
                        Repeat: (Docstring, 0, 1)
                            Docstring
                                <docstring> <<Regex: <_sre.SRE_Match object; span=(229, 269), match='"""\\n    A\\n        doc\\n    string\\n    """'>>> ws:None [16, 5 -> 20, 8]
                                Newline+ <<269, 270>> ws:None [20, 8 -> 21, 1]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(274, 278), match='pass'>>> ws:None [21, 5 -> 21, 9]
                                        Newline+ <<278, 279>> ws:None [21, 9 -> 22, 1]
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(283, 287), match='pass'>>> ws:None [22, 5 -> 22, 9]
                                        Newline+ <<287, 288>> ws:None [22, 9 -> 23, 1]
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(292, 296), match='pass'>>> ws:None [23, 5 -> 23, 9]
                                        Newline+ <<296, 297>> ws:None [23, 9 -> 24, 1]
                        Dedent <<>> ws:None [24, 1 -> 24, 1]
        ''',
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        '''\
        SingleStatement
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='Bool'>>> ws:None [1, 1 -> 1, 5]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [1, 22 -> 1, 27]
                        Type: [1, 22 -> 1, 25]
                        Name: [1, 26 -> 1, 27]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                    This is the
                    doc string
        ''',
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        '''\
        DoubleStatement
            Export: False
            Statements: 2
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(86, 92), match='String'>>> ws:None [8, 1 -> 8, 7]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [8, 24 -> 8, 29]
                        Type: [8, 24 -> 8, 27]
                        Name: [8, 28 -> 8, 29]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                    This is the doc string
        ''',
    )

    value = str(node.Children[2].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        '''\
        WithExport
            Export: True
            Statements: 3
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(186, 189), match='Int'>>> ws:(185, 186) [15, 8 -> 15, 11]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [15, 23 -> 15, 28]
                        Type: [15, 23 -> 15, 26]
                        Name: [15, 27 -> 15, 28]
                        Default: <No Default>

                    b
                        Parameter: [15, 30 -> 15, 36]
                        Type: [15, 30 -> 15, 34]
                        Name: [15, 35 -> 15, 36]
                        Default: <No Default>

                    c
                        Parameter: [15, 38 -> 15, 44]
                        Type: [15, 38 -> 15, 42]
                        Name: [15, 43 -> 15, 44]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                    A
                        doc
                    string
        ''',
    )

# ----------------------------------------------------------------------
def test_TraditionalSingleArg():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            # No trailing comma
            Type1 Func1(Int val a):
                pass

            # Trailing comma
            Type2 val Func2(Int val b,):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(20, 25), match='Type1'>>> ws:None [2, 1 -> 2, 6]
                        <name> <<Regex: <_sre.SRE_Match object; span=(26, 31), match='Func1'>>> ws:(25, 26) [2, 7 -> 2, 12]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(31, 32), match='('>>> ws:None [2, 12 -> 2, 13]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(32, 35), match='Int'>>> ws:None [2, 13 -> 2, 16]
                                                            Repeat: (Modifier, 0, 1)
                                                                Modifier
                                                                    'val' <<Regex: <_sre.SRE_Match object; span=(36, 39), match='val'>>> ws:(35, 36) [2, 17 -> 2, 20]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(40, 41), match='a'>>> ws:(39, 40) [2, 21 -> 2, 22]
                            ')' <<Regex: <_sre.SRE_Match object; span=(41, 42), match=')'>>> ws:None [2, 22 -> 2, 23]
                        ':' <<Regex: <_sre.SRE_Match object; span=(42, 43), match=':'>>> ws:None [2, 23 -> 2, 24]
                        Newline+ <<43, 44>> ws:None [2, 24 -> 3, 1]
                        Indent <<44, 48, (4)>> ws:None [3, 1 -> 3, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(48, 52), match='pass'>>> ws:None [3, 5 -> 3, 9]
                                        Newline+ <<52, 54>> ws:None [3, 9 -> 5, 1]
                        Dedent <<>> ws:None [5, 1 -> 5, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(71, 76), match='Type2'>>> ws:None [6, 1 -> 6, 6]
                                    Repeat: (Modifier, 0, 1)
                                        Modifier
                                            'val' <<Regex: <_sre.SRE_Match object; span=(77, 80), match='val'>>> ws:(76, 77) [6, 7 -> 6, 10]
                        <name> <<Regex: <_sre.SRE_Match object; span=(81, 86), match='Func2'>>> ws:(80, 81) [6, 11 -> 6, 16]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(86, 87), match='('>>> ws:None [6, 16 -> 6, 17]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(87, 90), match='Int'>>> ws:None [6, 17 -> 6, 20]
                                                            Repeat: (Modifier, 0, 1)
                                                                Modifier
                                                                    'val' <<Regex: <_sre.SRE_Match object; span=(91, 94), match='val'>>> ws:(90, 91) [6, 21 -> 6, 24]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(95, 96), match='b'>>> ws:(94, 95) [6, 25 -> 6, 26]
                                        Repeat: (Trailing Delimiter, 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(96, 97), match=','>>> ws:None [6, 26 -> 6, 27]
                            ')' <<Regex: <_sre.SRE_Match object; span=(97, 98), match=')'>>> ws:None [6, 27 -> 6, 28]
                        ':' <<Regex: <_sre.SRE_Match object; span=(98, 99), match=':'>>> ws:None [6, 28 -> 6, 29]
                        Newline+ <<99, 100>> ws:None [6, 29 -> 7, 1]
                        Indent <<100, 104, (4)>> ws:None [7, 1 -> 7, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(104, 108), match='pass'>>> ws:None [7, 5 -> 7, 9]
                                        Newline+ <<108, 109>> ws:None [7, 9 -> 8, 1]
                        Dedent <<>> ws:None [8, 1 -> 8, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func1
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(20, 25), match='Type1'>>> ws:None [2, 1 -> 2, 6]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [2, 13 -> 2, 22]
                        Type: [2, 13 -> 2, 20]
                        Name: [2, 21 -> 2, 22]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func2
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(71, 76), match='Type2'>>> ws:None [6, 1 -> 6, 6]
                    Repeat: (Modifier, 0, 1)
                        Modifier
                            'val' <<Regex: <_sre.SRE_Match object; span=(77, 80), match='val'>>> ws:(76, 77) [6, 7 -> 6, 10]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    b
                        Parameter: [6, 17 -> 6, 26]
                        Type: [6, 17 -> 6, 24]
                        Name: [6, 25 -> 6, 26]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_TraditionalMultipleArgs():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            # No trailing comma
            String view Func1(Int var a, Bool val b, Char ref c, Double view dee):
                pass

            # Trailing comma
            String view Func2(Int var a, Bool val b, Char ref c, Double view dee,):
                pass

            # Multiline
            String view Func3(
                Int var a,
                Bool val b,
                    Char ref c,

                Double view dee,
            ):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(20, 26), match='String'>>> ws:None [2, 1 -> 2, 7]
                                    Repeat: (Modifier, 0, 1)
                                        Modifier
                                            'view' <<Regex: <_sre.SRE_Match object; span=(27, 31), match='view'>>> ws:(26, 27) [2, 8 -> 2, 12]
                        <name> <<Regex: <_sre.SRE_Match object; span=(32, 37), match='Func1'>>> ws:(31, 32) [2, 13 -> 2, 18]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(37, 38), match='('>>> ws:None [2, 18 -> 2, 19]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(38, 41), match='Int'>>> ws:None [2, 19 -> 2, 22]
                                                            Repeat: (Modifier, 0, 1)
                                                                Modifier
                                                                    'var' <<Regex: <_sre.SRE_Match object; span=(42, 45), match='var'>>> ws:(41, 42) [2, 23 -> 2, 26]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(46, 47), match='a'>>> ws:(45, 46) [2, 27 -> 2, 28]
                                        Repeat: (Delimiter and Element, 0, None)
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(47, 48), match=','>>> ws:None [2, 28 -> 2, 29]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(49, 53), match='Bool'>>> ws:(48, 49) [2, 30 -> 2, 34]
                                                                    Repeat: (Modifier, 0, 1)
                                                                        Modifier
                                                                            'val' <<Regex: <_sre.SRE_Match object; span=(54, 57), match='val'>>> ws:(53, 54) [2, 35 -> 2, 38]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(58, 59), match='b'>>> ws:(57, 58) [2, 39 -> 2, 40]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(59, 60), match=','>>> ws:None [2, 40 -> 2, 41]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(61, 65), match='Char'>>> ws:(60, 61) [2, 42 -> 2, 46]
                                                                    Repeat: (Modifier, 0, 1)
                                                                        Modifier
                                                                            'ref' <<Regex: <_sre.SRE_Match object; span=(66, 69), match='ref'>>> ws:(65, 66) [2, 47 -> 2, 50]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(70, 71), match='c'>>> ws:(69, 70) [2, 51 -> 2, 52]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(71, 72), match=','>>> ws:None [2, 52 -> 2, 53]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(73, 79), match='Double'>>> ws:(72, 73) [2, 54 -> 2, 60]
                                                                    Repeat: (Modifier, 0, 1)
                                                                        Modifier
                                                                            'view' <<Regex: <_sre.SRE_Match object; span=(80, 84), match='view'>>> ws:(79, 80) [2, 61 -> 2, 65]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(85, 88), match='dee'>>> ws:(84, 85) [2, 66 -> 2, 69]
                            ')' <<Regex: <_sre.SRE_Match object; span=(88, 89), match=')'>>> ws:None [2, 69 -> 2, 70]
                        ':' <<Regex: <_sre.SRE_Match object; span=(89, 90), match=':'>>> ws:None [2, 70 -> 2, 71]
                        Newline+ <<90, 91>> ws:None [2, 71 -> 3, 1]
                        Indent <<91, 95, (4)>> ws:None [3, 1 -> 3, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(95, 99), match='pass'>>> ws:None [3, 5 -> 3, 9]
                                        Newline+ <<99, 101>> ws:None [3, 9 -> 5, 1]
                        Dedent <<>> ws:None [5, 1 -> 5, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(118, 124), match='String'>>> ws:None [6, 1 -> 6, 7]
                                    Repeat: (Modifier, 0, 1)
                                        Modifier
                                            'view' <<Regex: <_sre.SRE_Match object; span=(125, 129), match='view'>>> ws:(124, 125) [6, 8 -> 6, 12]
                        <name> <<Regex: <_sre.SRE_Match object; span=(130, 135), match='Func2'>>> ws:(129, 130) [6, 13 -> 6, 18]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(135, 136), match='('>>> ws:None [6, 18 -> 6, 19]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(136, 139), match='Int'>>> ws:None [6, 19 -> 6, 22]
                                                            Repeat: (Modifier, 0, 1)
                                                                Modifier
                                                                    'var' <<Regex: <_sre.SRE_Match object; span=(140, 143), match='var'>>> ws:(139, 140) [6, 23 -> 6, 26]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(144, 145), match='a'>>> ws:(143, 144) [6, 27 -> 6, 28]
                                        Repeat: (Delimiter and Element, 0, None)
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(145, 146), match=','>>> ws:None [6, 28 -> 6, 29]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(147, 151), match='Bool'>>> ws:(146, 147) [6, 30 -> 6, 34]
                                                                    Repeat: (Modifier, 0, 1)
                                                                        Modifier
                                                                            'val' <<Regex: <_sre.SRE_Match object; span=(152, 155), match='val'>>> ws:(151, 152) [6, 35 -> 6, 38]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(156, 157), match='b'>>> ws:(155, 156) [6, 39 -> 6, 40]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(157, 158), match=','>>> ws:None [6, 40 -> 6, 41]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(159, 163), match='Char'>>> ws:(158, 159) [6, 42 -> 6, 46]
                                                                    Repeat: (Modifier, 0, 1)
                                                                        Modifier
                                                                            'ref' <<Regex: <_sre.SRE_Match object; span=(164, 167), match='ref'>>> ws:(163, 164) [6, 47 -> 6, 50]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(168, 169), match='c'>>> ws:(167, 168) [6, 51 -> 6, 52]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(169, 170), match=','>>> ws:None [6, 52 -> 6, 53]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(171, 177), match='Double'>>> ws:(170, 171) [6, 54 -> 6, 60]
                                                                    Repeat: (Modifier, 0, 1)
                                                                        Modifier
                                                                            'view' <<Regex: <_sre.SRE_Match object; span=(178, 182), match='view'>>> ws:(177, 178) [6, 61 -> 6, 65]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(183, 186), match='dee'>>> ws:(182, 183) [6, 66 -> 6, 69]
                                        Repeat: (Trailing Delimiter, 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(186, 187), match=','>>> ws:None [6, 69 -> 6, 70]
                            ')' <<Regex: <_sre.SRE_Match object; span=(187, 188), match=')'>>> ws:None [6, 70 -> 6, 71]
                        ':' <<Regex: <_sre.SRE_Match object; span=(188, 189), match=':'>>> ws:None [6, 71 -> 6, 72]
                        Newline+ <<189, 190>> ws:None [6, 72 -> 7, 1]
                        Indent <<190, 194, (4)>> ws:None [7, 1 -> 7, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(194, 198), match='pass'>>> ws:None [7, 5 -> 7, 9]
                                        Newline+ <<198, 200>> ws:None [7, 9 -> 9, 1]
                        Dedent <<>> ws:None [9, 1 -> 9, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(212, 218), match='String'>>> ws:None [10, 1 -> 10, 7]
                                    Repeat: (Modifier, 0, 1)
                                        Modifier
                                            'view' <<Regex: <_sre.SRE_Match object; span=(219, 223), match='view'>>> ws:(218, 219) [10, 8 -> 10, 12]
                        <name> <<Regex: <_sre.SRE_Match object; span=(224, 229), match='Func3'>>> ws:(223, 224) [10, 13 -> 10, 18]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(229, 230), match='('>>> ws:None [10, 18 -> 10, 19]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(235, 238), match='Int'>>> ws:None [11, 5 -> 11, 8]
                                                            Repeat: (Modifier, 0, 1)
                                                                Modifier
                                                                    'var' <<Regex: <_sre.SRE_Match object; span=(239, 242), match='var'>>> ws:(238, 239) [11, 9 -> 11, 12]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(243, 244), match='a'>>> ws:(242, 243) [11, 13 -> 11, 14]
                                        Repeat: (Delimiter and Element, 0, None)
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(244, 245), match=','>>> ws:None [11, 14 -> 11, 15]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(250, 254), match='Bool'>>> ws:None [12, 5 -> 12, 9]
                                                                    Repeat: (Modifier, 0, 1)
                                                                        Modifier
                                                                            'val' <<Regex: <_sre.SRE_Match object; span=(255, 258), match='val'>>> ws:(254, 255) [12, 10 -> 12, 13]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(259, 260), match='b'>>> ws:(258, 259) [12, 14 -> 12, 15]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(260, 261), match=','>>> ws:None [12, 15 -> 12, 16]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(270, 274), match='Char'>>> ws:None [13, 9 -> 13, 13]
                                                                    Repeat: (Modifier, 0, 1)
                                                                        Modifier
                                                                            'ref' <<Regex: <_sre.SRE_Match object; span=(275, 278), match='ref'>>> ws:(274, 275) [13, 14 -> 13, 17]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(279, 280), match='c'>>> ws:(278, 279) [13, 18 -> 13, 19]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(280, 281), match=','>>> ws:None [13, 19 -> 13, 20]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(287, 293), match='Double'>>> ws:None [15, 5 -> 15, 11]
                                                                    Repeat: (Modifier, 0, 1)
                                                                        Modifier
                                                                            'view' <<Regex: <_sre.SRE_Match object; span=(294, 298), match='view'>>> ws:(293, 294) [15, 12 -> 15, 16]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(299, 302), match='dee'>>> ws:(298, 299) [15, 17 -> 15, 20]
                                        Repeat: (Trailing Delimiter, 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(302, 303), match=','>>> ws:None [15, 20 -> 15, 21]
                            ')' <<Regex: <_sre.SRE_Match object; span=(304, 305), match=')'>>> ws:None [16, 1 -> 16, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(305, 306), match=':'>>> ws:None [16, 2 -> 16, 3]
                        Newline+ <<306, 307>> ws:None [16, 3 -> 17, 1]
                        Indent <<307, 311, (4)>> ws:None [17, 1 -> 17, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(311, 315), match='pass'>>> ws:None [17, 5 -> 17, 9]
                                        Newline+ <<315, 316>> ws:None [17, 9 -> 18, 1]
                        Dedent <<>> ws:None [18, 1 -> 18, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func1
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(20, 26), match='String'>>> ws:None [2, 1 -> 2, 7]
                    Repeat: (Modifier, 0, 1)
                        Modifier
                            'view' <<Regex: <_sre.SRE_Match object; span=(27, 31), match='view'>>> ws:(26, 27) [2, 8 -> 2, 12]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [2, 19 -> 2, 28]
                        Type: [2, 19 -> 2, 26]
                        Name: [2, 27 -> 2, 28]
                        Default: <No Default>

                    b
                        Parameter: [2, 30 -> 2, 40]
                        Type: [2, 30 -> 2, 38]
                        Name: [2, 39 -> 2, 40]
                        Default: <No Default>

                    c
                        Parameter: [2, 42 -> 2, 52]
                        Type: [2, 42 -> 2, 50]
                        Name: [2, 51 -> 2, 52]
                        Default: <No Default>

                    dee
                        Parameter: [2, 54 -> 2, 69]
                        Type: [2, 54 -> 2, 65]
                        Name: [2, 66 -> 2, 69]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func2
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(118, 124), match='String'>>> ws:None [6, 1 -> 6, 7]
                    Repeat: (Modifier, 0, 1)
                        Modifier
                            'view' <<Regex: <_sre.SRE_Match object; span=(125, 129), match='view'>>> ws:(124, 125) [6, 8 -> 6, 12]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [6, 19 -> 6, 28]
                        Type: [6, 19 -> 6, 26]
                        Name: [6, 27 -> 6, 28]
                        Default: <No Default>

                    b
                        Parameter: [6, 30 -> 6, 40]
                        Type: [6, 30 -> 6, 38]
                        Name: [6, 39 -> 6, 40]
                        Default: <No Default>

                    c
                        Parameter: [6, 42 -> 6, 52]
                        Type: [6, 42 -> 6, 50]
                        Name: [6, 51 -> 6, 52]
                        Default: <No Default>

                    dee
                        Parameter: [6, 54 -> 6, 69]
                        Type: [6, 54 -> 6, 65]
                        Name: [6, 66 -> 6, 69]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[2].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func3
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(212, 218), match='String'>>> ws:None [10, 1 -> 10, 7]
                    Repeat: (Modifier, 0, 1)
                        Modifier
                            'view' <<Regex: <_sre.SRE_Match object; span=(219, 223), match='view'>>> ws:(218, 219) [10, 8 -> 10, 12]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [11, 5 -> 11, 14]
                        Type: [11, 5 -> 11, 12]
                        Name: [11, 13 -> 11, 14]
                        Default: <No Default>

                    b
                        Parameter: [12, 5 -> 12, 15]
                        Type: [12, 5 -> 12, 13]
                        Name: [12, 14 -> 12, 15]
                        Default: <No Default>

                    c
                        Parameter: [13, 9 -> 13, 19]
                        Type: [13, 9 -> 13, 17]
                        Name: [13, 18 -> 13, 19]
                        Default: <No Default>

                    dee
                        Parameter: [15, 5 -> 15, 20]
                        Type: [15, 5 -> 15, 16]
                        Name: [15, 17 -> 15, 20]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_TraditionalWithDefaults():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            String Func(Int a, Bool bee=true):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 11), match='Func'>>> ws:(6, 7) [1, 8 -> 1, 12]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(11, 12), match='('>>> ws:None [1, 12 -> 1, 13]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(12, 15), match='Int'>>> ws:None [1, 13 -> 1, 16]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(16, 17), match='a'>>> ws:(15, 16) [1, 17 -> 1, 18]
                                        Repeat: (Delimiter and Element, 0, None)
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(17, 18), match=','>>> ws:None [1, 18 -> 1, 19]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(19, 23), match='Bool'>>> ws:(18, 19) [1, 20 -> 1, 24]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(24, 27), match='bee'>>> ws:(23, 24) [1, 25 -> 1, 28]
                                                        Repeat: (With Default, 0, 1)
                                                            With Default
                                                                '=' <<Regex: <_sre.SRE_Match object; span=(27, 28), match='='>>> ws:None [1, 28 -> 1, 29]
                                                                DynamicStatementsType.Expressions
                                                                    1.0.0 Grammar
                                                                        Variable Name
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(28, 32), match='true'>>> ws:None [1, 29 -> 1, 33]
                            ')' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=')'>>> ws:None [1, 33 -> 1, 34]
                        ':' <<Regex: <_sre.SRE_Match object; span=(33, 34), match=':'>>> ws:None [1, 34 -> 1, 35]
                        Newline+ <<34, 35>> ws:None [1, 35 -> 2, 1]
                        Indent <<35, 39, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(39, 43), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<43, 44>> ws:None [2, 9 -> 3, 1]
                        Dedent <<>> ws:None [3, 1 -> 3, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [1, 13 -> 1, 18]
                        Type: [1, 13 -> 1, 16]
                        Name: [1, 17 -> 1, 18]
                        Default: <No Default>

                    bee
                        Parameter: [1, 20 -> 1, 33]
                        Type: [1, 20 -> 1, 24]
                        Name: [1, 25 -> 1, 28]
                        Default:
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(28, 32), match='true'>>> ws:None [1, 29 -> 1, 33]
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_TraditionalWithPositional():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            Int Func1(Int a, /, Bool b):
                pass

            String Func2(Int a, /):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 3), match='Int'>>> ws:None [1, 1 -> 1, 4]
                        <name> <<Regex: <_sre.SRE_Match object; span=(4, 9), match='Func1'>>> ws:(3, 4) [1, 5 -> 1, 10]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(9, 10), match='('>>> ws:None [1, 10 -> 1, 11]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(10, 13), match='Int'>>> ws:None [1, 11 -> 1, 14]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(14, 15), match='a'>>> ws:(13, 14) [1, 15 -> 1, 16]
                                        Repeat: (Delimiter and Element, 0, None)
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(15, 16), match=','>>> ws:None [1, 16 -> 1, 17]
                                                Or: {Parameter, '/', '*'}
                                                    '/' <<Regex: <_sre.SRE_Match object; span=(17, 18), match='/'>>> ws:(16, 17) [1, 18 -> 1, 19]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(18, 19), match=','>>> ws:None [1, 19 -> 1, 20]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(20, 24), match='Bool'>>> ws:(19, 20) [1, 21 -> 1, 25]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='b'>>> ws:(24, 25) [1, 26 -> 1, 27]
                            ')' <<Regex: <_sre.SRE_Match object; span=(26, 27), match=')'>>> ws:None [1, 27 -> 1, 28]
                        ':' <<Regex: <_sre.SRE_Match object; span=(27, 28), match=':'>>> ws:None [1, 28 -> 1, 29]
                        Newline+ <<28, 29>> ws:None [1, 29 -> 2, 1]
                        Indent <<29, 33, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(33, 37), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<37, 39>> ws:None [2, 9 -> 4, 1]
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(39, 45), match='String'>>> ws:None [4, 1 -> 4, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(46, 51), match='Func2'>>> ws:(45, 46) [4, 8 -> 4, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(51, 52), match='('>>> ws:None [4, 13 -> 4, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(52, 55), match='Int'>>> ws:None [4, 14 -> 4, 17]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(56, 57), match='a'>>> ws:(55, 56) [4, 18 -> 4, 19]
                                        Repeat: (Delimiter and Element, 0, None)
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(57, 58), match=','>>> ws:None [4, 19 -> 4, 20]
                                                Or: {Parameter, '/', '*'}
                                                    '/' <<Regex: <_sre.SRE_Match object; span=(59, 60), match='/'>>> ws:(58, 59) [4, 21 -> 4, 22]
                            ')' <<Regex: <_sre.SRE_Match object; span=(60, 61), match=')'>>> ws:None [4, 22 -> 4, 23]
                        ':' <<Regex: <_sre.SRE_Match object; span=(61, 62), match=':'>>> ws:None [4, 23 -> 4, 24]
                        Newline+ <<62, 63>> ws:None [4, 24 -> 5, 1]
                        Indent <<63, 67, (4)>> ws:None [5, 1 -> 5, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(67, 71), match='pass'>>> ws:None [5, 5 -> 5, 9]
                                        Newline+ <<71, 72>> ws:None [5, 9 -> 6, 1]
                        Dedent <<>> ws:None [6, 1 -> 6, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func1
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 3), match='Int'>>> ws:None [1, 1 -> 1, 4]
            Parameters:
                Positional:
                    a
                        Parameter: [1, 11 -> 1, 16]
                        Type: [1, 11 -> 1, 14]
                        Name: [1, 15 -> 1, 16]
                        Default: <No Default>
                Any:
                    b
                        Parameter: [1, 21 -> 1, 27]
                        Type: [1, 21 -> 1, 25]
                        Name: [1, 26 -> 1, 27]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func2
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(39, 45), match='String'>>> ws:None [4, 1 -> 4, 7]
            Parameters:
                Positional:
                    a
                        Parameter: [4, 14 -> 4, 19]
                        Type: [4, 14 -> 4, 17]
                        Name: [4, 18 -> 4, 19]
                        Default: <No Default>
                Any:
                    <No Parameters>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_TraditionalWithKeyword():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            Int Func(Int a, *, Bool b):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 3), match='Int'>>> ws:None [1, 1 -> 1, 4]
                        <name> <<Regex: <_sre.SRE_Match object; span=(4, 8), match='Func'>>> ws:(3, 4) [1, 5 -> 1, 9]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(8, 9), match='('>>> ws:None [1, 9 -> 1, 10]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(9, 12), match='Int'>>> ws:None [1, 10 -> 1, 13]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(13, 14), match='a'>>> ws:(12, 13) [1, 14 -> 1, 15]
                                        Repeat: (Delimiter and Element, 0, None)
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(14, 15), match=','>>> ws:None [1, 15 -> 1, 16]
                                                Or: {Parameter, '/', '*'}
                                                    '*' <<Regex: <_sre.SRE_Match object; span=(16, 17), match='*'>>> ws:(15, 16) [1, 17 -> 1, 18]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(17, 18), match=','>>> ws:None [1, 18 -> 1, 19]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(19, 23), match='Bool'>>> ws:(18, 19) [1, 20 -> 1, 24]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(24, 25), match='b'>>> ws:(23, 24) [1, 25 -> 1, 26]
                            ')' <<Regex: <_sre.SRE_Match object; span=(25, 26), match=')'>>> ws:None [1, 26 -> 1, 27]
                        ':' <<Regex: <_sre.SRE_Match object; span=(26, 27), match=':'>>> ws:None [1, 27 -> 1, 28]
                        Newline+ <<27, 28>> ws:None [1, 28 -> 2, 1]
                        Indent <<28, 32, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(32, 36), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<36, 37>> ws:None [2, 9 -> 3, 1]
                        Dedent <<>> ws:None [3, 1 -> 3, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 3), match='Int'>>> ws:None [1, 1 -> 1, 4]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [1, 10 -> 1, 15]
                        Type: [1, 10 -> 1, 13]
                        Name: [1, 14 -> 1, 15]
                        Default: <No Default>
                Keyword:
                    b
                        Parameter: [1, 20 -> 1, 26]
                        Type: [1, 20 -> 1, 24]
                        Name: [1, 25 -> 1, 26]
                        Default: <No Default>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_TraditionalWithPositionalAndKeyword():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            String ThisFunc(Int a, /, Int b, *, Int c):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 15), match='ThisFunc'>>> ws:(6, 7) [1, 8 -> 1, 16]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(15, 16), match='('>>> ws:None [1, 16 -> 1, 17]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Traditional
                                        Or: {Parameter, '/', '*'}
                                            Parameter
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(16, 19), match='Int'>>> ws:None [1, 17 -> 1, 20]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(20, 21), match='a'>>> ws:(19, 20) [1, 21 -> 1, 22]
                                        Repeat: (Delimiter and Element, 0, None)
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(21, 22), match=','>>> ws:None [1, 22 -> 1, 23]
                                                Or: {Parameter, '/', '*'}
                                                    '/' <<Regex: <_sre.SRE_Match object; span=(23, 24), match='/'>>> ws:(22, 23) [1, 24 -> 1, 25]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(24, 25), match=','>>> ws:None [1, 25 -> 1, 26]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(26, 29), match='Int'>>> ws:(25, 26) [1, 27 -> 1, 30]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(30, 31), match='b'>>> ws:(29, 30) [1, 31 -> 1, 32]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(31, 32), match=','>>> ws:None [1, 32 -> 1, 33]
                                                Or: {Parameter, '/', '*'}
                                                    '*' <<Regex: <_sre.SRE_Match object; span=(33, 34), match='*'>>> ws:(32, 33) [1, 34 -> 1, 35]
                                            Delimiter and Element
                                                ',' <<Regex: <_sre.SRE_Match object; span=(34, 35), match=','>>> ws:None [1, 35 -> 1, 36]
                                                Or: {Parameter, '/', '*'}
                                                    Parameter
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(36, 39), match='Int'>>> ws:(35, 36) [1, 37 -> 1, 40]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(40, 41), match='c'>>> ws:(39, 40) [1, 41 -> 1, 42]
                            ')' <<Regex: <_sre.SRE_Match object; span=(41, 42), match=')'>>> ws:None [1, 42 -> 1, 43]
                        ':' <<Regex: <_sre.SRE_Match object; span=(42, 43), match=':'>>> ws:None [1, 43 -> 1, 44]
                        Newline+ <<43, 44>> ws:None [1, 44 -> 2, 1]
                        Indent <<44, 48, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(48, 52), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<52, 53>> ws:None [2, 9 -> 3, 1]
                        Dedent <<>> ws:None [3, 1 -> 3, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        ThisFunc
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
            Parameters:
                Positional:
                    a
                        Parameter: [1, 17 -> 1, 22]
                        Type: [1, 17 -> 1, 20]
                        Name: [1, 21 -> 1, 22]
                        Default: <No Default>
                Any:
                    b
                        Parameter: [1, 27 -> 1, 32]
                        Type: [1, 27 -> 1, 30]
                        Name: [1, 31 -> 1, 32]
                        Default: <No Default>
                Keyword:
                    c
                        Parameter: [1, 37 -> 1, 42]
                        Type: [1, 37 -> 1, 40]
                        Name: [1, 41 -> 1, 42]
                        Default: <No Default>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_NewStyleSingleArg():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            String Func1(pos: Int a):
                pass

            String Func2(
                key: Bool b,
            ):
                pass

            Int Func3(any: Char c,):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 12), match='Func1'>>> ws:(6, 7) [1, 8 -> 1, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(12, 13), match='('>>> ws:None [1, 13 -> 1, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'pos' <<Regex: <_sre.SRE_Match object; span=(13, 16), match='pos'>>> ws:None [1, 14 -> 1, 17]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=':'>>> ws:None [1, 17 -> 1, 18]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:(17, 18) [1, 19 -> 1, 22]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='a'>>> ws:(21, 22) [1, 23 -> 1, 24]
                            ')' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=')'>>> ws:None [1, 24 -> 1, 25]
                        ':' <<Regex: <_sre.SRE_Match object; span=(24, 25), match=':'>>> ws:None [1, 25 -> 1, 26]
                        Newline+ <<25, 26>> ws:None [1, 26 -> 2, 1]
                        Indent <<26, 30, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(30, 34), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<34, 36>> ws:None [2, 9 -> 4, 1]
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(36, 42), match='String'>>> ws:None [4, 1 -> 4, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(43, 48), match='Func2'>>> ws:(42, 43) [4, 8 -> 4, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(48, 49), match='('>>> ws:None [4, 13 -> 4, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'key' <<Regex: <_sre.SRE_Match object; span=(54, 57), match='key'>>> ws:None [5, 5 -> 5, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(57, 58), match=':'>>> ws:None [5, 8 -> 5, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(59, 63), match='Bool'>>> ws:(58, 59) [5, 10 -> 5, 14]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(64, 65), match='b'>>> ws:(63, 64) [5, 15 -> 5, 16]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(65, 66), match=','>>> ws:None [5, 16 -> 5, 17]
                            ')' <<Regex: <_sre.SRE_Match object; span=(67, 68), match=')'>>> ws:None [6, 1 -> 6, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(68, 69), match=':'>>> ws:None [6, 2 -> 6, 3]
                        Newline+ <<69, 70>> ws:None [6, 3 -> 7, 1]
                        Indent <<70, 74, (4)>> ws:None [7, 1 -> 7, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(74, 78), match='pass'>>> ws:None [7, 5 -> 7, 9]
                                        Newline+ <<78, 80>> ws:None [7, 9 -> 9, 1]
                        Dedent <<>> ws:None [9, 1 -> 9, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(80, 83), match='Int'>>> ws:None [9, 1 -> 9, 4]
                        <name> <<Regex: <_sre.SRE_Match object; span=(84, 89), match='Func3'>>> ws:(83, 84) [9, 5 -> 9, 10]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(89, 90), match='('>>> ws:None [9, 10 -> 9, 11]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'any' <<Regex: <_sre.SRE_Match object; span=(90, 93), match='any'>>> ws:None [9, 11 -> 9, 14]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(93, 94), match=':'>>> ws:None [9, 14 -> 9, 15]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(95, 99), match='Char'>>> ws:(94, 95) [9, 16 -> 9, 20]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(100, 101), match='c'>>> ws:(99, 100) [9, 21 -> 9, 22]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(101, 102), match=','>>> ws:None [9, 22 -> 9, 23]
                            ')' <<Regex: <_sre.SRE_Match object; span=(102, 103), match=')'>>> ws:None [9, 23 -> 9, 24]
                        ':' <<Regex: <_sre.SRE_Match object; span=(103, 104), match=':'>>> ws:None [9, 24 -> 9, 25]
                        Newline+ <<104, 105>> ws:None [9, 25 -> 10, 1]
                        Indent <<105, 109, (4)>> ws:None [10, 1 -> 10, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(109, 113), match='pass'>>> ws:None [10, 5 -> 10, 9]
                                        Newline+ <<113, 114>> ws:None [10, 9 -> 11, 1]
                        Dedent <<>> ws:None [11, 1 -> 11, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func1
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
            Parameters:
                Positional:
                    a
                        Parameter: [1, 19 -> 1, 24]
                        Type: [1, 19 -> 1, 22]
                        Name: [1, 23 -> 1, 24]
                        Default: <No Default>
                Any:
                    <No Parameters>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func2
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(36, 42), match='String'>>> ws:None [4, 1 -> 4, 7]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    <No Parameters>
                Keyword:
                    b
                        Parameter: [5, 10 -> 5, 16]
                        Type: [5, 10 -> 5, 14]
                        Name: [5, 15 -> 5, 16]
                        Default: <No Default>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[2].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func3
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(80, 83), match='Int'>>> ws:None [9, 1 -> 9, 4]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    c
                        Parameter: [9, 16 -> 9, 22]
                        Type: [9, 16 -> 9, 20]
                        Name: [9, 21 -> 9, 22]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_NewStylePos():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            String Func1(pos: Int a, Bool b):
                pass

            String Func2(
                pos: Int a, Bool b
            ):
                pass

            Int Func3(
                pos:
                    Int a,
                    Bool b,
            ):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 12), match='Func1'>>> ws:(6, 7) [1, 8 -> 1, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(12, 13), match='('>>> ws:None [1, 13 -> 1, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'pos' <<Regex: <_sre.SRE_Match object; span=(13, 16), match='pos'>>> ws:None [1, 14 -> 1, 17]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=':'>>> ws:None [1, 17 -> 1, 18]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:(17, 18) [1, 19 -> 1, 22]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='a'>>> ws:(21, 22) [1, 23 -> 1, 24]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [1, 24 -> 1, 25]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='Bool'>>> ws:(24, 25) [1, 26 -> 1, 30]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(30, 31), match='b'>>> ws:(29, 30) [1, 31 -> 1, 32]
                            ')' <<Regex: <_sre.SRE_Match object; span=(31, 32), match=')'>>> ws:None [1, 32 -> 1, 33]
                        ':' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=':'>>> ws:None [1, 33 -> 1, 34]
                        Newline+ <<33, 34>> ws:None [1, 34 -> 2, 1]
                        Indent <<34, 38, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(38, 42), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<42, 44>> ws:None [2, 9 -> 4, 1]
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(44, 50), match='String'>>> ws:None [4, 1 -> 4, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(51, 56), match='Func2'>>> ws:(50, 51) [4, 8 -> 4, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(56, 57), match='('>>> ws:None [4, 13 -> 4, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'pos' <<Regex: <_sre.SRE_Match object; span=(62, 65), match='pos'>>> ws:None [5, 5 -> 5, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(65, 66), match=':'>>> ws:None [5, 8 -> 5, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(67, 70), match='Int'>>> ws:(66, 67) [5, 10 -> 5, 13]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(71, 72), match='a'>>> ws:(70, 71) [5, 14 -> 5, 15]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(72, 73), match=','>>> ws:None [5, 15 -> 5, 16]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(74, 78), match='Bool'>>> ws:(73, 74) [5, 17 -> 5, 21]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(79, 80), match='b'>>> ws:(78, 79) [5, 22 -> 5, 23]
                            ')' <<Regex: <_sre.SRE_Match object; span=(81, 82), match=')'>>> ws:None [6, 1 -> 6, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(82, 83), match=':'>>> ws:None [6, 2 -> 6, 3]
                        Newline+ <<83, 84>> ws:None [6, 3 -> 7, 1]
                        Indent <<84, 88, (4)>> ws:None [7, 1 -> 7, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(88, 92), match='pass'>>> ws:None [7, 5 -> 7, 9]
                                        Newline+ <<92, 94>> ws:None [7, 9 -> 9, 1]
                        Dedent <<>> ws:None [9, 1 -> 9, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(94, 97), match='Int'>>> ws:None [9, 1 -> 9, 4]
                        <name> <<Regex: <_sre.SRE_Match object; span=(98, 103), match='Func3'>>> ws:(97, 98) [9, 5 -> 9, 10]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(103, 104), match='('>>> ws:None [9, 10 -> 9, 11]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'pos' <<Regex: <_sre.SRE_Match object; span=(109, 112), match='pos'>>> ws:None [10, 5 -> 10, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(112, 113), match=':'>>> ws:None [10, 8 -> 10, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(122, 125), match='Int'>>> ws:None [11, 9 -> 11, 12]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(126, 127), match='a'>>> ws:(125, 126) [11, 13 -> 11, 14]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(127, 128), match=','>>> ws:None [11, 14 -> 11, 15]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(137, 141), match='Bool'>>> ws:None [12, 9 -> 12, 13]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(142, 143), match='b'>>> ws:(141, 142) [12, 14 -> 12, 15]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(143, 144), match=','>>> ws:None [12, 15 -> 12, 16]
                            ')' <<Regex: <_sre.SRE_Match object; span=(145, 146), match=')'>>> ws:None [13, 1 -> 13, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(146, 147), match=':'>>> ws:None [13, 2 -> 13, 3]
                        Newline+ <<147, 148>> ws:None [13, 3 -> 14, 1]
                        Indent <<148, 152, (4)>> ws:None [14, 1 -> 14, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(152, 156), match='pass'>>> ws:None [14, 5 -> 14, 9]
                                        Newline+ <<156, 157>> ws:None [14, 9 -> 15, 1]
                        Dedent <<>> ws:None [15, 1 -> 15, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func1
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
            Parameters:
                Positional:
                    a
                        Parameter: [1, 19 -> 1, 24]
                        Type: [1, 19 -> 1, 22]
                        Name: [1, 23 -> 1, 24]
                        Default: <No Default>

                    b
                        Parameter: [1, 26 -> 1, 32]
                        Type: [1, 26 -> 1, 30]
                        Name: [1, 31 -> 1, 32]
                        Default: <No Default>
                Any:
                    <No Parameters>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func2
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(44, 50), match='String'>>> ws:None [4, 1 -> 4, 7]
            Parameters:
                Positional:
                    a
                        Parameter: [5, 10 -> 5, 15]
                        Type: [5, 10 -> 5, 13]
                        Name: [5, 14 -> 5, 15]
                        Default: <No Default>

                    b
                        Parameter: [5, 17 -> 5, 23]
                        Type: [5, 17 -> 5, 21]
                        Name: [5, 22 -> 5, 23]
                        Default: <No Default>
                Any:
                    <No Parameters>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[2].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func3
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(94, 97), match='Int'>>> ws:None [9, 1 -> 9, 4]
            Parameters:
                Positional:
                    a
                        Parameter: [11, 9 -> 11, 14]
                        Type: [11, 9 -> 11, 12]
                        Name: [11, 13 -> 11, 14]
                        Default: <No Default>

                    b
                        Parameter: [12, 9 -> 12, 15]
                        Type: [12, 9 -> 12, 13]
                        Name: [12, 14 -> 12, 15]
                        Default: <No Default>
                Any:
                    <No Parameters>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_NewStyleKey():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            String Func1(key: Int a, Bool b):
                pass

            String Func2(
                key: Int a, Bool b
            ):
                pass

            Int Func3(
                key:
                    Int a,
                    Bool b,
            ):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 12), match='Func1'>>> ws:(6, 7) [1, 8 -> 1, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(12, 13), match='('>>> ws:None [1, 13 -> 1, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'key' <<Regex: <_sre.SRE_Match object; span=(13, 16), match='key'>>> ws:None [1, 14 -> 1, 17]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=':'>>> ws:None [1, 17 -> 1, 18]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:(17, 18) [1, 19 -> 1, 22]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='a'>>> ws:(21, 22) [1, 23 -> 1, 24]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [1, 24 -> 1, 25]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='Bool'>>> ws:(24, 25) [1, 26 -> 1, 30]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(30, 31), match='b'>>> ws:(29, 30) [1, 31 -> 1, 32]
                            ')' <<Regex: <_sre.SRE_Match object; span=(31, 32), match=')'>>> ws:None [1, 32 -> 1, 33]
                        ':' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=':'>>> ws:None [1, 33 -> 1, 34]
                        Newline+ <<33, 34>> ws:None [1, 34 -> 2, 1]
                        Indent <<34, 38, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(38, 42), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<42, 44>> ws:None [2, 9 -> 4, 1]
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(44, 50), match='String'>>> ws:None [4, 1 -> 4, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(51, 56), match='Func2'>>> ws:(50, 51) [4, 8 -> 4, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(56, 57), match='('>>> ws:None [4, 13 -> 4, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'key' <<Regex: <_sre.SRE_Match object; span=(62, 65), match='key'>>> ws:None [5, 5 -> 5, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(65, 66), match=':'>>> ws:None [5, 8 -> 5, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(67, 70), match='Int'>>> ws:(66, 67) [5, 10 -> 5, 13]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(71, 72), match='a'>>> ws:(70, 71) [5, 14 -> 5, 15]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(72, 73), match=','>>> ws:None [5, 15 -> 5, 16]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(74, 78), match='Bool'>>> ws:(73, 74) [5, 17 -> 5, 21]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(79, 80), match='b'>>> ws:(78, 79) [5, 22 -> 5, 23]
                            ')' <<Regex: <_sre.SRE_Match object; span=(81, 82), match=')'>>> ws:None [6, 1 -> 6, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(82, 83), match=':'>>> ws:None [6, 2 -> 6, 3]
                        Newline+ <<83, 84>> ws:None [6, 3 -> 7, 1]
                        Indent <<84, 88, (4)>> ws:None [7, 1 -> 7, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(88, 92), match='pass'>>> ws:None [7, 5 -> 7, 9]
                                        Newline+ <<92, 94>> ws:None [7, 9 -> 9, 1]
                        Dedent <<>> ws:None [9, 1 -> 9, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(94, 97), match='Int'>>> ws:None [9, 1 -> 9, 4]
                        <name> <<Regex: <_sre.SRE_Match object; span=(98, 103), match='Func3'>>> ws:(97, 98) [9, 5 -> 9, 10]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(103, 104), match='('>>> ws:None [9, 10 -> 9, 11]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'key' <<Regex: <_sre.SRE_Match object; span=(109, 112), match='key'>>> ws:None [10, 5 -> 10, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(112, 113), match=':'>>> ws:None [10, 8 -> 10, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(122, 125), match='Int'>>> ws:None [11, 9 -> 11, 12]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(126, 127), match='a'>>> ws:(125, 126) [11, 13 -> 11, 14]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(127, 128), match=','>>> ws:None [11, 14 -> 11, 15]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(137, 141), match='Bool'>>> ws:None [12, 9 -> 12, 13]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(142, 143), match='b'>>> ws:(141, 142) [12, 14 -> 12, 15]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(143, 144), match=','>>> ws:None [12, 15 -> 12, 16]
                            ')' <<Regex: <_sre.SRE_Match object; span=(145, 146), match=')'>>> ws:None [13, 1 -> 13, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(146, 147), match=':'>>> ws:None [13, 2 -> 13, 3]
                        Newline+ <<147, 148>> ws:None [13, 3 -> 14, 1]
                        Indent <<148, 152, (4)>> ws:None [14, 1 -> 14, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(152, 156), match='pass'>>> ws:None [14, 5 -> 14, 9]
                                        Newline+ <<156, 157>> ws:None [14, 9 -> 15, 1]
                        Dedent <<>> ws:None [15, 1 -> 15, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func1
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    <No Parameters>
                Keyword:
                    a
                        Parameter: [1, 19 -> 1, 24]
                        Type: [1, 19 -> 1, 22]
                        Name: [1, 23 -> 1, 24]
                        Default: <No Default>

                    b
                        Parameter: [1, 26 -> 1, 32]
                        Type: [1, 26 -> 1, 30]
                        Name: [1, 31 -> 1, 32]
                        Default: <No Default>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func2
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(44, 50), match='String'>>> ws:None [4, 1 -> 4, 7]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    <No Parameters>
                Keyword:
                    a
                        Parameter: [5, 10 -> 5, 15]
                        Type: [5, 10 -> 5, 13]
                        Name: [5, 14 -> 5, 15]
                        Default: <No Default>

                    b
                        Parameter: [5, 17 -> 5, 23]
                        Type: [5, 17 -> 5, 21]
                        Name: [5, 22 -> 5, 23]
                        Default: <No Default>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[2].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func3
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(94, 97), match='Int'>>> ws:None [9, 1 -> 9, 4]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    <No Parameters>
                Keyword:
                    a
                        Parameter: [11, 9 -> 11, 14]
                        Type: [11, 9 -> 11, 12]
                        Name: [11, 13 -> 11, 14]
                        Default: <No Default>

                    b
                        Parameter: [12, 9 -> 12, 15]
                        Type: [12, 9 -> 12, 13]
                        Name: [12, 14 -> 12, 15]
                        Default: <No Default>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_NewStyleAny():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            String Func1(any: Int a, Bool b):
                pass

            String Func2(
                any: Int a, Bool b
            ):
                pass

            Int Func3(
                any:
                    Int a,
                    Bool b,
            ):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 12), match='Func1'>>> ws:(6, 7) [1, 8 -> 1, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(12, 13), match='('>>> ws:None [1, 13 -> 1, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'any' <<Regex: <_sre.SRE_Match object; span=(13, 16), match='any'>>> ws:None [1, 14 -> 1, 17]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=':'>>> ws:None [1, 17 -> 1, 18]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:(17, 18) [1, 19 -> 1, 22]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='a'>>> ws:(21, 22) [1, 23 -> 1, 24]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [1, 24 -> 1, 25]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='Bool'>>> ws:(24, 25) [1, 26 -> 1, 30]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(30, 31), match='b'>>> ws:(29, 30) [1, 31 -> 1, 32]
                            ')' <<Regex: <_sre.SRE_Match object; span=(31, 32), match=')'>>> ws:None [1, 32 -> 1, 33]
                        ':' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=':'>>> ws:None [1, 33 -> 1, 34]
                        Newline+ <<33, 34>> ws:None [1, 34 -> 2, 1]
                        Indent <<34, 38, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(38, 42), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<42, 44>> ws:None [2, 9 -> 4, 1]
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(44, 50), match='String'>>> ws:None [4, 1 -> 4, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(51, 56), match='Func2'>>> ws:(50, 51) [4, 8 -> 4, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(56, 57), match='('>>> ws:None [4, 13 -> 4, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'any' <<Regex: <_sre.SRE_Match object; span=(62, 65), match='any'>>> ws:None [5, 5 -> 5, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(65, 66), match=':'>>> ws:None [5, 8 -> 5, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(67, 70), match='Int'>>> ws:(66, 67) [5, 10 -> 5, 13]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(71, 72), match='a'>>> ws:(70, 71) [5, 14 -> 5, 15]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(72, 73), match=','>>> ws:None [5, 15 -> 5, 16]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(74, 78), match='Bool'>>> ws:(73, 74) [5, 17 -> 5, 21]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(79, 80), match='b'>>> ws:(78, 79) [5, 22 -> 5, 23]
                            ')' <<Regex: <_sre.SRE_Match object; span=(81, 82), match=')'>>> ws:None [6, 1 -> 6, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(82, 83), match=':'>>> ws:None [6, 2 -> 6, 3]
                        Newline+ <<83, 84>> ws:None [6, 3 -> 7, 1]
                        Indent <<84, 88, (4)>> ws:None [7, 1 -> 7, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(88, 92), match='pass'>>> ws:None [7, 5 -> 7, 9]
                                        Newline+ <<92, 94>> ws:None [7, 9 -> 9, 1]
                        Dedent <<>> ws:None [9, 1 -> 9, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(94, 97), match='Int'>>> ws:None [9, 1 -> 9, 4]
                        <name> <<Regex: <_sre.SRE_Match object; span=(98, 103), match='Func3'>>> ws:(97, 98) [9, 5 -> 9, 10]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(103, 104), match='('>>> ws:None [9, 10 -> 9, 11]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'any' <<Regex: <_sre.SRE_Match object; span=(109, 112), match='any'>>> ws:None [10, 5 -> 10, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(112, 113), match=':'>>> ws:None [10, 8 -> 10, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(122, 125), match='Int'>>> ws:None [11, 9 -> 11, 12]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(126, 127), match='a'>>> ws:(125, 126) [11, 13 -> 11, 14]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(127, 128), match=','>>> ws:None [11, 14 -> 11, 15]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(137, 141), match='Bool'>>> ws:None [12, 9 -> 12, 13]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(142, 143), match='b'>>> ws:(141, 142) [12, 14 -> 12, 15]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(143, 144), match=','>>> ws:None [12, 15 -> 12, 16]
                            ')' <<Regex: <_sre.SRE_Match object; span=(145, 146), match=')'>>> ws:None [13, 1 -> 13, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(146, 147), match=':'>>> ws:None [13, 2 -> 13, 3]
                        Newline+ <<147, 148>> ws:None [13, 3 -> 14, 1]
                        Indent <<148, 152, (4)>> ws:None [14, 1 -> 14, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(152, 156), match='pass'>>> ws:None [14, 5 -> 14, 9]
                                        Newline+ <<156, 157>> ws:None [14, 9 -> 15, 1]
                        Dedent <<>> ws:None [15, 1 -> 15, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func1
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [1, 19 -> 1, 24]
                        Type: [1, 19 -> 1, 22]
                        Name: [1, 23 -> 1, 24]
                        Default: <No Default>

                    b
                        Parameter: [1, 26 -> 1, 32]
                        Type: [1, 26 -> 1, 30]
                        Name: [1, 31 -> 1, 32]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func2
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(44, 50), match='String'>>> ws:None [4, 1 -> 4, 7]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [5, 10 -> 5, 15]
                        Type: [5, 10 -> 5, 13]
                        Name: [5, 14 -> 5, 15]
                        Default: <No Default>

                    b
                        Parameter: [5, 17 -> 5, 23]
                        Type: [5, 17 -> 5, 21]
                        Name: [5, 22 -> 5, 23]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[2].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func3
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(94, 97), match='Int'>>> ws:None [9, 1 -> 9, 4]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [11, 9 -> 11, 14]
                        Type: [11, 9 -> 11, 12]
                        Name: [11, 13 -> 11, 14]
                        Default: <No Default>

                    b
                        Parameter: [12, 9 -> 12, 15]
                        Type: [12, 9 -> 12, 13]
                        Name: [12, 14 -> 12, 15]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_NewStylePosKey():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            String Func1(pos: Int a, Bool b, key: Char c,):
                pass

            String Func2(
                pos: Int a, Bool b
                key: Char c
            ):
                pass

            String Func3(
                pos:
                    Int a,
                    Bool b,
                key:
                    Char c,
            ):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 12), match='Func1'>>> ws:(6, 7) [1, 8 -> 1, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(12, 13), match='('>>> ws:None [1, 13 -> 1, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'pos' <<Regex: <_sre.SRE_Match object; span=(13, 16), match='pos'>>> ws:None [1, 14 -> 1, 17]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=':'>>> ws:None [1, 17 -> 1, 18]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:(17, 18) [1, 19 -> 1, 22]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='a'>>> ws:(21, 22) [1, 23 -> 1, 24]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [1, 24 -> 1, 25]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='Bool'>>> ws:(24, 25) [1, 26 -> 1, 30]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(30, 31), match='b'>>> ws:(29, 30) [1, 31 -> 1, 32]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(31, 32), match=','>>> ws:None [1, 32 -> 1, 33]
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'key' <<Regex: <_sre.SRE_Match object; span=(33, 36), match='key'>>> ws:(32, 33) [1, 34 -> 1, 37]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(36, 37), match=':'>>> ws:None [1, 37 -> 1, 38]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(38, 42), match='Char'>>> ws:(37, 38) [1, 39 -> 1, 43]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(43, 44), match='c'>>> ws:(42, 43) [1, 44 -> 1, 45]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=','>>> ws:None [1, 45 -> 1, 46]
                            ')' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=')'>>> ws:None [1, 46 -> 1, 47]
                        ':' <<Regex: <_sre.SRE_Match object; span=(46, 47), match=':'>>> ws:None [1, 47 -> 1, 48]
                        Newline+ <<47, 48>> ws:None [1, 48 -> 2, 1]
                        Indent <<48, 52, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(52, 56), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<56, 58>> ws:None [2, 9 -> 4, 1]
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(58, 64), match='String'>>> ws:None [4, 1 -> 4, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(65, 70), match='Func2'>>> ws:(64, 65) [4, 8 -> 4, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(70, 71), match='('>>> ws:None [4, 13 -> 4, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'pos' <<Regex: <_sre.SRE_Match object; span=(76, 79), match='pos'>>> ws:None [5, 5 -> 5, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(79, 80), match=':'>>> ws:None [5, 8 -> 5, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(81, 84), match='Int'>>> ws:(80, 81) [5, 10 -> 5, 13]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(85, 86), match='a'>>> ws:(84, 85) [5, 14 -> 5, 15]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(86, 87), match=','>>> ws:None [5, 15 -> 5, 16]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(88, 92), match='Bool'>>> ws:(87, 88) [5, 17 -> 5, 21]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(93, 94), match='b'>>> ws:(92, 93) [5, 22 -> 5, 23]
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'key' <<Regex: <_sre.SRE_Match object; span=(99, 102), match='key'>>> ws:None [6, 5 -> 6, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(102, 103), match=':'>>> ws:None [6, 8 -> 6, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(104, 108), match='Char'>>> ws:(103, 104) [6, 10 -> 6, 14]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(109, 110), match='c'>>> ws:(108, 109) [6, 15 -> 6, 16]
                            ')' <<Regex: <_sre.SRE_Match object; span=(111, 112), match=')'>>> ws:None [7, 1 -> 7, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(112, 113), match=':'>>> ws:None [7, 2 -> 7, 3]
                        Newline+ <<113, 114>> ws:None [7, 3 -> 8, 1]
                        Indent <<114, 118, (4)>> ws:None [8, 1 -> 8, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(118, 122), match='pass'>>> ws:None [8, 5 -> 8, 9]
                                        Newline+ <<122, 124>> ws:None [8, 9 -> 10, 1]
                        Dedent <<>> ws:None [10, 1 -> 10, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(124, 130), match='String'>>> ws:None [10, 1 -> 10, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(131, 136), match='Func3'>>> ws:(130, 131) [10, 8 -> 10, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(136, 137), match='('>>> ws:None [10, 13 -> 10, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'pos' <<Regex: <_sre.SRE_Match object; span=(142, 145), match='pos'>>> ws:None [11, 5 -> 11, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(145, 146), match=':'>>> ws:None [11, 8 -> 11, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(155, 158), match='Int'>>> ws:None [12, 9 -> 12, 12]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(159, 160), match='a'>>> ws:(158, 159) [12, 13 -> 12, 14]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(160, 161), match=','>>> ws:None [12, 14 -> 12, 15]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(170, 174), match='Bool'>>> ws:None [13, 9 -> 13, 13]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(175, 176), match='b'>>> ws:(174, 175) [13, 14 -> 13, 15]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(176, 177), match=','>>> ws:None [13, 15 -> 13, 16]
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'key' <<Regex: <_sre.SRE_Match object; span=(182, 185), match='key'>>> ws:None [14, 5 -> 14, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(185, 186), match=':'>>> ws:None [14, 8 -> 14, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(195, 199), match='Char'>>> ws:None [15, 9 -> 15, 13]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(200, 201), match='c'>>> ws:(199, 200) [15, 14 -> 15, 15]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(201, 202), match=','>>> ws:None [15, 15 -> 15, 16]
                            ')' <<Regex: <_sre.SRE_Match object; span=(203, 204), match=')'>>> ws:None [16, 1 -> 16, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(204, 205), match=':'>>> ws:None [16, 2 -> 16, 3]
                        Newline+ <<205, 206>> ws:None [16, 3 -> 17, 1]
                        Indent <<206, 210, (4)>> ws:None [17, 1 -> 17, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(210, 214), match='pass'>>> ws:None [17, 5 -> 17, 9]
                                        Newline+ <<214, 215>> ws:None [17, 9 -> 18, 1]
                        Dedent <<>> ws:None [18, 1 -> 18, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func1
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
            Parameters:
                Positional:
                    a
                        Parameter: [1, 19 -> 1, 24]
                        Type: [1, 19 -> 1, 22]
                        Name: [1, 23 -> 1, 24]
                        Default: <No Default>

                    b
                        Parameter: [1, 26 -> 1, 32]
                        Type: [1, 26 -> 1, 30]
                        Name: [1, 31 -> 1, 32]
                        Default: <No Default>
                Any:
                    <No Parameters>
                Keyword:
                    c
                        Parameter: [1, 39 -> 1, 45]
                        Type: [1, 39 -> 1, 43]
                        Name: [1, 44 -> 1, 45]
                        Default: <No Default>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func2
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(58, 64), match='String'>>> ws:None [4, 1 -> 4, 7]
            Parameters:
                Positional:
                    a
                        Parameter: [5, 10 -> 5, 15]
                        Type: [5, 10 -> 5, 13]
                        Name: [5, 14 -> 5, 15]
                        Default: <No Default>

                    b
                        Parameter: [5, 17 -> 5, 23]
                        Type: [5, 17 -> 5, 21]
                        Name: [5, 22 -> 5, 23]
                        Default: <No Default>
                Any:
                    <No Parameters>
                Keyword:
                    c
                        Parameter: [6, 10 -> 6, 16]
                        Type: [6, 10 -> 6, 14]
                        Name: [6, 15 -> 6, 16]
                        Default: <No Default>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[2].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func3
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(124, 130), match='String'>>> ws:None [10, 1 -> 10, 7]
            Parameters:
                Positional:
                    a
                        Parameter: [12, 9 -> 12, 14]
                        Type: [12, 9 -> 12, 12]
                        Name: [12, 13 -> 12, 14]
                        Default: <No Default>

                    b
                        Parameter: [13, 9 -> 13, 15]
                        Type: [13, 9 -> 13, 13]
                        Name: [13, 14 -> 13, 15]
                        Default: <No Default>
                Any:
                    <No Parameters>
                Keyword:
                    c
                        Parameter: [15, 9 -> 15, 15]
                        Type: [15, 9 -> 15, 13]
                        Name: [15, 14 -> 15, 15]
                        Default: <No Default>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_NewStyleWithDefaults():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            String Func1(pos: Int a, Bool bee, Char c=default_value1, key: Double d=default_value2):
                pass

            Int Func2(
                pos: Int a, Bool b,
                key: Char c=value1,
            ):
                pass

            Char Func3(
                pos:
                    Int a=value1,
                    Bool b=value2
                key:
                    Char c=value3,
                    Double d=value4
            ):
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 12), match='Func1'>>> ws:(6, 7) [1, 8 -> 1, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(12, 13), match='('>>> ws:None [1, 13 -> 1, 14]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'pos' <<Regex: <_sre.SRE_Match object; span=(13, 16), match='pos'>>> ws:None [1, 14 -> 1, 17]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=':'>>> ws:None [1, 17 -> 1, 18]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:(17, 18) [1, 19 -> 1, 22]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(22, 23), match='a'>>> ws:(21, 22) [1, 23 -> 1, 24]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [1, 24 -> 1, 25]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='Bool'>>> ws:(24, 25) [1, 26 -> 1, 30]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(30, 33), match='bee'>>> ws:(29, 30) [1, 31 -> 1, 34]
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(33, 34), match=','>>> ws:None [1, 34 -> 1, 35]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(35, 39), match='Char'>>> ws:(34, 35) [1, 36 -> 1, 40]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(40, 41), match='c'>>> ws:(39, 40) [1, 41 -> 1, 42]
                                                            Repeat: (With Default, 0, 1)
                                                                With Default
                                                                    '=' <<Regex: <_sre.SRE_Match object; span=(41, 42), match='='>>> ws:None [1, 42 -> 1, 43]
                                                                    DynamicStatementsType.Expressions
                                                                        1.0.0 Grammar
                                                                            Variable Name
                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(42, 56), match='default_value1'>>> ws:None [1, 43 -> 1, 57]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(56, 57), match=','>>> ws:None [1, 57 -> 1, 58]
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'key' <<Regex: <_sre.SRE_Match object; span=(58, 61), match='key'>>> ws:(57, 58) [1, 59 -> 1, 62]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(61, 62), match=':'>>> ws:None [1, 62 -> 1, 63]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(63, 69), match='Double'>>> ws:(62, 63) [1, 64 -> 1, 70]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(70, 71), match='d'>>> ws:(69, 70) [1, 71 -> 1, 72]
                                                    Repeat: (With Default, 0, 1)
                                                        With Default
                                                            '=' <<Regex: <_sre.SRE_Match object; span=(71, 72), match='='>>> ws:None [1, 72 -> 1, 73]
                                                            DynamicStatementsType.Expressions
                                                                1.0.0 Grammar
                                                                    Variable Name
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(72, 86), match='default_value2'>>> ws:None [1, 73 -> 1, 87]
                            ')' <<Regex: <_sre.SRE_Match object; span=(86, 87), match=')'>>> ws:None [1, 87 -> 1, 88]
                        ':' <<Regex: <_sre.SRE_Match object; span=(87, 88), match=':'>>> ws:None [1, 88 -> 1, 89]
                        Newline+ <<88, 89>> ws:None [1, 89 -> 2, 1]
                        Indent <<89, 93, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(93, 97), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<97, 99>> ws:None [2, 9 -> 4, 1]
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(99, 102), match='Int'>>> ws:None [4, 1 -> 4, 4]
                        <name> <<Regex: <_sre.SRE_Match object; span=(103, 108), match='Func2'>>> ws:(102, 103) [4, 5 -> 4, 10]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(108, 109), match='('>>> ws:None [4, 10 -> 4, 11]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'pos' <<Regex: <_sre.SRE_Match object; span=(114, 117), match='pos'>>> ws:None [5, 5 -> 5, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(117, 118), match=':'>>> ws:None [5, 8 -> 5, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(119, 122), match='Int'>>> ws:(118, 119) [5, 10 -> 5, 13]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(123, 124), match='a'>>> ws:(122, 123) [5, 14 -> 5, 15]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(124, 125), match=','>>> ws:None [5, 15 -> 5, 16]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(126, 130), match='Bool'>>> ws:(125, 126) [5, 17 -> 5, 21]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(131, 132), match='b'>>> ws:(130, 131) [5, 22 -> 5, 23]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(132, 133), match=','>>> ws:None [5, 23 -> 5, 24]
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'key' <<Regex: <_sre.SRE_Match object; span=(138, 141), match='key'>>> ws:None [6, 5 -> 6, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(141, 142), match=':'>>> ws:None [6, 8 -> 6, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(143, 147), match='Char'>>> ws:(142, 143) [6, 10 -> 6, 14]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(148, 149), match='c'>>> ws:(147, 148) [6, 15 -> 6, 16]
                                                    Repeat: (With Default, 0, 1)
                                                        With Default
                                                            '=' <<Regex: <_sre.SRE_Match object; span=(149, 150), match='='>>> ws:None [6, 16 -> 6, 17]
                                                            DynamicStatementsType.Expressions
                                                                1.0.0 Grammar
                                                                    Variable Name
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(150, 156), match='value1'>>> ws:None [6, 17 -> 6, 23]
                                                Repeat: (Trailing Delimiter, 0, 1)
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(156, 157), match=','>>> ws:None [6, 23 -> 6, 24]
                            ')' <<Regex: <_sre.SRE_Match object; span=(158, 159), match=')'>>> ws:None [7, 1 -> 7, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(159, 160), match=':'>>> ws:None [7, 2 -> 7, 3]
                        Newline+ <<160, 161>> ws:None [7, 3 -> 8, 1]
                        Indent <<161, 165, (4)>> ws:None [8, 1 -> 8, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(165, 169), match='pass'>>> ws:None [8, 5 -> 8, 9]
                                        Newline+ <<169, 171>> ws:None [8, 9 -> 10, 1]
                        Dedent <<>> ws:None [10, 1 -> 10, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(171, 175), match='Char'>>> ws:None [10, 1 -> 10, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(176, 181), match='Func3'>>> ws:(175, 176) [10, 6 -> 10, 11]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(181, 182), match='('>>> ws:None [10, 11 -> 10, 12]
                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                    Repeat: (New Style, 1, 3)
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'pos' <<Regex: <_sre.SRE_Match object; span=(187, 190), match='pos'>>> ws:None [11, 5 -> 11, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(190, 191), match=':'>>> ws:None [11, 8 -> 11, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(200, 203), match='Int'>>> ws:None [12, 9 -> 12, 12]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(204, 205), match='a'>>> ws:(203, 204) [12, 13 -> 12, 14]
                                                    Repeat: (With Default, 0, 1)
                                                        With Default
                                                            '=' <<Regex: <_sre.SRE_Match object; span=(205, 206), match='='>>> ws:None [12, 14 -> 12, 15]
                                                            DynamicStatementsType.Expressions
                                                                1.0.0 Grammar
                                                                    Variable Name
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(206, 212), match='value1'>>> ws:None [12, 15 -> 12, 21]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(212, 213), match=','>>> ws:None [12, 21 -> 12, 22]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(222, 226), match='Bool'>>> ws:None [13, 9 -> 13, 13]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(227, 228), match='b'>>> ws:(226, 227) [13, 14 -> 13, 15]
                                                            Repeat: (With Default, 0, 1)
                                                                With Default
                                                                    '=' <<Regex: <_sre.SRE_Match object; span=(228, 229), match='='>>> ws:None [13, 15 -> 13, 16]
                                                                    DynamicStatementsType.Expressions
                                                                        1.0.0 Grammar
                                                                            Variable Name
                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(229, 235), match='value2'>>> ws:None [13, 16 -> 13, 22]
                                        New Style
                                            Or: {'pos', 'any', 'key'}
                                                'key' <<Regex: <_sre.SRE_Match object; span=(240, 243), match='key'>>> ws:None [14, 5 -> 14, 8]
                                            ':' <<Regex: <_sre.SRE_Match object; span=(243, 244), match=':'>>> ws:None [14, 8 -> 14, 9]
                                            Delimited Elements
                                                Parameter
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(253, 257), match='Char'>>> ws:None [15, 9 -> 15, 13]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(258, 259), match='c'>>> ws:(257, 258) [15, 14 -> 15, 15]
                                                    Repeat: (With Default, 0, 1)
                                                        With Default
                                                            '=' <<Regex: <_sre.SRE_Match object; span=(259, 260), match='='>>> ws:None [15, 15 -> 15, 16]
                                                            DynamicStatementsType.Expressions
                                                                1.0.0 Grammar
                                                                    Variable Name
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(260, 266), match='value3'>>> ws:None [15, 16 -> 15, 22]
                                                Repeat: (Delimiter and Element, 0, None)
                                                    Delimiter and Element
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(266, 267), match=','>>> ws:None [15, 22 -> 15, 23]
                                                        Parameter
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(276, 282), match='Double'>>> ws:None [16, 9 -> 16, 15]
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(283, 284), match='d'>>> ws:(282, 283) [16, 16 -> 16, 17]
                                                            Repeat: (With Default, 0, 1)
                                                                With Default
                                                                    '=' <<Regex: <_sre.SRE_Match object; span=(284, 285), match='='>>> ws:None [16, 17 -> 16, 18]
                                                                    DynamicStatementsType.Expressions
                                                                        1.0.0 Grammar
                                                                            Variable Name
                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(285, 291), match='value4'>>> ws:None [16, 18 -> 16, 24]
                            ')' <<Regex: <_sre.SRE_Match object; span=(292, 293), match=')'>>> ws:None [17, 1 -> 17, 2]
                        ':' <<Regex: <_sre.SRE_Match object; span=(293, 294), match=':'>>> ws:None [17, 2 -> 17, 3]
                        Newline+ <<294, 295>> ws:None [17, 3 -> 18, 1]
                        Indent <<295, 299, (4)>> ws:None [18, 1 -> 18, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(299, 303), match='pass'>>> ws:None [18, 5 -> 18, 9]
                                        Newline+ <<303, 304>> ws:None [18, 9 -> 19, 1]
                        Dedent <<>> ws:None [19, 1 -> 19, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func1
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
            Parameters:
                Positional:
                    a
                        Parameter: [1, 19 -> 1, 24]
                        Type: [1, 19 -> 1, 22]
                        Name: [1, 23 -> 1, 24]
                        Default: <No Default>

                    bee
                        Parameter: [1, 26 -> 1, 34]
                        Type: [1, 26 -> 1, 30]
                        Name: [1, 31 -> 1, 34]
                        Default: <No Default>

                    c
                        Parameter: [1, 36 -> 1, 57]
                        Type: [1, 36 -> 1, 40]
                        Name: [1, 41 -> 1, 42]
                        Default:
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(42, 56), match='default_value1'>>> ws:None [1, 43 -> 1, 57]
                Any:
                    <No Parameters>
                Keyword:
                    d
                        Parameter: [1, 64 -> 1, 87]
                        Type: [1, 64 -> 1, 70]
                        Name: [1, 71 -> 1, 72]
                        Default:
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(72, 86), match='default_value2'>>> ws:None [1, 73 -> 1, 87]
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func2
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(99, 102), match='Int'>>> ws:None [4, 1 -> 4, 4]
            Parameters:
                Positional:
                    a
                        Parameter: [5, 10 -> 5, 15]
                        Type: [5, 10 -> 5, 13]
                        Name: [5, 14 -> 5, 15]
                        Default: <No Default>

                    b
                        Parameter: [5, 17 -> 5, 23]
                        Type: [5, 17 -> 5, 21]
                        Name: [5, 22 -> 5, 23]
                        Default: <No Default>
                Any:
                    <No Parameters>
                Keyword:
                    c
                        Parameter: [6, 10 -> 6, 23]
                        Type: [6, 10 -> 6, 14]
                        Name: [6, 15 -> 6, 16]
                        Default:
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(150, 156), match='value1'>>> ws:None [6, 17 -> 6, 23]
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[2].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func3
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(171, 175), match='Char'>>> ws:None [10, 1 -> 10, 5]
            Parameters:
                Positional:
                    a
                        Parameter: [12, 9 -> 12, 21]
                        Type: [12, 9 -> 12, 12]
                        Name: [12, 13 -> 12, 14]
                        Default:
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(206, 212), match='value1'>>> ws:None [12, 15 -> 12, 21]


                    b
                        Parameter: [13, 9 -> 13, 22]
                        Type: [13, 9 -> 13, 13]
                        Name: [13, 14 -> 13, 15]
                        Default:
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(229, 235), match='value2'>>> ws:None [13, 16 -> 13, 22]
                Any:
                    <No Parameters>
                Keyword:
                    c
                        Parameter: [15, 9 -> 15, 22]
                        Type: [15, 9 -> 15, 13]
                        Name: [15, 14 -> 15, 15]
                        Default:
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(260, 266), match='value3'>>> ws:None [15, 16 -> 15, 22]


                    d
                        Parameter: [16, 9 -> 16, 24]
                        Type: [16, 9 -> 16, 15]
                        Name: [16, 16 -> 16, 17]
                        Default:
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(285, 291), match='value4'>>> ws:None [16, 18 -> 16, 24]
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_NestedFunc():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            String Func1():
                Int Nested(Int a, Bool b):
                    pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 12), match='Func1'>>> ws:(6, 7) [1, 8 -> 1, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(12, 13), match='('>>> ws:None [1, 13 -> 1, 14]
                            ')' <<Regex: <_sre.SRE_Match object; span=(13, 14), match=')'>>> ws:None [1, 14 -> 1, 15]
                        ':' <<Regex: <_sre.SRE_Match object; span=(14, 15), match=':'>>> ws:None [1, 15 -> 1, 16]
                        Newline+ <<15, 16>> ws:None [1, 16 -> 2, 1]
                        Indent <<16, 20, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Function Declaration
                                        DynamicStatementsType.Types
                                            1.0.0 Grammar
                                                Standard
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(20, 23), match='Int'>>> ws:None [2, 5 -> 2, 8]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(24, 30), match='Nested'>>> ws:(23, 24) [2, 9 -> 2, 15]
                                        Parameters
                                            '(' <<Regex: <_sre.SRE_Match object; span=(30, 31), match='('>>> ws:None [2, 15 -> 2, 16]
                                            Repeat: (Or: {Repeat: (New Style, 1, 3), Traditional}, 0, 1)
                                                Or: {Repeat: (New Style, 1, 3), Traditional}
                                                    Traditional
                                                        Or: {Parameter, '/', '*'}
                                                            Parameter
                                                                DynamicStatementsType.Types
                                                                    1.0.0 Grammar
                                                                        Standard
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(31, 34), match='Int'>>> ws:None [2, 16 -> 2, 19]
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(35, 36), match='a'>>> ws:(34, 35) [2, 20 -> 2, 21]
                                                        Repeat: (Delimiter and Element, 0, None)
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(36, 37), match=','>>> ws:None [2, 21 -> 2, 22]
                                                                Or: {Parameter, '/', '*'}
                                                                    Parameter
                                                                        DynamicStatementsType.Types
                                                                            1.0.0 Grammar
                                                                                Standard
                                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(38, 42), match='Bool'>>> ws:(37, 38) [2, 23 -> 2, 27]
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(43, 44), match='b'>>> ws:(42, 43) [2, 28 -> 2, 29]
                                            ')' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=')'>>> ws:None [2, 29 -> 2, 30]
                                        ':' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=':'>>> ws:None [2, 30 -> 2, 31]
                                        Newline+ <<46, 47>> ws:None [2, 31 -> 3, 1]
                                        Indent <<47, 55, (8)>> ws:None [3, 1 -> 3, 9]
                                        Repeat: (DynamicStatementsType.Statements, 1, None)
                                            DynamicStatementsType.Statements
                                                1.0.0 Grammar
                                                    Pass
                                                        'pass' <<Regex: <_sre.SRE_Match object; span=(55, 59), match='pass'>>> ws:None [3, 9 -> 3, 13]
                                                        Newline+ <<59, 60>> ws:None [3, 13 -> 4, 1]
                                        Dedent <<>> ws:None [4, 1 -> 4, 1]
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func1
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    <No Parameters>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    # Nested
    value = str(
        node.Children[0].Children[0].Children[0].Info \
            .Statements[0].Info,
    )
    assert value == textwrap.dedent(
        """\
        Nested
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(20, 23), match='Int'>>> ws:None [2, 5 -> 2, 8]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    a
                        Parameter: [2, 16 -> 2, 21]
                        Type: [2, 16 -> 2, 19]
                        Name: [2, 20 -> 2, 21]
                        Default: <No Default>

                    b
                        Parameter: [2, 23 -> 2, 29]
                        Type: [2, 23 -> 2, 27]
                        Name: [2, 28 -> 2, 29]
                        Default: <No Default>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_FunctionNames():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            String Func?():
                pass

            String __Dunder__():
                pass
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(7, 12), match='Func?'>>> ws:(6, 7) [1, 8 -> 1, 13]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(12, 13), match='('>>> ws:None [1, 13 -> 1, 14]
                            ')' <<Regex: <_sre.SRE_Match object; span=(13, 14), match=')'>>> ws:None [1, 14 -> 1, 15]
                        ':' <<Regex: <_sre.SRE_Match object; span=(14, 15), match=':'>>> ws:None [1, 15 -> 1, 16]
                        Newline+ <<15, 16>> ws:None [1, 16 -> 2, 1]
                        Indent <<16, 20, (4)>> ws:None [2, 1 -> 2, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(20, 24), match='pass'>>> ws:None [2, 5 -> 2, 9]
                                        Newline+ <<24, 26>> ws:None [2, 9 -> 4, 1]
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Function Declaration
                        DynamicStatementsType.Types
                            1.0.0 Grammar
                                Standard
                                    <name> <<Regex: <_sre.SRE_Match object; span=(26, 32), match='String'>>> ws:None [4, 1 -> 4, 7]
                        <name> <<Regex: <_sre.SRE_Match object; span=(33, 43), match='__Dunder__'>>> ws:(32, 33) [4, 8 -> 4, 18]
                        Parameters
                            '(' <<Regex: <_sre.SRE_Match object; span=(43, 44), match='('>>> ws:None [4, 18 -> 4, 19]
                            ')' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=')'>>> ws:None [4, 19 -> 4, 20]
                        ':' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=':'>>> ws:None [4, 20 -> 4, 21]
                        Newline+ <<46, 47>> ws:None [4, 21 -> 5, 1]
                        Indent <<47, 51, (4)>> ws:None [5, 1 -> 5, 5]
                        Repeat: (DynamicStatementsType.Statements, 1, None)
                            DynamicStatementsType.Statements
                                1.0.0 Grammar
                                    Pass
                                        'pass' <<Regex: <_sre.SRE_Match object; span=(51, 55), match='pass'>>> ws:None [5, 5 -> 5, 9]
                                        Newline+ <<55, 56>> ws:None [5, 9 -> 6, 1]
                        Dedent <<>> ws:None [6, 1 -> 6, 1]
        """,
    )

    value = str(node.Children[0].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        Func?
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='String'>>> ws:None [1, 1 -> 1, 7]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    <No Parameters>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

    value = str(node.Children[1].Children[0].Children[0].Info)
    assert value == textwrap.dedent(
        """\
        __Dunder__
            Export: False
            Statements: 1
            Type:
                Standard
                    <name> <<Regex: <_sre.SRE_Match object; span=(26, 32), match='String'>>> ws:None [4, 1 -> 4, 7]
            Parameters:
                Positional:
                    <No Parameters>
                Any:
                    <No Parameters>
                Keyword:
                    <No Parameters>
            Docstring:
                <No Data>
        """,
    )

# ----------------------------------------------------------------------
def test_PositionalParameterAfterDefaultValueParameterError():
    # Traditional
    with pytest.raises(FuncParameters.NonDefaultParameterAfterDefaultValueParameterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                String val Func(Int val a, Bool val b=true, Char val c):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Parameters without a default value may not appear after a parameter with a default value has been defined"
    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 54
    assert ex.ColumnEnd == 55

    # New style
    with pytest.raises(FuncParameters.NonDefaultParameterAfterDefaultValueParameterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                String val Func(
                    pos:
                        Int val a,
                    any:
                        Bool val b=true,
                    key:
                        Char val cee,
                ):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Parameters without a default value may not appear after a parameter with a default value has been defined"
    assert ex.Line == 7
    assert ex.LineEnd == 7
    assert ex.Column == 18
    assert ex.ColumnEnd == 21

# ----------------------------------------------------------------------
def test_NewStyleParameterGroupOrderingError():
    with pytest.raises(FuncParameters.NewStyleParameterGroupOrderingError) as ex:
        Execute(
            textwrap.dedent(
                """\
                String val Func(
                    any:
                        Int val a,
                    pos:
                        Bool val b,
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

    with pytest.raises(FuncParameters.NewStyleParameterGroupOrderingError) as ex:
        Execute(
            textwrap.dedent(
                """\
                String val Func(
                    pos:
                        Int val a,
                    key:
                        Bool val b,
                    any:
                        Char val c,
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
def test_TraditionalDelimiterOrderError():
    with pytest.raises(FuncParameters.TraditionalDelimiterOrderError) as ex:
        Execute(
            textwrap.dedent(
                """\
                String val Func(Int val a, *, Bool val b, /, Char val c):
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
def test_TraditionalPositionalDelimiterError():
    with pytest.raises(FuncParameters.TraditionalPositionalDelimiterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                String val Func(/, Int val a):
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
def test_TraditionalKeywordDelimiterError():
    with pytest.raises(FuncParameters.TraditionalKeywordDelimiterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                String val Func(Int val a, *):
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
def test_TraditionalDuplicatePositionalDelimiterError():
    with pytest.raises(FuncParameters.TraditionalDuplicatePositionalDelimiterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                String val Func(Int val a, /, Bool val b, /, Char val c):
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
def test_TraditionalDuplicateKeywordDelimiterError():
    with pytest.raises(FuncParameters.TraditionalDuplicateKeywordDelimiterError) as ex:
        Execute(
            textwrap.dedent(
                """\
                String val Func(
                    Int val a, Bool val b,
                    *,
                    Char val c,
                    *,
                    Double val d,
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
def test_ErrorDuplicateNames():
    with pytest.raises(FuncParameters.DuplicateParameterNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Int val Func(Int val aaa, Bool val b, Char val aaa):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "The parameter name 'aaa' has already been specified"
    assert ex.ParameterName == "aaa"
    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 48
    assert ex.ColumnEnd == 51

# ----------------------------------------------------------------------
def test_InvalidFunctionNames():
    for invalid_name in [
        "invalidUppercase",
        "no.dots",
        "ends_with_double_under__",
        "__no_caps__",
    ]:
        with pytest.raises(NamingConventions.InvalidFunctionNameError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    String {}():
                        pass
                    """,
                ).format(invalid_name),
            )

        ex = ex.value

        expected_value = textwrap.dedent(
            """\
            '{}' is not a valid function name.

            Function names must:
                Begin with an uppercase letter
                Contain at least 2 upper-, lower-, numeric-, or underscore-characters
                Not end with double underscores (unless starting with double underscores)
            """,
        ).format(
            invalid_name,
        )

        assert str(ex) == expected_value, invalid_name
        assert ex.FunctionName == invalid_name
        assert ex.Line == 1
        assert ex.LineEnd == 1
        assert ex.Column == 8
        assert ex.ColumnEnd == 8 + len(invalid_name)

# ----------------------------------------------------------------------
def test_InvalidParameterNames():
    for invalid_name in [
        "Uppercase",
        "no.dots",
        "ends_with_double_under__",
    ]:
        with pytest.raises(NamingConventions.InvalidParameterNameError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    String Func(Int {}):
                        pass
                    """,
                ).format(invalid_name),
            )

        ex = ex.value

        expected_value = textwrap.dedent(
            """\
            '{}' is not a valid parameter name.

            Parameter names must:
                Begin with a lowercase letter
                Contain at least 1 upper-, lower-, numeric-, or underscore-characters
                Not end with double underscores
            """,
        ).format(
            invalid_name,
        )

        assert str(ex) == expected_value, invalid_name
        assert ex.ParameterName == invalid_name
        assert ex.Line == 1
        assert ex.LineEnd == 1
        assert ex.Column == 17
        assert ex.ColumnEnd == 17 + len(invalid_name)

# ----------------------------------------------------------------------
def test_DuplicateNewStyleGroupError():
    with pytest.raises(FuncParameters.NewStyleParameterGroupDuplicateError) as ex:
        Execute(
            textwrap.dedent(
                """\
                String Func(
                    pos:
                        Int a, Bool b
                    pos:
                        Char c
                ):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "The parameter group 'pos' has already been specified"
    assert ex.GroupName == "pos"
    assert ex.Line == 4
    assert ex.LineEnd == 4
    assert ex.Column == 5
    assert ex.ColumnEnd == 8

    with pytest.raises(FuncParameters.NewStyleParameterGroupDuplicateError) as ex:
        Execute(
            textwrap.dedent(
                """\
                String Func(
                    pos:
                        Int a, Bool b
                    key:
                        Char c
                    key:
                        Double d, Matrix m,
                ):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "The parameter group 'key' has already been specified"
    assert ex.GroupName == "key"
    assert ex.Line == 6
    assert ex.LineEnd == 6
    assert ex.Column == 5
    assert ex.ColumnEnd == 8
