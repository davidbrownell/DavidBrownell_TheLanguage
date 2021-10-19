# ----------------------------------------------------------------------
# |
# |  ClassStatementParserInfo_UnitTest.py
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
"""Unit test for ClassStatementParserInfo.py"""

import copy
import os

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ClassStatementParserInfo import *
    from ...Common.AutomatedTests import RegionCreator
    from ...Common.MethodModifier import MethodModifier


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class DummyStatementParserInfo(StatementParserInfo):
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        raise Exception("Not implemented")


# ----------------------------------------------------------------------
def test_ClassDependencyExplicitVisibility():
    region_creator = RegionCreator()

    info = ClassStatementDependencyParserInfo(
        [region_creator(), region_creator(), region_creator()],
        VisibilityModifier.public,
        "DependencyName",
    )

    assert info.Visibility == VisibilityModifier.public
    assert info.Name == "DependencyName"
    assert info.Regions__.Self__ == region_creator[0]
    assert info.Regions__.Visibility == region_creator[1]
    assert info.Regions__.Name == region_creator[2]


# ----------------------------------------------------------------------
def test_ClassDependencyDefautVisibility():
    region_creator = RegionCreator()

    info = ClassStatementDependencyParserInfo(
        [region_creator(), region_creator(), region_creator()],
        None,
        "DependencyName",
    )

    assert info.Visibility == VisibilityModifier.private
    assert info.Name == "DependencyName"
    assert info.Regions__.Self__ == region_creator[0]
    assert info.Regions__.Visibility == region_creator[0]
    assert info.Regions__.Name == region_creator[2]


# ----------------------------------------------------------------------
def test_ClassStatementExplicitPhase1():
    region_creator = RegionCreator()

    info = ClassStatementParserInfo(
        [
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            None,
            region_creator(),
            None,
        ],
        VisibilityModifier.public,
        ClassModifierType.mutable,
        ClassType.Class,
        "TheClass",
        None,
        None,
        None,
    )

    assert info.Visibility == VisibilityModifier.public
    assert info.ClassModifier == ClassModifierType.mutable
    assert info.ClassType == ClassType.Class
    assert info.Name == "TheClass"
    assert info.Base is None
    assert info.Implements is None
    assert info.Uses is None
    assert info.Statements == []
    assert info.Documentation is None

    assert info.Regions__.Self__ == region_creator[0]
    assert info.Regions__.Visibility == region_creator[1]
    assert info.Regions__.ClassModifier == region_creator[2]
    assert info.Regions__.ClassType == region_creator[3]
    assert info.Regions__.Name == region_creator[4]
    assert info.Regions__.Base is None
    assert info.Regions__.Implements is None
    assert info.Regions__.Uses is None
    assert info.Regions__.Statements == region_creator[5]
    assert info.Regions__.Documentation is None


# ----------------------------------------------------------------------
def test_ClassStatementDefaultVisibility():
    for class_type, expected_visibility in [
        (ClassType.Class, VisibilityModifier.private),
        (ClassType.Struct, VisibilityModifier.public),
    ]:
        region_creator = RegionCreator()

        info = ClassStatementParserInfo(
            [
                region_creator(),
                None,
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                region_creator(),
                None,
            ],
            None,
            ClassModifierType.mutable,
            class_type,
            "TheClass",
            None,
            None,
            None,
        )

        assert info.Visibility == expected_visibility
        assert info.Regions__.Visibility == info.Regions__.Self__


# ----------------------------------------------------------------------
def test_ClassStatementDefaultModifier():
    for class_type, expected_modifier in [
        (ClassType.Class, ClassModifierType.immutable),
        (ClassType.Struct, ClassModifierType.mutable),
    ]:
        region_creator = RegionCreator()

        info = ClassStatementParserInfo(
            [
                region_creator(),
                region_creator(),
                None,
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                region_creator(),
                None,
            ],
            VisibilityModifier.public,
            None,
            class_type,
            "TheClass",
            None,
            None,
            None,
        )

        assert info.ClassModifier == expected_modifier
        assert info.Regions__.ClassModifier == info.Regions__.Self__


