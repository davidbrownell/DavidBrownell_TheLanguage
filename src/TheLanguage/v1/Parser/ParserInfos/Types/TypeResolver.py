# ----------------------------------------------------------------------
# |
# |  TypeResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-27 12:43:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeResolver object"""

import os

from typing import List

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ConcreteType import ConcreteType
    from .GenericType import GenericType

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ..Statements.StatementParserInfo import StatementParserInfo

    from ...Common import MiniLanguageHelpers


# ----------------------------------------------------------------------
class TypeResolver(Interface.Interface):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def EvalMiniLanguageType(
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageType:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def EvalMiniLanguageExpression(
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageExpression.EvalResult:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def EvalConcreteType(
        parser_info: ExpressionParserInfo,
    ) -> ConcreteType:
        """Creates a concrete type for any valid expression"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def EvalStatements(
        statements: List[StatementParserInfo],
    ) -> None:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def GetOrCreateNestedGenericType(
        parser_info: StatementParserInfo,
    ) -> GenericType:
        raise Exception("Abstract method")  # pragma: no cover
