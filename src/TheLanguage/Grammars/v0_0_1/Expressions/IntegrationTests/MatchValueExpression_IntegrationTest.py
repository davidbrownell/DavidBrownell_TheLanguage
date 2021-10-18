# ----------------------------------------------------------------------
# |
# |  MatchValueExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 10:33:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for MatchValueExpression.py"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....IntegrationTests import *
    from ..MatchValueExpression import *


# ----------------------------------------------------------------------
def test_SingleCaseNoDefault():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = (
                match value Add1(one, two):
                    case three: expected1
            )

            value2 = (match value Add2(one, two):
                case three,:
                    expected2
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultipleCaseNoDefault():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = (
                match value Add1(one, two):
                    case three: expected1
                    case four:
                        unexpected1
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_SingleCaseWithDefault():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = (match value expr1:
                case case1: value1a
                default: value1b
            )

            value2 = (
                match value expr2:
                    case case2:
                        value2a
                    default:
                        value2b
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultipleCaseWithDefault():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = (
                match value expr1:
                    case case1: value1a
                    case case2: value1b
                    case case3:
                        value1c
                    default:
                        value1d
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultilineCase():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = (match value expr1:
                case case1: (
                    true1
                        if
                            cond1
                        else
                    false1
                )
            )

            value2 = (
                match value expr2:
                    case case2:
                        (
                            true2
                                if
                                    cond2
                                else
                            false2
                        )
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultipleTypeCaseSingleLine():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value = (
                match value expr:
                    case case1, case2: value1
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultipleTypeCaseSingleLineGroup():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = (match value expr1:
                case (case1, case2, case3,): value1a
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultipleTypeCaseMultipleLine():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = (
                match value expr1:
                    case case1, case2: value1a
                    case (case3, case4,):
                        value1b
                    case (
                        case5,
                            case6,
                                case7,
                    ):
                        value1c
                    default:
                        value1d
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_FuncArgument():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value = Func(
                a,
                (
                    match value expr:
                        case case1: value1
                        case case2: value2
                        default: value3
                ),
                b,
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_Complicated():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value = (
                match value expr1:
                    case case1: value1
                    case case2:
                        (
                            match value Func(
                                a,
                                b,
                                c,
                            ):
                                case case3:
                                    value3

                                case case4:
                                    value4

                                default:
                                    (
                                        true
                                        if cond1 else
                                        false
                                    )
                        )
                    case case5:
                        value5

                    default: value6


            )
            """,
        ),
    )))
