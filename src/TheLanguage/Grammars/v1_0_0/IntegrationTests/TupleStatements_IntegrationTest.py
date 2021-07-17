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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Execute
    from .. import TupleStatements


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
                        Element
                            Single
                                '(' <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
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
                        Element
                            Single
                                '(' <<Regex: <_sre.SRE_Match object; span=(13, 14), match='('>>> ws:None [3, 1 -> 3, 2]
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
            # BugBug
            # BugBug (a, b, c, d) = var3
            # BugBug (a, b, c, d,) = var4
            # BugBug
            # BugBug (a, b,
            # BugBug     c, d,
            # BugBug         e,
            # BugBug ) = var5
            # BugBug
            # BugBug # Nested
            # BugBug (a, (b, c), d) = var6
            """,
        ),
    ) == textwrap.dedent(
        """\
        """,
    )

# BugBug: test_SingleExpression
# BugBug: test_MultipleExpression
# BugBug: test_InvalidDeclarationSingle
# BugBug: test_InvalidDeclarationMultipleFirst
# BugBug: test_InvalidDeclarationMultipleSecond
