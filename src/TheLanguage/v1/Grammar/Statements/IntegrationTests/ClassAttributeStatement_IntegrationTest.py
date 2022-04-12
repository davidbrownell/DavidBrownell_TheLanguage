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
def test_Simple():
    CompareResultsFromFile(str(ExecuteParserPhrase(
        textwrap.dedent(
            """\
            class More:
                TheType1 var value1
                The.Type val value2
            """,
        ),
    )))
