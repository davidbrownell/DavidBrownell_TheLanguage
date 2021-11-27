import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Lexer.Phrases.DSL import DefaultCommentToken

    # Attributes

    # Expressions
    from .Expressions.BinaryExpression import BinaryExpression
    from .Expressions.BoolLiteralExpression import BoolLiteralExpression
    from .Expressions.CastExpression import CastExpression
    from .Expressions.CharacterLiteralExpression import CharacterLiteralExpression # TODO: Rename to CharLiteralExpression
    from .Expressions.FuncInvocationExpression import FuncInvocationExpression
    from .Expressions.GeneratorExpression import GeneratorExpression
    from .Expressions.GenericNameExpression import GenericNameExpression
    from .Expressions.GroupExpression import GroupExpression
    from .Expressions.IndexExpression import IndexExpression
    from .Expressions.IntegerLiteralExpression import IntegerLiteralExpression # TODO: Rename to IntLiteralExpression
    from .Expressions.LambdaExpression import LambdaExpression
    from .Expressions.MatchTypeExpression import MatchTypeExpression
    from .Expressions.MatchValueExpression import MatchValueExpression
    from .Expressions.NoneLiteralExpression import NoneLiteralExpression
    from .Expressions.NumberLiteralExpression import NumberLiteralExpression # TODO: Rename to NumLiteralExpression
    from .Expressions.SliceExpression import SliceExpression
    from .Expressions.StringLiteralExpression import StringLiteralExpression
    from .Expressions.TernaryExpression import TernaryExpression
    from .Expressions.TupleExpression import TupleExpression
    from .Expressions.UnaryExpression import UnaryExpression

    # Names
    from .Names.TupleName import TupleName
    from .Names.VariableName import VariableName

    # Statements
    from .Statements.AssertStatement import AssertStatement
    from .Statements.BinaryStatement import BinaryStatement
    from .Statements.BreakStatement import BreakStatement
    from .Statements.ClassMemberStatement import ClassMemberStatement
    from .Statements.ClassStatement import ClassStatement
    from .Statements.ContinueStatement import ContinueStatement
    from .Statements.DeleteStatement import DeleteStatement
    from .Statements.DocstringStatement import DocstringStatement
    from .Statements.ForStatement import ForStatement
    from .Statements.FuncDefinitionStatement import FuncDefinitionStatement
    from .Statements.FuncInvocationStatement import FuncInvocationStatement
    from .Statements.IfStatement import IfStatement
    from .Statements.ImportStatement import ImportStatement
    from .Statements.PassStatement import PassStatement
    from .Statements.PythonHackStatement import PythonHackStatement
    from .Statements.RaiseStatement import RaiseStatement
    from .Statements.ReturnStatement import ReturnStatement
    from .Statements.ScopedRefStatement import ScopedRefStatement
    from .Statements.ScopedStatement import ScopedStatement
    from .Statements.TryStatement import TryStatement
    from .Statements.TypeAliasStatement import TypeAliasStatement
    from .Statements.VariableDeclarationStatement import VariableDeclarationStatement
    from .Statements.VariableDeclarationOnceStatement import VariableDeclarationOnceStatement
    from .Statements.WhileStatement import WhileStatement
    from .Statements.YieldStatement import YieldStatement

    # TemplateDecoratorExpressions
    from .TemplateDecoratorExpressions.BoolLiteralTemplateDecoratorExpression import BoolLiteralTemplateDecoratorExpression
    from .TemplateDecoratorExpressions.GenericNameTemplateDecoratorExpression import GenericNameTemplateDecoratorExpression
    from .TemplateDecoratorExpressions.IntLiteralTemplateDecoratorExpression import IntLiteralTemplateDecoratorExpression
    from .TemplateDecoratorExpressions.NoneLiteralTemplateDecoratorExpression import NoneLiteralTemplateDecoratorExpression

    # TemplateDecoratorTypes
    from .TemplateDecoratorTypes.NoneTemplateDecoratorType import NoneTemplateDecoratorType
    from .TemplateDecoratorTypes.StandardTemplateDecoratorType import StandardTemplateDecoratorType
    from .TemplateDecoratorTypes.TupleTemplateDecoratorType import TupleTemplateDecoratorType
    from .TemplateDecoratorTypes.VariantTemplateDecoratorType import VariantTemplateDecoratorType

    # Types
    from .Types.FuncType import FuncType
    from .Types.NoneType import NoneType
    from .Types.StandardType import StandardType
    from .Types.TypeOfType import TypeOfType
    from .Types.TupleType import TupleType
    from .Types.VariantType import VariantType


# ----------------------------------------------------------------------
GrammarCommentToken                         = DefaultCommentToken

GrammarPhrases                              = [
    # Attributes

    # Expressions
    BinaryExpression(),
    BoolLiteralExpression(),
    CastExpression(),
    CharacterLiteralExpression(),
    FuncInvocationExpression(),
    GeneratorExpression(),
    GenericNameExpression(),
    GroupExpression(),
    IndexExpression(),
    IntegerLiteralExpression(),
    LambdaExpression(),
    MatchTypeExpression(),
    MatchValueExpression(),
    NoneLiteralExpression(),
    NumberLiteralExpression(),
    SliceExpression(),
    StringLiteralExpression(),
    TernaryExpression(),
    TupleExpression(),
    UnaryExpression(),

    # Names
    TupleName(),
    VariableName(),

    # Statements
    AssertStatement(),
    BinaryStatement(),
    BreakStatement(),
    ClassMemberStatement(),
    ClassStatement(),
    ContinueStatement(),
    DeleteStatement(),
    DocstringStatement(),
    ForStatement(),
    FuncDefinitionStatement(),
    FuncInvocationStatement(),
    IfStatement(),
    ImportStatement(".TheLanguage"), # TODO: fix this
    PassStatement(),
    PythonHackStatement(),
    RaiseStatement(),
    ReturnStatement(),
    ScopedRefStatement(),
    ScopedStatement(),
    TryStatement(),
    TypeAliasStatement(),
    VariableDeclarationStatement(),
    VariableDeclarationOnceStatement(),
    WhileStatement(),
    YieldStatement(),

    # TemplateDecoratorExpressions
    BoolLiteralTemplateDecoratorExpression(),
    GenericNameTemplateDecoratorExpression(),
    IntLiteralTemplateDecoratorExpression(),
    NoneLiteralTemplateDecoratorExpression(),

    # TemplateDecoratorTypes
    NoneTemplateDecoratorType(),
    StandardTemplateDecoratorType(),
    TupleTemplateDecoratorType(),
    VariantTemplateDecoratorType(),

    # Types
    FuncType(),
    NoneType(),
    StandardType(),
    TypeOfType(),
    TupleType(),
    VariantType(),
]
