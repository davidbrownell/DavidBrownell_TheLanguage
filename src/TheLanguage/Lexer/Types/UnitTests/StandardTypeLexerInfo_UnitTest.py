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
    regions = {
        "Self__": CreateRegion(1, 2, 300, 400),
        "TypeName": CreateRegion(5, 6, 7, 8),
        "Modifier": None,
    }

    info = StandardTypeLexerInfo(
        list(regions.values()),
        "TheName",
        None,
    )

    assert info.TypeName == "TheName"
    assert info.Modifier is None
    assert info.Regions == info.RegionsType(**regions)


# ----------------------------------------------------------------------
def test_DataWithModifier():
    regions = {
        "Self__": CreateRegion(1, 2, 300, 400),
        "TypeName": CreateRegion(5, 6, 7, 8),
        "Modifier": CreateRegion(9, 10, 11, 12),
    }

    for modifier in [
        TypeModifier.var,
        TypeModifier.val,
        TypeModifier.view,
    ]:
        info = StandardTypeLexerInfo(
            list(regions.values()),
            "TheName",
            modifier,
        )

        assert info.TypeName == "TheName"
        assert info.Modifier == modifier
        assert info.Regions == info.RegionsType(**regions)


# ----------------------------------------------------------------------
def test_InfoWithInvalidModifier():
    regions = {
        "Self__": CreateRegion(1, 2, 300, 400),
        "TypeName": CreateRegion(5, 6, 7, 8),
        "Modifier": CreateRegion(9, 10, 11, 12),
    }

    for modifier in [
        TypeModifier.mutable,
        TypeModifier.immutable,
        TypeModifier.isolated,
        TypeModifier.shared,
        TypeModifier.ref,
    ]:
        with pytest.raises(InvalidModifierError) as ex:
            StandardTypeLexerInfo(
                list(regions.values()),
                "TheName",
                modifier,
            )

        ex = ex.value

        assert str(ex) == "'{}' cannot be applied to standard types in this context; supported values are 'var', 'val', 'view'.".format(modifier.name)
        assert ex.Region == regions["Modifier"]
