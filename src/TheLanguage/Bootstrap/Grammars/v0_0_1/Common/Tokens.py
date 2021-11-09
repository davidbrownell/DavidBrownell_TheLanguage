import os
import re
import textwrap

from typing import Callable, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Error import Error

    from ....Lexer.Components.Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        PopIgnoreWhitespaceControlToken,
        PopPreserveWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        PushPreserveWhitespaceControlToken,
        RegexToken,
    )


# ----------------------------------------------------------------------
Dedent                                      = DedentToken()
Indent                                      = IndentToken()
Newline                                     = NewlineToken()

PopIgnoreWhitespaceControl                  = PopIgnoreWhitespaceControlToken()
PushIgnoreWhitespaceControl                 = PushIgnoreWhitespaceControlToken()

PopPreserveWhitespaceControl                = PopPreserveWhitespaceControlToken()
PushPreserveWhitespaceControl               = PushPreserveWhitespaceControlToken()

# The following keywords are special and should not be consumed by the generic expression below.
# Without this special consideration, the phrase (for example):
#
#   value = move (foo,)
#
# is ambiguous, as it could be considered:
#
#   - Function invocation expression: 'move' is the function name and '(foo,)' are the arguments
#   - Unary expression: 'move' is the operator and '(foo,)' is a tuple
#
# A word should be added to this list if any of these conditions are true:
#
#   A) A literal keyword (should always begin with an uppercase)
#   B) Non-enum word potentially followed by a tuple
#
ReservedKeywords                            = [
    # ----------------------------------------------------------------------
    # |  Expressions

    # ../Expressions.BinaryExpression.py
    "and",                                  # (B)
    "or",                                   # (B)
    "in",                                   # (B)
    "not in",                               # (B)
    "is",                                   # (B)

    # ../Expressions.BoolLiteralExpression.py
    "True",                                 # (A)
    "False",                                # (A)

    # ../Expressions/CastExpression.py
    "as",                                   # (B)

    # ../Expression/GeneratorExpression.py
    "for",                                  # (B)
    "if",                                   # (B)

    # ../Expressions/LambdaExpression.py
    "lambda",                               # (B)

    # ../Expressions/MatchTypeExpression.py|MatchValueExpression.py
    "case",                                 # (B)

    # ../Expressions/NoneLiteralExpression.py
    "None",

    # ../Expressions/TernaryExpression.py
    "if",                                   # (B)
    "else",                                 # (B)

    # ../Expressions/UnaryExpression.py
    "await",                                # (B)
    "copy",                                 # (B)
    "final",                                # (B)
    "move",                                 # (B)
    "not",                                  # (B)

    # ----------------------------------------------------------------------
    # |  Statements

    # ../Statements/AssertStatement.py
    "assert",                               # (B)

    # ../Statements/ForStatement.py
    "in",                                   # (B)

    # ../Statements/IfStatement.py
    "if",                                   # (B)
    "elif",                                 # (B)

    # ../Statements/ImportStatement.py
    "from",

    # ../Statements/RaiseStatement.py
    "raise",                                # (B)

    # ../Statements/ReturnStatement.py
    "return",                               # (B)

    # ../Statements/WhileStatement.py
    "while",                                # (B)

    # ../Statements/YieldStatement.py
    "yield",                                # (B)
    "from",                                 # (B)

    # ----------------------------------------------------------------------
    # |  Types

    # ../Types/NoneType.py
    "None",                                 # (A)
]

ReservedKeywords                            = set(ReservedKeywords)


# ----------------------------------------------------------------------
ArgumentNameRegex                           = re.compile(r"^[a-z][a-zA-Z0-9_]*(?<!__)$")
AttributeNameRegex                          = re.compile(r"^[A-Z][a-zA-Z0-9_]*(?<!__)$")
ParameterNameRegex                          = re.compile(r"^[a-z][a-zA-Z0-9_]*(?<!__)$")
TypeNameRegex                               = re.compile(r"^_?[A-Z][a-zA-Z0-9_]*(?<!__)$")
VariableNameRegex                           = re.compile(r"^_?[a-z][a-zA-Z0-9_]*(?<!__)$")
TemplateTypeParameterNameRegex              = re.compile(r"^_?[A-Z][a-zA-Z0-9_]*(?<!__)$")
TemplateDecoratorParameterNameRegex         = re.compile(r"^[a-zA-Z0-9_]+(?<!__)'$")
ConstraintParameterNameRegex                = re.compile(r"^[a-z][a-zA-Z0-9_]*(?<!__)'$")

FuncNameRegex                               = re.compile(
    textwrap.dedent(
        r"""(?#
            Start                           )^(?#
            Underscores                     )_{0,2}(?#
            Func Name                       )(?P<alphanum>[A-Z][a-zA-Z0-9_]+)(?#
            Don't end with an underscore;
                that will come later        )(?<!_)(?#
            Exceptional Suffix              )(?P<exceptional_suffix>\?)?(?#
            Compile-time Suffix             )(?P<compile_time_suffix>')?(?#
            Underscores                     )_{0,2}(?#
            End                             )$(?#
        )""",
    ),
)


# ----------------------------------------------------------------------
def _CreateGenericNameToken(
    token_name: str,
    filter_func: Optional[Callable[[str], bool]],
) -> RegexToken:
    if filter_func is None:
        initial_char = "[a-zA-Z]"
        filter_func = lambda value: True
    elif filter_func == str.islower:
        initial_char = "[a-z]"
    elif filter_func == str.isupper:
        initial_char = "[A-Z]"
    else:
        assert False, filter_func  # pragma: no cover

    return RegexToken(
        token_name,
        re.compile(
            textwrap.dedent(
                r"""(?P<value>(?#
                    Initial Underscores [optional]                          )_*(?#
                    Alpha                                                   ){initial_char}(?#
                    Alphanumeric                                            )[a-zA-Z0-9_]*(?#
                    Don't end with an underscore; that will come later      )(?<!_)(?#
                    Don't leave any alphanumeric                            )(?![a-zA-Z0-9])(?#
                    Tokens to ignore                                        ){tokens_to_ignore}(?#
                    Exceptional Mark [optional]                             )\??(?#
                    Compile-time Mark [optional]                            )'?(?#
                    Trailing Underscores [optional]                         )_*(?#
                ))""",
            ).format(
                initial_char=initial_char,
                tokens_to_ignore="".join(
                    [
                        r"(?<!\b{})".format(re.escape(keyword))
                        for keyword in ReservedKeywords
                        if filter_func(keyword[0])
                    ],
                ),
            ),
        ),
    )


GenericName                                 = _CreateGenericNameToken("<generic_name>", None)
GenericUpperName                            = _CreateGenericNameToken("<generic_upper_name>", str.isupper)
GenericLowerName                            = _CreateGenericNameToken("<generic_lower_name>", str.islower)

del _CreateGenericNameToken


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidTokenError(Error):
    Value: str
    TokenType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Value}' is not a valid '{TokenType}' token.", # TODO: Additional error info
    )
