# ----------------------------------------------------------------------
# |
# |  TupleType_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-06 18:44:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for TupleType.py"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TupleType import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def test_TupleTypes():
    assert Execute(
        textwrap.dedent(
            """\
            # Using the 'as' statement: <expr> 'as' <type>

            single = value as (Aa,)

            multiple1 = value as (Aa, Bb)
            multiple2 = value as (Aa, Bb,)

            single_multiline = value as (
                Aa
                    ,
            )
            multiple_multiline = value as (
                Aa,
                    Bb
                        ,
                    Cc,
            Dd)

            # Tuple as a variable, expression, and type
            (a, b, c) = (d, e, f) as (Gg, Hh, Ii)

            # This statement doesn't make sense, but should parse
            ((a, b), c, d) = (e, (f, g), h) as (Ii, Jj, (Kk, Ll))
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
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(57, 62), match='value'>>> ws:(56, 57) [3, 10 -> 3, 15]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(63, 65), match='as'>>> ws:(62, 63) [3, 16 -> 3, 18]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Single
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(66, 67), match='('>>> ws:(65, 66) [3, 19 -> 3, 20]
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(67, 69), match='Aa'>>> ws:None [3, 20 -> 3, 22]
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(69, 70), match=','>>> ws:None [3, 22 -> 3, 23]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(70, 71), match=')'>>> ws:None [3, 23 -> 3, 24]
                        Newline+ <<71, 73>> ws:None [3, 24 -> 5, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(73, 82), match='multiple1'>>> ws:None [5, 1 -> 5, 10]
                        '=' <<Regex: <_sre.SRE_Match object; span=(83, 84), match='='>>> ws:(82, 83) [5, 11 -> 5, 12]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(85, 90), match='value'>>> ws:(84, 85) [5, 13 -> 5, 18]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(91, 93), match='as'>>> ws:(90, 91) [5, 19 -> 5, 21]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(94, 95), match='('>>> ws:(93, 94) [5, 22 -> 5, 23]
                                                    Delimited Elements
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(95, 97), match='Aa'>>> ws:None [5, 23 -> 5, 25]
                                                        Repeat: (Delimiter and Element, 1, None)
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(97, 98), match=','>>> ws:None [5, 25 -> 5, 26]
                                                                DynamicStatementsType.Types
                                                                    1.0.0 Grammar
                                                                        Standard
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(99, 101), match='Bb'>>> ws:(98, 99) [5, 27 -> 5, 29]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(101, 102), match=')'>>> ws:None [5, 29 -> 5, 30]
                        Newline+ <<102, 103>> ws:None [5, 30 -> 6, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(103, 112), match='multiple2'>>> ws:None [6, 1 -> 6, 10]
                        '=' <<Regex: <_sre.SRE_Match object; span=(113, 114), match='='>>> ws:(112, 113) [6, 11 -> 6, 12]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(115, 120), match='value'>>> ws:(114, 115) [6, 13 -> 6, 18]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(121, 123), match='as'>>> ws:(120, 121) [6, 19 -> 6, 21]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(124, 125), match='('>>> ws:(123, 124) [6, 22 -> 6, 23]
                                                    Delimited Elements
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(125, 127), match='Aa'>>> ws:None [6, 23 -> 6, 25]
                                                        Repeat: (Delimiter and Element, 1, None)
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(127, 128), match=','>>> ws:None [6, 25 -> 6, 26]
                                                                DynamicStatementsType.Types
                                                                    1.0.0 Grammar
                                                                        Standard
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(129, 131), match='Bb'>>> ws:(128, 129) [6, 27 -> 6, 29]
                                                        Repeat: (Trailing Delimiter, 0, 1)
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(131, 132), match=','>>> ws:None [6, 29 -> 6, 30]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(132, 133), match=')'>>> ws:None [6, 30 -> 6, 31]
                        Newline+ <<133, 135>> ws:None [6, 31 -> 8, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(135, 151), match='single_multiline'>>> ws:None [8, 1 -> 8, 17]
                        '=' <<Regex: <_sre.SRE_Match object; span=(152, 153), match='='>>> ws:(151, 152) [8, 18 -> 8, 19]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(154, 159), match='value'>>> ws:(153, 154) [8, 20 -> 8, 25]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(160, 162), match='as'>>> ws:(159, 160) [8, 26 -> 8, 28]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Single
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(163, 164), match='('>>> ws:(162, 163) [8, 29 -> 8, 30]
                                                    DynamicStatementsType.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(169, 171), match='Aa'>>> ws:None [9, 5 -> 9, 7]
                                                    ',' <<Regex: <_sre.SRE_Match object; span=(180, 181), match=','>>> ws:None [10, 9 -> 10, 10]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(182, 183), match=')'>>> ws:None [11, 1 -> 11, 2]
                        Newline+ <<183, 184>> ws:None [11, 2 -> 12, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(184, 202), match='multiple_multiline'>>> ws:None [12, 1 -> 12, 19]
                        '=' <<Regex: <_sre.SRE_Match object; span=(203, 204), match='='>>> ws:(202, 203) [12, 20 -> 12, 21]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(205, 210), match='value'>>> ws:(204, 205) [12, 22 -> 12, 27]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(211, 213), match='as'>>> ws:(210, 211) [12, 28 -> 12, 30]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(214, 215), match='('>>> ws:(213, 214) [12, 31 -> 12, 32]
                                                    Delimited Elements
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(220, 222), match='Aa'>>> ws:None [13, 5 -> 13, 7]
                                                        Repeat: (Delimiter and Element, 1, None)
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(222, 223), match=','>>> ws:None [13, 7 -> 13, 8]
                                                                DynamicStatementsType.Types
                                                                    1.0.0 Grammar
                                                                        Standard
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(232, 234), match='Bb'>>> ws:None [14, 9 -> 14, 11]
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(247, 248), match=','>>> ws:None [15, 13 -> 15, 14]
                                                                DynamicStatementsType.Types
                                                                    1.0.0 Grammar
                                                                        Standard
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(257, 259), match='Cc'>>> ws:None [16, 9 -> 16, 11]
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(259, 260), match=','>>> ws:None [16, 11 -> 16, 12]
                                                                DynamicStatementsType.Types
                                                                    1.0.0 Grammar
                                                                        Standard
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(261, 263), match='Dd'>>> ws:None [17, 1 -> 17, 3]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(263, 264), match=')'>>> ws:None [17, 3 -> 17, 4]
                        Newline+ <<264, 266>> ws:None [17, 4 -> 19, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Tuple Variable Declaration
                        Tuple Element
                            Multiple
                                '(' <<Regex: <_sre.SRE_Match object; span=(310, 311), match='('>>> ws:None [20, 1 -> 20, 2]
                                Delimited Elements
                                    Or: {<name>, Tuple Element}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(311, 312), match='a'>>> ws:None [20, 2 -> 20, 3]
                                    Repeat: (Delimiter and Element, 1, None)
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(312, 313), match=','>>> ws:None [20, 3 -> 20, 4]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(314, 315), match='b'>>> ws:(313, 314) [20, 5 -> 20, 6]
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(315, 316), match=','>>> ws:None [20, 6 -> 20, 7]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(317, 318), match='c'>>> ws:(316, 317) [20, 8 -> 20, 9]
                                ')' <<Regex: <_sre.SRE_Match object; span=(318, 319), match=')'>>> ws:None [20, 9 -> 20, 10]
                        '=' <<Regex: <_sre.SRE_Match object; span=(320, 321), match='='>>> ws:(319, 320) [20, 11 -> 20, 12]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Tuple Expression
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(322, 323), match='('>>> ws:(321, 322) [20, 13 -> 20, 14]
                                                    Delimited Elements
                                                        DynamicStatementsType.Expressions
                                                            1.0.0 Grammar
                                                                Variable Name
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(323, 324), match='d'>>> ws:None [20, 14 -> 20, 15]
                                                        Repeat: (Delimiter and Element, 1, None)
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(324, 325), match=','>>> ws:None [20, 15 -> 20, 16]
                                                                DynamicStatementsType.Expressions
                                                                    1.0.0 Grammar
                                                                        Variable Name
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(326, 327), match='e'>>> ws:(325, 326) [20, 17 -> 20, 18]
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(327, 328), match=','>>> ws:None [20, 18 -> 20, 19]
                                                                DynamicStatementsType.Expressions
                                                                    1.0.0 Grammar
                                                                        Variable Name
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(329, 330), match='f'>>> ws:(328, 329) [20, 20 -> 20, 21]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(330, 331), match=')'>>> ws:None [20, 21 -> 20, 22]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(332, 334), match='as'>>> ws:(331, 332) [20, 23 -> 20, 25]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(335, 336), match='('>>> ws:(334, 335) [20, 26 -> 20, 27]
                                                    Delimited Elements
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(336, 338), match='Gg'>>> ws:None [20, 27 -> 20, 29]
                                                        Repeat: (Delimiter and Element, 1, None)
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(338, 339), match=','>>> ws:None [20, 29 -> 20, 30]
                                                                DynamicStatementsType.Types
                                                                    1.0.0 Grammar
                                                                        Standard
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(340, 342), match='Hh'>>> ws:(339, 340) [20, 31 -> 20, 33]
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(342, 343), match=','>>> ws:None [20, 33 -> 20, 34]
                                                                DynamicStatementsType.Types
                                                                    1.0.0 Grammar
                                                                        Standard
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(344, 346), match='Ii'>>> ws:(343, 344) [20, 35 -> 20, 37]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(346, 347), match=')'>>> ws:None [20, 37 -> 20, 38]
                        Newline+ <<347, 349>> ws:None [20, 38 -> 22, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Tuple Variable Declaration
                        Tuple Element
                            Multiple
                                '(' <<Regex: <_sre.SRE_Match object; span=(403, 404), match='('>>> ws:None [23, 1 -> 23, 2]
                                Delimited Elements
                                    Or: {<name>, Tuple Element}
                                        Tuple Element
                                            Multiple
                                                '(' <<Regex: <_sre.SRE_Match object; span=(404, 405), match='('>>> ws:None [23, 2 -> 23, 3]
                                                Delimited Elements
                                                    Or: {<name>, Tuple Element}
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(405, 406), match='a'>>> ws:None [23, 3 -> 23, 4]
                                                    Repeat: (Delimiter and Element, 1, None)
                                                        Delimiter and Element
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(406, 407), match=','>>> ws:None [23, 4 -> 23, 5]
                                                            Or: {<name>, Tuple Element}
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(408, 409), match='b'>>> ws:(407, 408) [23, 6 -> 23, 7]
                                                ')' <<Regex: <_sre.SRE_Match object; span=(409, 410), match=')'>>> ws:None [23, 7 -> 23, 8]
                                    Repeat: (Delimiter and Element, 1, None)
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(410, 411), match=','>>> ws:None [23, 8 -> 23, 9]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(412, 413), match='c'>>> ws:(411, 412) [23, 10 -> 23, 11]
                                        Delimiter and Element
                                            ',' <<Regex: <_sre.SRE_Match object; span=(413, 414), match=','>>> ws:None [23, 11 -> 23, 12]
                                            Or: {<name>, Tuple Element}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(415, 416), match='d'>>> ws:(414, 415) [23, 13 -> 23, 14]
                                ')' <<Regex: <_sre.SRE_Match object; span=(416, 417), match=')'>>> ws:None [23, 14 -> 23, 15]
                        '=' <<Regex: <_sre.SRE_Match object; span=(418, 419), match='='>>> ws:(417, 418) [23, 16 -> 23, 17]
                        DynamicStatementsType.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatementsType.Expressions
                                        1.0.0 Grammar
                                            Tuple Expression
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(420, 421), match='('>>> ws:(419, 420) [23, 18 -> 23, 19]
                                                    Delimited Elements
                                                        DynamicStatementsType.Expressions
                                                            1.0.0 Grammar
                                                                Variable Name
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(421, 422), match='e'>>> ws:None [23, 19 -> 23, 20]
                                                        Repeat: (Delimiter and Element, 1, None)
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(422, 423), match=','>>> ws:None [23, 20 -> 23, 21]
                                                                DynamicStatementsType.Expressions
                                                                    1.0.0 Grammar
                                                                        Tuple Expression
                                                                            Multiple
                                                                                '(' <<Regex: <_sre.SRE_Match object; span=(424, 425), match='('>>> ws:(423, 424) [23, 22 -> 23, 23]
                                                                                Delimited Elements
                                                                                    DynamicStatementsType.Expressions
                                                                                        1.0.0 Grammar
                                                                                            Variable Name
                                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(425, 426), match='f'>>> ws:None [23, 23 -> 23, 24]
                                                                                    Repeat: (Delimiter and Element, 1, None)
                                                                                        Delimiter and Element
                                                                                            ',' <<Regex: <_sre.SRE_Match object; span=(426, 427), match=','>>> ws:None [23, 24 -> 23, 25]
                                                                                            DynamicStatementsType.Expressions
                                                                                                1.0.0 Grammar
                                                                                                    Variable Name
                                                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(428, 429), match='g'>>> ws:(427, 428) [23, 26 -> 23, 27]
                                                                                ')' <<Regex: <_sre.SRE_Match object; span=(429, 430), match=')'>>> ws:None [23, 27 -> 23, 28]
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(430, 431), match=','>>> ws:None [23, 28 -> 23, 29]
                                                                DynamicStatementsType.Expressions
                                                                    1.0.0 Grammar
                                                                        Variable Name
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(432, 433), match='h'>>> ws:(431, 432) [23, 30 -> 23, 31]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(433, 434), match=')'>>> ws:None [23, 31 -> 23, 32]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(435, 437), match='as'>>> ws:(434, 435) [23, 33 -> 23, 35]
                                    DynamicStatementsType.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(438, 439), match='('>>> ws:(437, 438) [23, 36 -> 23, 37]
                                                    Delimited Elements
                                                        DynamicStatementsType.Types
                                                            1.0.0 Grammar
                                                                Standard
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(439, 441), match='Ii'>>> ws:None [23, 37 -> 23, 39]
                                                        Repeat: (Delimiter and Element, 1, None)
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(441, 442), match=','>>> ws:None [23, 39 -> 23, 40]
                                                                DynamicStatementsType.Types
                                                                    1.0.0 Grammar
                                                                        Standard
                                                                            <name> <<Regex: <_sre.SRE_Match object; span=(443, 445), match='Jj'>>> ws:(442, 443) [23, 41 -> 23, 43]
                                                            Delimiter and Element
                                                                ',' <<Regex: <_sre.SRE_Match object; span=(445, 446), match=','>>> ws:None [23, 43 -> 23, 44]
                                                                DynamicStatementsType.Types
                                                                    1.0.0 Grammar
                                                                        Tuple Type
                                                                            Multiple
                                                                                '(' <<Regex: <_sre.SRE_Match object; span=(447, 448), match='('>>> ws:(446, 447) [23, 45 -> 23, 46]
                                                                                Delimited Elements
                                                                                    DynamicStatementsType.Types
                                                                                        1.0.0 Grammar
                                                                                            Standard
                                                                                                <name> <<Regex: <_sre.SRE_Match object; span=(448, 450), match='Kk'>>> ws:None [23, 46 -> 23, 48]
                                                                                    Repeat: (Delimiter and Element, 1, None)
                                                                                        Delimiter and Element
                                                                                            ',' <<Regex: <_sre.SRE_Match object; span=(450, 451), match=','>>> ws:None [23, 48 -> 23, 49]
                                                                                            DynamicStatementsType.Types
                                                                                                1.0.0 Grammar
                                                                                                    Standard
                                                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(452, 454), match='Ll'>>> ws:(451, 452) [23, 50 -> 23, 52]
                                                                                ')' <<Regex: <_sre.SRE_Match object; span=(454, 455), match=')'>>> ws:None [23, 52 -> 23, 53]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(455, 456), match=')'>>> ws:None [23, 53 -> 23, 54]
                        Newline+ <<456, 457>> ws:None [23, 54 -> 24, 1]
        """,
    )
