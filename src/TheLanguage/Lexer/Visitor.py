# ----------------------------------------------------------------------
# |
# |  Visitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-31 18:55:12
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

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.Visitor import Visitor as _VisitorBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .AST import ExpressionNode, Node, StatementNode, TypeNode, VariableNode

    # Expressions
    from .Expressions.BinaryExpression import BinaryExpression
    from .Expressions.CastExpression import CastExpression
    from .Expressions.FuncDefinitionExpression import FuncDefinitionExpression
    from .Expressions.FuncInvocationExpression import FuncInvocationExpression
    from .Expressions.GeneratorExpression import GeneratorExpression
    from .Expressions.QuickRefExpression import QuickRefExpression
    from .Expressions.TernaryExpression import TernaryExpression
    from .Expressions.TransferExpression import TransferExpression
    from .Expressions.TupleExpression import TupleExpression
    from .Expressions.UnaryExpression import UnaryExpression
    from .Expressions.VariableExpression import VariableExpression

    # Statements
    from .Statements.BinaryStatement import BinaryStatement
    from .Statements.ClassStatement import ClassStatement
    from .Statements.DeleteStatement import DeleteStatement
    from .Statements.DocstringStatement import DocstringStatement
    from .Statements.ForStatement import ForStatement
    from .Statements.FuncDefinitionStatement import FuncDefinitionStatement
    from .Statements.FuncInvocationStatement import FuncInvocationStatement
    from .Statements.IfStatement import IfStatement
    from .Statements.LoopControlStatement import LoopControlStatement
    from .Statements.MethodDefinitionStatement import MethodDefinitionStatement
    from .Statements.NoopStatement import NoopStatement
    from .Statements.ReturnStatement import ReturnStatement
    from .Statements.ScopedRefsStatement import ScopedRefsStatement
    from .Statements.SmartIfStatement import SmartIfStatement
    from .Statements.ThrowExceptionStatement import ThrowExceptionStatement
    from .Statements.TryCatchExceptionStatement import TryCatchExceptionStatement
    from .Statements.TupleStatement import TupleStatement
    from .Statements.TypeAliasStatement import TypeAliasStatement
    from .Statements.VariableDeclarationStatement import VariableDeclarationStatement
    from .Statements.WhileStatement import WhileStatement
    from .Statements.YieldStatement import YieldStatement

    # Types
    from .Types.FirstClassFunctionType import FirstClassFunctionType
    from .Types.StandardType import StandardType
    from .Types.TupleType import TupleType
    from .Types.VariantType import VariantType

    # Variables
    from .Variables.StandardVariable import StandardVariable
    from .Variables.TupleVariable import TupleVariable


