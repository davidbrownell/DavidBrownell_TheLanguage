# ----------------------------------------------------------------------
# |
# |  LeftRecursiveSequencePhrase_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-23 09:09:42
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for LeftRecursiveSequencePhrase.py"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..LeftRecursiveSequencePhrase import *


# ----------------------------------------------------------------------
def test_BugBug():
    assert True
