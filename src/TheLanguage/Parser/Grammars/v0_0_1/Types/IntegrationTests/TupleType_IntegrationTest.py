# ----------------------------------------------------------------------
# |
# |  TupleType_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 22:30:25
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

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import ResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TupleType import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_Single():
    assert Execute(
        textwrap.dedent(
            """\
            (Int var,) Func():
                pass
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_Multiple():
    assert Execute(
        textwrap.dedent(
            """\
            (
                Int var,
                Char view
            ) Func():
                pass
            """,
        ),
    ) == ResultsFromFile()
