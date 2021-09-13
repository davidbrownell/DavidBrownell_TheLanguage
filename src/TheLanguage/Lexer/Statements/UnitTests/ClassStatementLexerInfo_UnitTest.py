# ----------------------------------------------------------------------
# |
# |  ClassStatementLexerInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 09:52:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ClassStatementLexerInfo.py"""

import copy
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
    from ..ClassStatementLexerInfo import *
    from ...Common.AutomatedTests import CreateRegion


# ----------------------------------------------------------------------
def test_ClassDependencyLexerData():
    data = ClassDependencyLexerData(VisibilityModifier.public, "Dependency")

    assert data.Visibility == VisibilityModifier.public
    assert data.Name == "Dependency"


# ----------------------------------------------------------------------
def test_ClassDepdendencyLexerRegions():
    regions_fields = set(field.name for field in fields(ClassDependencyLexerRegions))

    assert regions_fields == set(["Self__", "Visibility", "Name"])


# ----------------------------------------------------------------------
def test_ClassDependencyLexerInfoExplicitVisibility():
    info = ClassDependencyLexerInfo(
        ClassDependencyLexerRegions(
            CreateRegion(1, 2, 3000, 4000),
            CreateRegion(1, 2, 3, 4),
            CreateRegion(5, 6, 7, 8),
        ),
        VisibilityModifier.public,
        "DependencyName",
    )

    assert info.Data.Visibility == VisibilityModifier.public
    assert info.Data.Name == "DependencyName"
    assert info.Regions.Self__ == CreateRegion(1, 2, 3000, 4000)
    assert info.Regions.Visibility == CreateRegion(1, 2, 3, 4)
    assert info.Regions.Name == CreateRegion(5, 6, 7, 8)


# ----------------------------------------------------------------------
def test_ClassDependencyLexerInfoDefaultVisibility():
    info = ClassDependencyLexerInfo(
        ClassDependencyLexerRegions(
            CreateRegion(1, 2, 3000, 4000),
            None,
            CreateRegion(5, 6, 7, 8),
        ),
        None,
        "DependencyWithDefaultVisibility",
    )

    assert info.Data.Visibility == VisibilityModifier.private
    assert info.Data.Name == "DependencyWithDefaultVisibility"
    assert info.Regions.Self__ == CreateRegion(1, 2, 3000, 4000)
    assert info.Regions.Visibility == CreateRegion(1, 2, 3000, 4000)
    assert info.Regions.Name == CreateRegion(5, 6, 7, 8)


# ----------------------------------------------------------------------
def test_ClassStatementLexerData():
    for class_type in ClassType:
        visibility = VisibilityModifier.public if class_type in [ClassType.Interface, ClassType.Exception] else VisibilityModifier.private
        class_modifier = ClassModifier.mutable if class_type in [ClassType.Struct] else ClassModifier.immutable

        data = ClassStatementLexerData(
            visibility,
            class_modifier,
            class_type,
            "ClassName",
            None,
            [],
            [],
        )

        assert data.Visibility == visibility
        assert data.ClassModifier == class_modifier
        assert data.ClassType == class_type
        assert data.Name == "ClassName"
        assert data.Base is None
        assert data.Interfaces == []
        assert data.Mixins == []


# ----------------------------------------------------------------------
class TestClassStatementLexerDataValidateMethods(object):
    _struct_data                            = ClassStatementLexerData(
        VisibilityModifier.private,
        ClassModifier.mutable,
        ClassType.Struct,
        "TheStruct",
        None,
        [],
        [],
    )

    # ----------------------------------------------------------------------
    def test_PublicMember(self):
        self._struct_data.ValidateMemberVisibility(VisibilityModifier.public, CreateRegion(1, 2, 3, 4))

    # ----------------------------------------------------------------------
    def test_PrivateMember(self):
        with pytest.raises(InvalidMemberVisibilityError) as ex:
            self._struct_data.ValidateMemberVisibility(VisibilityModifier.private, CreateRegion(1, 2, 3, 4))

        ex = ex.value

        assert str(ex) == "'private' is not a supported visibility for members of 'struct' types; supported values are 'public'."
        assert ex.Region == CreateRegion(1, 2, 3, 4)

    # ----------------------------------------------------------------------
    def test_MutableModifier(self):
        self._struct_data.ValidateMemberClassModifier(ClassModifier.mutable, CreateRegion(1, 2, 3, 4))

    # ----------------------------------------------------------------------
    def test_ImmutableModifier(self):
        with pytest.raises(InvalidMemberClassModifierError) as ex:
            self._struct_data.ValidateMemberClassModifier(ClassModifier.immutable, CreateRegion(1, 2, 3, 4))

        ex = ex.value

        assert str(ex) == "'immutable' is not a supported modifier for members of 'struct' types; supported values are 'mutable'."
        assert ex.Region == CreateRegion(1, 2, 3, 4)


