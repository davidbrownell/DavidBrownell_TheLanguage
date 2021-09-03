# ----------------------------------------------------------------------
# |
# |  ClassCompilerStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-03 11:41:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for ClassCompilerStatement.py"""

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
    from ..ClassCompilerStatement import *
    from ...Common.AutomatedTests import Execute

    from ...Common.Impl.MultilineStatementBase import (
        InvalidMultilineHeaderError,
        InvalidMultilineFooterError,
        InvalidMultilineIndentError,
        InvalidMultilineContentError,
    )

    from .....Components.Normalize import NoClosingMultilineTokenError


# ----------------------------------------------------------------------
def test_SingleLine():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                <<<!!!
                Single line 1.
                !!!>>>

                if cond:
                    <<<!!!
                    Single line 2.
                    !!!>>>

                <<<!!!
                With escape \\!!!>>>
                !!!>>>
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Multiline():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                <<<!!!
                Multi
                line
                1
                !!!>>>

                if cond:
                    <<<!!!
                    Multi
                    line
                        **1**
                      **2**
                    !!!>>>

                <<<!!!
                With
                escape
                \\!!!>>>
                more.
                !!!>>>
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Nested():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                <<<!!!
                We should see

                <<<
                All
                >>>

                of this content.
                !!!>>>
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_InvalidHeaderError():
    with pytest.raises(NoClosingMultilineTokenError) as ex:
        Execute(
            textwrap.dedent(
                """\
                <<<!!!This is not valid
                !!!>>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "A closing token was not found to match this multi-line opening token."
    assert ex.Line == 2
    assert ex.Column == 1

    with pytest.raises(NoClosingMultilineTokenError) as ex:
        Execute(
            textwrap.dedent(
                """\
                if cond:
                    <<<!!!This is not valid
                    !!!>>>
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
        Execute(
            textwrap.dedent(
                """\
                <<<!!!
                Text!!!>>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "A closing token was not found to match this multi-line opening token."
    assert ex.Line == 1
    assert ex.Column == 1

    with pytest.raises(NoClosingMultilineTokenError) as ex:
        Execute(
            textwrap.dedent(
                """\
                if cond:
                    <<<!!!
                    Text!!!>>>
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
        Execute(
            textwrap.dedent(
                """\
                if cond:
                    <<<!!!
                    One
                Two
                    !!!>>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Multi-line content must be aligned vertically with the header ('<<<!!!') [Line 2]."
    assert ex.Line == 2
    assert ex.Column == 5
    assert ex.LineEnd == 5
    assert ex.ColumnEnd == 11

    # More complicated test
    with pytest.raises(InvalidMultilineIndentError) as ex:
        Execute(
            textwrap.dedent(
                """\
                if cond:
                    <<<!!!
                    One
                        Two
                      Three
                   Four
                    Five
                    !!!>>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Multi-line content must be aligned vertically with the header ('<<<!!!') [Line 4]."
    assert ex.Line == 2
    assert ex.Column == 5
    assert ex.LineEnd == 8
    assert ex.ColumnEnd == 11

# ----------------------------------------------------------------------
def test_EmptyContentError():
    with pytest.raises(InvalidMultilineContentError) as ex:
        Execute(
            textwrap.dedent(
                """\
                <<<!!!
                !!!>>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Multi-line content cannot be empty."
    assert ex.Line == 1
    assert ex.Column == 1
    assert ex.LineEnd == 2
    assert ex.ColumnEnd == 7

    # With indent
    with pytest.raises(InvalidMultilineContentError) as ex:
        Execute(
            textwrap.dedent(
                """\
                if cond:
                    <<<!!!
                    !!!>>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Multi-line content cannot be empty."
    assert ex.Line == 2
    assert ex.Column == 5
    assert ex.LineEnd == 3
    assert ex.ColumnEnd == 11
