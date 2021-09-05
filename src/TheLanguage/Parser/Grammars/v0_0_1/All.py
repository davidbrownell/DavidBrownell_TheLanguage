# ----------------------------------------------------------------------
# |
# |  All.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 15:10:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""All grammar phrases for this grammar"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Expressions.BinaryExpression import BinaryExpression
    from .Expressions.CastExpression import CastExpression
    from .Expressions.FuncInvocationExpression import FuncInvocationExpression
    from .Expressions.GeneratorExpression import GeneratorExpression
    from .Expressions.GroupExpression import GroupExpression
    from .Expressions.IndexExpression import IndexExpression
    from .Expressions.LambdaExpression import LambdaExpression
    from .Expressions.MatchTypeExpression import MatchTypeExpression
    from .Expressions.MatchValueExpression import MatchValueExpression
    from .Expressions.TernaryExpression import TernaryExpression
    from .Expressions.TupleExpression import TupleExpression
    from .Expressions.UnaryExpression import UnaryExpression
    from .Expressions.VariableExpression import VariableExpression

    from .Names.TupleName import TupleName
    from .Names.VariableName import VariableName

    from .Statements.BinaryStatement import BinaryStatement
    from .Statements.ClassAttributeStatement import ClassAttributeStatement
    from .Statements.ClassCompilerStatement import ClassCompilerStatement
    from .Statements.ClassStatement import ClassStatement
    from .Statements.DeleteStatement import DeleteStatement
    from .Statements.DocstringStatement import DocstringStatement
    from .Statements.ForStatement import ForStatement
    from .Statements.FuncAndMethodDefinitionStatement import FuncAndMethodDefinitionStatement
    from .Statements.FuncInvocationStatement import FuncInvocationStatement
    from .Statements.IfStatement import IfStatement
    from .Statements.ImportStatement import ImportStatement
    from .Statements.PassStatement import PassStatement
    from .Statements.RaiseStatement import RaiseStatement
    from .Statements.ReturnStatement import ReturnStatement
    from .Statements.ScopedRefStatement import ScopedRefStatement
    from .Statements.TryExceptStatement import TryExceptStatement
    from .Statements.TypeAliasStatement import TypeAliasStatement
    from .Statements.VariableDeclarationStatement import VariableDeclarationStatement
    from .Statements.WhileStatement import WhileStatement
    from .Statements.YieldStatement import YieldStatement

    from .Types.FuncType import FuncType
    from .Types.StandardType import StandardType
    from .Types.TupleType import TupleType
    from .Types.VariantType import VariantType


# ----------------------------------------------------------------------
GrammarPhrases                              = [
    # Expressions
    BinaryExpression(),
    CastExpression(),
    FuncInvocationExpression(),
    GeneratorExpression(),
    GroupExpression(),
    IndexExpression(),
    LambdaExpression(),
    MatchTypeExpression(),
    MatchValueExpression(),
    TernaryExpression(),
    TupleExpression(),
    UnaryExpression(),
    VariableExpression(),

    # Names
    TupleName(),
    VariableName(),

    # Statements
    BinaryStatement(),
    ClassAttributeStatement(),
    ClassCompilerStatement(),
    ClassStatement(),
    DeleteStatement(),
    DocstringStatement(),
    ForStatement(),
    FuncAndMethodDefinitionStatement(),
    FuncInvocationStatement(),
    IfStatement(),
    ImportStatement(".TheLanguage",),       # TODO: Update this once the language has a name
    PassStatement(),
    RaiseStatement(),
    ReturnStatement(),
    ScopedRefStatement(),
    TryExceptStatement(),
    TypeAliasStatement(),
    VariableDeclarationStatement(),
    WhileStatement(),
    YieldStatement(),

    # Types
    FuncType(),
    StandardType(),
    TupleType(),
    VariantType(),
]