# ----------------------------------------------------------------------
@Interface.clsinit
class Visitor(_VisitorBase):
    """\
    TODO: Describe
    """

    EXPRESSIONS                             = [
        BinaryExpression,
        CastExpression,
        FuncDefinitionExpression,
        FuncInvocationExpression,
        GeneratorExpression,
        QuickRefExpression,
        TernaryExpression,
        TransferExpression,
        TupleExpression,
        UnaryExpression,
        VariableExpression,
    ]

    STATEMENTS                              = [
        BinaryStatement,
        ClassStatement,
        DeleteStatement,
        DocstringStatement,
        ForStatement,
        FuncDefinitionStatement,
        FuncInvocationStatement,
        IfStatement,
        LoopControlStatement,
        MethodDefinitionStatement,
        NoopStatement,
        ReturnStatement,
        ScopedRefsStatement,
        SmartIfStatement,
        ThrowExceptionStatement,
        TryCatchExceptionStatement,
        TupleStatement,
        TypeAliasStatement,
        VariableDeclarationStatement,
        WhileStatement,
        YieldStatement,
    ]

    TYPES                                   = [
        FirstClassFunctionType,
        StandardType,
        TupleType,
        VariantType,
    ]

    VARIABLES                               = [
        StandardVariable,
        TupleVariable,
    ]

    # ----------------------------------------------------------------------
    # |  Generic Types
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnExpression(
        node: ExpressionNode,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStatement(
        node: StatementNode,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnType(
        node: TypeNode,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariable(
        node: TypeNode,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |  Expressions
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBinaryExpression(
        node: BinaryExpression,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnCastExpression(
        node: CastExpression,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncDefinitionExpression(
        node: FuncDefinitionExpression,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncInvocationExpression(
        node: FuncInvocationExpression,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnGeneratorExpression(
        node: GeneratorExpression,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnQuickRefExpression(
        node: QuickRefExpression,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTernaryExpression(
        node: TernaryExpression,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTransferExpression(
        node: TransferExpression,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover


    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleExpression(
        node: TupleExpression,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnUnaryExpression(
        node: UnaryExpression,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariableExpression(
        node: VariableExpression,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |  Statements
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnBinaryStatement(
        node: BinaryStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnClassStatement(
        node: ClassStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnDeleteStatement(
        node: DeleteStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnDocstringStatement(
        node: DocstringStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnForStatement(
        node: ForStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncDefinitionStatement(
        node: FuncDefinitionStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFuncInvocationStatement(
        node: FuncInvocationStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIfStatement(
        node: IfStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnLoopControlStatement(
        node: LoopControlStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnMethodDefinitionStatement(
        node: MethodDefinitionStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnNoopStatement(
        node: NoopStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnReturnStatement(
        node: ReturnStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnScopedRefsStatement(
        node: ScopedRefsStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnSmartIfStatement(
        node: SmartIfStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnThrowExceptionStatement(
        node: ThrowExceptionStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTryCatchExceptionStatement(
        node: TryCatchExceptionStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleStatement(
        node: TupleStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTypeAliasStatement(
        node: TypeAliasStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariableDeclarationStatement(
        node: VariableDeclarationStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnWhileStatement(
        node: WhileStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnYieldStatement(
        node: YieldStatement,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |  Types
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnFirstClassFunctionType(
        node: FirstClassFunctionType,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStandardType(
        node: StandardType,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleType(
        node: TupleType,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnVariantType(
        node: VariantType,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |  Variables
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStandardVariable(
        node: StandardVariable,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnTupleVariable(
        node: TupleVariable,
        *args,
        **kwargs,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def __clsinit__(cls):
        cls._method_map = {
            # Generic
            ExpressionNode : cls.OnExpression,
            StatementNode : cls.OnStatement,
            TypeNode : cls.OnType,
            VariableNode : cls.OnVariable,

            # Expressions
            BinaryExpression : cls.OnBinaryExpression,
            CastExpression : cls.OnCastExpression,
            FuncDefinitionExpression : cls.OnFuncDefinitionExpression,
            FuncInvocationExpression : cls.OnFuncInvocationExpression,
            GeneratorExpression : cls.OnGeneratorExpression,
            QuickRefExpression : cls.OnQuickRefExpression,
            TernaryExpression : cls.OnTernaryExpression,
            TransferExpression : cls.OnTransferExpression,
            TupleExpression : cls.OnTupleExpression,
            UnaryExpression : cls.OnUnaryExpression,
            VariableExpression : cls.OnVariableExpression,

            # Statements
            BinaryStatement : cls.OnBinaryStatement,
            ClassStatement : cls.OnClassStatement,
            DeleteStatement : cls.OnDeleteStatement,
            DocstringStatement : cls.OnDocstringStatement,
            ForStatement : cls.OnForStatement,
            FuncDefinitionStatement : cls.OnFuncDefinitionStatement,
            FuncInvocationStatement : cls.OnFuncInvocationStatement,
            IfStatement : cls.OnIfStatement,
            LoopControlStatement : cls.OnLoopControlStatement,
            MethodDefinitionStatement : cls.OnMethodDefinitionStatement,
            NoopStatement : cls.OnNoopStatement,
            ReturnStatement : cls.OnReturnStatement,
            ScopedRefsStatement : cls.OnScopedRefsStatement,
            SmartIfStatement : cls.OnSmartIfStatement,
            ThrowExceptionStatement : cls.OnThrowExceptionStatement,
            TryCatchExceptionStatement : cls.OnTryCatchExceptionStatement,
            TupleStatement : cls.OnTupleStatement,
            TypeAliasStatement : cls.OnTypeAliasStatement,
            VariableDeclarationStatement : cls.OnVariableDeclarationStatement,
            WhileStatement : cls.OnWhileStatement,
            YieldStatement : cls.OnYieldStatement,

            # Types
            FirstClassFunctionType : cls.OnFirstClassFunctionType,
            StandardType : cls.OnStandardType,
            TupleType : cls.OnTupleType,
            VariantType : cls.OnVariantType,

            # Variables
            StandardVariable : cls.OnStandardVariable,
            TupleVariable : cls.OnTupleVariable,
        }

    # ----------------------------------------------------------------------
    @classmethod
    def Accept(
        cls,
        node: Node,
        *args,
        **kwargs,
    ):

        method_map_keys = [
            ExpressionNode if isinstance(node, ExpressionNode) else
                StatementNode if isinstance(node, StatementNode) else
                    TypeNode if isinstance(node, TypeNode) else
                        VariableNode if isinstance(node, VariableNode) else
                            None,
            type(node),
        ]

        for method_map_key in method_map_keys:
            method = cls._method_map.get(method_map_key, None)
            assert method is not None, (method_map_key, node)

            method(node, *args, **kwargs)
