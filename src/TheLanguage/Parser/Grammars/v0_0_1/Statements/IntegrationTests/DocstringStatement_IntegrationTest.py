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
    from ...Common.AutomatedTests import Execute
    from .....Components.Normalize import NoClosingMultilineTokenError


# ----------------------------------------------------------------------
def test_SingleLine():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                <<<
                Single line 1.
                >>>

                if cond:
                    <<<
                    Single line 2.
                    >>>

                <<<
                With escape \\>>>
                >>>
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultiLine():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                <<<
                Multi
                line
                1
                >>>

                if cond:
                    <<<
                    Multi
                    line
                        **1**
                      **2**
                    >>>

                <<<
                With
                escape
                \\>>>
                more.
                >>>
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
        Execute(
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
        Execute(
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
        Execute(
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
    with pytest.raises(InvalidDocstringIndentError) as ex:
        Execute(
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

    assert str(ex) == "Docstring content must be aligned vertically with the header ('<<<') [Docstring line 2]."
    assert ex.Line == 2
    assert ex.Column == 5
    assert ex.LineEnd == 5
    assert ex.ColumnEnd == 8

    # More complicated test
    with pytest.raises(InvalidDocstringIndentError) as ex:
        Execute(
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

    assert str(ex) == "Docstring content must be aligned vertically with the header ('<<<') [Docstring line 4]."
    assert ex.Line == 2
    assert ex.Column == 5
    assert ex.LineEnd == 8
    assert ex.ColumnEnd == 8

# ----------------------------------------------------------------------
def test_EmptyContentError():
    with pytest.raises(InvalidDocstringContentError) as ex:
        Execute(
            textwrap.dedent(
                """\
                <<<
                >>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Docstrings cannot be empty."
    assert ex.Line == 1
    assert ex.Column == 1
    assert ex.LineEnd == 2
    assert ex.ColumnEnd == 4

    # With indent
    with pytest.raises(InvalidDocstringContentError) as ex:
        Execute(
            textwrap.dedent(
                """\
                if cond:
                    <<<
                    >>>
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Docstrings cannot be empty."
    assert ex.Line == 2
    assert ex.Column == 5
    assert ex.LineEnd == 3
    assert ex.ColumnEnd == 8
