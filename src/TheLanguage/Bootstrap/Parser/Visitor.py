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

    from .Common.ClassType import ClassType
    from .Common.ConstraintArgumentParserInfo import ConstraintArgumentParserInfo
    from .Common.ConstraintParametersParserInfo import ConstraintParameterParserInfo, ConstraintParametersParserInfo
    from .Common.FunctionArgumentParserInfo import FunctionArgumentParserInfo
    from .Common.FunctionParametersParserInfo import FunctionParameterTypeParserInfo, FunctionParameterParserInfo, FunctionParametersParserInfo
    from .Common.MethodModifier import MethodModifier
    from .Common.TemplateArgumentParserInfo import TemplateArgumentParserInfo
    from .Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo, TemplateDecoratorParameterParserInfo, TemplateParametersParserInfo
    from .Common.TypeModifier import TypeModifier

    from .Expressions.BinaryExpressionParserInfo import (
        BinaryExpressionParserInfo,
        OperatorType as BinaryExpressionOperatorType,
    )

    from .Expressions.CastExpressionParserInfo import CastExpressionParserInfo
    from .Expressions.FuncInvocationExpressionParserInfo import FuncInvocationExpressionParserInfo
    from .Expressions.GeneratorExpressionParserInfo import GeneratorExpressionParserInfo
    from .Expressions.GenericNameExpressionParserInfo import GenericNameExpressionParserInfo
    from .Expressions.GroupExpressionParserInfo import GroupExpressionParserInfo
    from .Expressions.IndexExpressionParserInfo import IndexExpressionParserInfo
    from .Expressions.LambdaExpressionParserInfo import LambdaExpressionParserInfo
    from .Expressions.MatchTypeExpressionParserInfo import MatchTypeExpressionClauseParserInfo, MatchTypeExpressionParserInfo
    from .Expressions.MatchValueExpressionParserInfo import MatchValueExpressionClauseParserInfo, MatchValueExpressionParserInfo
    from .Expressions.TernaryExpressionParserInfo import TernaryExpressionParserInfo
    from .Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo
    from .Expressions.UnaryExpressionParserInfo import (
        UnaryExpressionParserInfo,
        OperatorType as UnaryExpressionOperatorType,
    )

    from .Literals.BoolLiteralParserInfo import BoolLiteralParserInfo
    from .Literals.CharacterLiteralParserInfo import CharacterLiteralParserInfo
    from .Literals.IntLiteralParserInfo import IntLiteralParserInfo
    from .Literals.NoneLiteralParserInfo import NoneLiteralParserInfo
    from .Literals.NumberLiteralParserInfo import NumberLiteralParserInfo
    from .Literals.StringLiteralParserInfo import StringLiteralParserInfo

    from .Names.TupleNameParserInfo import TupleNameParserInfo
    from .Names.VariableNameParserInfo import VariableNameParserInfo

    from .Statements.AssertStatementParserInfo import AssertStatementParserInfo
    from .Statements.BinaryStatementParserInfo import (
        BinaryStatementParserInfo,
        OperatorType as BinaryStatementOperatorType,
    )

    from .Statements.BreakStatementParserInfo import BreakStatementParserInfo
    from .Statements.ClassMemberStatementParserInfo import ClassMemberStatementParserInfo
    from .Statements.ClassStatementParserInfo import ClassStatementDependencyParserInfo, ClassStatementParserInfo
    from .Statements.ContinueStatementParserInfo import ContinueStatementParserInfo
    from .Statements.DeleteStatementParserInfo import DeleteStatementParserInfo
    from .Statements.FuncDefinitionStatementParserInfo import (
        FuncDefinitionStatementParserInfo,
        OperatorType as FuncDefinitionStatementOperatorType,
        COMPILE_TIME_OPERATORS as FUNC_DEFINITION_COMPILE_TIME_OPERATORS,
    )
    from .Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from .Statements.IfStatementParserInfo import IfStatementClauseParserInfo, IfStatementParserInfo
    from .Statements.ImportStatementParserInfo import (
        ImportStatementItemParserInfo,
        ImportStatementParserInfo,
        ImportType as ImportStatementImportType,
    )
    from .Statements.IterateStatementParserInfo import IterateStatementParserInfo
    from .Statements.NoopStatementParserInfo import NoopStatementParserInfo
    from .Statements.PythonHackStatementParserInfo import PythonHackStatementParserInfo
    from .Statements.RaiseStatementParserInfo import RaiseStatementParserInfo
    from .Statements.ReturnStatementParserInfo import ReturnStatementParserInfo
    from .Statements.ScopedRefStatementParserInfo import ScopedRefStatementParserInfo
    from .Statements.ScopedStatementParserInfo import ScopedStatementParserInfo
    from .Statements.TryStatementParserInfo import TryStatementClauseParserInfo, TryStatementParserInfo
    from .Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo
    from .Statements.VariableDeclarationStatementParserInfo import VariableDeclarationStatementParserInfo
    from .Statements.VariableDeclarationOnceStatementParserInfo import VariableDeclarationOnceStatementParserInfo
    from .Statements.WhileStatementParserInfo import WhileStatementParserInfo
    from .Statements.YieldStatementParserInfo import YieldStatementParserInfo

    from .Types.FuncTypeParserInfo import FuncTypeParserInfo
    from .Types.NoneTypeParserInfo import NoneTypeParserInfo
    from .Types.StandardTypeParserInfo import StandardTypeParserInfo
    from .Types.TypeOfTypeParserInfo import TypeOfTypeParserInfo
    from .Types.TupleTypeParserInfo import TupleTypeParserInfo
    from .Types.VariantTypeParserInfo import VariantTypeParserInfo


