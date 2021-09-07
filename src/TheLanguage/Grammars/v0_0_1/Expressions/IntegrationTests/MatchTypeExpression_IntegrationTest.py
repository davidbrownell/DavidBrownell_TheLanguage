# ----------------------------------------------------------------------
# |
# |  MatchTypeExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-31 08:36:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for MatchTypeExpression.py"""

import os
import textwrap

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import CompareResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..MatchTypeExpression import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_SingleCaseNoDefault():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value1 = (
                    match type Add1(one, two):
                        case Int1: expected1
                )

                value2 = (match type Add2(one, two):
                    case Int2,:
                        expected2
                )
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultipleCaseNoDefault():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value1 = (
                    match type Add1(one, two):
                        case Int1: expected1
                        case Int2:
                            expected2
                )
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_SingleCaseWithDefault():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value1 = (match type expr1:
                    case Int1: value1a
                    default: value1b
                )

                value2 = (
                    match type expr2:
                        case Int2:
                            value2a
                        default:
                            value2b
                )
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultipleCaseWithDefault():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value1 = (
                    match type expr1:
                        case Int1: value1a
                        case Int2: value1b
                        case Int3:
                            value1c
                        default:
                            value1d
                )
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultilineCase():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value1 = (match type expr1:
                    case Int1: (
                        true1
                            if
                                cond1
                            else
                        false1
                    )
                )

                value2 = (
                    match type expr2:
                        case Int2:
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
        ),
    )


# ----------------------------------------------------------------------
def test_MultipleTypeCaseSingleLine():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value = (
                    match type expr:
                        case Int1, Int2: value1
                )
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultipleTypeCaseSingleLineGroup():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value1 = (match type expr1:
                    case (Int1a, Int2a, Int3a,): value1a
                )
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultipleTypeCaseMultipleLine():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value1 = (
                    match type expr1:
                        case Int1, Int2: value1a
                        case (Int3, Int4,):
                            value1b
                        case (
                            Int5,
                                Int6,
                                    Int7,
                        ):
                            value1c
                        default:
                            value1d
                )
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_FuncArgument():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value = Func(
                    a,
                    (
                        match type expr:
                            case Int1: value1
                            case Int2: value2
                            default: value3
                    ),
                    b,
                )
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Complicated():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value = (
                    match type expr1:
                        case Int1: value1
                        case Int2:
                            (
                                match type Func(
                                    a,
                                    b,
                                    c,
                                ):
                                    case Char1:
                                        value2

                                    case Char2:
                                        value3

                                    default:
                                        (
                                            true
                                            if cond1 else
                                            false
                                        )
                            )
                        case Int3:
                            value4

                        default: value5


                )
                """,
            ),
        ),
    )
