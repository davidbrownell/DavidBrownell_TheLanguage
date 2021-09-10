# ----------------------------------------------------------------------
# |
# |  VariableNameLexerInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 09:35:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for VariableName.py"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..VariableNameLexerInfo import *
    from ...Common.AutomatedTests import CreateRegion


# ----------------------------------------------------------------------
def test_Data():
    data = VariableNameLexerData("TheName")

    assert data.Name == "TheName"


# ----------------------------------------------------------------------
def test_Regions():
    regions = VariableNameLexerRegions(
        CreateRegion(100, 200, 300, 400),
        CreateRegion(1, 2, 3, 4),
    )

    assert regions.Self__ == CreateRegion(100, 200, 300, 400)
    assert regions.Name == CreateRegion(1, 2, 3, 4)