# ----------------------------------------------------------------------
def test_ClassStatementWithBase():
    region_creator = RegionCreator()

    info = ClassStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            region_creator(),
            None,
        ],
        VisibilityModifier.public,
        ClassModifierType.mutable,
        ClassType.Class,
        "TheClass",
        ClassStatementDependencyParserInfo(
            [region_creator(container=True), None, region_creator()],
            None,
            "TheBase",
        ),
        None,
        None,
    )

    assert info.Base.Visibility == VisibilityModifier.private
    assert info.Base.Name == "TheBase"

    assert info.Regions__.Base == region_creator[5]
    assert info.Base.Regions__.Self__ == region_creator[7]
    assert info.Base.Regions__.Visibility == info.Base.Regions__.Self__
    assert info.Base.Regions__.Name == region_creator[8]


# ----------------------------------------------------------------------
def test_ClassStatementWithImplements():
    region_creator = RegionCreator()

    info = ClassStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            region_creator(),
            None,
            region_creator(),
            None,
        ],
        VisibilityModifier.public,
        ClassModifierType.mutable,
        ClassType.Class,
        "TheClass",
        None,
        [
            ClassStatementDependencyParserInfo(
                [region_creator(container=True), region_creator(), region_creator()],
                VisibilityModifier.public,
                "Interface1",
            ),
            ClassStatementDependencyParserInfo(
                [region_creator(container=True), None, region_creator()],
                None,
                "Interface2",
            ),
        ],
        None,
    )

    assert len(info.Implements) == 2
    assert info.Regions__.Implements == region_creator[5]

    assert info.Implements[0].Visibility == VisibilityModifier.public
    assert info.Implements[0].Name == "Interface1"
    assert info.Implements[0].Regions__.Self__ == region_creator[7]
    assert info.Implements[0].Regions__.Visibility == region_creator[8]
    assert info.Implements[0].Regions__.Name == region_creator[9]

    assert info.Implements[1].Visibility == VisibilityModifier.private
    assert info.Implements[1].Name == "Interface2"
    assert info.Implements[1].Regions__.Self__ == region_creator[10]
    assert info.Implements[1].Regions__.Visibility == info.Implements[1].Regions__.Self__
    assert info.Implements[1].Regions__.Name == region_creator[11]


# ----------------------------------------------------------------------
def test_ClassStatementWithUses():
    region_creator = RegionCreator()

    info = ClassStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            region_creator(),
            region_creator(),
            None,
        ],
        VisibilityModifier.public,
        ClassModifierType.mutable,
        ClassType.Class,
        "TheClass",
        None,
        None,
        [
            ClassStatementDependencyParserInfo(
                [region_creator(container=True), region_creator(), region_creator()],
                VisibilityModifier.public,
                "Uses1",
            ),
        ],
    )

    assert len(info.Uses) == 1
    assert info.Regions__.Uses == region_creator[5]

    assert info.Uses[0].Visibility == VisibilityModifier.public
    assert info.Uses[0].Name == "Uses1"
    assert info.Uses[0].Regions__.Self__ == region_creator[7]
    assert info.Uses[0].Regions__.Visibility == region_creator[8]
    assert info.Uses[0].Regions__.Name == region_creator[9]


# ----------------------------------------------------------------------
def test_ClassStatementFinalConstructNoDocumentation():
    region_creator = RegionCreator()

    info = ClassStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            None,
            region_creator(),
            None,
        ],
        VisibilityModifier.public,
        ClassModifierType.mutable,
        ClassType.Class,
        "TheClass",
        None,
        None,
        None,
    )

    info.FinalConstruct(
        [
            DummyStatementParserInfo([region_creator(container=True)]),
            DummyStatementParserInfo([region_creator(container=True)]),
        ],
        None,
    )

    assert len(info.Statements) == 2
    assert info.Regions__.Statements == region_creator[5]

    assert info.Statements[0].Regions__.Self__ == region_creator[6]
    assert info.Statements[1].Regions__.Self__ == region_creator[7]

    assert info.Documentation is None
    assert info.Regions__.Documentation is None


