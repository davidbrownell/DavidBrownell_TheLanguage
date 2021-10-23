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

from typing import List, Optional, Tuple, Union

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
    from .Common.VisitorTools import VisitType

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
    from .Literals.NoneLiteralParserInfo import NoneLiteralParserInfo
    from .Literals.NumberLiteralParserInfo import NumberLiteralParserInfo
    from .Literals.StringLiteralParserInfo import StringLiteralParserInfo

    # Names
    from .Names.TupleNameParserInfo import TupleNameParserInfo
    from .Names.VariableNameParserInfo import VariableNameParserInfo

    # Statements
    from .Statements.BinaryStatementParserInfo import BinaryStatementParserInfo
    from .Statements.BreakStatementParserInfo import BreakStatementParserInfo
    from .Statements.ClassMemberStatementParserInfo import ClassMemberStatementParserInfo
    from .Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from .Statements.ContinueStatementParserInfo import ContinueStatementParserInfo
    from .Statements.DeleteStatementParserInfo import DeleteStatementParserInfo
    from .Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
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
        visit_type: VisitType,
        parser_info: RootParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
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
        visit_type: VisitType,
        parser_info: ArgumentParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnParameters(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: ParametersParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnParameter(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: ParameterParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
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
        visit_type: VisitType,
        parser_info: BinaryExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnCastExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: CastExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncInvocationExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: FuncInvocationExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncNameExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: FuncNameExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnGeneratorExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: GeneratorExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnGroupExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: GroupExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIndexExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: IndexExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnLambdaExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: LambdaExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchTypeExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: MatchTypeExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchTypeExpressionClause(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: MatchTypeExpressionClauseParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchValueExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: MatchValueExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchValueExpressionClause(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: MatchValueExpressionClauseParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTernaryExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: TernaryExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: TupleExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnUnaryExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: UnaryExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariableExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: VariableExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Literals
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnNoneLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: NoneLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnNumberLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: NumberLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStringLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: StringLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
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
        visit_type: VisitType,
        parser_info: TupleNameParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariableName(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: VariableNameParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Statements
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBinaryStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: BinaryStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBreakStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: BreakStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnClassMemberStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: ClassMemberStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnClassStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: ClassStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnClassStatementDependency(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: ClassStatementDependencyParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnContinueStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: ContinueStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnDeleteStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: DeleteStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncDefinitionStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: FuncDefinitionStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncInvocationStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: FuncInvocationStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIfStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: IfStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnImportStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: ImportStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnImportStatementItem(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: ImportStatementItemParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIterateStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: IterateStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnNoopStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: NoopStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnRaiseStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: RaiseStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnReturnStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: ReturnStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnScopedRefStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: ScopedRefStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTryStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: TryStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTryStatementClause(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: TryStatementClauseParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTypeAliasStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: TypeAliasStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariableDeclarationStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: VariableDeclarationStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnWhileStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: WhileStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnYieldStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: YieldStatementParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
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
        visit_type: VisitType,
        parser_info: StandardTypeParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: TupleTypeParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariantType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        visit_type: VisitType,
        parser_info: VariantTypeParserInfo,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def Accept(
        cls,
        parser_info: ParserInfo,
        stack: Optional[List[Union[str, ParserInfo, Tuple[ParserInfo, str]]]]=None,
        *args,
        **kwargs,
    ):
        parser_info.Accept(cls, stack or [], *args, **kwargs)
