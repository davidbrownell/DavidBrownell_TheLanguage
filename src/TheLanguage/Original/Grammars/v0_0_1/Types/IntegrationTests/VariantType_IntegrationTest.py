# ----------------------------------------------------------------------
# |
# |  VariantType_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 11:48:33
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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....IntegrationTests import *
    from ..VariantType import *


# ----------------------------------------------------------------------
def test_TwoTypes():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            (Int var | Bool) Func():
                pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultipleTypes():
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_WithNone():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            (None | Int) Func1(): pass
            (Int | None) Func2(): pass
            (Int | None | String) Func3(): pass
            """,
        ),
    )))
