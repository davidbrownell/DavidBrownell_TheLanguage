# ----------------------------------------------------------------------
# |
# |  ClassMemberStatementLexerInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 10:49:22
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ClassMemberStatementLexerInfo.py"""

import copy
import os

import dataclasses
import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ClassMemberStatementLexerInfo import *
    from ..ClassStatementLexerInfo import *
    from ...Common.AutomatedTests import CreateRegion
    from ...Types.StandardTypeLexerInfo import *


# ----------------------------------------------------------------------
class TestStandard(object):
    _type                                   = StandardTypeLexerInfo(
        [
            CreateRegion(1000, 2000, 30000, 40000),
            CreateRegion(1000, 2000, 7000, 8000),
            None,
        ],
        "TheType",
        None,

    )

    _regions                                = {
        "Self__": CreateRegion(1, 2, 3000, 4000),
        "Visibility": CreateRegion(1, 2, 3, 4),
        "Type": CreateRegion(5, 6, 7, 8),
        "Name": CreateRegion(9, 10, 11, 12),
        "ClassModifier": CreateRegion(13, 14, 15, 16),
        "DefaultValue": CreateRegion(17, 18, 19, 20),
    }

    _regions_no_default                     = copy.deepcopy(_regions)
    _regions_no_default["DefaultValue"] = None

    _class_lexer_info                       = ClassStatementLexerInfo(
        [
            CreateRegion(5, 6, 7000, 8000),
            CreateRegion(900, 1000, 1100, 1200),
            CreateRegion(1300, 1400, 1500, 1600),
            CreateRegion(1700, 1800, 1900, 2000),
            CreateRegion(2100, 2200, 2300, 2400),
            CreateRegion(2500, 2600, 2700, 2800),
            CreateRegion(2900, 3000, 3100, 3200),
            CreateRegion(3300, 3400, 3500, 3600),
            CreateRegion(3700, 3800, 3900, 4000),
            None,
        ],
        VisibilityModifier.public,
        ClassModifier.immutable,
        ClassType.Class,
        "TheClass",
        None,
        [],
        [],
    )

    _interface_lexer_info                   = ClassStatementLexerInfo(
        [
            CreateRegion(41, 42, 43000, 44000),
            CreateRegion(4500, 4600, 4700, 4800),
            CreateRegion(4900, 5000, 5100, 5200),
            CreateRegion(5300, 5400, 5500, 5600),
            CreateRegion(5700, 5800, 5900, 6000),
            CreateRegion(6100, 6200, 6300, 6400),
            CreateRegion(6500, 6600, 6700, 6800),
            CreateRegion(6900, 7000, 7100, 7200),
            CreateRegion(7300, 7400, 7500, 7600),
            None,
        ],
        VisibilityModifier.public,
        ClassModifier.immutable,
        ClassType.Interface,
        "TheInterface",
        None,
        [],
        [],
    )

    _struct_lexer_info                      = ClassStatementLexerInfo(
        [
            CreateRegion(77, 78, 79000, 80000),
            CreateRegion(8100, 8200, 8300, 8400),
            CreateRegion(8500, 8600, 8700, 8800),
            CreateRegion(8900, 9000, 9100, 9200),
            CreateRegion(9300, 9400, 9500, 9600),
            CreateRegion(9700, 9800, 9900, 10000),
            CreateRegion(10100, 10200, 10300, 10400),
            CreateRegion(10500, 10600, 10700, 10800),
            CreateRegion(10900, 11000, 11100, 11200),
            None,
        ],
        VisibilityModifier.private,
        ClassModifier.mutable,
        ClassType.Struct,
        "TheStruct",
        None,
        [],
        [],
    )

    # ----------------------------------------------------------------------
    def test_Data(self):
        info = ClassMemberStatementLexerInfo(
            list(self._regions_no_default.values()),
            self._class_lexer_info,
            VisibilityModifier.private,
            self._type,
            "MemberName",
            ClassModifier.immutable,
            None,
        )

        assert info.Visibility == VisibilityModifier.private
        assert info.Type == self._type
        assert info.Name == "MemberName"
        assert info.ClassModifier == ClassModifier.immutable
        assert info.DefaultValue is None

        assert info.Regions == info.RegionsType(**self._regions_no_default)

    # ----------------------------------------------------------------------
    def test_InfoWithDefault(self):
        info = ClassMemberStatementLexerInfo(
            list(self._regions.values()),
            self._class_lexer_info,
            VisibilityModifier.public,
            self._type,
            "MemberName",
            ClassModifier.immutable,
            self._type,
        )

        assert info.Visibility == VisibilityModifier.public
        assert info.Type == self._type
        assert info.Name == "MemberName"
        assert info.ClassModifier == ClassModifier.immutable
        assert info.DefaultValue == self._type

        assert info.Regions == info.RegionsType(**self._regions)

    # ----------------------------------------------------------------------
    def test_InvalidClassStatement(self):
        with pytest.raises(InvalidClassMemberError) as ex:
            ClassMemberStatementLexerInfo(
                list(self._regions.values()),
                None,
                VisibilityModifier.public,
                self._type,
                "MemberName",
                ClassModifier.immutable,
                None,
            )

        ex = ex.value

        assert str(ex) == "Data member statements must be enclosed within a class-like object."
        assert ex.Region == self._regions["Self__"]

    # ----------------------------------------------------------------------
    def test_NotSupported(self):
        with pytest.raises(DataMembersNotSupportedError) as ex:
            ClassMemberStatementLexerInfo(
                list(self._regions_no_default.values()),
                self._interface_lexer_info,
                VisibilityModifier.public,
                self._type,
                "MemberName",
                ClassModifier.immutable,
                None,
            )

        ex = ex.value

        assert str(ex) == "Data members are not supported for 'interface' types."
        assert ex.Region == self._regions["Self__"]

    # ----------------------------------------------------------------------
    def test_DefaultVisibility(self):
        for class_statement_info, class_modifier, expected_visibility in [
            (self._class_lexer_info, ClassModifier.immutable, VisibilityModifier.private),
            (self._struct_lexer_info, ClassModifier.mutable, VisibilityModifier.public),
        ]:
            info = ClassMemberStatementLexerInfo(
                list(self._regions_no_default.values()),
                class_statement_info,
                None,
                self._type,
                "TheMember",
                class_modifier,
                None,
            )

            assert info.ClassModifier == class_modifier

            assert info.Visibility == expected_visibility
            assert info.Regions.Visibility == self._regions_no_default["Self__"]

    # ----------------------------------------------------------------------
    def test_InvalidVisibility(self):
        with pytest.raises(InvalidMemberVisibilityError) as ex:
            ClassMemberStatementLexerInfo(
                list(self._regions_no_default.values()),
                self._struct_lexer_info,
                VisibilityModifier.private,
                self._type,
                "TheMember",
                ClassModifier.mutable,
                None,
            )

        ex = ex.value

        assert str(ex) == "'private' is not a supported visibility for members of 'struct' types; supported values are 'public'."
        assert ex.Region == self._regions_no_default["Visibility"]
        assert ex.ClassType == "struct"
        assert ex.Visibility == "private"
        assert ex.AllowedVisibilities == "'public'"

    # ----------------------------------------------------------------------
    def test_DefaultModifier(self):
        for class_statement_info, expected_modifier in [
            (self._class_lexer_info, ClassModifier.immutable),
            (self._struct_lexer_info, ClassModifier.mutable),
        ]:
            info = ClassMemberStatementLexerInfo(
                list(self._regions_no_default.values()),
                class_statement_info,
                VisibilityModifier.public,
                self._type,
                "TheMember",
                None,
                None,
            )

            assert info.ClassModifier == expected_modifier
            assert info.Regions.ClassModifier == self._regions_no_default["Self__"]

    # ----------------------------------------------------------------------
    def test_InvalidModifier(self):
        with pytest.raises(InvalidMemberClassModifierError) as ex:
            ClassMemberStatementLexerInfo(
                list(self._regions_no_default.values()),
                self._struct_lexer_info,
                VisibilityModifier.public,
                self._type,
                "TheMember",
                ClassModifier.immutable,
                None,
            )

        ex = ex.value

        assert str(ex) == "'immutable' is not a supported modifier for members of 'struct' types; supported values are 'mutable'."
        assert ex.Region == self._regions_no_default["ClassModifier"]
        assert ex.ClassType == "struct"
        assert ex.Modifier == "immutable"
        assert ex.AllowedModifiers == "'mutable'"
