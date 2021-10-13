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

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ClassStatementParserInfo import *
    from ...Common.AutomatedTests import RegionCreator


# ----------------------------------------------------------------------
def test_ClassDependencyExplicitVisibility():
    region_creator = RegionCreator()

    info = ClassDependencyParserInfo(
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

    info = ClassDependencyParserInfo(
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
        ClassDependencyParserInfo(
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
            ClassDependencyParserInfo(
                [region_creator(container=True), region_creator(), region_creator()],
                VisibilityModifier.public,
                "Interface1",
            ),
            ClassDependencyParserInfo(
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
            ClassDependencyParserInfo(
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
            StatementParserInfo([region_creator(container=True)]),
            StatementParserInfo([region_creator(container=True)]),
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
            StatementParserInfo([region_creator(container=True)]),
            StatementParserInfo([region_creator(container=True)]),
        ],
        ("The documentation", region_creator()),
    )

    assert len(info.Statements) == 2
    assert info.Regions__.Statements == region_creator[5]

    assert info.Statements[0].Regions__.Self__ == region_creator[7]
    assert info.Statements[1].Regions__.Self__ == region_creator[8]

    assert info.Documentation == "The documentation"
    assert info.Regions__.Documentation == region_creator[9]


# TODO: Test errors generated
