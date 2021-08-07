# ----------------------------------------------------------------------
# |
# |  VariantType_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-28 00:56:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for VariantType.py"""

import os
import textwrap

from typing import cast, Generator, Union

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..VariantType import *
    from ...Common.AutomatedTests import Execute, ExecuteEx
    from ...Common.GrammarAST import RootNode
    from ...Common.NamingConventions import InvalidTypeNameError

    from .....Components.Statement import Statement


# ----------------------------------------------------------------------
def test_TwoTypes():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            var1 = value1 as (Int | Float)

            var2 = value2 as (
                String
                | Char
            )
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='var1'>>> ws:None [1, 1 -> 1, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='='>>> ws:(4, 5) [1, 6 -> 1, 7]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(7, 13), match='value1'>>> ws:(6, 7) [1, 8 -> 1, 14]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(14, 16), match='as'>>> ws:(13, 14) [1, 15 -> 1, 17]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Variant
                                                '(' <<Regex: <_sre.SRE_Match object; span=(17, 18), match='('>>> ws:(16, 17) [1, 18 -> 1, 19]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:None [1, 19 -> 1, 22]
                                                '|' <<Regex: <_sre.SRE_Match object; span=(22, 23), match='|'>>> ws:(21, 22) [1, 23 -> 1, 24]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(24, 29), match='Float'>>> ws:(23, 24) [1, 25 -> 1, 30]
                                                ')' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=')'>>> ws:None [1, 30 -> 1, 31]
                        Newline+ <<30, 32>> ws:None [1, 31 -> 3, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(32, 36), match='var2'>>> ws:None [3, 1 -> 3, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(37, 38), match='='>>> ws:(36, 37) [3, 6 -> 3, 7]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(39, 45), match='value2'>>> ws:(38, 39) [3, 8 -> 3, 14]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(46, 48), match='as'>>> ws:(45, 46) [3, 15 -> 3, 17]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Variant
                                                '(' <<Regex: <_sre.SRE_Match object; span=(49, 50), match='('>>> ws:(48, 49) [3, 18 -> 3, 19]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(55, 61), match='String'>>> ws:None [4, 5 -> 4, 11]
                                                '|' <<Regex: <_sre.SRE_Match object; span=(66, 67), match='|'>>> ws:None [5, 5 -> 5, 6]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(68, 72), match='Char'>>> ws:(67, 68) [5, 7 -> 5, 11]
                                                ')' <<Regex: <_sre.SRE_Match object; span=(73, 74), match=')'>>> ws:None [6, 1 -> 6, 2]
                        Newline+ <<74, 75>> ws:None [6, 2 -> 7, 1]
        """,
    )

    variants = list(_GenerateVariants(node))
    assert len(variants) == 2

    value = "".join([str(the_type) for the_type in variants[0].Info.Types])
    assert value == textwrap.dedent(
        """\
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:None [1, 19 -> 1, 22]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(24, 29), match='Float'>>> ws:(23, 24) [1, 25 -> 1, 30]
        """,
    )

    value = "".join([str(the_type) for the_type in variants[1].Info.Types])
    assert value == textwrap.dedent(
        """\
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(55, 61), match='String'>>> ws:None [4, 5 -> 4, 11]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(68, 72), match='Char'>>> ws:(67, 68) [5, 7 -> 5, 11]
        """,
    )

# ----------------------------------------------------------------------
def test_FourTypes():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            var1 = value1 as (Int | Float | String | Char)

            var2 = value2 as (
                A1
                | B22
                | C333
                | D4444
            )
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='var1'>>> ws:None [1, 1 -> 1, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='='>>> ws:(4, 5) [1, 6 -> 1, 7]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(7, 13), match='value1'>>> ws:(6, 7) [1, 8 -> 1, 14]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(14, 16), match='as'>>> ws:(13, 14) [1, 15 -> 1, 17]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Variant
                                                '(' <<Regex: <_sre.SRE_Match object; span=(17, 18), match='('>>> ws:(16, 17) [1, 18 -> 1, 19]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:None [1, 19 -> 1, 22]
                                                '|' <<Regex: <_sre.SRE_Match object; span=(22, 23), match='|'>>> ws:(21, 22) [1, 23 -> 1, 24]
                                                Repeat: (Sep and Type, 0, None)
                                                    Sep and Type
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(24, 29), match='Float'>>> ws:(23, 24) [1, 25 -> 1, 30]
                                                        '|' <<Regex: <_sre.SRE_Match object; span=(30, 31), match='|'>>> ws:(29, 30) [1, 31 -> 1, 32]
                                                    Sep and Type
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(32, 38), match='String'>>> ws:(31, 32) [1, 33 -> 1, 39]
                                                        '|' <<Regex: <_sre.SRE_Match object; span=(39, 40), match='|'>>> ws:(38, 39) [1, 40 -> 1, 41]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(41, 45), match='Char'>>> ws:(40, 41) [1, 42 -> 1, 46]
                                                ')' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=')'>>> ws:None [1, 46 -> 1, 47]
                        Newline+ <<46, 48>> ws:None [1, 47 -> 3, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(48, 52), match='var2'>>> ws:None [3, 1 -> 3, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(53, 54), match='='>>> ws:(52, 53) [3, 6 -> 3, 7]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(55, 61), match='value2'>>> ws:(54, 55) [3, 8 -> 3, 14]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(62, 64), match='as'>>> ws:(61, 62) [3, 15 -> 3, 17]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Variant
                                                '(' <<Regex: <_sre.SRE_Match object; span=(65, 66), match='('>>> ws:(64, 65) [3, 18 -> 3, 19]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(71, 73), match='A1'>>> ws:None [4, 5 -> 4, 7]
                                                '|' <<Regex: <_sre.SRE_Match object; span=(78, 79), match='|'>>> ws:None [5, 5 -> 5, 6]
                                                Repeat: (Sep and Type, 0, None)
                                                    Sep and Type
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(80, 83), match='B22'>>> ws:(79, 80) [5, 7 -> 5, 10]
                                                        '|' <<Regex: <_sre.SRE_Match object; span=(88, 89), match='|'>>> ws:None [6, 5 -> 6, 6]
                                                    Sep and Type
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(90, 94), match='C333'>>> ws:(89, 90) [6, 7 -> 6, 11]
                                                        '|' <<Regex: <_sre.SRE_Match object; span=(99, 100), match='|'>>> ws:None [7, 5 -> 7, 6]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(101, 106), match='D4444'>>> ws:(100, 101) [7, 7 -> 7, 12]
                                                ')' <<Regex: <_sre.SRE_Match object; span=(107, 108), match=')'>>> ws:None [8, 1 -> 8, 2]
                        Newline+ <<108, 109>> ws:None [8, 2 -> 9, 1]
        """,
    )

    variants = list(_GenerateVariants(node))
    assert len(variants) == 2

    value = "".join([str(the_type) for the_type in variants[0].Info.Types])
    assert value == textwrap.dedent(
        """\
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:None [1, 19 -> 1, 22]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(24, 29), match='Float'>>> ws:(23, 24) [1, 25 -> 1, 30]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(32, 38), match='String'>>> ws:(31, 32) [1, 33 -> 1, 39]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(41, 45), match='Char'>>> ws:(40, 41) [1, 42 -> 1, 46]
        """,
    )

    value = "".join([str(the_type) for the_type in variants[1].Info.Types])
    assert value == textwrap.dedent(
        """\
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(71, 73), match='A1'>>> ws:None [4, 5 -> 4, 7]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(80, 83), match='B22'>>> ws:(79, 80) [5, 7 -> 5, 10]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(90, 94), match='C333'>>> ws:(89, 90) [6, 7 -> 6, 11]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(101, 106), match='D4444'>>> ws:(100, 101) [7, 7 -> 7, 12]
        """,
    )

# ----------------------------------------------------------------------
def test_NestedVariant():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            var1 = value1 as ((Bool1 | Char1 | Double1) | Float1 | Matrix1)

            var2 = value2 as (
                Bool2
                | (Char2 | Double2)
                | Float2
                | Matrix2
            )

            var3 = value3 as (
                Bool3 | Char3
                | (Double3 | Float3 | Matrix3)
            )
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='var1'>>> ws:None [1, 1 -> 1, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='='>>> ws:(4, 5) [1, 6 -> 1, 7]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(7, 13), match='value1'>>> ws:(6, 7) [1, 8 -> 1, 14]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(14, 16), match='as'>>> ws:(13, 14) [1, 15 -> 1, 17]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Variant
                                                '(' <<Regex: <_sre.SRE_Match object; span=(17, 18), match='('>>> ws:(16, 17) [1, 18 -> 1, 19]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Variant
                                                            '(' <<Regex: <_sre.SRE_Match object; span=(18, 19), match='('>>> ws:None [1, 19 -> 1, 20]
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(19, 24), match='Bool1'>>> ws:None [1, 20 -> 1, 25]
                                                            '|' <<Regex: <_sre.SRE_Match object; span=(25, 26), match='|'>>> ws:(24, 25) [1, 26 -> 1, 27]
                                                            Repeat: (Sep and Type, 0, None)
                                                                Sep and Type
                                                                    DynamicStatementsType.Types
                                                                        1.0.0 Grammar
                                                                            Standard
                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(27, 32), match='Char1'>>> ws:(26, 27) [1, 28 -> 1, 33]
                                                                    '|' <<Regex: <_sre.SRE_Match object; span=(33, 34), match='|'>>> ws:(32, 33) [1, 34 -> 1, 35]
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(35, 42), match='Double1'>>> ws:(34, 35) [1, 36 -> 1, 43]
                                                            ')' <<Regex: <_sre.SRE_Match object; span=(42, 43), match=')'>>> ws:None [1, 43 -> 1, 44]
                                                '|' <<Regex: <_sre.SRE_Match object; span=(44, 45), match='|'>>> ws:(43, 44) [1, 45 -> 1, 46]
                                                Repeat: (Sep and Type, 0, None)
                                                    Sep and Type
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(46, 52), match='Float1'>>> ws:(45, 46) [1, 47 -> 1, 53]
                                                        '|' <<Regex: <_sre.SRE_Match object; span=(53, 54), match='|'>>> ws:(52, 53) [1, 54 -> 1, 55]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(55, 62), match='Matrix1'>>> ws:(54, 55) [1, 56 -> 1, 63]
                                                ')' <<Regex: <_sre.SRE_Match object; span=(62, 63), match=')'>>> ws:None [1, 63 -> 1, 64]
                        Newline+ <<63, 65>> ws:None [1, 64 -> 3, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(65, 69), match='var2'>>> ws:None [3, 1 -> 3, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(70, 71), match='='>>> ws:(69, 70) [3, 6 -> 3, 7]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(72, 78), match='value2'>>> ws:(71, 72) [3, 8 -> 3, 14]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(79, 81), match='as'>>> ws:(78, 79) [3, 15 -> 3, 17]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Variant
                                                '(' <<Regex: <_sre.SRE_Match object; span=(82, 83), match='('>>> ws:(81, 82) [3, 18 -> 3, 19]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(88, 93), match='Bool2'>>> ws:None [4, 5 -> 4, 10]
                                                '|' <<Regex: <_sre.SRE_Match object; span=(98, 99), match='|'>>> ws:None [5, 5 -> 5, 6]
                                                Repeat: (Sep and Type, 0, None)
                                                    Sep and Type
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Variant
                                                                    '(' <<Regex: <_sre.SRE_Match object; span=(100, 101), match='('>>> ws:(99, 100) [5, 7 -> 5, 8]
                                                                    DynamicStatementsType.Types
                                                                        1.0.0 Grammar
                                                                            Standard
                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(101, 106), match='Char2'>>> ws:None [5, 8 -> 5, 13]
                                                                    '|' <<Regex: <_sre.SRE_Match object; span=(107, 108), match='|'>>> ws:(106, 107) [5, 14 -> 5, 15]
                                                                    DynamicStatementsType.Types
                                                                        1.0.0 Grammar
                                                                            Standard
                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(109, 116), match='Double2'>>> ws:(108, 109) [5, 16 -> 5, 23]
                                                                    ')' <<Regex: <_sre.SRE_Match object; span=(116, 117), match=')'>>> ws:None [5, 23 -> 5, 24]
                                                        '|' <<Regex: <_sre.SRE_Match object; span=(122, 123), match='|'>>> ws:None [6, 5 -> 6, 6]
                                                    Sep and Type
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(124, 130), match='Float2'>>> ws:(123, 124) [6, 7 -> 6, 13]
                                                        '|' <<Regex: <_sre.SRE_Match object; span=(135, 136), match='|'>>> ws:None [7, 5 -> 7, 6]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(137, 144), match='Matrix2'>>> ws:(136, 137) [7, 7 -> 7, 14]
                                                ')' <<Regex: <_sre.SRE_Match object; span=(145, 146), match=')'>>> ws:None [8, 1 -> 8, 2]
                        Newline+ <<146, 148>> ws:None [8, 2 -> 10, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(148, 152), match='var3'>>> ws:None [10, 1 -> 10, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(153, 154), match='='>>> ws:(152, 153) [10, 6 -> 10, 7]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(155, 161), match='value3'>>> ws:(154, 155) [10, 8 -> 10, 14]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(162, 164), match='as'>>> ws:(161, 162) [10, 15 -> 10, 17]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Variant
                                                '(' <<Regex: <_sre.SRE_Match object; span=(165, 166), match='('>>> ws:(164, 165) [10, 18 -> 10, 19]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(171, 176), match='Bool3'>>> ws:None [11, 5 -> 11, 10]
                                                '|' <<Regex: <_sre.SRE_Match object; span=(177, 178), match='|'>>> ws:(176, 177) [11, 11 -> 11, 12]
                                                Repeat: (Sep and Type, 0, None)
                                                    Sep and Type
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(179, 184), match='Char3'>>> ws:(178, 179) [11, 13 -> 11, 18]
                                                        '|' <<Regex: <_sre.SRE_Match object; span=(189, 190), match='|'>>> ws:None [12, 5 -> 12, 6]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Variant
                                                            '(' <<Regex: <_sre.SRE_Match object; span=(191, 192), match='('>>> ws:(190, 191) [12, 7 -> 12, 8]
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(192, 199), match='Double3'>>> ws:None [12, 8 -> 12, 15]
                                                            '|' <<Regex: <_sre.SRE_Match object; span=(200, 201), match='|'>>> ws:(199, 200) [12, 16 -> 12, 17]
                                                            Repeat: (Sep and Type, 0, None)
                                                                Sep and Type
                                                                    DynamicStatementsType.Types
                                                                        1.0.0 Grammar
                                                                            Standard
                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(202, 208), match='Float3'>>> ws:(201, 202) [12, 18 -> 12, 24]
                                                                    '|' <<Regex: <_sre.SRE_Match object; span=(209, 210), match='|'>>> ws:(208, 209) [12, 25 -> 12, 26]
                                                            DynamicStatementsType.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(211, 218), match='Matrix3'>>> ws:(210, 211) [12, 27 -> 12, 34]
                                                            ')' <<Regex: <_sre.SRE_Match object; span=(218, 219), match=')'>>> ws:None [12, 34 -> 12, 35]
                                                ')' <<Regex: <_sre.SRE_Match object; span=(220, 221), match=')'>>> ws:None [13, 1 -> 13, 2]
                        Newline+ <<221, 222>> ws:None [13, 2 -> 14, 1]
        """,
    )

    variants = list(_GenerateVariants(node))
    assert len(variants) == 6

    value = "".join([str(the_type) for the_type in variants[0].Info.Types])
    assert value == textwrap.dedent(
        """\
        Variant
            '(' <<Regex: <_sre.SRE_Match object; span=(18, 19), match='('>>> ws:None [1, 19 -> 1, 20]
            DynamicStatementsType.Types
                1.0.0 Grammar
                    Standard
                        <name> <<Regex: <_sre.SRE_Match object; span=(19, 24), match='Bool1'>>> ws:None [1, 20 -> 1, 25]
            '|' <<Regex: <_sre.SRE_Match object; span=(25, 26), match='|'>>> ws:(24, 25) [1, 26 -> 1, 27]
            Repeat: (Sep and Type, 0, None)
                Sep and Type
                    DynamicStatementsType.Types
                        1.0.0 Grammar
                            Standard
                                <name> <<Regex: <_sre.SRE_Match object; span=(27, 32), match='Char1'>>> ws:(26, 27) [1, 28 -> 1, 33]
                    '|' <<Regex: <_sre.SRE_Match object; span=(33, 34), match='|'>>> ws:(32, 33) [1, 34 -> 1, 35]
            DynamicStatementsType.Types
                1.0.0 Grammar
                    Standard
                        <name> <<Regex: <_sre.SRE_Match object; span=(35, 42), match='Double1'>>> ws:(34, 35) [1, 36 -> 1, 43]
            ')' <<Regex: <_sre.SRE_Match object; span=(42, 43), match=')'>>> ws:None [1, 43 -> 1, 44]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(46, 52), match='Float1'>>> ws:(45, 46) [1, 47 -> 1, 53]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(55, 62), match='Matrix1'>>> ws:(54, 55) [1, 56 -> 1, 63]
        """,
    )

    value = "".join([str(the_type) for the_type in variants[1].Info.Types])
    assert value == textwrap.dedent(
        """\
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(19, 24), match='Bool1'>>> ws:None [1, 20 -> 1, 25]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(27, 32), match='Char1'>>> ws:(26, 27) [1, 28 -> 1, 33]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(35, 42), match='Double1'>>> ws:(34, 35) [1, 36 -> 1, 43]
        """,
    )

    value = "".join([str(the_type) for the_type in variants[2].Info.Types])
    assert value == textwrap.dedent(
        """\
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(88, 93), match='Bool2'>>> ws:None [4, 5 -> 4, 10]
        Variant
            '(' <<Regex: <_sre.SRE_Match object; span=(100, 101), match='('>>> ws:(99, 100) [5, 7 -> 5, 8]
            DynamicStatementsType.Types
                1.0.0 Grammar
                    Standard
                        <name> <<Regex: <_sre.SRE_Match object; span=(101, 106), match='Char2'>>> ws:None [5, 8 -> 5, 13]
            '|' <<Regex: <_sre.SRE_Match object; span=(107, 108), match='|'>>> ws:(106, 107) [5, 14 -> 5, 15]
            DynamicStatementsType.Types
                1.0.0 Grammar
                    Standard
                        <name> <<Regex: <_sre.SRE_Match object; span=(109, 116), match='Double2'>>> ws:(108, 109) [5, 16 -> 5, 23]
            ')' <<Regex: <_sre.SRE_Match object; span=(116, 117), match=')'>>> ws:None [5, 23 -> 5, 24]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(124, 130), match='Float2'>>> ws:(123, 124) [6, 7 -> 6, 13]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(137, 144), match='Matrix2'>>> ws:(136, 137) [7, 7 -> 7, 14]
        """,
    )

    value = "".join([str(the_type) for the_type in variants[3].Info.Types])
    assert value == textwrap.dedent(
        """\
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(101, 106), match='Char2'>>> ws:None [5, 8 -> 5, 13]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(109, 116), match='Double2'>>> ws:(108, 109) [5, 16 -> 5, 23]
        """,
    )

    value = "".join([str(the_type) for the_type in variants[4].Info.Types])
    assert value == textwrap.dedent(
        """\
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(171, 176), match='Bool3'>>> ws:None [11, 5 -> 11, 10]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(179, 184), match='Char3'>>> ws:(178, 179) [11, 13 -> 11, 18]
        Variant
            '(' <<Regex: <_sre.SRE_Match object; span=(191, 192), match='('>>> ws:(190, 191) [12, 7 -> 12, 8]
            DynamicStatementsType.Types
                1.0.0 Grammar
                    Standard
                        <name> <<Regex: <_sre.SRE_Match object; span=(192, 199), match='Double3'>>> ws:None [12, 8 -> 12, 15]
            '|' <<Regex: <_sre.SRE_Match object; span=(200, 201), match='|'>>> ws:(199, 200) [12, 16 -> 12, 17]
            Repeat: (Sep and Type, 0, None)
                Sep and Type
                    DynamicStatementsType.Types
                        1.0.0 Grammar
                            Standard
                                <name> <<Regex: <_sre.SRE_Match object; span=(202, 208), match='Float3'>>> ws:(201, 202) [12, 18 -> 12, 24]
                    '|' <<Regex: <_sre.SRE_Match object; span=(209, 210), match='|'>>> ws:(208, 209) [12, 25 -> 12, 26]
            DynamicStatementsType.Types
                1.0.0 Grammar
                    Standard
                        <name> <<Regex: <_sre.SRE_Match object; span=(211, 218), match='Matrix3'>>> ws:(210, 211) [12, 27 -> 12, 34]
            ')' <<Regex: <_sre.SRE_Match object; span=(218, 219), match=')'>>> ws:None [12, 34 -> 12, 35]
        """,
    )

    value = "".join([str(the_type) for the_type in variants[5].Info.Types])
    assert value == textwrap.dedent(
        """\
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(192, 199), match='Double3'>>> ws:None [12, 8 -> 12, 15]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(202, 208), match='Float3'>>> ws:(201, 202) [12, 18 -> 12, 24]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(211, 218), match='Matrix3'>>> ws:(210, 211) [12, 27 -> 12, 34]
        """,
    )

# ----------------------------------------------------------------------
def test_Tuple():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            var1 = value1 as (Int | (Char, Double, Float) | Matrix)
            """,
        ),
    )

    assert result == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='var1'>>> ws:None [1, 1 -> 1, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(5, 6), match='='>>> ws:(4, 5) [1, 6 -> 1, 7]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(7, 13), match='value1'>>> ws:(6, 7) [1, 8 -> 1, 14]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(14, 16), match='as'>>> ws:(13, 14) [1, 15 -> 1, 17]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Variant
                                                '(' <<Regex: <_sre.SRE_Match object; span=(17, 18), match='('>>> ws:(16, 17) [1, 18 -> 1, 19]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:None [1, 19 -> 1, 22]
                                                '|' <<Regex: <_sre.SRE_Match object; span=(22, 23), match='|'>>> ws:(21, 22) [1, 23 -> 1, 24]
                                                Repeat: (Sep and Type, 0, None)
                                                    Sep and Type
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Tuple Type
                                                                    Multiple
                                                                        '(' <<Regex: <_sre.SRE_Match object; span=(24, 25), match='('>>> ws:(23, 24) [1, 25 -> 1, 26]
                                                                        Delimited Elements
                                                                            DynamicStatementsType.Types
                                                                                1.0.0 Grammar
                                                                                    Standard
                                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='Char'>>> ws:None [1, 26 -> 1, 30]
                                                                            Repeat: (Delimiter and Element, 1, None)
                                                                                Delimiter and Element
                                                                                    ',' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=','>>> ws:None [1, 30 -> 1, 31]
                                                                                    DynamicStatementsType.Types
                                                                                        1.0.0 Grammar
                                                                                            Standard
                                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(31, 37), match='Double'>>> ws:(30, 31) [1, 32 -> 1, 38]
                                                                                Delimiter and Element
                                                                                    ',' <<Regex: <_sre.SRE_Match object; span=(37, 38), match=','>>> ws:None [1, 38 -> 1, 39]
                                                                                    DynamicStatementsType.Types
                                                                                        1.0.0 Grammar
                                                                                            Standard
                                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(39, 44), match='Float'>>> ws:(38, 39) [1, 40 -> 1, 45]
                                                                        ')' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=')'>>> ws:None [1, 45 -> 1, 46]
                                                        '|' <<Regex: <_sre.SRE_Match object; span=(46, 47), match='|'>>> ws:(45, 46) [1, 47 -> 1, 48]
                                                DynamicStatementsType.Types
                                                    1.0.0 Grammar
                                                        Standard
                                                            <name> <<Regex: <_sre.SRE_Match object; span=(48, 54), match='Matrix'>>> ws:(47, 48) [1, 49 -> 1, 55]
                                                ')' <<Regex: <_sre.SRE_Match object; span=(54, 55), match=')'>>> ws:None [1, 55 -> 1, 56]
                        Newline+ <<55, 56>> ws:None [1, 56 -> 2, 1]
        """,
    )

    variants = list(_GenerateVariants(node))
    assert len(variants) == 1

    value = "".join([str(the_type) for the_type in variants[0].Info.Types])
    assert value == textwrap.dedent(
        """\
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(18, 21), match='Int'>>> ws:None [1, 19 -> 1, 22]
        Tuple Type
            Multiple
                '(' <<Regex: <_sre.SRE_Match object; span=(24, 25), match='('>>> ws:(23, 24) [1, 25 -> 1, 26]
                Delimited Elements
                    DynamicStatementsType.Types
                        1.0.0 Grammar
                            Standard
                                <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='Char'>>> ws:None [1, 26 -> 1, 30]
                    Repeat: (Delimiter and Element, 1, None)
                        Delimiter and Element
                            ',' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=','>>> ws:None [1, 30 -> 1, 31]
                            DynamicStatementsType.Types
                                1.0.0 Grammar
                                    Standard
                                        <name> <<Regex: <_sre.SRE_Match object; span=(31, 37), match='Double'>>> ws:(30, 31) [1, 32 -> 1, 38]
                        Delimiter and Element
                            ',' <<Regex: <_sre.SRE_Match object; span=(37, 38), match=','>>> ws:None [1, 38 -> 1, 39]
                            DynamicStatementsType.Types
                                1.0.0 Grammar
                                    Standard
                                        <name> <<Regex: <_sre.SRE_Match object; span=(39, 44), match='Float'>>> ws:(38, 39) [1, 40 -> 1, 45]
                ')' <<Regex: <_sre.SRE_Match object; span=(44, 45), match=')'>>> ws:None [1, 45 -> 1, 46]
        Standard
            <name> <<Regex: <_sre.SRE_Match object; span=(48, 54), match='Matrix'>>> ws:(47, 48) [1, 49 -> 1, 55]
        """,
    )

# ----------------------------------------------------------------------
def test_InvalidType():
    # Standard
    with pytest.raises(InvalidTypeNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                var = value as (Int | invalid_name | Char)
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == textwrap.dedent(
        """\
        'invalid_name' is not a valid type name.

        Type names must:
            Begin with an uppercase letter
            Contain at least 2 upper-, lower-, numeric-, or underscore-characters
            Not end with double underscores
        """,
    )

    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 23
    assert ex.ColumnEnd == 35

    # Nested Tuple
    with pytest.raises(InvalidTypeNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                var = value as (Int | (invalid_name, Char))
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == textwrap.dedent(
        """\
        'invalid_name' is not a valid type name.

        Type names must:
            Begin with an uppercase letter
            Contain at least 2 upper-, lower-, numeric-, or underscore-characters
            Not end with double underscores
        """,
    )

    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 24
    assert ex.ColumnEnd == 36

    # Nested Variant
    with pytest.raises(InvalidTypeNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                var = value as (Int | (Double | invalid_name) | Char)
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == textwrap.dedent(
        """\
        'invalid_name' is not a valid type name.

        Type names must:
            Begin with an uppercase letter
            Contain at least 2 upper-, lower-, numeric-, or underscore-characters
            Not end with double underscores
        """,
    )

    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 33
    assert ex.ColumnEnd == 45

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _GenerateVariants(
    node: Union[GrammarDSL.Node, RootNode],
) -> Generator[GrammarDSL.Node, None, None]:
    if node.Type is not None and cast(Statement, node.Type).Name == VariantType.NODE_NAME:
        yield cast(GrammarDSL.Node, node)

    for child in node.Children:
        if isinstance(child, GrammarDSL.Node):
            yield from _GenerateVariants(child)
