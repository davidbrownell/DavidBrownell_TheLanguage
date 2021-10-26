# ----------------------------------------------------------------------
# |
# |  FuncDefinitionStatementParserInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-08 16:08:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for FuncDefinitionStatementParserInfo.py"""

import os

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..FuncDefinitionStatementParserInfo import *
    from ..ClassStatementParserInfo import ClassStatementParserInfo, ClassType
    from ...Common.AutomatedTests import RegionCreator
    from ...Common.ParametersParserInfo import ParameterParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class DummyTypeParserInfo(TypeParserInfo):
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        raise Exception("Not implemented")


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class DummyStatementParserInfo(StatementParserInfo):
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        raise Exception("Not implemented")


# ----------------------------------------------------------------------
def test_StandardFunctionNoParameters():
    region_creator = RegionCreator()

    info = FuncDefinitionStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            None,
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        None,
        VisibilityModifier.public,
        MethodModifierType.standard,
        None,
        DummyTypeParserInfo([region_creator(container=True)]),
        "TheFunc",
        False,
        [
            DummyStatementParserInfo([region_creator(container=True)]),
            DummyStatementParserInfo([region_creator(container=True)]),
        ],
        None,
    )

    assert info.Visibility == VisibilityModifier.public
    assert info.MethodModifier == MethodModifierType.standard
    assert info.ReturnType is not None
    assert info.Name == "TheFunc"
    assert info.Parameters is False
    assert info.ClassModifier is None
    assert len(info.Statements) == 2
    assert info.Documentation is None
    assert info.IsAsync is None
    assert info.IsDeferred is None
    assert info.IsExceptional is None
    assert info.IsGenerator is None
    assert info.IsSynchronized is None

    assert info.Regions__.Self__ == region_creator[0]
    assert info.Regions__.Visibility == region_creator[1]
    assert info.Regions__.MethodModifier == region_creator[2]
    assert info.Regions__.ReturnType == region_creator[3]
    assert info.Regions__.Name == region_creator[4]
    assert info.Regions__.Parameters == region_creator[5]
    assert info.Regions__.ClassModifier is None
    assert info.Regions__.Statements == region_creator[6]
    assert info.Regions__.IsAsync is None
    assert info.Regions__.IsDeferred is None
    assert info.Regions__.IsExceptional is None
    assert info.Regions__.IsGenerator is None
    assert info.Regions__.IsSynchronized is None


# ----------------------------------------------------------------------
def test_StandardFunctionWithParameters():
    region_creator = RegionCreator()

    info = FuncDefinitionStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            None,
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        None,
        VisibilityModifier.public,
        MethodModifierType.standard,
        None,
        DummyTypeParserInfo([region_creator(container=True)]),
        "TheFunc",
        ParametersParserInfo(
            [region_creator(container=True), region_creator(), None, None],
            [
                ParameterParserInfo(
                    [
                        region_creator(container=True),
                        region_creator(),
                        region_creator(),
                        None,
                        None,
                    ],
                    DummyTypeParserInfo([region_creator(container=True)]),
                    "param1",
                    None,
                    None,
                ),
                ParameterParserInfo(
                    [
                        region_creator(container=True),
                        region_creator(),
                        region_creator(),
                        None,
                        None,
                    ],
                    DummyTypeParserInfo([region_creator(container=True)]),
                    "param2",
                    None,
                    None,
                ),
            ],
            None,
            None,
        ),
        [
            DummyStatementParserInfo([region_creator(container=True)]),
            DummyStatementParserInfo([region_creator(container=True)]),
        ],
        None,
    )

    assert not isinstance(info.Parameters, bool)
    assert info.Regions__.Parameters == region_creator[5]

    assert len(info.Parameters.Positional) == 2
    assert info.Parameters.Regions__.Positional == region_creator[9]

    assert info.Parameters.Positional[0].Name == "param1"
    assert info.Parameters.Positional[0].Regions__.Self__ == region_creator[10]
    assert info.Parameters.Positional[0].Regions__.Type == region_creator[11]
    assert info.Parameters.Positional[0].Regions__.Name == region_creator[12]

    assert info.Parameters.Positional[1].Name == "param2"
    assert info.Parameters.Positional[1].Regions__.Self__ == region_creator[14]
    assert info.Parameters.Positional[1].Regions__.Type == region_creator[15]
    assert info.Parameters.Positional[1].Regions__.Name == region_creator[16]


