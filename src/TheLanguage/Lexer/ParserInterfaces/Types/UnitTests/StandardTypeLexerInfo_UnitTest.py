# ----------------------------------------------------------------------
# |
# |  StandardTypeLexerInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 08:45:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for StandardTypeLexerInfo.py"""

import os

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..StandardTypeLexerInfo import *
    from ...Common.AutomatedTests import CreateRegion


# ----------------------------------------------------------------------
def test_DataNoModifier():
    data = StandardTypeLexerData("TheName", None)

    assert data.TypeName == "TheName"
    assert data.Modifier is None


# ----------------------------------------------------------------------
def test_DataWithModifier():
    for modifier in [
        TypeModifier.var,
        TypeModifier.val,
        TypeModifier.view,
    ]:
        data = StandardTypeLexerData("TheName", modifier)

        assert data.TypeName == "TheName"
        assert data.Modifier == modifier


# ----------------------------------------------------------------------
def test_RegionsNoModifier():
    regions = StandardTypeLexerRegions(
        CreateRegion(100, 200, 300, 400),
        CreateRegion(1, 2, 3, 4),
        None,
    )

    assert regions.Self__ == CreateRegion(100, 200, 300, 400)
    assert regions.TypeName == CreateRegion(1, 2, 3, 4)
    assert regions.Modifier is None


# ----------------------------------------------------------------------
def test_RegionsWithModifier():
    regions = StandardTypeLexerRegions(
        CreateRegion(100, 200, 300, 400),
        CreateRegion(1, 2, 3, 4),
        CreateRegion(5, 6, 7, 8),
    )

    assert regions.Self__ == CreateRegion(100, 200, 300, 400)
    assert regions.TypeName == CreateRegion(1, 2, 3, 4)
    assert regions.Modifier == CreateRegion(5, 6, 7, 8)


# ----------------------------------------------------------------------
def test_Info():
    data = StandardTypeLexerData("TheName", None)
    regions = StandardTypeLexerRegions(
        CreateRegion(100, 200, 300, 400),
        CreateRegion(1, 2, 3, 4),
        None,
    )

    info = StandardTypeLexerInfo(data, regions)

    assert info.Data == data
    assert info.Regions == regions


# ----------------------------------------------------------------------
def test_InfoWithInvalidModifier():
    for modifier in [
        TypeModifier.mutable,
        TypeModifier.immutable,
        TypeModifier.isolated,
        TypeModifier.shared,
        TypeModifier.ref,
    ]:
        with pytest.raises(InvalidModifierError) as ex:
            StandardTypeLexerInfo(
                StandardTypeLexerData("TheName", modifier),
                StandardTypeLexerRegions(
                    CreateRegion(100, 200, 300, 400),
                    CreateRegion(1, 2, 3, 4),
                    CreateRegion(5, 6, 7, 8),
                ),
            )

        ex = ex.value

        assert str(ex) == "'{}' cannot be applied to standard types in this context.".format(modifier.name)
        assert ex.Region == CreateRegion(5, 6, 7, 8)
