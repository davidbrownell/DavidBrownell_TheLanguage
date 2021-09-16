# ----------------------------------------------------------------------
# |
# |  CastExpressionLexerInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 15:10:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for CastExpressionLexerInfo.py"""

import os

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..CastExpressionLexerInfo import *
    from ...Common.AutomatedTests import CreateRegion

    from ...Types.StandardTypeLexerInfo import StandardTypeLexerInfo, TypeLexerInfo


# ----------------------------------------------------------------------
class TestStandard(object):
    _expression_info                        = ExpressionLexerInfo(
        [CreateRegion(100, 200, 300, 400)],  # type: ignore
    )

    _type_info                              = TypeLexerInfo(
        [CreateRegion(500, 600, 700, 800)],  # type: ignore
    )

    # ----------------------------------------------------------------------
    def test_InfoWithType(self):
        info = CastExpressionLexerInfo(
            [
                CreateRegion(1, 2, 300, 400),
                CreateRegion(5, 6, 7, 8),
                CreateRegion(9, 10, 11, 12),
            ],
            self._expression_info, self._type_info,
        )

        assert info.Expression == self._expression_info
        assert info.Type == self._type_info

        assert info.Regions.Self__ == CreateRegion(1, 2, 300, 400)
        assert info.Regions.Expression == CreateRegion(5, 6, 7, 8)
        assert info.Regions.Type == CreateRegion(9, 10, 11, 12)

    # ----------------------------------------------------------------------
    def test_InfoWithModifier(self):
        info = CastExpressionLexerInfo(
            [
                CreateRegion(1, 2, 300, 400),
                CreateRegion(5, 6, 7, 8),
                CreateRegion(9, 10, 11, 12),
            ],
            self._expression_info, TypeModifier.val,
        )

        assert info.Expression == self._expression_info
        assert info.Type == TypeModifier.val

        assert info.Regions.Self__ == CreateRegion(1, 2, 300, 400)
        assert info.Regions.Expression == CreateRegion(5, 6, 7, 8)
        assert info.Regions.Type == CreateRegion(9, 10, 11, 12)

    # ----------------------------------------------------------------------
    def test_InfoInvalidType(self):
        with pytest.raises(TypeWithModifierError) as ex:
            CastExpressionLexerInfo(
                [
                    CreateRegion(13, 14, 1500, 1600),
                    CreateRegion(17, 18, 19, 20),
                    CreateRegion(21, 22, 23, 24),
                ],
                self._expression_info,
                StandardTypeLexerInfo(
                    [
                        CreateRegion(1, 2, 300, 400),
                        CreateRegion(5, 6, 7, 8),
                        CreateRegion(9, 10, 11, 12),
                    ],
                    "TheType",
                    TypeModifier.val,
                ),
            )

        ex = ex.value

        assert str(ex) == "Cast expressions may specify a type or a modifier, but not both."
        assert ex.Region == CreateRegion(9, 10, 11, 12)

    # ----------------------------------------------------------------------
    def test_InfoInvalidModifier(self):
        with pytest.raises(InvalidModifierError) as ex:
            CastExpressionLexerInfo(
                [
                    CreateRegion(1, 2, 300, 400),
                    CreateRegion(5, 6, 7, 8),
                    CreateRegion(9, 10, 11, 12),
                ],
                self._expression_info,
                TypeModifier.mutable,
            )

        ex = ex.value

        assert str(ex) == "'mutable' cannot be used with cast expressions; supported values are 'ref', 'val', 'view'."
        assert ex.Region == CreateRegion(9, 10, 11, 12)
