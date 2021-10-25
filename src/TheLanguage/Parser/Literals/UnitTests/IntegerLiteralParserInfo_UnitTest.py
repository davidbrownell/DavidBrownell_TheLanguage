# ----------------------------------------------------------------------
# |
# |  IntegerLiteralParserInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-22 10:12:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for IntegerLiteralParserInfo.py"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..IntegerLiteralParserInfo import *


# ----------------------------------------------------------------------
# TODO: Remove this in favor of a real test once the ParserInfo object does something more interesting
def test_Placeholder():
    assert True