# ----------------------------------------------------------------------
def test_ClassStatementFinalConstructWithDocumentation():
    region_creator = RegionCreator()

    info = ClassStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            None,
            region_creator(),
            region_creator(),
        ],
        VisibilityModifier.public,
        ClassModifierType.mutable,
        ClassType.Class,
        "TheClass",
        None,
        None,
        None,
    )

    info.FinalConstruct(
        [
            DummyStatementParserInfo([region_creator(container=True)]),
            DummyStatementParserInfo([region_creator(container=True)]),
        ],
        ("The documentation", region_creator()),
    )

    assert len(info.Statements) == 2
    assert info.Regions__.Statements == region_creator[5]

    assert info.Statements[0].Regions__.Self__ == region_creator[7]
    assert info.Statements[1].Regions__.Self__ == region_creator[8]

    assert info.Documentation == "The documentation"
    assert info.Regions__.Documentation == region_creator[9]


# ----------------------------------------------------------------------
class TestErrors(object):
    _type_info                              = TypeInfo(
        # Visibility
        VisibilityModifier.private,
        [VisibilityModifier.private],

        VisibilityModifier.private,
        [VisibilityModifier.private],

        # Base
        VisibilityModifier.private,
        [VisibilityModifier.private],
        [ClassType.Mixin],

        # Implements
        VisibilityModifier.private,
        [VisibilityModifier.private],
        [ClassType.Mixin],

        # Uses
        VisibilityModifier.private,
        [VisibilityModifier.private],
        [ClassType.Mixin],

        # Modifiers
        ClassModifierType.mutable,
        [ClassModifierType.mutable],

        # Methods
        MethodModifier.final,
        [MethodModifier.final],

        # Members
        False,
        False,
    )

    # ----------------------------------------------------------------------
    def test_InvalidClassVisibilityError(self):
        with pytest.raises(InvalidClassVisibilityError) as ex:
            region_creator = RegionCreator()

            ClassStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(expected_error=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    region_creator(),
                    None,
                ],
                VisibilityModifier.public,
                ClassModifierType.immutable,
                ClassType.Class,
                "TheClass",
                None,
                None,
                None,
                self._type_info,
            )

        ex = ex.value

        assert str(ex) == "'public' is not a supported visibility for 'class' types; supported values are 'private'."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_InvalidClassModifierError(self):
        with pytest.raises(InvalidClassModifierError) as ex:
            region_creator = RegionCreator()

            ClassStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(expected_error=True),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    region_creator(),
                    None,
                ],
                VisibilityModifier.private,
                ClassModifierType.immutable,
                ClassType.Class,
                "TheClass",
                None,
                None,
                None,
                self._type_info,
            )

        ex = ex.value

        assert str(ex) == "'immutable' is not a supported modifier for 'class' types; supported values are 'mutable'."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_InvalidBaseError(self):
        type_info = copy.deepcopy(self._type_info)

        object.__setattr__(type_info, "AllowedBaseTypes", [])

        with pytest.raises(InvalidBaseError) as ex:
            region_creator = RegionCreator()

            ClassStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(expected_error=True),
                    None,
                    None,
                    region_creator(),
                    None,
                ],
                VisibilityModifier.private,
                ClassModifierType.mutable,
                ClassType.Class,
                "TheClass",
                True, # Note that this type isn't valid, but enough to trigger the error
                None,
                None,
                type_info,
            )

        ex = ex.value

        assert str(ex) == "Base-types cannot be used with 'class' types."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_InvalidBaseVisibilityError(self):
        with pytest.raises(InvalidBaseVisibilityError) as ex:
            region_creator = RegionCreator()

            ClassStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    region_creator(),
                    None,
                ],
                VisibilityModifier.private,
                ClassModifierType.mutable,
                ClassType.Class,
                "TheClass",
                ClassStatementDependencyParserInfo(
                    [
                        region_creator(container=True),
                        region_creator(expected_error=True),
                        region_creator(),
                    ],
                    VisibilityModifier.public,
                    "TheBase",
                ),
                None,
                None,
                self._type_info,
            )

        ex = ex.value

        assert str(ex) == "'public' is not a supported visibility for bases of 'class' types; supported values are 'private'."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    @pytest.mark.skip("TODO: No way to test this yet")
    def test_InvalidBaseTypeError(self):
        with pytest.raises(InvalidBaseTypeError) as ex:
            region_creator = RegionCreator()

            ClassStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    region_creator(),
                    None,
                ],
                visibility,
                class_modifier,
                class_type,
                "TheClass",
                None,
                None,
                None,
                self._type_info,
            )

        ex = ex.value

        assert str(ex) == ""
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_InvalidImplementsError(self):
        type_info = copy.deepcopy(self._type_info)

        object.__setattr__(type_info, "AllowedImplementsTypes", [])

        with pytest.raises(InvalidImplementsError) as ex:
            region_creator = RegionCreator()

            ClassStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    region_creator(expected_error=True),
                    None,
                    region_creator(),
                    None,
                ],
                VisibilityModifier.private,
                ClassModifierType.mutable,
                ClassType.Class,
                "TheClass",
                None,
                True, # Note that this type isn't valid, but enough to trigger the error
                None,
                type_info,
            )

        ex = ex.value

        assert str(ex) == "Implements-types cannot be used with 'class' types."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_InvalidImplementsVisibilityError(self):
        with pytest.raises(InvalidImplementsVisibilityError) as ex:
            region_creator = RegionCreator()

            ClassStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    region_creator(),
                    None,
                    region_creator(),
                    None,
                ],
                VisibilityModifier.private,
                ClassModifierType.mutable,
                ClassType.Class,
                "TheClass",
                None,
                [
                    ClassStatementDependencyParserInfo(
                        [
                            region_creator(container=True),
                            region_creator(expected_error=True),
                            region_creator(),
                        ],
                        VisibilityModifier.public,
                        "TheImplements",
                    ),
                ],
                None,
                self._type_info,
            )

        ex = ex.value

        assert str(ex) == "'public' is not a supported visibility for types implemented by 'class' types; supported values are 'private'."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    @pytest.mark.skip("TODO: No way to test this yet")
    def test_InvalidImplementsTypeError(self):
        with pytest.raises(InvalidImplementsTypeError) as ex:
            region_creator = RegionCreator()

            ClassStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    region_creator(),
                    None,
                ],
                visibility,
                class_modifier,
                class_type,
                "TheClass",
                None,
                None,
                None,
                self._type_info,
            )

        ex = ex.value

        assert str(ex) == ""
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_InvalidUsesError(self):
        type_info = copy.deepcopy(self._type_info)

        object.__setattr__(type_info, "AllowedUsesTypes", [])

        with pytest.raises(InvalidUsesError) as ex:
            region_creator = RegionCreator()

            ClassStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    region_creator(expected_error=True),
                    region_creator(),
                    None,
                ],
                VisibilityModifier.private,
                ClassModifierType.mutable,
                ClassType.Class,
                "TheClass",
                None,
                None,
                True, # Note that this type isn't valid, but enough to trigger the error
                type_info,
            )

        ex = ex.value

        assert str(ex) == "Uses-types cannot be used with 'class' types."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_InvalidUsesVisibilityError(self):
        with pytest.raises(InvalidUsesVisibilityError) as ex:
            region_creator = RegionCreator()

            ClassStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    region_creator(),
                    region_creator(),
                    None,
                ],
                VisibilityModifier.private,
                ClassModifierType.mutable,
                ClassType.Class,
                "TheClass",
                None,
                None,
                [
                    ClassStatementDependencyParserInfo(
                        [
                            region_creator(container=True),
                            region_creator(expected_error=True),
                            region_creator(),
                        ],
                        VisibilityModifier.public,
                        "TheUses",
                    ),
                ],
                self._type_info,
            )

        ex = ex.value

        assert str(ex) == "'public' is not a supported visibility for types used by 'class' types; supported values are 'private'."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    @pytest.mark.skip("TODO: No way to test this yet")
    def test_InvalidUsesTypeError(self):
        with pytest.raises(InvalidUsesTypeError) as ex:
            region_creator = RegionCreator()

            ClassStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    region_creator(),
                    None,
                ],
                visibility,
                class_modifier,
                class_type,
                "TheClass",
                None,
                None,
                None,
                self._type_info,
            )

        ex = ex.value

        assert str(ex) == ""
        assert ex.Region == region_creator.ExpectedErrorRegion()
