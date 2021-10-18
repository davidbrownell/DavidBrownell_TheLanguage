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
DoNotMatchKeywords                          = [
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

    # ../Expressions/UnaryExpression.py
    "await",                                # Coroutines
    "copy",                                 # Transfer
    "move",                                 # Transfer
    "not",                                  # Logical
]


# ----------------------------------------------------------------------

# This token is intended to be a generic token that will match every name used in the grammar so that
# we don't see complicated syntax errors when incorrect naming conventions are used. Grammars leveraging
# this token should perform more specific regex matching during their custom validation process.
def _CreateVariableName():
    regex_suffixes = []

    for do_not_match_keyword in DoNotMatchKeywords:
        regex_suffixes.append(r"(?<!{})".format(re.escape(do_not_match_keyword)))

    regex = r"(?P<value>_?[a-z][A-Za-z0-9_]*)(?<!__)\b{}".format("".join(regex_suffixes))

    return RegexToken("<variable_name>", re.compile(regex))


VariableName                                = _CreateVariableName()

del _CreateVariableName


# ----------------------------------------------------------------------
ArgumentName                                = RegexToken(
    "<argument_name>",
    re.compile(r"(?P<value>[a-z][A-Za-z0-9_]*)(?<!__)\b"),
)


AttributeName                               = RegexToken(
    "<attribute_name>",
    re.compile(r"(?P<value>[A-Z][A-Za-z0-9_]+(?<!__))\b"),
)


FuncName                                    = RegexToken(
    "<func_name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Underscores                             )_{0,2}(?#
                Func Name                               )(?P<alphanum>[A-Z][A-Za-z0-9_]+)(?<!_)(?#
                generator suffix                        )(?P<generator_suffix>\.\.\.)?(?#
                exceptional suffix                      )(?P<exceptional_suffix>\?)?(?#
                Underscores                             )_{0,2}(?#
                End of Word                             )(?#
            ))""",
        ),
    ),
)


ParameterName                               = RegexToken(
    "<parameter_name>",
    re.compile(r"(?P<value>[a-z][A-Za-z0-9_]*)(?<!__)\b"),
)


TypeName                                    = RegexToken(
    "<type_name>",
    re.compile(r"(?P<value>_?[A-Z][A-Za-z0-9_]+(?<!__))\b"),
)
