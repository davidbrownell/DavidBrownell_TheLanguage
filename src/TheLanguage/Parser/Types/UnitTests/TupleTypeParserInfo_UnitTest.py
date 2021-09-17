# ----------------------------------------------------------------------
# |
# |  TupleTypeParserInfo_UnitTest.py
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
"""Unit test for TupleTypeParserInfo"""

import os

from dataclasses import fields

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TupleTypeParserInfo import *
    from ..StandardTypeParserInfo import *
    from ...Common.AutomatedTests import CreateRegion


# ----------------------------------------------------------------------
class TestStandard(object):
    _standard_type1                         = StandardTypeParserInfo(
        [
            CreateRegion(1, 2, 300, 400),
            CreateRegion(1, 2, 3, 4),
            None,
        ],
        "Type1",
        None,
    )

    _standard_type2                         = StandardTypeParserInfo(
        [
            CreateRegion(5, 6, 700, 800),
            CreateRegion(5, 6, 7, 8),
            CreateRegion(9, 10, 11, 12),
        ],
        "Type2",
        TypeModifier.val,
    )

    # ----------------------------------------------------------------------
    def test_Single(self):
        regions = {
            "Self__": CreateRegion(1, 2, 300, 400),
            "Types": CreateRegion(5, 6, 7, 8),
        }

        info = TupleTypeParserInfo(
            list(regions.values()),
            [self._standard_type1],
        )

        assert info.Types == [self._standard_type1]
        assert info.Regions == info.RegionsType(**regions)

    # ----------------------------------------------------------------------
    def test_Multiple(self):
        regions = {
            "Self__": CreateRegion(1, 2, 300, 400),
            "Types": CreateRegion(5, 6, 7, 8),
        }

        info = TupleTypeParserInfo(
            list(regions.values()),
            [self._standard_type1, self._standard_type2],
        )

        assert info.Types == [self._standard_type1, self._standard_type2]
        assert info.Regions == info.RegionsType(**regions)
