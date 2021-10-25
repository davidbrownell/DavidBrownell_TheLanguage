# ----------------------------------------------------------------------
# |
# |  Tokens.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-29 10:25:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Tokens used in the creation of multiple phrases"""

import os
import re
import textwrap

from typing import Callable, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
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


# ----------------------------------------------------------------------
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
# We should not generically match these keywords:
#
ReservedKeywords                            = [
    # ../Statements/BreakStatement.py
    "break",

    # ../Statements/ContinueStatement.py
    "continue",

    # ../Statements/DeleteStatement.py
    "del",

    # ../Statements/RaiseStatement.py
    "raise",

    # ../Statements/ReturnStatement.py
    "return",

    # ../Statements/ScopedRefStatement.py
    "as", # TODO: Is this necessary?

    # ../Statements/YieldStatement.py
    "yield",

    # ../Expressions.BoolLiteralExpression.py
    "True",
    "False",

    # ../Expressions/NoneLiteralExpression.py
    "None",

    # ../Expressions/UnaryExpression.py
    "await",                                # Coroutines
    "copy",                                 # Transfer
    "move",                                 # Transfer
    "not",                                  # Logical
]


# ----------------------------------------------------------------------
def _CreateToken(
    token_name: str,
    regex: str,
    filter_func: Callable[[str], bool],
    *,
    template_var: Optional[str]=None,
):
    regex_suffixes = []

    for reserved_keyword in ReservedKeywords:
        if not filter_func(reserved_keyword[0]):
            continue

        regex_suffixes.append(r"(?<!{})".format(re.escape(reserved_keyword)))

    regex_suffixes = "".join(regex_suffixes)

    if template_var is not None:
        regex = regex.format(**{template_var: regex_suffixes})
    else:
        regex = "{}{}".format(regex, regex_suffixes)

    return RegexToken(token_name, re.compile(regex))


# ----------------------------------------------------------------------
ArgumentName                                = _CreateToken("<argument_name>", r"(?P<value>[a-z][A-Za-z0-9_]*)(?<!__)\b", str.islower)
VariableName                                = _CreateToken("<variable_name>", r"(?P<value>_?[a-z][A-Za-z0-9_]*)(?<!__)\b", str.islower)
ParameterName                               = _CreateToken("<parameter_name>", r"(?P<value>[a-z][A-Za-z0-9_]*)(?<!__)\b", str.islower)

AttributeName                               = _CreateToken("<attribute_name>", r"(?P<value>[A-Z][A-Za-z0-9_]+(?<!__))\b", str.isupper)
TypeName                                    = _CreateToken("<type_name>", r"(?P<value>_?[A-Z][A-Za-z0-9_]+(?<!__))\b", str.isupper)

FuncName                                    = _CreateToken(
    "<func_name>",
    textwrap.dedent(
        r"""(?P<value>(?#
            Underscores                                 )_{{0,2}}(?#
            Func Name                                   )(?P<alphanum>[A-Z][A-Za-z0-9_]+)(?#
            Do not end with an underscore               )(?<!_)(?#
            Do not match an extra alpha char            )(?![A-Za-z0-9])(?#
            Do not match tokens                         ){tokens}(?#
            generator suffix                            )(?P<generator_suffix>\.\.\.)?(?#
            exceptional suffix                          )(?P<exceptional_suffix>\?)?(?#
            Underscores                                 )(?:__)?(?#
        ))""",
    ),
    str.isupper,
    template_var="tokens",
)