# ----------------------------------------------------------------------
def test_FunctionWithDocumentation():
    region_creator = RegionCreator()

    info = FuncDefinitionStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            None,
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            None,
            None,
            None,
        ],
        None,
        VisibilityModifier.public,
        MethodModifierType.standard,
        None,
        DummyTypeParserInfo([region_creator(container=True)]),
        "TheFunc",
        False,
        [
            DummyStatementParserInfo([region_creator(container=True)]),
        ],
        "The docs",
    )

    assert info.Documentation == "The docs"
    assert info.Regions__.Documentation == region_creator[7]


# ----------------------------------------------------------------------
def test_FunctionIsAsync():
    region_creator = RegionCreator()

    info = FuncDefinitionStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            None,
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            region_creator(),
            None,
            None,
            None,
            None,
        ],
        None,
        VisibilityModifier.public,
        MethodModifierType.standard,
        None,
        DummyTypeParserInfo([region_creator(container=True)]),
        "TheFunc",
        False,
        [
            DummyStatementParserInfo([region_creator(container=True)]),
        ],
        None,
        True,
        None,
        None,
        None,
        None,
    )

    assert info.IsAsync
    assert info.Regions__.IsAsync == region_creator[7]


# ----------------------------------------------------------------------
def test_FunctionIsDeferred():
    region_creator = RegionCreator()

    info = FuncDefinitionStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
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
            None,
            None,
        ],
        None,
        VisibilityModifier.public,
        MethodModifierType.standard,
        None,
        DummyTypeParserInfo([region_creator(container=True)]),
        "TheFunc",
        False,
        None,
        None,
        None,
        True,
        None,
        None,
        None,
    )

    assert info.IsDeferred
    assert info.Regions__.IsDeferred == region_creator[6]


# ----------------------------------------------------------------------
def test_FunctionIsExceptional():
    region_creator = RegionCreator()

    info = FuncDefinitionStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            None,
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            None,
            region_creator(),
            None,
            None,
        ],
        None,
        VisibilityModifier.public,
        MethodModifierType.standard,
        None,
        DummyTypeParserInfo([region_creator(container=True)]),
        "TheFunc",
        False,
        [
            DummyStatementParserInfo([region_creator(container=True)]),
        ],
        None,
        None,
        None,
        True,
        None,
        None,
    )

    assert info.IsExceptional
    assert info.Regions__.IsExceptional == region_creator[7]


# ----------------------------------------------------------------------
def test_FunctionIsGenerator():
    region_creator = RegionCreator()

    info = FuncDefinitionStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            None,
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            None,
            None,
            region_creator(),
            None,
        ],
        None,
        VisibilityModifier.public,
        MethodModifierType.standard,
        None,
        DummyTypeParserInfo([region_creator(container=True)]),
        "TheFunc",
        False,
        [
            DummyStatementParserInfo([region_creator(container=True)]),
        ],
        None,
        None,
        None,
        None,
        True,
        None,
    )

    assert info.IsGenerator
    assert info.Regions__.IsGenerator == region_creator[7]


# ----------------------------------------------------------------------
def test_FunctionIsSynchronized():
    region_creator = RegionCreator()

    info = FuncDefinitionStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            region_creator(),
            None,
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            None,
            None,
            None,
            region_creator(),
        ],
        None,
        VisibilityModifier.public,
        MethodModifierType.standard,
        None,
        DummyTypeParserInfo([region_creator(container=True)]),
        "TheFunc",
        False,
        [
            DummyStatementParserInfo([region_creator(container=True)]),
        ],
        None,
        None,
        None,
        None,
        None,
        True,
    )

    assert info.IsSynchronized
    assert info.Regions__.IsSynchronized == region_creator[7]