# ----------------------------------------------------------------------
def test_MutableOnImmutableClass():
    data = ClassStatementLexerData(
        VisibilityModifier.public,
        ClassModifier.immutable,
        ClassType.Class,
        "TheClass",
        None,
        [],
        [],
    )

    with pytest.raises(InvalidMutableClassModifierError) as ex:
        data.ValidateMemberClassModifier(ClassModifier.mutable, CreateRegion(1, 2, 3, 4))

    ex = ex.value

    assert str(ex) == "'mutable' is not a valid member modifier for an immutable 'class' type."
    assert ex.Region == CreateRegion(1, 2, 3, 4)


# ----------------------------------------------------------------------
def test_ClassStatementLexerRegions():
    regions = ClassStatementLexerRegions(
        CreateRegion(1, 2, 3000, 4000),
        CreateRegion(1, 2, 3, 4),
        CreateRegion(5, 6, 7, 8),
        CreateRegion(9, 10, 11, 12),
        CreateRegion(13, 14, 15, 16),
        CreateRegion(17, 18, 19, 20),
        CreateRegion(21, 22, 23, 24),
        CreateRegion(25, 26, 27, 28),
        CreateRegion(29, 30, 31, 32),
    )

    assert regions.Self__ == CreateRegion(1, 2, 3000, 4000)
    assert regions.Visibility == CreateRegion(1, 2, 3, 4)
    assert regions.ClassModifier == CreateRegion(5, 6, 7, 8)
    assert regions.ClassType == CreateRegion(9, 10, 11, 12)
    assert regions.Name == CreateRegion(13, 14, 15, 16)
    assert regions.Base == CreateRegion(17, 18, 19, 20)
    assert regions.Interfaces == CreateRegion(21, 22, 23, 24)
    assert regions.Mixins == CreateRegion(25, 26, 27, 28)


