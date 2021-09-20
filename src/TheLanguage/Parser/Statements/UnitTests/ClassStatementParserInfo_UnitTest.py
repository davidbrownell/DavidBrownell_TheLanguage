# ----------------------------------------------------------------------
# |
# |  ClassStatementParserInfo_UnitTest.py
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
"""Unit tests for ClassStatementParserInfo.py"""

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
    from ..ClassStatementParserInfo import *
    from ...Common.AutomatedTests import CreateRegion


# ----------------------------------------------------------------------
def test_ClassDependencyParserInfoExplicitVisibility():
    info = ClassDependencyParserInfo(
        [
            CreateRegion(1, 2, 3000, 4000),
            CreateRegion(1, 2, 3, 4),
            CreateRegion(5, 6, 7, 8),
        ],
        VisibilityModifier.public,
        "DependencyName",
    )

    assert info.Visibility == VisibilityModifier.public
    assert info.Name == "DependencyName"
    assert info.Regions.Self__ == CreateRegion(1, 2, 3000, 4000)
    assert info.Regions.Visibility == CreateRegion(1, 2, 3, 4)
    assert info.Regions.Name == CreateRegion(5, 6, 7, 8)


# ----------------------------------------------------------------------
def test_ClassDependencyParserInfoDefaultVisibility():
    info = ClassDependencyParserInfo(
        [
            CreateRegion(1, 2, 3000, 4000),
            None,
            CreateRegion(5, 6, 7, 8),
        ],
        None,
        "DependencyWithDefaultVisibility",
    )

    assert info.Visibility == VisibilityModifier.private
    assert info.Name == "DependencyWithDefaultVisibility"
    assert info.Regions.Self__ == CreateRegion(1, 2, 3000, 4000)
    assert info.Regions.Visibility == CreateRegion(1, 2, 3000, 4000)
    assert info.Regions.Name == CreateRegion(5, 6, 7, 8)


# ----------------------------------------------------------------------
def test_ClassStatementParserData():
    for class_type in ClassType:
        visibility = VisibilityModifier.public if class_type in [ClassType.Interface, ClassType.Exception] else VisibilityModifier.private
        class_modifier = ClassModifier.mutable if class_type in [ClassType.Struct] else ClassModifier.immutable

        info = ClassStatementParserInfo(
            [
                CreateRegion(1, 2, 3000, 4000),
                CreateRegion(5, 6, 7, 8),
                CreateRegion(9, 10, 11, 12),
                CreateRegion(13, 14, 15, 16),
                CreateRegion(17, 18, 19, 20),
                CreateRegion(21, 22, 23, 24),
                CreateRegion(25, 26, 27, 28),
                CreateRegion(29, 30, 31, 32),
                None,
                None,
            ],
            visibility,
            class_modifier,
            class_type,
            "ClassName",
            None,
            [],
            [],
        )

        assert info.Visibility == visibility
        assert info.ClassModifier == class_modifier
        assert info.ClassType == class_type
        assert info.Name == "ClassName"
        assert info.Base is None
        assert info.Interfaces == []
        assert info.Mixins == []
        assert info.Statements == []


