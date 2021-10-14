# ----------------------------------------------------------------------
# |
# |  All.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-29 08:58:36
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
    from ...Lexer.Phrases.DSL import DefaultCommentToken

    # Attributes

    # Expressions
    from .Expressions.BinaryExpression import BinaryExpression
    from .Expressions.CastExpression import CastExpression
    from .Expressions.FuncInvocationExpression import FuncInvocationExpression
    from .Expressions.FuncNameExpression import FuncNameExpression
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

    # Names
    from .Names.TupleName import TupleName
    from .Names.VariableName import VariableName

    # Statements
    from .Statements.BinaryStatement import BinaryStatement
    from .Statements.BreakStatement import BreakStatement
    from .Statements.ClassStatement import ClassStatement
    from .Statements.ContinueStatement import ContinueStatement
    from .Statements.DeleteStatement import DeleteStatement
    from .Statements.DocstringStatement import DocstringStatement
    from .Statements.ForStatement import ForStatement
    from .Statements.FuncDefinitionStatement import FuncDefinitionStatement
    from .Statements.IfStatement import IfStatement
    from .Statements.PassStatement import PassStatement
    from .Statements.RaiseStatement import RaiseStatement
    from .Statements.ReturnStatement import ReturnStatement
    from .Statements.ScopedRefStatement import ScopedRefStatement
    from .Statements.TryStatement import TryStatement
    from .Statements.VariableDeclarationStatement import VariableDeclarationStatement
    from .Statements.WhileStatement import WhileStatement
    from .Statements.YieldStatement import YieldStatement

    # TODO: Remaining
    #       - ClassMemberStatement
    #       - FuncInvocationStatement
    #       - ImportStatement
    #       - TypeAliasStatement


    # Types
    from .Types.StandardType import StandardType
    from .Types.TupleType import TupleType
    from .Types.VariantType import VariantType


# ----------------------------------------------------------------------
GrammarCommentToken                         = DefaultCommentToken

GrammarPhrases                              = [
    # Attributes
    # TODO: Deferred
    # TODO: Synchronized

    # Expressions
    BinaryExpression(),
    CastExpression(),
    FuncInvocationExpression(),
    FuncNameExpression(),
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
    # TODO: AnonymousFunction

    # Names
    TupleName(),
    VariableName(),

    # Statements
    BinaryStatement(),
    BreakStatement(),
    ClassStatement(),
    ContinueStatement(),
    DeleteStatement(),
    DocstringStatement(),
    ForStatement(),
    FuncDefinitionStatement(),
    IfStatement(),
    PassStatement(),
    RaiseStatement(),
    ReturnStatement(),
    ScopedRefStatement(),
    TryStatement(),
    VariableDeclarationStatement(),
    WhileStatement(),
    YieldStatement(),
    # TODO: CompilerStatement

    # Types
    StandardType(),
    TupleType(),
    VariantType(),
    # TODO: Func type
    # TODO: TypeProgression (for use with Generators?)
]