# ----------------------------------------------------------------------
def test_FunctionDefaultVisibility():
    region_creator = RegionCreator()

    info = FuncDefinitionStatementParserInfo(
        [
            region_creator(container=True),
            None,
            region_creator(),
            None,
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        None,
        None,
        MethodModifierType.standard,
        None,
        DummyTypeParserInfo([region_creator(container=True)]),
        "TheFunc",
        False,
        [
            DummyStatementParserInfo([region_creator(container=True)]),
        ],
        None,
    )

    assert info.Visibility == VisibilityModifier.private
    assert info.Regions__.Visibility == info.Regions__.Self__


# ----------------------------------------------------------------------
def test_FunctionDefaultMethodModifier():
    region_creator = RegionCreator()

    info = FuncDefinitionStatementParserInfo(
        [
            region_creator(container=True),
            region_creator(),
            None,
            None,
            region_creator(),
            region_creator(),
            region_creator(),
            region_creator(),
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        None,
        VisibilityModifier.public,
        None,
        None,
        DummyTypeParserInfo([region_creator(container=True)]),
        "TheFunc",
        False,
        [
            DummyStatementParserInfo([region_creator(container=True)]),
        ],
        None,
    )

    assert info.MethodModifier == MethodModifierType.standard
    assert info.Regions__.MethodModifier == info.Regions__.Self__


# ----------------------------------------------------------------------
def test_DeferredStatementsError():
    region_creator = RegionCreator()

    with pytest.raises(DeferredStatementsError) as ex:
        FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
                None,
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(expected_error=True),
                None,
                None,
                region_creator(),
                None,
                None,
                None,
            ],
            None,
            VisibilityModifier.public,
            MethodModifierType.standard,
            None,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheFunc",
            False,
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            None,
            None,
            True,
        )

    ex = ex.value

    assert str(ex) == "Statements are not expected for deferred functions or methods."
    assert ex.Region == region_creator.ExpectedErrorRegion()


# ----------------------------------------------------------------------
def test_InvalidFunctionMethodModifierError():
    region_creator = RegionCreator()

    with pytest.raises(InvalidFunctionMethodModifierError) as ex:
        FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(expected_error=True),
                None,
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            None,
            VisibilityModifier.public,
            MethodModifierType.abstract,
            None,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheFunc",
            False,
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            None,
        )

    ex = ex.value

    assert str(ex) == "'abstract' is not supported for functions."
    assert ex.Region == region_creator.ExpectedErrorRegion()


# ----------------------------------------------------------------------
def test_InvalidFunctionClassModifierError():
    region_creator = RegionCreator()

    with pytest.raises(InvalidFunctionClassModifierError) as ex:
        FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
                region_creator(expected_error=True),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            None,
            VisibilityModifier.public,
            MethodModifierType.standard,
            ClassModifierType.immutable,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheFunc",
            False,
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            None,
        )

    ex = ex.value

    assert str(ex) == "Class modifiers are not supported for functions."
    assert ex.Region == region_creator.ExpectedErrorRegion()


# ----------------------------------------------------------------------
def test_FunctionStatementsRequiredError():
    region_creator = RegionCreator()

    with pytest.raises(FunctionStatementsRequiredError) as ex:
        FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True, expected_error=True),
                region_creator(),
                region_creator(),
                None,
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            None,
            VisibilityModifier.public,
            MethodModifierType.standard,
            None,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheFunc",
            False,
            None,
            None,
        )

    ex = ex.value

    assert str(ex) == "Functions must have statements."
    assert ex.Region == region_creator.ExpectedErrorRegion()


