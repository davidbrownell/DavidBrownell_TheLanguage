# ----------------------------------------------------------------------
# |
# |  TupleNameLexerInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 09:38:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for TupleNameLexerInfo.py"""

import os

from dataclasses import fields

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TupleNameLexerInfo import *
    from ..VariableNameLexerInfo import *
    from ...Common.AutomatedTests import CreateRegion


# ----------------------------------------------------------------------
class TestStandard(object):
    _name1                                  = NameLexerInfo(
        VariableNameLexerData("Name1"),
        VariableNameLexerRegions(
            CreateRegion(100, 200, 300, 400),
            CreateRegion(1, 2, 3, 4),
        ),
    )

    _name2                                  = NameLexerInfo(
        VariableNameLexerData("Name2"),
        VariableNameLexerRegions(
            CreateRegion(500, 600, 700, 800),
            CreateRegion(5, 6, 7, 8),
        ),
    )

    # ----------------------------------------------------------------------
    def test_Single(self):
        data = TupleNameLexerData([self._name1])

        assert data.Names == [self._name1]

    # ----------------------------------------------------------------------
    def test_Multiple(self):
        data = TupleNameLexerData([self._name1, self._name2])

        assert data.Names == [self._name1, self._name2]


# ----------------------------------------------------------------------
def test_Regions():
    regions_fields = set(field.name for field in fields(TupleNameLexerRegions))

    assert regions_fields == set(["Self__", "Names"])
