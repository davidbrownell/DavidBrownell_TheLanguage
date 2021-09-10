# ----------------------------------------------------------------------
# |
# |  FuncAndMethodDefinitionStatementLexerInfo_UnitTest.py
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
"""Unit tests for FuncAndMethodDefinitionStatementLexerInfo.py"""

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
    from ..FuncAndMethodDefinitionStatementLexerInfo import *
    from ..ClassStatementLexerInfo import *
    from ...Common.AutomatedTests import CreateRegion
    from ...Types.StandardTypeLexerInfo import *


# ----------------------------------------------------------------------
class TestStandard(object):
    _return_type                            = StandardTypeLexerInfo(
        StandardTypeLexerData("TheType", None),
        StandardTypeLexerRegions(
            CreateRegion(1000, 2000, 3000, 4000),
            CreateRegion(5000, 6000, 7000, 8000),
            None,
        ),
    )

    _regions                                = FuncAndMethodDefinitionStatementLexerRegions(
        CreateRegion(100, 200, 300, 400),
        CreateRegion(1, 2, 3, 4),
        CreateRegion(5, 6, 7, 8),
        CreateRegion(9, 10, 11, 12),
        CreateRegion(13, 14, 15, 16),
        CreateRegion(17, 18, 19, 20),
        CreateRegion(21, 22, 23, 24),
    )

    _regions_no_modifier                    = copy.deepcopy(_regions)
    object.__setattr__(_regions_no_modifier, "ClassModifier", None)

    _class_lexer_info                       = ClassStatementLexerInfo(
        ClassStatementLexerRegions(
            CreateRegion(500, 600, 700, 800),
            CreateRegion(900, 1000, 1100, 1200),
            CreateRegion(1300, 1400, 1500, 1600),
            CreateRegion(1700, 1800, 1900, 2000),
            CreateRegion(2100, 2200, 2300, 2400),
            CreateRegion(2500, 2600, 2700, 2800),
            CreateRegion(2900, 3000, 3100, 3200),
            CreateRegion(3300, 3400, 3500, 3600),
        ),
        VisibilityModifier.public,
        ClassModifier.mutable,
        ClassType.Class,
        "TheClass",
        None,
        [],
        [],
    )

    _interface_lexer_info                   = ClassStatementLexerInfo(
        ClassStatementLexerRegions(
            CreateRegion(3700, 3800, 3900, 4000),
            CreateRegion(4100, 4200, 4300, 4400),
            CreateRegion(4500, 4600, 4700, 4800),
            CreateRegion(4900, 5000, 5100, 5200),
            CreateRegion(5300, 5400, 5500, 5600),
            CreateRegion(5700, 5800, 5900, 6000),
            CreateRegion(6100, 6200, 6300, 6400),
            CreateRegion(6500, 6600, 6700, 6800),
        ),
        VisibilityModifier.public,
        ClassModifier.immutable,
        ClassType.Interface,
        "TheInterface",
        None,
        [],
        [],
    )

    _struct_lexer_info                      = ClassStatementLexerInfo(
        ClassStatementLexerRegions(
            CreateRegion(6900, 7000, 7100, 7200),
            CreateRegion(7300, 7400, 7500, 7600),
            CreateRegion(7700, 7800, 7900, 8000),
            CreateRegion(8100, 8200, 8300, 8400),
            CreateRegion(8500, 8600, 8700, 8800),
            CreateRegion(8900, 9000, 9100, 9200),
            CreateRegion(9300, 9400, 9500, 9600),
            CreateRegion(9700, 9800, 9900, 10000),
        ),
        VisibilityModifier.private,
        ClassModifier.mutable,
        ClassType.Struct,
        "TheStruct",
        None,
        [],
        [],
    )

    _deferred_lexer_info                    = ClassStatementLexerInfo(
        ClassStatementLexerRegions(
            CreateRegion(10100, 10200, 10300, 10400),
            CreateRegion(10500, 10600, 10700, 10800),
            CreateRegion(10900, 11000, 11100, 11200),
            CreateRegion(11300, 11400, 11500, 11600),
            CreateRegion(11700, 11800, 11900, 12000),
            CreateRegion(12100, 12200, 12300, 12400),
            CreateRegion(12500, 12600, 12700, 12800),
            CreateRegion(12900, 13000, 13100, 13200),
        ),
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
        data = FuncAndMethodDefinitionStatementLexerData(
            VisibilityModifier.public,
            MethodType.standard,
            self._return_type,
            "TheFunc",
            [self._return_type],
            None,
        )

        assert data.Visibility == VisibilityModifier.public
        assert data.MethodType == MethodType.standard
        assert data.ReturnType == self._return_type
        assert data.Name == "TheFunc"
        assert data.Parameters == [self._return_type]
        assert data.ClassModifier is None

    # ----------------------------------------------------------------------
    def test_DataOperatorFunc(self):
        data = FuncAndMethodDefinitionStatementLexerData(
            VisibilityModifier.public,
            MethodType.standard,
            self._return_type,
            OperatorType.Add,
            [self._return_type],
            None,
        )

        assert data.Visibility == VisibilityModifier.public
        assert data.MethodType == MethodType.standard
        assert data.ReturnType == self._return_type
        assert data.Name == OperatorType.Add
        assert data.Parameters == [self._return_type]
        assert data.ClassModifier is None

    # ----------------------------------------------------------------------
    def test_Regions(self):
        assert self._regions.Self__ == CreateRegion(100, 200, 300, 400)
        assert self._regions.Visibility == CreateRegion(1, 2, 3, 4)
        assert self._regions.MethodType == CreateRegion(5, 6, 7, 8)
        assert self._regions.ReturnType == CreateRegion(9, 10, 11, 12)
        assert self._regions.Name == CreateRegion(13, 14, 15, 16)
        assert self._regions.Parameters == CreateRegion(17, 18, 19, 20)
        assert self._regions.ClassModifier == CreateRegion(21, 22, 23, 24)

    # ----------------------------------------------------------------------
    def test_Info(self):
        info = FuncAndMethodDefinitionStatementLexerInfo(
            self._regions,
            self._class_lexer_info,
            VisibilityModifier.public,
            MethodType.standard,
            self._return_type,
            "Method",
            [self._return_type],
            ClassModifier.immutable,
            True,
        )

        assert info.Data.Visibility == VisibilityModifier.public
        assert info.Data.MethodType == MethodType.standard
        assert info.Data.ReturnType == self._return_type
        assert info.Data.Name == "Method"
        assert info.Data.Parameters == [self._return_type]
        assert info.Data.ClassModifier == ClassModifier.immutable

        assert info.Regions == self._regions

    # ----------------------------------------------------------------------
    def test_FunctionDefaultVisibility(self):
        info = FuncAndMethodDefinitionStatementLexerInfo(
            self._regions_no_modifier,
            None,
            None,
            MethodType.standard,
            self._return_type,
            "Function",
            [],
            None,
            True,
        )

        assert info.Data.Visibility == VisibilityModifier.private
        assert info.Regions.Visibility == info.Regions.Self__

    # ----------------------------------------------------------------------
    def test_FunctionDefaultMethodType(self):
        info = FuncAndMethodDefinitionStatementLexerInfo(
            self._regions_no_modifier,
            None,
            VisibilityModifier.public,
            None,
            self._return_type,
            "Function",
            [],
            None,
            True,
        )

        assert info.Data.MethodType == MethodType.standard
        assert info.Regions.MethodType == info.Regions.Self__

    # ----------------------------------------------------------------------
    def test_FunctionInvalidMethodType(self):
        with pytest.raises(InvalidFunctionMethodTypeError) as ex:
            FuncAndMethodDefinitionStatementLexerInfo(
                self._regions_no_modifier,
                None,
                VisibilityModifier.public,
                MethodType.abstract,
                self._return_type,
                "Function",
                [],
                None,
                True,
            )

        ex = ex.value

        assert str(ex) == "'abstract' is not supported for functions."
        assert ex.MethodType == "abstract"
        assert ex.Region == self._regions_no_modifier.MethodType

    # ----------------------------------------------------------------------
    def test_FunctionInvalidClassModifier(self):
        with pytest.raises(InvalidFunctionClassModifierError) as ex:
            FuncAndMethodDefinitionStatementLexerInfo(
                self._regions,
                None,
                VisibilityModifier.public,
                MethodType.standard,
                self._return_type,
                "Function",
                [],
                ClassModifier.mutable,
                True,
            )

        ex = ex.value

        assert str(ex) == "Class modifiers are not supported for functions."
        assert ex.Region == self._regions.ClassModifier

    # ----------------------------------------------------------------------
    def test_FunctionMissingStatements(self):
        with pytest.raises(FunctionStatementsRequiredError) as ex:
            FuncAndMethodDefinitionStatementLexerInfo(
                self._regions_no_modifier,
                None,
                VisibilityModifier.public,
                MethodType.standard,
                self._return_type,
                "Function",
                [],
                None,
                False,
            )

        ex = ex.value

        assert str(ex) == "Functions must have statements."
        assert ex.Region == self._regions_no_modifier.Self__

    # ----------------------------------------------------------------------
    def test_MethodDefaultVisibility(self):
        for class_info, expected_visibility in [
            (self._class_lexer_info, VisibilityModifier.private),
            (self._struct_lexer_info, VisibilityModifier.public),
        ]:
            info = FuncAndMethodDefinitionStatementLexerInfo(
                self._regions,
                class_info,
                None,
                MethodType.standard,
                self._return_type,
                "Method",
                [],
                ClassModifier.mutable,
                True,
            )

            assert info.Data.Visibility == expected_visibility
            assert info.Regions.Visibility == info.Regions.Self__

    # ----------------------------------------------------------------------
    def test_MethodInvalidVisibility(self):
        with pytest.raises(InvalidMemberVisibilityError) as ex:
            FuncAndMethodDefinitionStatementLexerInfo(
                self._regions,
                self._struct_lexer_info,
                VisibilityModifier.private,
                MethodType.standard,
                self._return_type,
                "Method",
                [],
                ClassModifier.mutable,
                True,
            )

        ex = ex.value

        assert str(ex) == "'private' is not a supported visibility for members of 'struct' types; supported values are 'public'."
        assert ex.Region == self._regions.Visibility

    # ----------------------------------------------------------------------
    def test_MethodDefaultMethodType(self):
        for class_info, expected_method_type, statements_expected in [
            (self._class_lexer_info, MethodType.standard, True),
            (self._struct_lexer_info, MethodType.standard, True),
            (self._interface_lexer_info, MethodType.abstract, False),
        ]:
            info = FuncAndMethodDefinitionStatementLexerInfo(
                self._regions_no_modifier,
                class_info,
                VisibilityModifier.public,
                None,
                self._return_type,
                "Method",
                [],
                None,
                statements_expected,
            )

            assert info.Data.MethodType == expected_method_type
            assert info.Regions.MethodType == info.Regions.Self__

    # ----------------------------------------------------------------------
    def test_MethodInvalidMethodType(self):
        with pytest.raises(InvalidMethodTypeError) as ex:
            FuncAndMethodDefinitionStatementLexerInfo(
                self._regions,
                self._interface_lexer_info,
                VisibilityModifier.public,
                MethodType.static,
                self._return_type,
                "Method",
                [],
                None,
                False,
            )

        ex = ex.value

        assert str(ex) == "'static' is not a supported method type modifier for members of 'interface' types; supported values are 'standard', 'abstract', 'virtual', 'override', 'final'."
        assert ex.Region == self._regions.MethodType

    # ----------------------------------------------------------------------
    def test_MethodDefaultClassModifier(self):
        for class_info, expected_class_modifier in [
            (self._class_lexer_info, ClassModifier.immutable),
            (self._struct_lexer_info, ClassModifier.mutable),
        ]:
            info = FuncAndMethodDefinitionStatementLexerInfo(
                self._regions_no_modifier,
                class_info,
                VisibilityModifier.public,
                MethodType.standard,
                self._return_type,
                "Method",
                [],
                None,
                True,
            )

            assert info.Data.ClassModifier == expected_class_modifier
            assert info.Regions.ClassModifier == info.Regions.Self__

    # ----------------------------------------------------------------------
    def test_MethodClassModifierOnStatic(self):
        with pytest.raises(InvalidClassModifierOnStaticError) as ex:
            FuncAndMethodDefinitionStatementLexerInfo(
                self._regions,
                self._class_lexer_info,
                VisibilityModifier.public,
                MethodType.static,
                self._return_type,
                "Method",
                [],
                ClassModifier.mutable,
                True,
            )

        ex = ex.value

        assert str(ex) == "Class modifiers are not supported for 'static' methods."
        assert ex.Region == self._regions.ClassModifier

    # ----------------------------------------------------------------------
    def test_MethodInvalidClassModifier(self):
        with pytest.raises(InvalidMemberClassModifierError) as ex:
            FuncAndMethodDefinitionStatementLexerInfo(
                self._regions,
                self._struct_lexer_info,
                VisibilityModifier.public,
                MethodType.standard,
                self._return_type,
                "Method",
                [],
                ClassModifier.immutable,
                True,
            )

        ex = ex.value

        assert str(ex) == "'immutable' is not a supported modifier for members of 'struct' types; supported values are 'mutable'."
        assert ex.Region == self._regions.ClassModifier

    # ----------------------------------------------------------------------
    def test_MethodStatementsUnexpected(self):
        for class_info, method_type in [
            (self._class_lexer_info, MethodType.abstract),
            (self._deferred_lexer_info, MethodType.deferred),
        ]:
            with pytest.raises(MethodStatementsUnexpectedError) as ex:
                FuncAndMethodDefinitionStatementLexerInfo(
                    self._regions_no_modifier,
                    class_info,
                    VisibilityModifier.public,
                    method_type,
                    self._return_type,
                    "Method",
                    [],
                    None,
                    True,
                )

            ex = ex.value

            assert str(ex) == "Statements are not expected for '{}' methods.".format(method_type.name)
            assert ex.Region == self._regions_no_modifier.Self__

    # ----------------------------------------------------------------------
    def test_MethodStatementsExpected(self):
        for method_type in MethodType:
            if method_type == MethodType.abstract or method_type == MethodType.deferred:
                continue

            with pytest.raises(MethodStatementsRequiredError) as ex:
                FuncAndMethodDefinitionStatementLexerInfo(
                    self._regions_no_modifier,
                    self._class_lexer_info,
                    VisibilityModifier.public,
                    method_type,
                    self._return_type,
                    "Method",
                    [],
                    None,
                    False,
                )

            ex = ex.value

            assert str(ex) == "Statements are required for '{}' methods.".format(method_type.name)
            assert ex.Region == self._regions_no_modifier.Self__