# ----------------------------------------------------------------------
class TestClassStatementLexerInfo(object):
    _default_regions                        = ClassStatementLexerRegions(
        CreateRegion(1, 2, 3000, 4000),
        CreateRegion(1, 2, 3, 4),
        CreateRegion(5, 6, 7, 8),
        CreateRegion(9, 10, 11, 12),
        CreateRegion(13, 14, 15, 16),
        CreateRegion(17, 18, 19, 20),
        CreateRegion(21, 22, 23, 24),
        CreateRegion(25, 26, 27, 28),
        CreateRegion(29, 30, 31, 32),
    )

    _dependency                             = ClassDependencyLexerInfo(
        ClassDependencyLexerRegions(
            CreateRegion(5, 7, 70000, 80000),
            CreateRegion(1000, 2000, 3000, 4000),
            CreateRegion(5000, 6000, 7000, 8000),
        ),
        VisibilityModifier.public,
        "Base",
    )

    # ----------------------------------------------------------------------
    def test_DefaultClassVisibility(self):
        for class_type, expected_visibility in [
            (ClassType.Class, VisibilityModifier.private),
            (ClassType.Exception, VisibilityModifier.public),
        ]:
            info = ClassStatementLexerInfo(
                self._default_regions,
                None,
                ClassModifier.immutable,
                class_type,
                "TheClass",
                None,
                [],
                [],
            )

            assert info.Data.Visibility == expected_visibility

            regions = copy.deepcopy(self._default_regions)

            object.__setattr__(regions, "Visibility", self._default_regions.Self__)

            assert info.Regions == regions

    # ----------------------------------------------------------------------
    def test_InvalidClassVisibility(self):
        with pytest.raises(InvalidClassVisibilityError) as ex:
            ClassStatementLexerInfo(
                self._default_regions,
                VisibilityModifier.public,
                ClassModifier.immutable,
                ClassType.Struct,
                "TheStruct",
                None,
                [],
                [],
            )

        ex = ex.value

        assert str(ex) == "'public' is not a supported visibility for 'struct' types; supported values are 'private'."
        assert ex.Region == self._default_regions.Visibility

    # ----------------------------------------------------------------------
    def test_DefaultClassModifier(self):
        for class_type, expected_modifier in [
            (ClassType.Class, ClassModifier.immutable),
            (ClassType.Struct, ClassModifier.mutable),
        ]:
            info = ClassStatementLexerInfo(
                self._default_regions,
                VisibilityModifier.private,
                None,
                class_type,
                "TheClass",
                None,
                [],
                [],
            )

            assert info.Data.ClassModifier == expected_modifier

            regions = copy.deepcopy(self._default_regions)

            object.__setattr__(regions, "ClassModifier", self._default_regions.Self__)

            assert info.Regions == regions

    # ----------------------------------------------------------------------
    def test_InvalidClassModifier(self):
        with pytest.raises(InvalidClassModifierError) as ex:
            ClassStatementLexerInfo(
                self._default_regions,
                VisibilityModifier.private,
                ClassModifier.immutable,
                ClassType.Struct,
                "TheStruct",
                None,
                [],
                [],
            )

        ex = ex.value

        assert str(ex) == "'immutable' is not a supported modifier for 'struct' types; supported values are 'mutable'."
        assert ex.Region == self._default_regions.ClassModifier

    # ----------------------------------------------------------------------
    def test_Base(self):
        info = ClassStatementLexerInfo(
            self._default_regions,
            VisibilityModifier.private,
            ClassModifier.immutable,
            ClassType.Class,
            "TheClass",
            self._dependency,
            [],
            [],
        )

        assert info.Data.Base == self._dependency
        assert info.Regions == self._default_regions

    # ----------------------------------------------------------------------
    def test_InvalidBase(self):
        with pytest.raises(InvalidBaseError) as ex:
            ClassStatementLexerInfo(
                self._default_regions,
                VisibilityModifier.private,
                ClassModifier.immutable,
                ClassType.Interface,
                "TheInterface",
                self._dependency,
                [],
                [],
            )

        ex = ex.value

        assert str(ex) == "Base classes cannot be used with 'interface' types."
        assert ex.Region == self._default_regions.Base

    # ----------------------------------------------------------------------
    def test_Interfaces(self):
        info = ClassStatementLexerInfo(
            self._default_regions,
            VisibilityModifier.private,
            ClassModifier.immutable,
            ClassType.Class,
            "TheClass",
            None,
            [self._dependency],
            [],
        )

        assert info.Data.Interfaces == [self._dependency]
        assert info.Regions == self._default_regions

    # ----------------------------------------------------------------------
    def test_InvalidInterfaces(self):
        with pytest.raises(InvalidInterfacesError) as ex:
            ClassStatementLexerInfo(
                self._default_regions,
                VisibilityModifier.private,
                ClassModifier.immutable,
                ClassType.Mixin,
                "TheMixin",
                None,
                [self._dependency],
                [],
            )

        ex = ex.value

        assert str(ex) == "Interfaces cannot be used with 'mixin' types."
        assert ex.Region == self._default_regions.Interfaces

    # ----------------------------------------------------------------------
    def test_Mixins(self):
        info = ClassStatementLexerInfo(
            self._default_regions,
            VisibilityModifier.private,
            ClassModifier.immutable,
            ClassType.Class,
            "TheClass",
            None,
            [],
            [self._dependency],
        )

        assert info.Data.Mixins == [self._dependency]
        assert info.Regions == self._default_regions

    # ----------------------------------------------------------------------
    def test_InvalidMixins(self):
        with pytest.raises(InvalidMixinsError) as ex:
            ClassStatementLexerInfo(
                self._default_regions,
                VisibilityModifier.private,
                ClassModifier.immutable,
                ClassType.Interface,
                "TheInterface",
                None,
                [],
                [self._dependency],
            )

        ex = ex.value

        assert str(ex) == "Mixins cannot be used with 'interface' types."
        assert ex.Region == self._default_regions.Mixins