# ----------------------------------------------------------------------
class Visitor(VisitorBase):
    # ----------------------------------------------------------------------
    @classmethod
    @Interface.extensionmethod
    def Accept(
        cls,
        parser_info: ParserInfo,
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        *args,
        **kwargs,
    ):
        parser_info.Accept(cls, stack, *args, **kwargs)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnRoot(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: RootParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnConstraintArgument(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ConstraintArgumentParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnConstraintParameter(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ConstraintParameterParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnConstraintParameters(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ConstraintParametersParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFunctionArgument(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FunctionArgumentParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFunctionParameterType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FunctionParameterTypeParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFunctionParameter(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FunctionParameterParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFunctionParameters(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FunctionParametersParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTemplateArgument(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TemplateArgumentParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTemplateTypeParameter(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TemplateTypeParameterParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTemplateDecoratorParameter(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TemplateDecoratorParameterParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTemplateParameters(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TemplateParametersParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBinaryExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: BinaryExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnCastExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: CastExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncInvocationExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FuncInvocationExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnGeneratorExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: GeneratorExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnGenericNameExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: GenericNameExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnGroupExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: GroupExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIndexExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: IndexExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnLambdaExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: LambdaExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchTypeExpressionClause(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: MatchTypeExpressionClauseParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchTypeExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: MatchTypeExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchValueExpressionClause(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: MatchValueExpressionClauseParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMatchValueExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: MatchValueExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTernaryExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TernaryExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TupleExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnUnaryExpression(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: UnaryExpressionParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBoolLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: BoolLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnCharacterLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: CharacterLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIntLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: IntLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnNoneLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: NoneLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnNumberLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: NumberLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStringLiteral(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: StringLiteralParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleName(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TupleNameParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariableName(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: VariableNameParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnAssertStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: AssertStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBinaryStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: BinaryStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBreakStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: BreakStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnClassMemberStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ClassMemberStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnClassStatementDependency(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ClassStatementDependencyParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnClassStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ClassStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnContinueStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ContinueStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnDeleteStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: DeleteStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncDefinitionStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FuncDefinitionStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncInvocationStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FuncInvocationStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIfStatementClause(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: IfStatementClauseParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIfStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: IfStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnImportStatementItem(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ImportStatementItemParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnImportStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ImportStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIterateStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: IterateStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnNoopStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: NoopStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnPythonHackStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: PythonHackStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnRaiseStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: RaiseStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnReturnStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ReturnStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnScopedRefStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ScopedRefStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnScopedStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: ScopedStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTryStatementClause(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TryStatementClauseParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTryStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TryStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTypeAliasStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TypeAliasStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariableDeclarationStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: VariableDeclarationStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariableDeclarationOnceStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: VariableDeclarationOnceStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnWhileStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: WhileStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnYieldStatement(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: YieldStatementParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: FuncTypeParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnNoneType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: NoneTypeParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStandardType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: StandardTypeParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTypeOfType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TypeOfTypeParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: TupleTypeParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariantType(
        stack: List[Union[str, ParserInfo, Tuple[ParserInfo, str]]],
        parser_info: VariantTypeParserInfo,
        *args,
        **kwargs,
    ) -> Union[None, bool, Callable[[], Any]]:
        raise Exception("Abstract method")
