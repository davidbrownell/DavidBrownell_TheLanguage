# ----------------------------------------------------------------------
# |
# |  DocstringStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-29 06:36:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for DocstringStatement.py"""

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
    from ..DocstringStatement import *
    from ...Common.AutomatedTests import ExecuteEx

    from ...Common.Impl.MultilineStatementBase import (
        InvalidMultilineHeaderError,
        InvalidMultilineFooterError,
        InvalidMultilineIndentError,
        InvalidMultilineContentError,
    )

    from .....Parser.Components.Normalize import NoClosingMultilineTokenError


# ----------------------------------------------------------------------
def test_SingleLine():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            <<<
            Single line 1.
            >>>

            class Foo():
                <<<
                Single line 2.
                >>>
                pass

            class Bar():
                <<<
                With escape \\>>>
                >>>

                pass
            """,
        ),
    )

    CompareResultsFromFile(result)

    # Item 1
    leaf, value = DocstringStatement.GetInfo(node.Children[0].Children[0].Children[0])

    assert leaf.IterBegin.Line == 1
    assert leaf.IterBegin.Column == 1
    assert leaf.IterEnd.Line == 3
    assert leaf.IterEnd.Column == 4
    assert value == "Single line 1."

    # Item 2 (This is a pain to get to)
    leaf, value = DocstringStatement.GetInfo(node.Children[1].Children[0].Children[0].Children[4].Children[1].Children[0].Children[2].Children[0].Children[0].Children[0])

    assert leaf.IterBegin.Line == 6
    assert leaf.IterBegin.Column == 5
    assert leaf.IterEnd.Line == 8
    assert leaf.IterEnd.Column == 8
    assert value == "Single line 2."

    # Item 3 (This is a pain to get to)
    leaf, value = DocstringStatement.GetInfo(node.Children[2].Children[0].Children[0].Children[4].Children[1].Children[0].Children[2].Children[0].Children[0].Children[0])

    assert leaf.IterBegin.Line == 12
    assert leaf.IterBegin.Column == 5
    assert leaf.IterEnd.Line == 14
    assert leaf.IterEnd.Column == 8
    assert value == "With escape >>>"


# ----------------------------------------------------------------------
def test_Multiline():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            <<<
            Multi
            line
            1
            >>>

            class Foo():
                <<<
                Multi
                line
                    **1**
                  **2**
                >>>
                pass

            class Bar():
                <<<
                With
                escape
                \\>>>
                more.
                >>>
                pass
            """,
        ),
    )

    CompareResultsFromFile(result)

    # Item 1
    leaf, value = DocstringStatement.GetInfo(node.Children[0].Children[0].Children[0])

    assert leaf.IterBegin.Line == 1
    assert leaf.IterBegin.Column == 1
    assert leaf.IterEnd.Line == 5
    assert leaf.IterEnd.Column == 4
    assert value == "Multi\nline\n1"

    # Item 2 (This is a pain to get to)
    leaf, value = DocstringStatement.GetInfo(node.Children[1].Children[0].Children[0].Children[4].Children[1].Children[0].Children[2].Children[0].Children[0].Children[0])

    assert leaf.IterBegin.Line == 8
    assert leaf.IterBegin.Column == 5
    assert leaf.IterEnd.Line == 13
    assert leaf.IterEnd.Column == 8
    assert value == "Multi\nline\n    **1**\n  **2**"

    # Item 3
    leaf, value = DocstringStatement.GetInfo(node.Children[2].Children[0].Children[0].Children[4].Children[1].Children[0].Children[2].Children[0].Children[0].Children[0])

    assert leaf.IterBegin.Line == 17
    assert leaf.IterBegin.Column == 5
    assert leaf.IterEnd.Line == 22
    assert leaf.IterEnd.Column == 8
    assert value == "With\nescape\n>>>\nmore."


# ----------------------------------------------------------------------
def test_InvalidHeaderError():
    with pytest.raises(NoClosingMultilineTokenError) as ex:
        ExecuteEx(
            textwrap.dedent(
                """\
                <<<This is not valid
                >>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "A closing token was not found to match this multi-line opening token."
    assert ex.Line == 2
    assert ex.Column == 1

    with pytest.raises(NoClosingMultilineTokenError) as ex:
        ExecuteEx(
            textwrap.dedent(
                """\
                if cond:
                    <<<This is not valid
                    >>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "A closing token was not found to match this multi-line opening token."
    assert ex.Line == 3
    assert ex.Column == 5


# ----------------------------------------------------------------------
def test_InvalidFooterError():
    with pytest.raises(NoClosingMultilineTokenError) as ex:
        ExecuteEx(
            textwrap.dedent(
                """\
                <<<
                Text>>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "A closing token was not found to match this multi-line opening token."
    assert ex.Line == 1
    assert ex.Column == 1

    with pytest.raises(NoClosingMultilineTokenError) as ex:
        ExecuteEx(
            textwrap.dedent(
                """\
                if cond:
                    <<<
                    Text>>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "A closing token was not found to match this multi-line opening token."
    assert ex.Line == 2
    assert ex.Column == 5


# ----------------------------------------------------------------------
def test_InvalidIndentError():
    with pytest.raises(InvalidMultilineIndentError) as ex:
        ExecuteEx(
            textwrap.dedent(
                """\
                if cond:
                    <<<
                    One
                Two
                    >>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Multi-line content must be aligned vertically with the header ('<<<') [Line 2]."
    assert ex.Region.Begin.Line == 2
    assert ex.Region.Begin.Column == 5
    assert ex.Region.End.Line == 5
    assert ex.Region.End.Column == 8

    # More complicated test
    with pytest.raises(InvalidMultilineIndentError) as ex:
        ExecuteEx(
            textwrap.dedent(
                """\
                if cond:
                    <<<
                    One
                        Two
                      Three
                   Four
                    Five
                    >>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Multi-line content must be aligned vertically with the header ('<<<') [Line 4]."
    assert ex.Region.Begin.Line == 2
    assert ex.Region.Begin.Column == 5
    assert ex.Region.End.Line == 8
    assert ex.Region.End.Column == 8

# ----------------------------------------------------------------------
def test_EmptyContentError():
    with pytest.raises(InvalidMultilineContentError) as ex:
        ExecuteEx(
            textwrap.dedent(
                """\
                <<<
                >>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Multi-line content cannot be empty."
    assert ex.Region.Begin.Line == 1
    assert ex.Region.Begin.Column == 1
    assert ex.Region.End.Line == 2
    assert ex.Region.End.Column == 4

    # With indent
    with pytest.raises(InvalidMultilineContentError) as ex:
        ExecuteEx(
            textwrap.dedent(
                """\
                if cond:
                    <<<
                    >>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Multi-line content cannot be empty."
    assert ex.Region.Begin.Line == 2
    assert ex.Region.Begin.Column == 5
    assert ex.Region.End.Line == 3
    assert ex.Region.End.Column == 8