# ----------------------------------------------------------------------
class TestClassStatementParserDataValidateMethods(object):
    _struct_data                            = ClassStatementParserInfo(
        [
            CreateRegion(1, 2, 3000, 4000),
            CreateRegion(5, 6, 7, 8),
            CreateRegion(9, 10, 11, 12),
            CreateRegion(13, 14, 15, 16),
            CreateRegion(17, 18, 19, 20),
            CreateRegion(21, 22, 23, 24),
            CreateRegion(25, 26, 27, 28),
            CreateRegion(29, 30, 31, 32),
            None,
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
    data = ClassStatementParserInfo(
        [
            CreateRegion(1, 2, 3000, 4000),
            CreateRegion(5, 6, 7, 8),
            CreateRegion(9, 10, 11, 12),
            CreateRegion(13, 14, 15, 16),
            CreateRegion(17, 18, 19, 20),
            CreateRegion(21, 22, 23, 24),
            CreateRegion(25, 26, 27, 28),
            CreateRegion(29, 30, 31, 32),
            None,
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

    with pytest.raises(InvalidMutableClassModifierError) as ex:
        data.ValidateMemberClassModifier(ClassModifier.mutable, CreateRegion(1, 2, 3, 4))

    ex = ex.value

    assert str(ex) == "'mutable' is not a valid member modifier for an immutable 'class' type."
    assert ex.Region == CreateRegion(1, 2, 3, 4)


# ----------------------------------------------------------------------
class TestClassStatementParserInfo(object):
    _default_regions                        = {
        "Self__": CreateRegion(1, 2, 3000, 4000),
        "Visibility": CreateRegion(1, 2, 3, 4),
        "ClassModifier": CreateRegion(5, 6, 7, 8),
        "ClassType": CreateRegion(9, 10, 11, 12),
        "Name": CreateRegion(13, 14, 15, 16),
        "Base": CreateRegion(17, 18, 19, 20),
        "Interfaces": CreateRegion(21, 22, 23, 24),
        "Mixins": CreateRegion(25, 26, 27, 28),
        "Statements": CreateRegion(29, 30, 31, 32),
        "Documentation" : None,
    }

    _dependency                             = ClassDependencyParserInfo(
        [
            CreateRegion(5, 7, 70000, 80000),
            CreateRegion(1000, 2000, 3000, 4000),
            CreateRegion(5000, 6000, 7000, 8000),
        ],
        VisibilityModifier.public,
        "Base",
    )

    # ----------------------------------------------------------------------
    def test_DefaultClassVisibility(self):
        for class_type, expected_visibility in [
            (ClassType.Class, VisibilityModifier.private),
            (ClassType.Exception, VisibilityModifier.public),
        ]:
            info = ClassStatementParserInfo(
                list(self._default_regions.values()),
                None,
                ClassModifier.immutable,
                class_type,
                "TheClass",
                None,
                [],
                [],
            )

            assert info.Visibility == expected_visibility

            regions = copy.deepcopy(self._default_regions)
            regions["Visibility"] = self._default_regions["Self__"]

            assert info.Regions == info.RegionsType(**regions)

    # ----------------------------------------------------------------------
    def test_InvalidClassVisibility(self):
        with pytest.raises(InvalidClassVisibilityError) as ex:
            ClassStatementParserInfo(
                list(self._default_regions.values()),
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
        assert ex.Region == self._default_regions["Visibility"]

    # ----------------------------------------------------------------------
    def test_DefaultClassModifier(self):
        for class_type, expected_modifier in [
            (ClassType.Class, ClassModifier.immutable),
            (ClassType.Struct, ClassModifier.mutable),
        ]:
            info = ClassStatementParserInfo(
                list(self._default_regions.values()),
                VisibilityModifier.private,
                None,
                class_type,
                "TheClass",
                None,
                [],
                [],
            )

            assert info.ClassModifier == expected_modifier

            regions = copy.deepcopy(self._default_regions)
            regions["ClassModifier"] = self._default_regions["Self__"]

            assert info.Regions == info.RegionsType(**regions)

    # ----------------------------------------------------------------------
    def test_InvalidClassModifier(self):
        with pytest.raises(InvalidClassModifierError) as ex:
            ClassStatementParserInfo(
                list(self._default_regions.values()),
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
        assert ex.Region == self._default_regions["ClassModifier"]

    # ----------------------------------------------------------------------
    def test_Base(self):
        info = ClassStatementParserInfo(
            list(self._default_regions.values()),
            VisibilityModifier.private,
            ClassModifier.immutable,
            ClassType.Class,
            "TheClass",
            self._dependency,
            [],
            [],
        )

        assert info.Base == self._dependency
        assert info.Regions == info.RegionsType(**self._default_regions)

    # ----------------------------------------------------------------------
    def test_InvalidBase(self):
        with pytest.raises(InvalidBaseError) as ex:
            ClassStatementParserInfo(
                list(self._default_regions.values()),
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
        assert ex.Region == self._default_regions["Base"]

    # ----------------------------------------------------------------------
    def test_Interfaces(self):
        info = ClassStatementParserInfo(
            list(self._default_regions.values()),
            VisibilityModifier.private,
            ClassModifier.immutable,
            ClassType.Class,
            "TheClass",
            None,
            [self._dependency],
            [],
        )

        assert info.Interfaces == [self._dependency]
        assert info.Regions == info.RegionsType(**self._default_regions)

    # ----------------------------------------------------------------------
    def test_InvalidInterfaces(self):
        with pytest.raises(InvalidInterfacesError) as ex:
            ClassStatementParserInfo(
                list(self._default_regions.values()),
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
        assert ex.Region == self._default_regions["Interfaces"]

    # ----------------------------------------------------------------------
    def test_Mixins(self):
        info = ClassStatementParserInfo(
            list(self._default_regions.values()),
            VisibilityModifier.private,
            ClassModifier.immutable,
            ClassType.Class,
            "TheClass",
            None,
            [],
            [self._dependency],
        )

        assert info.Mixins == [self._dependency]
        assert info.Regions == info.RegionsType(**self._default_regions)

    # ----------------------------------------------------------------------
    def test_InvalidMixins(self):
        with pytest.raises(InvalidMixinsError) as ex:
            ClassStatementParserInfo(
                list(self._default_regions.values()),
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
        assert ex.Region == self._default_regions["Mixins"]

    # ----------------------------------------------------------------------
    def test_FinalConstructNoDocumentation(self):
        regions = copy.deepcopy(self._default_regions)

        regions["Base"] = None
        regions["Interfaces"] = None
        regions["Mixins"] = None

        info = ClassStatementParserInfo(
            list(regions.values()),
            VisibilityModifier.private,
            ClassModifier.immutable,
            ClassType.Class,
            "TheClass",
            None, # Base
            None, # Interfaces
            None, # Mixins
        )

        assert info.Regions == info.RegionsType(**regions)

        info.FinalConstruct([None], None)

        assert info.Regions == info.RegionsType(**regions)

    # ----------------------------------------------------------------------
    def test_FinalConstructWithDocumentation(self):
        regions = copy.deepcopy(self._default_regions)

        regions["Base"] = None
        regions["Interfaces"] = None
        regions["Mixins"] = None

        info = ClassStatementParserInfo(
            list(regions.values()),
            VisibilityModifier.private,
            ClassModifier.immutable,
            ClassType.Class,
            "TheClass",
            None, # Base
            None, # Interfaces
            None, # Mixins
        )

        assert info.Regions == info.RegionsType(**regions)

        regions["Documentation"] = CreateRegion(33, 34, 35, 36)

        info.FinalConstruct([None], ("Here are the docs", regions["Documentation"]))

        assert info.Regions == info.RegionsType(**regions)

    # ----------------------------------------------------------------------
    def test_StatementsRequiredError(self):
        with pytest.raises(StatementsRequiredError) as ex:
            regions = copy.deepcopy(self._default_regions)

            regions["Base"] = None
            regions["Interfaces"] = None
            regions["Mixins"] = None

            info = ClassStatementParserInfo(
                list(regions.values()),
                VisibilityModifier.private,
                ClassModifier.immutable,
                ClassType.Class,
                "TheClass",
                None, # Base
                None, # Interfaces
                None, # Mixins
            )

            info.FinalConstruct([], None)

        ex = ex.value

        assert str(ex) == "Statements are reqired for 'class' types."
        assert ex.Region == self._default_regions["Statements"]
