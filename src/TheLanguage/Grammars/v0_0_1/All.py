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
    # TODO from .Statements.ClassStatement import ClassStatement
    from .Statements.DocstringStatement import DocstringStatement
    from .Statements.FuncDefinitionStatement import FuncDefinitionStatement
    from .Statements.PassStatement import PassStatement
    from .Statements.VariableDeclarationStatement import VariableDeclarationStatement

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
    # TODO: ClassStatement(),
    DocstringStatement(),
    FuncDefinitionStatement(),
    PassStatement(),
    VariableDeclarationStatement(),

    # Types
    StandardType(),
    TupleType(),
    VariantType(),
    # TODO: Func type
    # TODO: TypeProgression (for use with Generators?)
]
