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

from contextlib import contextmanager

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ...ParserInfos.Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo
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


# ----------------------------------------------------------------------
class ExpressionsMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnBinaryExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnBooleanExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnCallExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnCharacterExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnFuncOrTypeExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnIndexExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnIntegerExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnNoneExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnNumberExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnStringExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTernaryExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTupleExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTypeCheckExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnUnaryExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnVariableExpressionParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnVariantExpressionParserInfo(*args, **kwargs):
        yield
