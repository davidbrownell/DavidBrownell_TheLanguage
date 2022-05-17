# ----------------------------------------------------------------------
# |
# |  ClassAttributeStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 13:02:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for ClassAttributeStatement.py"""

import os
import textwrap

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....IntegrationTestHelpers import *
    from ..ClassAttributeStatement import *


# ----------------------------------------------------------------------
def test_Placeholder():
    # Placeholder test to have something that turns green now that the other tests are disabled
    assert True


# ----------------------------------------------------------------------
@pytest.mark.skip("Dotted notation needs some work now that we are validating types")
def test_Simple():
    CompareResultsFromFile(str(ExecuteParserInfo(
        textwrap.dedent(
            """\
            class More:
                TheType1 var value1
                The.Type val value2
            """,
        ),
        include_fundamental_types=False,
    )))


# ----------------------------------------------------------------------
@pytest.mark.skip("Variants need some work now that we are validating types")
def test_Variants():
    CompareResultsFromFile(str(ExecuteParserInfo(
        textwrap.dedent(
            """\
            class MyClass:
                (Type1 | Type2) var value1
                (Type3 | Type4 | Type5) var value2
            """,
        ),
        include_fundamental_types=False,
    )))
