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
    from ...Common.AutomatedTests import CreateRegion
    from ...Types.StandardTypeParserInfo import StandardTypeParserInfo


# ----------------------------------------------------------------------
def test_TypeWithModifierError():
    with pytest.raises(TypeWithModifierError) as ex:
        CastExpressionParserInfo(
            [
                CreateRegion(1, 2, 3000, 4000),
                CreateRegion(5, 6, 7, 8),
                CreateRegion(9, 10, 11, 12),
            ],
            ExpressionParserInfo([CreateRegion(13, 14, 150, 160)]),
            StandardTypeParserInfo(
                [
                    CreateRegion(17, 18, 190, 200),
                    CreateRegion(21, 22, 23, 24),
                    CreateRegion(25, 26, 27, 28),
                ],
                "TheType",
                TypeModifier.val,
            ),
        )

    ex = ex.value

    assert str(ex) == "Cast expressions may specify a type or a modifier, but not both."
    assert ex.Region == CreateRegion(25, 26, 27, 28)


# ----------------------------------------------------------------------
def test_InvalidModifierError():
    with pytest.raises(InvalidModifierError) as ex:
        CastExpressionParserInfo(
            [
                CreateRegion(1, 2, 3000, 4000),
                CreateRegion(5, 6, 7, 8),
                CreateRegion(9, 10, 11, 12),
            ],
            ExpressionParserInfo([CreateRegion(13, 14, 150, 160)]),
            TypeModifier.mutable,
        )

    ex = ex.value

    assert str(ex) == "'mutable' cannot be used in cast expressions; supported values are 'ref', 'val', 'view'."
    assert ex.Region == CreateRegion(9, 10, 11, 12)
