# ----------------------------------------------------------------------
# |
# |  TupleTypeLexerInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 09:20:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for TupleTypeLexerInfo"""

import os

from dataclasses import fields

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TupleTypeLexerInfo import *
    from ..StandardTypeLexerInfo import *
    from ...Common.AutomatedTests import CreateRegion


# ----------------------------------------------------------------------
class TestStandard(object):
    _standard_type1                         = StandardTypeLexerInfo(
        StandardTypeLexerData("Type1", None),
        StandardTypeLexerRegions(
            CreateRegion(100, 200, 300, 400),
            CreateRegion(1, 2, 3, 4),
            None,
        ),
    )

    _standard_type2                         = StandardTypeLexerInfo(
        StandardTypeLexerData("Type2", TypeModifier.val),
        StandardTypeLexerRegions(
            CreateRegion(500, 600, 700, 800),
            CreateRegion(5, 6, 7, 8),
            CreateRegion(9, 10, 11, 12),
        ),
    )

    # ----------------------------------------------------------------------
    def test_Single(self):
        data = TupleTypeLexerData([self._standard_type1])

        assert data.Types == [self._standard_type1]

    # ----------------------------------------------------------------------
    def test_Multiple(self):
        data = TupleTypeLexerData([self._standard_type1, self._standard_type2])

        assert data.Types == [self._standard_type1, self._standard_type2]


# ----------------------------------------------------------------------
def test_Regions():
    region_fields = set(field.name for field in fields(TupleTypeLexerRegions))

    assert region_fields == set(["Self__", "Types"])
