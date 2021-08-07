# ----------------------------------------------------------------------
# |
# |  TupleVariableDeclarationStatement_IntegrationTests.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-06 18:52:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for TupleVariableDeclarationStatement.py"""

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
    from ..TupleVariableDeclarationStatement import *
    from ...Common.AutomatedTests import Execute


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
                        DynamicStatementsType.Expressions
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
                        DynamicStatementsType.Expressions
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
                                Delimited Elements
                                    Or: {<name>, Tuple Element}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(1, 2), match='a'>>> ws:None [1, 2 -> 1, 3]
                                    Repeat: (Delimiter and Element, 1, None)
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(2, 3), match=','>>> ws:None [1, 3 -> 1, 4]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(4, 5), match='b'>>> ws:(3, 4) [1, 5 -> 1, 6]
                                ')' <<Regex: <_sre.SRE_Match object; span=(5, 6), match=')'>>> ws:None [1, 6 -> 1, 7]
                        '=' <<Regex: <_sre.SRE_Match object; span=(7, 8), match='='>>> ws:(6, 7) [1, 8 -> 1, 9]
                        DynamicStatementsType.Expressions
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
                                Delimited Elements
                                    Or: {<name>, Tuple Element}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(15, 16), match='a'>>> ws:None [2, 2 -> 2, 3]
                                    Repeat: (Delimiter and Element, 1, None)
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(16, 17), match=','>>> ws:None [2, 3 -> 2, 4]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(18, 19), match='b'>>> ws:(17, 18) [2, 5 -> 2, 6]
                                    Repeat: (Trailing Delimiter, 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(19, 20), match=','>>> ws:None [2, 6 -> 2, 7]
                                ')' <<Regex: <_sre.SRE_Match object; span=(20, 21), match=')'>>> ws:None [2, 7 -> 2, 8]
                        '=' <<Regex: <_sre.SRE_Match object; span=(22, 23), match='='>>> ws:(21, 22) [2, 9 -> 2, 10]
                        DynamicStatementsType.Expressions
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
                                Delimited Elements
                                    Or: {<name>, Tuple Element}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(31, 32), match='a'>>> ws:None [4, 2 -> 4, 3]
                                    Repeat: (Delimiter and Element, 1, None)
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(32, 33), match=','>>> ws:None [4, 3 -> 4, 4]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(34, 35), match='b'>>> ws:(33, 34) [4, 5 -> 4, 6]
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(35, 36), match=','>>> ws:None [4, 6 -> 4, 7]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(37, 38), match='c'>>> ws:(36, 37) [4, 8 -> 4, 9]
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(38, 39), match=','>>> ws:None [4, 9 -> 4, 10]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(40, 41), match='d'>>> ws:(39, 40) [4, 11 -> 4, 12]
                                ')' <<Regex: <_sre.SRE_Match object; span=(41, 42), match=')'>>> ws:None [4, 12 -> 4, 13]
                        '=' <<Regex: <_sre.SRE_Match object; span=(43, 44), match='='>>> ws:(42, 43) [4, 14 -> 4, 15]
                        DynamicStatementsType.Expressions
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
                                Delimited Elements
                                    Or: {<name>, Tuple Element}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(51, 52), match='a'>>> ws:None [5, 2 -> 5, 3]
                                    Repeat: (Delimiter and Element, 1, None)
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(52, 53), match=','>>> ws:None [5, 3 -> 5, 4]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(54, 55), match='b'>>> ws:(53, 54) [5, 5 -> 5, 6]
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(55, 56), match=','>>> ws:None [5, 6 -> 5, 7]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(57, 58), match='c'>>> ws:(56, 57) [5, 8 -> 5, 9]
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(58, 59), match=','>>> ws:None [5, 9 -> 5, 10]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(60, 61), match='d'>>> ws:(59, 60) [5, 11 -> 5, 12]
                                    Repeat: (Trailing Delimiter, 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(61, 62), match=','>>> ws:None [5, 12 -> 5, 13]
                                ')' <<Regex: <_sre.SRE_Match object; span=(62, 63), match=')'>>> ws:None [5, 13 -> 5, 14]
                        '=' <<Regex: <_sre.SRE_Match object; span=(64, 65), match='='>>> ws:(63, 64) [5, 15 -> 5, 16]
                        DynamicStatementsType.Expressions
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
                                Delimited Elements
                                    Or: {<name>, Tuple Element}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(73, 74), match='a'>>> ws:None [7, 2 -> 7, 3]
                                    Repeat: (Delimiter and Element, 1, None)
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(74, 75), match=','>>> ws:None [7, 3 -> 7, 4]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(76, 77), match='b'>>> ws:(75, 76) [7, 5 -> 7, 6]
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(77, 78), match=','>>> ws:None [7, 6 -> 7, 7]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(83, 84), match='c'>>> ws:None [8, 5 -> 8, 6]
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(84, 85), match=','>>> ws:None [8, 6 -> 8, 7]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(86, 87), match='d'>>> ws:(85, 86) [8, 8 -> 8, 9]
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(87, 88), match=','>>> ws:None [8, 9 -> 8, 10]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(97, 98), match='e'>>> ws:None [9, 9 -> 9, 10]
                                    Repeat: (Trailing Delimiter, 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(98, 99), match=','>>> ws:None [9, 10 -> 9, 11]
                                ')' <<Regex: <_sre.SRE_Match object; span=(100, 101), match=')'>>> ws:None [10, 1 -> 10, 2]
                        '=' <<Regex: <_sre.SRE_Match object; span=(102, 103), match='='>>> ws:(101, 102) [10, 3 -> 10, 4]
                        DynamicStatementsType.Expressions
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
                                Delimited Elements
                                    Or: {<name>, Tuple Element}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(120, 121), match='a'>>> ws:None [13, 2 -> 13, 3]
                                    Repeat: (Delimiter and Element, 1, None)
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(121, 122), match=','>>> ws:None [13, 3 -> 13, 4]
                                            Or: {<name>, Tuple Element}
                                                Tuple Element
                                                    Multiple
                                                        '(' <<Regex: <_sre.SRE_Match object; span=(123, 124), match='('>>> ws:(122, 123) [13, 5 -> 13, 6]
                                                        Delimited Elements
                                                            Or: {<name>, Tuple Element}
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(124, 125), match='b'>>> ws:None [13, 6 -> 13, 7]
                                                            Repeat: (Delimiter and Element, 1, None)
                                                                Delimiter and Element
                                                                    ',' <<Regex: <_sre.SRE_Match object; span=(125, 126), match=','>>> ws:None [13, 7 -> 13, 8]
                                                                    Or: {<name>, Tuple Element}
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(127, 128), match='c'>>> ws:(126, 127) [13, 9 -> 13, 10]
                                                        ')' <<Regex: <_sre.SRE_Match object; span=(128, 129), match=')'>>> ws:None [13, 10 -> 13, 11]
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(129, 130), match=','>>> ws:None [13, 11 -> 13, 12]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(131, 132), match='d'>>> ws:(130, 131) [13, 13 -> 13, 14]
                                ')' <<Regex: <_sre.SRE_Match object; span=(132, 133), match=')'>>> ws:None [13, 14 -> 13, 15]
                        '=' <<Regex: <_sre.SRE_Match object; span=(134, 135), match='='>>> ws:(133, 134) [13, 16 -> 13, 17]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(136, 140), match='var6'>>> ws:(135, 136) [13, 18 -> 13, 22]
                        Newline+ <<140, 141>> ws:None [13, 22 -> 14, 1]
        """,
    )

# ----------------------------------------------------------------------

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
                Contain at least 1 upper-, lower-, numeric-, or underscore-characters
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
                Contain at least 1 upper-, lower-, numeric-, or underscore-characters
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
                Contain at least 1 upper-, lower-, numeric-, or underscore-characters
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
                Contain at least 1 upper-, lower-, numeric-, or underscore-characters
                Not end with double underscores
            """,
        ).format(
            invalid_var,
        )

        assert str(ex) == expected_value, invalid_var
