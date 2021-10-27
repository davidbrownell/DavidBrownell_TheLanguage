# ----------------------------------------------------------------------
# |
# |  Visitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-18 13:59:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Visitor object"""

import os

from typing import Any, Callable, List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.Visitor import Visitor as VisitorBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ParserInfo import ParserInfo
    from .RootParserInfo import RootParserInfo

    # Common
    from .Common.ArgumentParserInfo import ArgumentParserInfo
    from .Common.MethodModifier import MethodModifier   # Convenience
    from .Common.ParametersParserInfo import ParametersParserInfo, ParameterParserInfo

    # Expressions
    from .Expressions.BinaryExpressionParserInfo import (
        BinaryExpressionParserInfo,
        OperatorType as BinaryExpressionOperatorType,   # Convenience
    )
    from .Expressions.CastExpressionParserInfo import CastExpressionParserInfo
    from .Expressions.FuncInvocationExpressionParserInfo import FuncInvocationExpressionParserInfo
    from .Expressions.FuncNameExpressionParserInfo import FuncNameExpressionParserInfo
    from .Expressions.GeneratorExpressionParserInfo import GeneratorExpressionParserInfo
    from .Expressions.GroupExpressionParserInfo import GroupExpressionParserInfo
    from .Expressions.IndexExpressionParserInfo import IndexExpressionParserInfo
    from .Expressions.LambdaExpressionParserInfo import LambdaExpressionParserInfo
    from .Expressions.MatchTypeExpressionParserInfo import MatchTypeExpressionParserInfo, MatchTypeExpressionClauseParserInfo
    from .Expressions.MatchValueExpressionParserInfo import MatchValueExpressionParserInfo, MatchValueExpressionClauseParserInfo
    from .Expressions.TernaryExpressionParserInfo import TernaryExpressionParserInfo
    from .Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo

    from .Expressions.UnaryExpressionParserInfo import (
        UnaryExpressionParserInfo,
        OperatorType as UnaryExpressionOperatorType,    # Convenience
    )

    from .Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo

    # Literals
    from .Literals.BoolLiteralParserInfo import BoolLiteralParserInfo
    from .Literals.IntegerLiteralParserInfo import IntegerLiteralParserInfo
    from .Literals.NoneLiteralParserInfo import NoneLiteralParserInfo
    from .Literals.NumberLiteralParserInfo import NumberLiteralParserInfo
    from .Literals.StringLiteralParserInfo import StringLiteralParserInfo

    # Names
    from .Names.TupleNameParserInfo import TupleNameParserInfo
    from .Names.VariableNameParserInfo import VariableNameParserInfo

    # Statements
    from .Statements.AssertStatementParserInfo import AssertStatementParserInfo
    from .Statements.BinaryStatementParserInfo import BinaryStatementParserInfo
    from .Statements.BreakStatementParserInfo import BreakStatementParserInfo
    from .Statements.ClassMemberStatementParserInfo import ClassMemberStatementParserInfo
    from .Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from .Statements.ContinueStatementParserInfo import ContinueStatementParserInfo
    from .Statements.DeleteStatementParserInfo import DeleteStatementParserInfo
    from .Statements.FuncDefinitionStatementParserInfo import (
        FuncDefinitionStatementParserInfo,
        OperatorType as FuncDefinitionStatementOperatorType,  # Convenience
    )
    from .Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from .Statements.IfStatementParserInfo import IfStatementParserInfo
    from .Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportStatementItemParserInfo
    from .Statements.IterateStatementParserInfo import IterateStatementParserInfo
    from .Statements.NoopStatementParserInfo import NoopStatementParserInfo
    from .Statements.RaiseStatementParserInfo import RaiseStatementParserInfo
    from .Statements.ReturnStatementParserInfo import ReturnStatementParserInfo
    from .Statements.ScopedRefStatementParserInfo import ScopedRefStatementParserInfo
    from .Statements.TryStatementParserInfo import TryStatementParserInfo, TryStatementClauseParserInfo
    from .Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo
    from .Statements.VariableDeclarationStatementParserInfo import VariableDeclarationStatementParserInfo
    from .Statements.WhileStatementParserInfo import WhileStatementParserInfo
    from .Statements.YieldStatementParserInfo import YieldStatementParserInfo

    # Types
    from .Types.StandardTypeParserInfo import StandardTypeParserInfo
    from .Types.TupleTypeParserInfo import TupleTypeParserInfo
    from .Types.VariantTypeParserInfo import VariantTypeParserInfo


# ----------------------------------------------------------------------
class Visitor(VisitorBase):
    # ----------------------------------------------------------------------
    # |
    # |  Root
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnRoot(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: RootParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Common
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnArgument(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ArgumentParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnParameters(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ParametersParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnParameter(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ParameterParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Expressions
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBinaryExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: BinaryExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnCastExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: CastExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncInvocationExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FuncInvocationExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncNameExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FuncNameExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnGeneratorExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: GeneratorExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnGroupExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: GroupExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIndexExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: IndexExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnLambdaExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: LambdaExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchTypeExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: MatchTypeExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchTypeExpressionClause(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: MatchTypeExpressionClauseParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchValueExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: MatchValueExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchValueExpressionClause(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: MatchValueExpressionClauseParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTernaryExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TernaryExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TupleExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnUnaryExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: UnaryExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariableExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: VariableExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Literals
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBoolLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: BoolLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIntegerLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: IntegerLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnNoneLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: NoneLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnNumberLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: NumberLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStringLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: StringLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Names
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleName(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TupleNameParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariableName(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: VariableNameParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Statements
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnAssertStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: AssertStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBinaryStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: BinaryStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBreakStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: BreakStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnClassMemberStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ClassMemberStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnClassStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ClassStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnClassStatementDependency(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ClassStatementDependencyParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnContinueStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ContinueStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnDeleteStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: DeleteStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncDefinitionStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FuncDefinitionStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncInvocationStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FuncInvocationStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIfStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: IfStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnImportStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ImportStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnImportStatementItem(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ImportStatementItemParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIterateStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: IterateStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnNoopStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: NoopStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnRaiseStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: RaiseStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnReturnStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ReturnStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnScopedRefStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ScopedRefStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTryStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TryStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTryStatementClause(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TryStatementClauseParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTypeAliasStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TypeAliasStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariableDeclarationStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: VariableDeclarationStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnWhileStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: WhileStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnYieldStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: YieldStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Types
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStandardType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: StandardTypeParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TupleTypeParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariantType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: VariantTypeParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def Accept(
        cls,
        parser_info: ParserInfo,
        *args,
        stack: Optional[List[Union[str, ParserInfo, Tuple[ParserInfo, str]]]]=None,
        **kwargs,
    ):
        parser_info.Accept(cls, stack or [], *args, **kwargs)
