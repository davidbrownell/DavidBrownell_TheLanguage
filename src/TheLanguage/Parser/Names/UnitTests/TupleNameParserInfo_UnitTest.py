# ----------------------------------------------------------------------
# |
# |  TupleNameParserInfo_UnitTest.py
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
"""Unit test for TupleNameParserInfo.py"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TupleNameParserInfo import *
    from ..VariableNameParserInfo import *
    from ...Common.AutomatedTests import CreateRegion


# ----------------------------------------------------------------------
class TestStandard(object):
    _name1                                  = VariableNameParserInfo(
        [
            CreateRegion(1, 2, 300, 400),
            CreateRegion(1, 2, 3, 4),
        ],
        "Name1",
    )

    _name2                                  = VariableNameParserInfo(
        [
            CreateRegion(5, 6, 700, 800),
            CreateRegion(5, 6, 7, 8),
        ],
        "Name2",
    )

    # ----------------------------------------------------------------------
    def test_Single(self):
        info = TupleNameParserInfo(
            [
                CreateRegion(1, 2, 3000, 4000),
                CreateRegion(1, 2, 3000, 4000),
            ],
            [self._name1],
        )

        assert info.Names == [self._name1]

    # ----------------------------------------------------------------------
    def test_Multiple(self):
        info = TupleNameParserInfo(
            [
                CreateRegion(1, 2, 3000, 4000),
                CreateRegion(1, 2, 3000, 4000),
            ],
            [self._name1, self._name2],
        )

        assert info.Names == [self._name1, self._name2]
