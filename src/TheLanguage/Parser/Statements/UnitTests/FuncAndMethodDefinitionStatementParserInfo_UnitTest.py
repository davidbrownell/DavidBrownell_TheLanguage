# ----------------------------------------------------------------------
# |
# |  FuncAndMethodDefinitionStatementParserInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 10:50:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for FuncAndMethodDefinitionStatementParserInfo.py"""

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
    from ..FuncAndMethodDefinitionStatementParserInfo import *
    from ..ClassStatementParserInfo import *
    from ...Common.AutomatedTests import CreateRegion
    from ...Types.StandardTypeParserInfo import *


# ----------------------------------------------------------------------
class TestStandard(object):
    _return_type                            = StandardTypeParserInfo(
        [
            CreateRegion(1, 2, 30000, 40000),
            CreateRegion(5000, 6000, 7000, 8000),
            None,
        ],
        "TheType",
        None,
    )

    _regions                                = {
        "Self__": CreateRegion(1, 2, 3000, 4000),
        "Visibility": CreateRegion(1, 2, 3, 4),
        "MethodType": CreateRegion(5, 6, 7, 8),
        "ReturnType": CreateRegion(9, 10, 11, 12),
        "Name": CreateRegion(13, 14, 15, 16),
        "Parameters": CreateRegion(17, 18, 19, 20),
        "ClassModifier": CreateRegion(21, 22, 23, 24),
        "Statements": CreateRegion(25, 26, 27, 28),
        "Documentation": None,
    }

    _regions_no_modifier                    = copy.deepcopy(_regions)
    _regions_no_modifier["ClassModifier"] = None

    _class_lexer_info                       = ClassStatementParserInfo(
        [
            CreateRegion(5, 6, 70000, 80000),
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
        ClassModifier.mutable,
        ClassType.Class,
        "TheClass",
        None,
        [],
        [],
    )

    _interface_lexer_info                   = ClassStatementParserInfo(
        [
            CreateRegion(41, 42, 430000, 440000),
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

    _struct_lexer_info                      = ClassStatementParserInfo(
        [
            CreateRegion(77, 78, 790000, 800000),
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

    _deferred_lexer_info                    = ClassStatementParserInfo(
        [
            CreateRegion(113, 114, 1150000, 1160000),
            CreateRegion(11700, 11800, 11900, 12000),
            CreateRegion(12100, 12200, 12300, 12400),
            CreateRegion(12500, 12600, 12700, 12800),
            CreateRegion(12900, 13000, 13100, 13200),
            CreateRegion(13300, 13400, 13500, 13600),
            CreateRegion(13700, 13800, 13900, 14000),
            CreateRegion(14100, 14200, 14300, 14400),
            CreateRegion(14500, 14600, 14700, 14800),
            None,
        ],
        VisibilityModifier.public,
        ClassModifier.mutable,
        ClassType.Primitive,
        "ThePrimitive",
        None,
        [],
        [],
    )

    # ----------------------------------------------------------------------
    def test_DataStringFunc(self):
        info = FuncAndMethodDefinitionStatementParserInfo(
            list(self._regions_no_modifier.values()),
            None,
            VisibilityModifier.public,
            MethodType.standard,
            self._return_type,
            "TheFunc",
            [self._return_type],
            None,
            [None],
            None,
        )

        assert info.Visibility == VisibilityModifier.public
        assert info.MethodType == MethodType.standard
        assert info.ReturnType == self._return_type
        assert info.Name == "TheFunc"
        assert info.Parameters == [self._return_type]
        assert info.ClassModifier is None
        assert info.Regions == info.RegionsType(**self._regions_no_modifier)

    # ----------------------------------------------------------------------
    def test_DataOperatorFunc(self):
        info = FuncAndMethodDefinitionStatementParserInfo(
            list(self._regions_no_modifier.values()),
            None,
            VisibilityModifier.public,
            MethodType.standard,
            self._return_type,
            OperatorType.Add,
            [self._return_type],
            None,
            [None],
            None,
        )

        assert info.Visibility == VisibilityModifier.public
        assert info.MethodType == MethodType.standard
        assert info.ReturnType == self._return_type
        assert info.Name == OperatorType.Add
        assert info.Parameters == [self._return_type]
        assert info.ClassModifier is None
        assert info.Regions == info.RegionsType(**self._regions_no_modifier)

    # ----------------------------------------------------------------------
    def test_Info(self):
        info = FuncAndMethodDefinitionStatementParserInfo(
            list(self._regions.values()),
            self._class_lexer_info,
            VisibilityModifier.public,
            MethodType.standard,
            self._return_type,
            "Method",
            [self._return_type],
            ClassModifier.immutable,
            [None],
            None,
        )

        assert info.Visibility == VisibilityModifier.public
        assert info.MethodType == MethodType.standard
        assert info.ReturnType == self._return_type
        assert info.Name == "Method"
        assert info.Parameters == [self._return_type]
        assert info.ClassModifier == ClassModifier.immutable
        assert info.Regions == info.RegionsType(**self._regions)

    # ----------------------------------------------------------------------
    def test_FunctionDefaultVisibility(self):
        info = FuncAndMethodDefinitionStatementParserInfo(
            list(self._regions_no_modifier.values()),
            None,
            None,
            MethodType.standard,
            self._return_type,
            "Function",
            [],
            None,
            [None],
            None,
        )

        assert info.Visibility == VisibilityModifier.private
        assert info.Regions.Visibility == info.Regions.Self__

    # ----------------------------------------------------------------------
    def test_FunctionDefaultMethodType(self):
        info = FuncAndMethodDefinitionStatementParserInfo(
            list(self._regions_no_modifier.values()),
            None,
            VisibilityModifier.public,
            None,
            self._return_type,
            "Function",
            [],
            None,
            [None],
            None,
        )

        assert info.MethodType == MethodType.standard
        assert info.Regions.MethodType == info.Regions.Self__

    # ----------------------------------------------------------------------
    def test_FunctionInvalidMethodType(self):
        with pytest.raises(InvalidFunctionMethodTypeError) as ex:
            FuncAndMethodDefinitionStatementParserInfo(
                list(self._regions_no_modifier.values()),
                None,
                VisibilityModifier.public,
                MethodType.abstract,
                self._return_type,
                "Function",
                [],
                None,
                [None],
                None,
            )

        ex = ex.value

        assert str(ex) == "'abstract' is not supported for functions."
        assert ex.MethodType == "abstract"
        assert ex.Region == self._regions_no_modifier["MethodType"]

    # ----------------------------------------------------------------------
    def test_FunctionInvalidClassModifier(self):
        with pytest.raises(InvalidFunctionClassModifierError) as ex:
            FuncAndMethodDefinitionStatementParserInfo(
                list(self._regions.values()),
                None,
                VisibilityModifier.public,
                MethodType.standard,
                self._return_type,
                "Function",
                [],
                ClassModifier.mutable,
                [None],
                None,
            )

        ex = ex.value

        assert str(ex) == "Class modifiers are not supported for functions."
        assert ex.Region == self._regions["ClassModifier"]

    # ----------------------------------------------------------------------
    def test_FunctionMissingStatements(self):
        with pytest.raises(FunctionStatementsRequiredError) as ex:
            FuncAndMethodDefinitionStatementParserInfo(
                list(self._regions_no_modifier.values()),
                None,
                VisibilityModifier.public,
                MethodType.standard,
                self._return_type,
                "Function",
                [],
                None,
                None,
                None,
            )

        ex = ex.value

        assert str(ex) == "Functions must have statements."
        assert ex.Region == self._regions_no_modifier["Self__"]

    # ----------------------------------------------------------------------
    def test_MethodDefaultVisibility(self):
        for class_info, expected_visibility in [
            (self._class_lexer_info, VisibilityModifier.private),
            (self._struct_lexer_info, VisibilityModifier.public),
        ]:
            info = FuncAndMethodDefinitionStatementParserInfo(
                list(self._regions.values()),
                class_info,
                None,
                MethodType.standard,
                self._return_type,
                "Method",
                [],
                ClassModifier.mutable,
                [None],
                None,
            )

            assert info.Visibility == expected_visibility
            assert info.Regions.Visibility == info.Regions.Self__

    # ----------------------------------------------------------------------
    def test_MethodInvalidVisibility(self):
        with pytest.raises(InvalidMemberVisibilityError) as ex:
            FuncAndMethodDefinitionStatementParserInfo(
                list(self._regions.values()),
                self._struct_lexer_info,
                VisibilityModifier.private,
                MethodType.standard,
                self._return_type,
                "Method",
                [],
                ClassModifier.mutable,
                [None],
                None,
            )

        ex = ex.value

        assert str(ex) == "'private' is not a supported visibility for members of 'struct' types; supported values are 'public'."
        assert ex.Region == self._regions["Visibility"]

    # ----------------------------------------------------------------------
    def test_MethodDefaultMethodType(self):
        for class_info, expected_method_type, statements_expected in [
            (self._class_lexer_info, MethodType.standard, True),
            (self._struct_lexer_info, MethodType.standard, True),
            (self._interface_lexer_info, MethodType.abstract, False),
        ]:
            regions = copy.deepcopy(self._regions)

            if not statements_expected:
                regions["Statements"] = None

            info = FuncAndMethodDefinitionStatementParserInfo(
                list(regions.values()),
                class_info,
                VisibilityModifier.public,
                None,
                self._return_type,
                "Method",
                [],
                None,
                [None] if statements_expected else None,
                None,
            )

            assert info.MethodType == expected_method_type
            assert info.Regions.MethodType == info.Regions.Self__

    # ----------------------------------------------------------------------
    def test_MethodInvalidMethodType(self):
        with pytest.raises(InvalidMethodTypeError) as ex:
            FuncAndMethodDefinitionStatementParserInfo(
                list(self._regions.values()),
                self._interface_lexer_info,
                VisibilityModifier.public,
                MethodType.static,
                self._return_type,
                "Method",
                [],
                None,
                None,
                None,
            )

        ex = ex.value

        assert str(ex) == "'static' is not a supported method type modifier for members of 'interface' types; supported values are 'standard', 'abstract', 'virtual', 'override', 'final'."
        assert ex.Region == self._regions["MethodType"]

    # ----------------------------------------------------------------------
    def test_MethodDefaultClassModifier(self):
        for class_info, expected_class_modifier in [
            (self._class_lexer_info, ClassModifier.immutable),
            (self._struct_lexer_info, ClassModifier.mutable),
        ]:
            info = FuncAndMethodDefinitionStatementParserInfo(
                list(self._regions_no_modifier.values()),
                class_info,
                VisibilityModifier.public,
                MethodType.standard,
                self._return_type,
                "Method",
                [],
                None,
                [None],
                None,
            )

            assert info.ClassModifier == expected_class_modifier
            assert info.Regions.ClassModifier == info.Regions.Self__

    # ----------------------------------------------------------------------
    def test_MethodClassModifierOnStatic(self):
        with pytest.raises(InvalidClassModifierOnStaticError) as ex:
            FuncAndMethodDefinitionStatementParserInfo(
                list(self._regions.values()),
                self._class_lexer_info,
                VisibilityModifier.public,
                MethodType.static,
                self._return_type,
                "Method",
                [],
                ClassModifier.mutable,
                [None],
                None,
            )

        ex = ex.value

        assert str(ex) == "Class modifiers are not supported for 'static' methods."
        assert ex.Region == self._regions["ClassModifier"]

    # ----------------------------------------------------------------------
    def test_MethodInvalidClassModifier(self):
        with pytest.raises(InvalidMemberClassModifierError) as ex:
            FuncAndMethodDefinitionStatementParserInfo(
                list(self._regions.values()),
                self._struct_lexer_info,
                VisibilityModifier.public,
                MethodType.standard,
                self._return_type,
                "Method",
                [],
                ClassModifier.immutable,
                [None],
                None,
            )

        ex = ex.value

        assert str(ex) == "'immutable' is not a supported modifier for members of 'struct' types; supported values are 'mutable'."
        assert ex.Region == self._regions["ClassModifier"]

    # ----------------------------------------------------------------------
    def test_MethodStatementsUnexpected(self):
        for class_info, method_type in [
            (self._class_lexer_info, MethodType.abstract),
            (self._deferred_lexer_info, MethodType.deferred),
        ]:
            with pytest.raises(MethodStatementsUnexpectedError) as ex:
                FuncAndMethodDefinitionStatementParserInfo(
                    list(self._regions_no_modifier.values()),
                    class_info,
                    VisibilityModifier.public,
                    method_type,
                    self._return_type,
                    "Method",
                    [],
                    None,
                    [None],
                    None,
                )

            ex = ex.value

            assert str(ex) == "Statements are not expected for '{}' methods.".format(method_type.name)
            assert ex.Region == self._regions_no_modifier["Self__"]

    # ----------------------------------------------------------------------
    def test_MethodStatementsExpected(self):
        for method_type in MethodType:
            if method_type == MethodType.abstract or method_type == MethodType.deferred:
                continue

            with pytest.raises(MethodStatementsRequiredError) as ex:
                FuncAndMethodDefinitionStatementParserInfo(
                    list(self._regions_no_modifier.values()),
                    self._class_lexer_info,
                    VisibilityModifier.public,
                    method_type,
                    self._return_type,
                    "Method",
                    [],
                    None,
                    None,
                    None,
                )

            ex = ex.value

            assert str(ex) == "Statements are required for '{}' methods.".format(method_type.name)
            assert ex.Region == self._regions_no_modifier["Self__"]
