# ----------------------------------------------------------------------
# |
# |  ClassMemberStatementParserInfo_UnitTest.py
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
"""Unit test for ClassMemberStatementParserInfo.py"""

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
    from ..ClassMemberStatementParserInfo import *
    from ..ClassStatementParserInfo import *
    from ...Common.AutomatedTests import RegionCreator
    from ...Common.MethodModifier import MethodModifier


# ----------------------------------------------------------------------
def _CreateClassStatementParserInfo(
    type_info: TypeInfo,
    visibility: VisibilityModifier=VisibilityModifier.private,
    class_modifier: ClassModifierType=ClassModifierType.immutable,
    name: str="CustomClass",
) -> ClassStatementParserInfo:
    region_creator = RegionCreator()

    return ClassStatementParserInfo(
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
        ],  # type: ignore
        visibility,  # type: ignore
        class_modifier,  # type: ignore
        ClassType.Class,
        name,
        None,
        None,
        None,
        type_info,  # type: ignore
    )


# ----------------------------------------------------------------------
class TestStandard(object):
    region_creator                          = RegionCreator()

    _immutable_class_parser_info            = ClassStatementParserInfo(
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
        ],  # type: ignore
        VisibilityModifier.public,  # type: ignore
        ClassModifierType.immutable,  # type: ignore
        ClassType.Class,
        "ImmutableClass",
        None,
        None,
        None,
    )

    _mutable_class_parser_info              = ClassStatementParserInfo(
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
        ],  # type: ignore
        VisibilityModifier.public,  # type: ignore
        ClassModifierType.mutable,  # type: ignore
        ClassType.Class,
        "MutableClass",
        None,
        None,
        None,
    )

    _struct_parser_info                     = ClassStatementParserInfo(
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
        ],  # type: ignore
        VisibilityModifier.public,  # type: ignore
        ClassModifierType.mutable,  # type: ignore
        ClassType.Struct,
        "ImmutableStruct",
        None,
        None,
        None,
    )

    _restricted_class_type_info             = TypeInfo(
        # Visibility
        VisibilityModifier.private,
        [VisibilityModifier.private],

        VisibilityModifier.private,
        [VisibilityModifier.private],

        # Base
        VisibilityModifier.private,
        [VisibilityModifier.private],
        [],

        # Implements
        VisibilityModifier.private,
        [VisibilityModifier.private],
        [],

        # Uses
        VisibilityModifier.private,
        [VisibilityModifier.private],
        [],

        # Modifiers
        ClassModifierType.immutable,
        [ClassModifierType.immutable],

        # Methods
        MethodModifier.standard,
        [MethodModifier.standard],

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    )

    _restricted_parser_info                 = _CreateClassStatementParserInfo(
        _restricted_class_type_info,
    )

    # ----------------------------------------------------------------------
    def test_Data(self):
        region_creator = RegionCreator()

        info = ClassMemberStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                None,
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.protected,
            ClassModifierType.mutable,
            TypeParserInfo([region_creator(container=True)]),
            "TheMember",
            None,
        )

        assert info.Visibility == VisibilityModifier.protected
        assert info.ClassModifier == ClassModifierType.mutable
        assert info.Type is not None
        assert info.Name == "TheMember"
        assert info.InitializedValue is None

        assert info.Regions__.Self__ == region_creator[0]
        assert info.Regions__.Visibility == region_creator[1]
        assert info.Regions__.ClassModifier == region_creator[2]
        assert info.Regions__.Type == region_creator[3]
        assert info.Regions__.Name == region_creator[4]
        assert info.Regions__.InitializedValue is None

    # ----------------------------------------------------------------------
    def test_InitializedValue(self):
        region_creator = RegionCreator()

        info = ClassMemberStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
            ],
            self._mutable_class_parser_info,
            VisibilityModifier.protected,
            ClassModifierType.mutable,
            TypeParserInfo([region_creator(container=True)]),
            "TheMember",
            ExpressionParserInfo([region_creator(container=True)]),
        )

        assert info.Visibility == VisibilityModifier.protected
        assert info.ClassModifier == ClassModifierType.mutable
        assert info.Type is not None
        assert info.Name == "TheMember"
        assert info.InitializedValue is not None

        assert info.Regions__.Self__ == region_creator[0]
        assert info.Regions__.Visibility == region_creator[1]
        assert info.Regions__.ClassModifier == region_creator[2]
        assert info.Regions__.Type == region_creator[3]
        assert info.Regions__.Name == region_creator[4]
        assert info.Regions__.InitializedValue == region_creator[5]

    # ----------------------------------------------------------------------
    def test_DefaultVisibility(self):
        for parser_info, expected_visibility in [
            (self._immutable_class_parser_info, VisibilityModifier.private),
            (self._struct_parser_info, VisibilityModifier.public),
        ]:
            region_creator = RegionCreator()

            info = ClassMemberStatementParserInfo(
                [
                    region_creator(container=True),
                    None,
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                ],
                parser_info,
                None,
                ClassModifierType.immutable,
                TypeParserInfo([region_creator(container=True)]),
                "TheMember",
                None,
            )

            assert info.Visibility == expected_visibility
            assert info.Regions__.Visibility == info.Regions__.Self__

    # ----------------------------------------------------------------------
    def test_DefaultModifier(self):
        for parser_info, expected_modifier in [
            (self._immutable_class_parser_info, ClassModifierType.immutable),
            (self._struct_parser_info, ClassModifierType.mutable),
        ]:
            region_creator = RegionCreator()

            info = ClassMemberStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    None,
                    region_creator(),
                    region_creator(),
                    None,
                ],
                parser_info,
                VisibilityModifier.public,
                None,
                TypeParserInfo([region_creator(container=True)]),
                "TheMember",
                None,
            )

            assert info.ClassModifier == expected_modifier
            assert info.Regions__.ClassModifier == info.Regions__.Self__

    # ----------------------------------------------------------------------
    def test_InvalidMemberVisibilityError(self):
        with pytest.raises(InvalidMemberVisibilityError) as ex:
            region_creator = RegionCreator()

            ClassMemberStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(expected_error=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                ],
                self._restricted_parser_info,
                VisibilityModifier.public,
                ClassModifierType.immutable,
                TypeParserInfo([region_creator(container=True)]),
                "TheMember",
                None,
            )

        ex = ex.value

        assert str(ex) == "'public' is not a supported visibility for members of 'class' types; supported values are 'private'."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_InvalidMemberClassModifierError(self):
        with pytest.raises(InvalidMemberClassModifierError) as ex:
            region_creator = RegionCreator()

            ClassMemberStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(expected_error=True),
                    region_creator(),
                    region_creator(),
                    None,
                ],
                self._restricted_parser_info,
                VisibilityModifier.private,
                ClassModifierType.mutable,
                TypeParserInfo([region_creator(container=True)]),
                "TheMember",
                None,
            )

        ex = ex.value

        assert str(ex) == "'mutable' is not a supported modifier for members of 'class' types; supported values are 'immutable'."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_InvalidMemberMutableModifierError(self):
        restricted_type_info = copy.deepcopy(self._restricted_class_type_info)
        object.__setattr__(restricted_type_info, "AllowedClassModifiers", [ClassModifierType.immutable, ClassModifierType.mutable])

        with pytest.raises(InvalidMemberMutableModifierError) as ex:
            region_creator = RegionCreator()

            ClassMemberStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(expected_error=True),
                    region_creator(),
                    region_creator(),
                    None,
                ],
                _CreateClassStatementParserInfo(restricted_type_info),
                VisibilityModifier.private,
                ClassModifierType.mutable,
                TypeParserInfo([region_creator(container=True)]),
                "TheMember",
                None,
            )

        ex = ex.value

        assert str(ex) == "'mutable' is not a valid member modifier for an immutable 'class' type."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_InvalidClassMemberError(self):
        with pytest.raises(InvalidClassMemberError) as ex:
            region_creator = RegionCreator()

            ClassMemberStatementParserInfo(
                [
                    region_creator(container=True, expected_error=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                ],
                None,
                VisibilityModifier.private,
                ClassModifierType.immutable,
                TypeParserInfo([region_creator(container=True)]),
                "TheMember",
                None,
            )

        ex = ex.value

        assert str(ex) == "Data member statements must be enclosed within a class-like object."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_DataMembersNotSupportedError(self):
        restricted_type_info = copy.deepcopy(self._restricted_class_type_info)
        object.__setattr__(restricted_type_info, "AllowDataMembers", False)

        with pytest.raises(DataMembersNotSupportedError) as ex:
            region_creator = RegionCreator()

            ClassMemberStatementParserInfo(
                [
                    region_creator(container=True, expected_error=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                ],
                _CreateClassStatementParserInfo(restricted_type_info),
                VisibilityModifier.private,
                ClassModifierType.immutable,
                TypeParserInfo([region_creator(container=True)]),
                "TheMember",
                None,
            )

        ex = ex.value

        assert str(ex) == "Data members are not supported for 'class' types."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_PublicMutableDataMembersNotSupportedError(self):
        restricted_type_info = copy.deepcopy(self._restricted_class_type_info)
        object.__setattr__(restricted_type_info, "AllowedMemberVisibilities", [VisibilityModifier.public, VisibilityModifier.private])
        object.__setattr__(restricted_type_info, "AllowedClassModifiers", [ClassModifierType.immutable, ClassModifierType.mutable])

        with pytest.raises(PublicMutableDataMembersNotSupportedError) as ex:
            region_creator = RegionCreator()

            ClassMemberStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(expected_error=True),
                    region_creator(),
                    region_creator(),
                    None,
                ],
                _CreateClassStatementParserInfo(
                    restricted_type_info,
                    class_modifier=ClassModifierType.mutable,
                ),
                VisibilityModifier.public,
                ClassModifierType.mutable,
                TypeParserInfo([region_creator(container=True)]),
                "TheMember",
                None,
            )

        ex = ex.value

        assert str(ex) == "Public mutable data members are not supported for 'class' types."
        assert ex.Region == region_creator.ExpectedErrorRegion()
