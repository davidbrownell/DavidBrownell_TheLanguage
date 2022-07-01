# ----------------------------------------------------------------------
# |
# |  ExpressionsMixin.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-16 10:17:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ExpressionsMixin object"""

import os

from contextlib import contextmanager, ExitStack
from typing import Optional, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ...Error import CreateError, ErrorException
    from ...Common import MiniLanguageHelpers

    from ...ParserInfos.ParserInfo import ParserInfoType, VisitResult

    from ...ParserInfos.Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo

    from ...ParserInfos.Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo, OperatorType as BinaryExpressionOperatorType
    from ...ParserInfos.Expressions.BooleanExpressionParserInfo import BooleanExpressionParserInfo
    from ...ParserInfos.Expressions.CallExpressionParserInfo import CallExpressionParserInfo
    from ...ParserInfos.Expressions.CharacterExpressionParserInfo import CharacterExpressionParserInfo
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...ParserInfos.Expressions.IndexExpressionParserInfo import IndexExpressionParserInfo
    from ...ParserInfos.Expressions.IntegerExpressionParserInfo import IntegerExpressionParserInfo
    from ...ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ...ParserInfos.Expressions.NumberExpressionParserInfo import NumberExpressionParserInfo
    from ...ParserInfos.Expressions.StringExpressionParserInfo import StringExpressionParserInfo
    from ...ParserInfos.Expressions.TernaryExpressionParserInfo import TernaryExpressionParserInfo
    from ...ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo
    from ...ParserInfos.Expressions.TypeCheckExpressionParserInfo import TypeCheckExpressionParserInfo
    from ...ParserInfos.Expressions.UnaryExpressionParserInfo import UnaryExpressionParserInfo
    from ...ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo
    from ...ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo

    from ...ParserInfos.Statements.StatementParserInfo import ScopeFlag, StatementParserInfo


# ----------------------------------------------------------------------
InvalidTypeError                            = CreateError(
    "'{name}' is not a valid type",
    name=str,
)


# ----------------------------------------------------------------------
class ExpressionsMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @contextmanager
    def OnBinaryExpressionParserInfo(
        self,
        parser_info: BinaryExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnBooleanExpressionParserInfo(
        self,
        parser_info: BooleanExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnCallExpressionParserInfo(
        self,
        parser_info: CallExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnCharacterExpressionParserInfo(
        self,
        parser_info: CharacterExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncOrTypeExpressionParserInfo(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIndexExpressionParserInfo(
        self,
        parser_info: IndexExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIntegerExpressionParserInfo(
        self,
        parser_info: IntegerExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnNoneExpressionParserInfo(
        self,
        parser_info: NoneExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnNumberExpressionParserInfo(
        self,
        parser_info: NumberExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnStringExpressionParserInfo(
        self,
        parser_info: StringExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTernaryExpressionParserInfo(
        self,
        parser_info: TernaryExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTupleExpressionParserInfo(
        self,
        parser_info: TupleExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTypeCheckExpressionParserInfo(
        self,
        parser_info: TypeCheckExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnUnaryExpressionParserInfo(
        self,
        parser_info: UnaryExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnVariableExpressionParserInfo(
        self,
        parser_info: VariableExpressionParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnVariantExpressionParserInfo(
        self,
        parser_info: VariantExpressionParserInfo,
    ):
        yield
