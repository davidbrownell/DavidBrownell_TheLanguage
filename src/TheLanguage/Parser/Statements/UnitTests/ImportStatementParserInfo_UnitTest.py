# ----------------------------------------------------------------------
# |
# |  ImportStatementParserInfo_UnitTest.py
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
"""Unit test for ImportStatementParserInfo.py"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ImportStatementParserInfo import *
    from ...Common.AutomatedTests import RegionCreator


# ----------------------------------------------------------------------
def test_Standard():
    region_creator = RegionCreator()

    info = ImportStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
        ],
        VisibilityModifier.public,
        "TheFilename",
        [
            ImportStatementItemParserInfo(
                [region_creator(container=True), region_creator(), region_creator()],
                "Import1",
                "Alias",
            ),
            ImportStatementItemParserInfo(
                [region_creator(container=True), region_creator(), None],
                "Import2",
                None,
            ),
        ],
        ImportType.SourceIsModule,
    )

    assert info.Visibility == VisibilityModifier.public
    assert info.ImportType == ImportType.SourceIsModule
    assert info.SourceFilename == "TheFilename"
    assert len(info.ImportItems) == 2
    assert info.ImportItems[0].Name == "Import1"
    assert info.ImportItems[0].Alias == "Alias"
    assert info.ImportItems[1].Name == "Import2"
    assert info.ImportItems[1].Alias is None

    assert info.Regions__.Self__ == region_creator[0]
    assert info.Regions__.Visibility == region_creator[1]
    assert info.Regions__.SourceFilename == region_creator[2]

    assert info.ImportItems[0].Regions__.Self__ == region_creator[3]
    assert info.ImportItems[0].Regions__.Name == region_creator[4]
    assert info.ImportItems[0].Regions__.Alias == region_creator[5]

    assert info.ImportItems[1].Regions__.Self__ == region_creator[6]
    assert info.ImportItems[1].Regions__.Name == region_creator[7]
    assert info.ImportItems[1].Regions__.Alias is None


# ----------------------------------------------------------------------
def test_DefaultVisibility():
    region_creator = RegionCreator()

    info = ImportStatementParserInfo(
        [
            region_creator(container=True),
            None,
            region_creator(),
        ],
        None,
        "TheFilename",
        [
            ImportStatementItemParserInfo(
                [region_creator(container=True), region_creator(), region_creator()],
                "Import1",
                "Alias",
            ),
        ],
        ImportType.SourceIsModule,
    )

    assert info.Visibility == VisibilityModifier.private
    assert info.Regions__.Visibility == info.Regions__.Self__