# ----------------------------------------------------------------------
class TestMethods(object):
    region_creator                         = RegionCreator()

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
        VisibilityModifier.public,
        ClassModifierType.mutable,
        ClassType.Class,
        "TheClass",
        None,
        None,
        None,
    )

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
        VisibilityModifier.public,
        ClassModifierType.immutable,
        ClassType.Class,
        "TheClass",
        None,
        None,
        None,
    )

    _exception_parser_info                  = ClassStatementParserInfo(
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
        VisibilityModifier.public,
        ClassModifierType.immutable,
        ClassType.Exception,
        "TheException",
        None,
        None,
        None,
    )

    _interface_parser_info                  = ClassStatementParserInfo(
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
        VisibilityModifier.public,
        ClassModifierType.immutable,
        ClassType.Interface,
        "TheInterface",
        None,
        None,
        None,
    )

    del region_creator

    # ----------------------------------------------------------------------
    def test_NoParameters(self):
        region_creator = RegionCreator()

        info = FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                None,
                None,
                None,
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.public,
            MethodModifierType.standard,
            ClassModifierType.immutable,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheMethod",
            False,
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            None,
        )

        assert info.Visibility == VisibilityModifier.public
        assert info.MethodModifier == MethodModifierType.standard
        assert info.ReturnType is not None
        assert info.Name == "TheMethod"
        assert info.Parameters is False
        assert info.ClassModifier == ClassModifierType.immutable
        assert len(info.Statements) == 1
        assert info.Documentation is None
        assert info.IsAsync is None
        assert info.IsDeferred is None
        assert info.IsExceptional is None
        assert info.IsGenerator is None
        assert info.IsSynchronized is None

        assert info.Regions__.Self__ == region_creator[0]
        assert info.Regions__.Visibility == region_creator[1]
        assert info.Regions__.MethodModifier == region_creator[2]
        assert info.Regions__.ClassModifier == region_creator[3]
        assert info.Regions__.ReturnType == region_creator[4]
        assert info.Regions__.Name == region_creator[5]
        assert info.Regions__.Parameters == region_creator[6]
        assert info.Regions__.Statements == region_creator[7]
        assert info.Regions__.IsAsync is None
        assert info.Regions__.IsDeferred is None
        assert info.Regions__.IsExceptional is None
        assert info.Regions__.IsGenerator is None
        assert info.Regions__.IsSynchronized is None

    # ----------------------------------------------------------------------
    def test_WithParameters(self):
        region_creator = RegionCreator()

        info = FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                None,
                None,
                None,
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.public,
            MethodModifierType.standard,
            ClassModifierType.immutable,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheMethod",
            ParametersParserInfo(
                [region_creator(container=True), region_creator(), None, None],
                [
                    ParameterParserInfo(
                        [
                            region_creator(container=True),
                            region_creator(),
                            region_creator(),
                            None,
                            None,
                        ],
                        DummyTypeParserInfo([region_creator(container=True)]),
                        "param1",
                        None,
                        None,
                    ),
                    ParameterParserInfo(
                        [
                            region_creator(container=True),
                            region_creator(),
                            region_creator(),
                            None,
                            None,
                        ],
                        DummyTypeParserInfo([region_creator(container=True)]),
                        "param2",
                        None,
                        None,
                    ),
                ],
                None,
                None,
            ),
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            None,
        )

        assert not isinstance(info.Parameters, bool)
        assert info.Regions__.Parameters == region_creator[6]

        assert len(info.Parameters.Positional) == 2
        assert info.Parameters.Regions__.Positional == region_creator[10]

        assert info.Parameters.Positional[0].Name == "param1"
        assert info.Parameters.Positional[0].Regions__.Self__ == region_creator[11]
        assert info.Parameters.Positional[0].Regions__.Type == region_creator[12]
        assert info.Parameters.Positional[0].Regions__.Name == region_creator[13]

        assert info.Parameters.Positional[1].Name == "param2"
        assert info.Parameters.Positional[1].Regions__.Self__ == region_creator[15]
        assert info.Parameters.Positional[1].Regions__.Type == region_creator[16]
        assert info.Parameters.Positional[1].Regions__.Name == region_creator[17]

    # ----------------------------------------------------------------------
    def test_WithDocumentation(self):
        region_creator = RegionCreator()

        info = FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                None,
                None,
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.public,
            MethodModifierType.standard,
            ClassModifierType.immutable,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheMethod",
            False,
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            "The docs!",
        )

        assert info.Documentation == "The docs!"
        assert info.Regions__.Documentation == region_creator[8]

    # ----------------------------------------------------------------------
    def test_OperatorName(self):
        region_creator = RegionCreator()

        info = FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                None,
                None,
                None,
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.public,
            MethodModifierType.standard,
            ClassModifierType.immutable,
            DummyTypeParserInfo([region_creator(container=True)]),
            OperatorType.BitAnd,
            False,
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            None,
        )

        assert info.Name == OperatorType.BitAnd
        assert info.Regions__.Name == region_creator[5]

    # ----------------------------------------------------------------------
    def test_IsAsync(self):
        region_creator = RegionCreator()

        info = FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                region_creator(),
                None,
                None,
                None,
                None,
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.public,
            MethodModifierType.standard,
            ClassModifierType.immutable,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheMethod",
            False,
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            None,
            True,
            None,
            None,
            None,
            None,
        )

        assert info.IsAsync
        assert info.Regions__.IsAsync == region_creator[8]

    # ----------------------------------------------------------------------
    def test_IsDeferred(self):
        region_creator = RegionCreator()

        info = FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
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
                None,
                None,
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.public,
            MethodModifierType.standard,
            ClassModifierType.immutable,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheMethod",
            False,
            None,
            None,
            None,
            True,
            None,
            None,
            None,
        )

        assert info.IsDeferred
        assert info.Regions__.IsDeferred == region_creator[7]

    # ----------------------------------------------------------------------
    def test_IsExceptional(self):
        region_creator = RegionCreator()

        info = FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
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
                None,
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.public,
            MethodModifierType.standard,
            ClassModifierType.immutable,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheMethod",
            False,
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            None,
            None,
            None,
            True,
            None,
            None,
        )

        assert info.IsExceptional
        assert info.Regions__.IsExceptional == region_creator[8]

    # ----------------------------------------------------------------------
    def test_IsGenerator(self):
        region_creator = RegionCreator()

        info = FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                None,
                region_creator(),
                None,
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.public,
            MethodModifierType.standard,
            ClassModifierType.immutable,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheMethod",
            False,
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            None,
            None,
            None,
            None,
            True,
            None,
        )

        assert info.IsGenerator
        assert info.Regions__.IsGenerator == region_creator[8]

    # ----------------------------------------------------------------------
    def test_IsSynchronized(self):
        region_creator = RegionCreator()

        info = FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                None,
                None,
                region_creator(),
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.public,
            MethodModifierType.standard,
            ClassModifierType.immutable,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheMethod",
            False,
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            None,
            None,
            None,
            None,
            None,
            True,
        )

        assert info.IsSynchronized
        assert info.Regions__.IsSynchronized == region_creator[8]

    # ----------------------------------------------------------------------
    def test_DefaultVisibility(self):
        for parser_info, expected_visibility in [
            (self._mutable_class_parser_info, VisibilityModifier.private),
            (self._exception_parser_info, VisibilityModifier.public),
        ]:
            region_creator = RegionCreator()

            info = FuncDefinitionStatementParserInfo(
                [
                    region_creator(container=True),
                    None,
                    region_creator(),
                    None,
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],  # type: ignore
                parser_info,
                None,
                MethodModifierType.standard,
                None,
                DummyTypeParserInfo([region_creator(container=True)]),
                "TheMethod",
                False,
                [
                    DummyStatementParserInfo([region_creator(container=True)]),
                ],
                None,
            )

        assert info.Visibility == expected_visibility
        assert info.Regions__.Visibility == info.Regions__.Self__

    # ----------------------------------------------------------------------
    def test_InvalidVisibility(self):
        with pytest.raises(InvalidMemberVisibilityError) as ex:
            region_creator = RegionCreator()

            FuncDefinitionStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(expected_error=True),
                    region_creator(),
                    None,
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],  # type: ignore
                self._interface_parser_info,
                VisibilityModifier.private,
                MethodModifierType.abstract,
                None,
                DummyTypeParserInfo([region_creator(container=True)]),
                "TheMethod",
                False,
                None,
                None,
            )

        ex = ex.value

        assert str(ex) == "'private' is not a supported visibility for members of 'interface' types; supported values are 'public'."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_DefaultMethodType(self):
        region_creator = RegionCreator()

        info = FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True),
                region_creator(),
                None,
                None,
                region_creator(),
                region_creator(),
                region_creator(),
                region_creator(),
                None,
                None,
                None,
                None,
                None,
                None,
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.public,
            None,
            None,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheMethod",
            False,
            [
                DummyStatementParserInfo([region_creator(container=True)]),
            ],
            None,
        )

        assert info.MethodModifier == MethodModifierType.standard
        assert info.Regions__.MethodModifier == info.Regions__.Self__

    # ----------------------------------------------------------------------
    def test_InvalidMethodTypeError(self):
        with pytest.raises(InvalidMethodModifierError) as ex:
            region_creator = RegionCreator()

            info = FuncDefinitionStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(expected_error=True),
                    None,
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],  # type: ignore
                self._interface_parser_info,
                VisibilityModifier.public,
                MethodModifierType.standard,
                None,
                DummyTypeParserInfo([region_creator(container=True)]),
                "TheMethod",
                False,
                [
                    DummyStatementParserInfo([region_creator(container=True)]),
                ],
                None,
            )

        ex = ex.value

        assert str(ex) == "'standard' is not a supported method type modifier for members of 'interface' types; supported values are ''abstract', 'override', 'virtual''."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_DefaultClassModifier(self):
        for parser_info, expected_class_modifier in [
            (self._immutable_class_parser_info, ClassModifierType.immutable),
            (self._exception_parser_info, ClassModifierType.immutable),
        ]:
            region_creator = RegionCreator()

            info = FuncDefinitionStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    None,
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],  # type: ignore
                parser_info,
                VisibilityModifier.public,
                MethodModifierType.standard,
                None,
                DummyTypeParserInfo([region_creator(container=True)]),
                "TheMethod",
                False,
                [
                    DummyStatementParserInfo([region_creator(container=True)]),
                ],
                None,
            )

            assert info.ClassModifier == expected_class_modifier
            assert info.Regions__.ClassModifier == info.Regions__.Self__

    # ----------------------------------------------------------------------
    def test_InvalidClassModifierError(self):
        with pytest.raises(InvalidMemberClassModifierError) as ex:
            region_creator = RegionCreator()

            FuncDefinitionStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(expected_error=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],  # type: ignore
                self._exception_parser_info,
                VisibilityModifier.public,
                MethodModifierType.standard,
                ClassModifierType.mutable,
                DummyTypeParserInfo([region_creator(container=True)]),
                "TheMethod",
                False,
                [
                    DummyStatementParserInfo([region_creator(container=True)]),
                ],
                None,
            )

        ex = ex.value

        assert str(ex) == "'mutable' is not a supported modifier for members of 'exception' types; supported values are 'immutable'."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_InvalidMutableClassModifierError(self):
        with pytest.raises(InvalidMemberMutableModifierError) as ex:
            region_creator = RegionCreator()

            FuncDefinitionStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(expected_error=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],  # type: ignore
                self._immutable_class_parser_info,
                VisibilityModifier.public,
                MethodModifierType.standard,
                ClassModifierType.mutable,
                DummyTypeParserInfo([region_creator(container=True)]),
                "TheMethod",
                False,
                [
                    DummyStatementParserInfo([region_creator(container=True)]),
                ],
                None,
            )

        ex = ex.value

        assert str(ex) == "'mutable' is not a valid member modifier for an immutable 'class' type."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_ClassModifierOnStaticError(self):
        with pytest.raises(InvalidClassModifierError) as ex:
            region_creator = RegionCreator()

            FuncDefinitionStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    region_creator(expected_error=True),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],  # type: ignore
                self._mutable_class_parser_info,
                VisibilityModifier.public,
                MethodModifierType.static,
                ClassModifierType.immutable,
                DummyTypeParserInfo([region_creator(container=True)]),
                "TheMethod",
                False,
                [
                    DummyStatementParserInfo([region_creator(container=True)]),
                ],
                None,
            )

        ex = ex.value

        assert str(ex) == "Class modifiers are not supported for 'static' methods."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_DeferredStatements(self):
        with pytest.raises(DeferredStatementsError) as ex:
            region_creator = RegionCreator()

            FuncDefinitionStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    None,
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(expected_error=True),
                    None,
                    None,
                    region_creator(),
                    None,
                    None,
                    None,
                ],  # type: ignore
                self._mutable_class_parser_info,
                VisibilityModifier.public,
                MethodModifierType.standard,
                None,
                DummyTypeParserInfo([region_creator(container=True)]),
                "TheMethod",
                False,
                [
                    DummyStatementParserInfo([region_creator(container=True)]),
                ],
                None,
                None,
                True,
                None,
                None,
                None,
            )

        ex = ex.value

        assert str(ex) == "Statements are not expected for deferred functions or methods."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_StatementsUnexpectedError(self):
        with pytest.raises(MethodStatementsUnexpectedError) as ex:
            region_creator = RegionCreator()

            FuncDefinitionStatementParserInfo(
                [
                    region_creator(container=True),
                    region_creator(),
                    region_creator(),
                    None,
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    region_creator(expected_error=True),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],  # type: ignore
                self._mutable_class_parser_info,
                VisibilityModifier.public,
                MethodModifierType.abstract,
                None,
                DummyTypeParserInfo([region_creator(container=True)]),
                "TheMethod",
                False,
                [
                    DummyStatementParserInfo([region_creator(container=True)]),
                ],
                None,
            )

        ex = ex.value

        assert str(ex) == "Statements are not expected for 'abstract' methods."
        assert ex.Region == region_creator.ExpectedErrorRegion()

    # ----------------------------------------------------------------------
    def test_StatementsExpectedError(self):
        # Not deferred
        with pytest.raises(MethodStatementsRequiredError) as ex:
            region_creator = RegionCreator()

            info = FuncDefinitionStatementParserInfo(
                [
                    region_creator(container=True, expected_error=True),
                    region_creator(),
                    region_creator(),
                    None,
                    region_creator(),
                    region_creator(),
                    region_creator(),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],  # type: ignore
                self._mutable_class_parser_info,
                VisibilityModifier.public,
                MethodModifierType.standard,
                None,
                DummyTypeParserInfo([region_creator(container=True)]),
                "TheMethod",
                False,
                None,
                None,
            )

        ex = ex.value

        assert str(ex) == "Statements are required for 'standard' methods."
        assert ex.Region == region_creator.ExpectedErrorRegion()

        # Not an error if the method is deferred
        region_creator = RegionCreator()

        FuncDefinitionStatementParserInfo(
            [
                region_creator(container=True, expected_error=True),
                region_creator(),
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
                None,
                None,
            ],  # type: ignore
            self._mutable_class_parser_info,
            VisibilityModifier.public,
            MethodModifierType.standard,
            None,
            DummyTypeParserInfo([region_creator(container=True)]),
            "TheMethod",
            False,
            None,
            None,
            None,
            True,
            None,
            None,
            None,
        )
