# ----------------------------------------------------------------------
# |
# |  AsExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-18 14:10:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for AsExpression.py"""

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
    from ..AsExpression import *


# ----------------------------------------------------------------------
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            var = type as Foo
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 3), match='var'>>> ws:None [1, 1 -> 1, 4]
                        '=' <<Regex: <_sre.SRE_Match object; span=(4, 5), match='='>>> ws:(3, 4) [1, 5 -> 1, 6]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(6, 10), match='type'>>> ws:(5, 6) [1, 7 -> 1, 11]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(11, 13), match='as'>>> ws:(10, 11) [1, 12 -> 1, 14]
                                    DynamicStatements.Types
                                        1.0.0 Grammar
                                            Standard
                                                <name> <<Regex: <_sre.SRE_Match object; span=(14, 17), match='Foo'>>> ws:(13, 14) [1, 15 -> 1, 18]
                        Newline+ <<17, 18>> ws:None [1, 18 -> 2, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_Tuple():
    assert Execute(
        textwrap.dedent(
            """\
            var = type as (Foo, Bar,)

            var2 = type2 as (

                Foo,
                    Bar,
                                    Baz
            )
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 3), match='var'>>> ws:None [1, 1 -> 1, 4]
                        '=' <<Regex: <_sre.SRE_Match object; span=(4, 5), match='='>>> ws:(3, 4) [1, 5 -> 1, 6]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(6, 10), match='type'>>> ws:(5, 6) [1, 7 -> 1, 11]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(11, 13), match='as'>>> ws:(10, 11) [1, 12 -> 1, 14]
                                    DynamicStatements.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(14, 15), match='('>>> ws:(13, 14) [1, 15 -> 1, 16]
                                                    DynamicStatements.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(15, 18), match='Foo'>>> ws:None [1, 16 -> 1, 19]
                                                    Repeat: (Comma and Element, 1, None)
                                                        Comma and Element
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(18, 19), match=','>>> ws:None [1, 19 -> 1, 20]
                                                            DynamicStatements.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(20, 23), match='Bar'>>> ws:(19, 20) [1, 21 -> 1, 24]
                                                    Repeat: (',', 0, 1)
                                                        ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [1, 24 -> 1, 25]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(24, 25), match=')'>>> ws:None [1, 25 -> 1, 26]
                        Newline+ <<25, 27>> ws:None [1, 26 -> 3, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(27, 31), match='var2'>>> ws:None [3, 1 -> 3, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(32, 33), match='='>>> ws:(31, 32) [3, 6 -> 3, 7]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(34, 39), match='type2'>>> ws:(33, 34) [3, 8 -> 3, 13]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(40, 42), match='as'>>> ws:(39, 40) [3, 14 -> 3, 16]
                                    DynamicStatements.Types
                                        1.0.0 Grammar
                                            Tuple Type
                                                Multiple
                                                    '(' <<Regex: <_sre.SRE_Match object; span=(43, 44), match='('>>> ws:(42, 43) [3, 17 -> 3, 18]
                                                    DynamicStatements.Types
                                                        1.0.0 Grammar
                                                            Standard
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(50, 53), match='Foo'>>> ws:None [5, 5 -> 5, 8]
                                                    Repeat: (Comma and Element, 1, None)
                                                        Comma and Element
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(53, 54), match=','>>> ws:None [5, 8 -> 5, 9]
                                                            DynamicStatements.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(63, 66), match='Bar'>>> ws:None [6, 9 -> 6, 12]
                                                        Comma and Element
                                                            ',' <<Regex: <_sre.SRE_Match object; span=(66, 67), match=','>>> ws:None [6, 12 -> 6, 13]
                                                            DynamicStatements.Types
                                                                1.0.0 Grammar
                                                                    Standard
                                                                        <name> <<Regex: <_sre.SRE_Match object; span=(92, 95), match='Baz'>>> ws:None [7, 25 -> 7, 28]
                                                    ')' <<Regex: <_sre.SRE_Match object; span=(96, 97), match=')'>>> ws:None [8, 1 -> 8, 2]
                        Newline+ <<97, 98>> ws:None [8, 2 -> 9, 1]
        """,
    )
