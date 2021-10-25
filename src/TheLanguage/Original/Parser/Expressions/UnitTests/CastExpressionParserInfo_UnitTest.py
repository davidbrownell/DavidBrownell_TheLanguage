# ----------------------------------------------------------------------
# |
# |  CastExpressionParserInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 09:14:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for CastExpressionParserInfo.py"""

import os

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..CastExpressionParserInfo import *
    from ...Common.AutomatedTests import RegionCreator
    from ...Types.StandardTypeParserInfo import StandardTypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class DummyExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        raise Excpetion("Not implemented")


# ----------------------------------------------------------------------
def test_TypeWithModifierError():
    region_creator = RegionCreator()

    with pytest.raises(TypeWithModifierError) as ex:
        CastExpressionParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
            ],
            DummyExpressionParserInfo([region_creator(container=True)]),
            StandardTypeParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(expected_error=True),
                ],
                "TheType",
                TypeModifier.val,
            ),
        )

    ex = ex.value

    assert str(ex) == "Cast expressions may specify a type or a modifier, but not both."
    assert ex.Region == region_creator.ExpectedErrorRegion()


# ----------------------------------------------------------------------
def test_InvalidModifierError():
    region_creator = RegionCreator()

    with pytest.raises(InvalidModifierError) as ex:
        CastExpressionParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(expected_error=True),
            ],
            DummyExpressionParserInfo([region_creator(container=True),]),
            TypeModifier.mutable,
        )

    ex = ex.value

    assert str(ex) == "'mutable' cannot be used in cast expressions; supported values are 'ref', 'val', 'view'."
    assert ex.Region == region_creator.ExpectedErrorRegion()
