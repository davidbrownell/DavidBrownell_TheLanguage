# ----------------------------------------------------------------------
# |
# |  VariantType_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 14:40:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for VariantType.py"""

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
    from ..VariantType import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_TwoTypes():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                (Int var | Bool) Func():
                    pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultipleTypes():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                (
                    Int var
                    | Char view
                    | Double
                    | Foo var
                ) Func():
                    pass
                """,
            ),
        ),
    )
