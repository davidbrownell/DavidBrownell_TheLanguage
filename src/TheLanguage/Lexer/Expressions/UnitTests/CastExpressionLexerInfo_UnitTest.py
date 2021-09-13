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

from dataclasses import fields

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..CastExpressionLexerInfo import *
    from ...Common.AutomatedTests import CreateRegion

    from ...Types.StandardTypeLexerInfo import (
        StandardTypeLexerData,
        StandardTypeLexerInfo,
        StandardTypeLexerRegions,
        TypeLexerData,
    )


# ----------------------------------------------------------------------
class TestStandard(object):
    _expression_info                        = ExpressionLexerInfo(
        ExpressionLexerData(),
        LexerRegions(CreateRegion(100, 200, 300, 400)),
    )

    _type_info                              = TypeLexerInfo(
        TypeLexerData(),
        LexerRegions(CreateRegion(500, 600, 700, 800)),
    )

    # ----------------------------------------------------------------------
    def test_DataWithType(self):
        data = CastExpressionLexerData(self._expression_info, self._type_info)

        assert data.Expression == self._expression_info
        assert data.Type == self._type_info

    # ----------------------------------------------------------------------
    def test_DataWithModifier(self):
        data = CastExpressionLexerData(self._expression_info, TypeModifier.val)

        assert data.Expression == self._expression_info
        assert data.Type == TypeModifier.val

    # ----------------------------------------------------------------------
    def test_InfoWithType(self):
        info = CastExpressionLexerInfo(
            CastExpressionLexerData(self._expression_info, self._type_info),
            CastExpressionLexerRegions(
                CreateRegion(1, 2, 3, 4),
                CreateRegion(5, 6, 7, 8),
                CreateRegion(9, 10, 11, 12),
            ),
        )

        assert info.Data.Expression == self._expression_info
        assert info.Data.Type == self._type_info

        assert info.Regions.Self__ == CreateRegion(1, 2, 3, 4)
        assert info.Regions.Expression == CreateRegion(5, 6, 7, 8)
        assert info.Regions.Type == CreateRegion(9, 10, 11, 12)

    # ----------------------------------------------------------------------
    def test_InfoWithModifier(self):
        info = CastExpressionLexerInfo(
            CastExpressionLexerData(self._expression_info, TypeModifier.val),
            CastExpressionLexerRegions(
                CreateRegion(1, 2, 3, 4),
                CreateRegion(5, 6, 7, 8),
                CreateRegion(9, 10, 11, 12),
            ),
        )

        assert info.Data.Expression == self._expression_info
        assert info.Data.Type == TypeModifier.val

        assert info.Regions.Self__ == CreateRegion(1, 2, 3, 4)
        assert info.Regions.Expression == CreateRegion(5, 6, 7, 8)
        assert info.Regions.Type == CreateRegion(9, 10, 11, 12)

    # ----------------------------------------------------------------------
    def test_InfoInvalidType(self):
        with pytest.raises(TypeWithModifierError) as ex:
            CastExpressionLexerInfo(
                CastExpressionLexerData(
                    self._expression_info,
                    StandardTypeLexerInfo(
                        StandardTypeLexerData("TheType", TypeModifier.val),
                        StandardTypeLexerRegions(
                            CreateRegion(1, 2, 3, 4),
                            CreateRegion(5, 6, 7, 8),
                            CreateRegion(9, 10, 11, 12),
                        ),
                    ),
                ),
                CastExpressionLexerRegions(
                    CreateRegion(13, 14, 15, 16),
                    CreateRegion(17, 18, 19, 20),
                    CreateRegion(21, 22, 23, 24),
                ),
            )

        ex = ex.value

        assert str(ex) == "Cast expressions may specify a type or a modifier, but not both."
        assert ex.Region == CreateRegion(9, 10, 11, 12)

    # ----------------------------------------------------------------------
    def test_InfoInvalidModifier(self):
        with pytest.raises(InvalidModifierError) as ex:
            CastExpressionLexerInfo(
                CastExpressionLexerData(
                    self._expression_info,
                    TypeModifier.mutable,
                ),
                CastExpressionLexerRegions(
                    CreateRegion(1, 2, 3, 4),
                    CreateRegion(5, 6, 7, 8),
                    CreateRegion(9, 10, 11, 12),
                ),
            )

        ex = ex.value

        assert str(ex) == "'mutable' cannot be used with cast expressions; supported values are 'ref', 'val', 'view'."
        assert ex.Region == CreateRegion(9, 10, 11, 12)


# ----------------------------------------------------------------------
def test_Regions():
    region_fields = set(field.name for field in fields(CastExpressionLexerRegions))

    assert region_fields == set(["Self__", "Expression", "Type"])
