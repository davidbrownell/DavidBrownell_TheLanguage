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

    # Names

    # Statements
    from .Statements.ClassMemberStatement import ClassMemberStatement
    from .Statements.ClassStatement import ClassStatement
    from .Statements.DocstringStatement import DocstringStatement
    from .Statements.PassStatement import PassStatement

    # TemplateDecoratorExpressions
    from .TemplateDecoratorExpressions.IntLiteralTemplateDecoratorExpression import IntLiteralTemplateDecoratorExpression

    # TemplateDecoratorTypes
    from .TemplateDecoratorTypes.StandardTemplateDecoratorType import StandardTemplateDecoratorType

    # Types
    from .Types.StandardType import StandardType


# ----------------------------------------------------------------------
GrammarCommentToken                         = DefaultCommentToken

GrammarPhrases                              = [
    # Attributes

    # Expressions

    # Names

    # Statements
    ClassMemberStatement(),
    ClassStatement(),
    DocstringStatement(),
    PassStatement(),

    # TemplateDecoratorExpressions
    IntLiteralTemplateDecoratorExpression(),

    # TemplateDecoratorTypes
    StandardTemplateDecoratorType(),

    # Types
    StandardType(),
]
