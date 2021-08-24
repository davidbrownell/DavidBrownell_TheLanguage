# ----------------------------------------------------------------------
# |
# |  GroupExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-23 11:27:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for GroupExpression.py"""

import os
import textwrap

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import ResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GroupExpression import *
    from ...Common.AutomatedTests import Execute

    from .....Components.Phrase import Phrase # BugBug
    from .....Phrases.DynamicPhrase import DynamicPhrase # BugBug
    import sys # BugBug


# ----------------------------------------------------------------------
def test_Standard():
    result = Execute(
        textwrap.dedent(
            """\
            value3 = (one + two - three) * (four + five)
            """,
        ),
    )

    # assert result == ResultsFromFile()

    DynamicPhrase.DisplayStats(sys.stdout, verbose=True) # BugBug
    Phrase.ParseResult.DisplayStats(sys.stdout) # BugBug
