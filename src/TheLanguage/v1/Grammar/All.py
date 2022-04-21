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
    from .Expressions.GroupExpression import GroupExpression
    from .Expressions.LiteralExpression import LiteralExpression
    from .Expressions.TernaryExpression import TernaryExpression
    from .Expressions.TypeCheckExpression import TypeCheckExpression
    from .Expressions.UnaryExpression import UnaryExpression
    from .Expressions.VariableExpression import VariableExpression

    from .Statements.ClassAttributeStatement import ClassAttributeStatement
    from .Statements.ClassStatement import ClassStatement
    from .Statements.FuncDefinitionStatement import FuncDefinitionStatement
    from .Statements.ImportStatement import ImportStatement
    from .Statements.PassStatement import PassStatement
    from .Statements.SpecialMethodStatement import SpecialMethodStatement
    from .Statements.TypeAliasStatement import TypeAliasStatement

    from .Types.StandardType import StandardType
    from .Types.TupleType import TupleType
    from .Types.VariantType import VariantType


# ----------------------------------------------------------------------
GrammarPhrases                              = [
    # Expressions
    BinaryExpression(),
    GroupExpression(),
    LiteralExpression(),
    TernaryExpression(),
    TypeCheckExpression(),
    UnaryExpression(),
    VariableExpression(),

    # Statements
    ClassAttributeStatement(),
    ClassStatement(),
    FuncDefinitionStatement(),
    ImportStatement(
        ".TheLanguage",
    ),
    PassStatement(),
    SpecialMethodStatement(),
    TypeAliasStatement(),

    # Types
    StandardType(),
    TupleType(),
    VariantType(),
]
