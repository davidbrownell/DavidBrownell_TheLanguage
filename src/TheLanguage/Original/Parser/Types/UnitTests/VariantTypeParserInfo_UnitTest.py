# ----------------------------------------------------------------------
# |
# |  VariantTypeParserInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 09:10:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for VariantTypeParserInfo.py"""

import os

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..VariantTypeParserInfo import *
    from ...Common.AutomatedTests import RegionCreator


# ----------------------------------------------------------------------
def test_Standard():
    region_creator = RegionCreator()

    info = VariantTypeParserInfo(
        [region_creator(container=True)],
        [
            TypeParserInfo([region_creator(container=True)]),
            TypeParserInfo([region_creator(container=True)]),
            None,
        ],
    )

    assert len(info.Types) == 3

    assert info.Regions__.Self__ == region_creator[0]
    assert info.Types[0].Regions__.Self__ == region_creator[1]
    assert info.Types[1].Regions__.Self__ == region_creator[2]
    assert info.Types[2] is None


# ----------------------------------------------------------------------
def test_MultipleEmptyTypesError():
    region_creator = RegionCreator()

    with pytest.raises(MultipleEmptyTypesError) as ex:
        VariantTypeParserInfo(
            [region_creator(container=True, expected_error=True)],
            [
                None,
                TypeParserInfo([region_creator(container=True)]),
                None,
                TypeParserInfo([region_creator(container=True)]),
            ],
        )

    ex = ex.value

    assert str(ex) == "Multiple 'empty' types were encountered."
    assert ex.Region == region_creator.ExpectedErrorRegion()
