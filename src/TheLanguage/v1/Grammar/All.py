# ----------------------------------------------------------------------
# |
# |  All.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 08:35:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""All phrases used to lex content"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Expressions.BinaryExpression import BinaryExpression
    from .Expressions.CallExpression import CallExpression
    from .Expressions.FuncOrTypeExpression import FuncOrTypeExpression
    from .Expressions.GroupExpression import GroupExpression
    from .Expressions.IndexExpression import IndexExpression
    from .Expressions.LiteralExpression import LiteralExpression
    from .Expressions.TernaryExpression import TernaryExpression
    from .Expressions.TupleExpression import TupleExpression
    from .Expressions.TypeCheckExpression import TypeCheckExpression
    from .Expressions.UnaryExpression import UnaryExpression
    from .Expressions.VariableExpression import VariableExpression
    from .Expressions.VariantExpression import VariantExpression

    from .Statements.ClassAttributeStatement import ClassAttributeStatement
    from .Statements.ClassStatement import ClassStatement
    from .Statements.ClassUsingStatement import ClassUsingStatement
    from .Statements.DocstringStatement import DocstringStatement
    from .Statements.FuncDefinitionStatement import FuncDefinitionStatement
    from .Statements.FuncInvocationStatement import FuncInvocationStatement
    from .Statements.IfStatement import IfStatement
    from .Statements.ImportStatement import ImportStatement
    from .Statements.PassStatement import PassStatement
    from .Statements.SpecialMethodStatement import SpecialMethodStatement
    from .Statements.TypeAliasStatement import TypeAliasStatement


# ----------------------------------------------------------------------
GrammarPhrases                              = [
    # Expressions

    # This must be the first expression so that FuncOrTypeExpression doesn't consume
    # things that are upper case (e.g. True, False, None).
    LiteralExpression(),

    BinaryExpression(),
    CallExpression(),
    FuncOrTypeExpression(),
    GroupExpression(),
    IndexExpression(),
    TernaryExpression(),
    # TODO: Tuples negatively impact performance too much right now
    # TupleExpression(),
    TypeCheckExpression(),
    UnaryExpression(),
    VariableExpression(),
    VariantExpression(),

    # Statements
    ClassAttributeStatement(),
    ClassStatement(),
    ClassUsingStatement(),
    DocstringStatement(),
    FuncDefinitionStatement(),
    FuncInvocationStatement(),
    IfStatement(),
    ImportStatement(
        ".TheLanguage",
    ),
    PassStatement(),
    SpecialMethodStatement(),
    TypeAliasStatement(),
]
