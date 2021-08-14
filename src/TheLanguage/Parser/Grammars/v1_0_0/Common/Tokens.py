# ----------------------------------------------------------------------
# |
# |  Tokens.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 15:51:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Tokens used across multiple phrases"""

import os
import re

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....Components.Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        RegexToken,
    )


# ----------------------------------------------------------------------
Dedent                                      = DedentToken()
Indent                                      = IndentToken()
Newline                                     = NewlineToken()
PopIgnoreWhitespaceControl                  = PopIgnoreWhitespaceControlToken()
PushIgnoreWhitespaceControl                 = PushIgnoreWhitespaceControlToken()

# These keywords are special and should not be consumed by the generic expression below. Without
# this special consideration, the phrase (for example):
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
    # ../Statements/DeleteStatement.py
    "del",

    # ../Statements/ReturnStatement.py
    "return",

    # ../Statements/ThrowStatement.py
    "throw",

    # ../Statements/YieldStatement.py
    "yield",

    # ../Expressions/UnaryExpression.py
    "not",                                  # Logical
    "move",                                 # Transfer
    "copy",                                 # Transfer
]


# ----------------------------------------------------------------------

# This token is intended to be a generic token that will match every name used in the grammar so that
# we don't see complicated syntax errors when incorrect naming conventions are used. Grammars leveraging
# this token should perform more specific regex matching during their custom validation process.
def _CreateGenericName():
    regex_suffixes = []

    for do_not_match_keyword in DoNotMatchKeywords:
        regex_suffixes.append(r"(?<!{})".format(re.escape(do_not_match_keyword)))

    regex = r"(?P<value>[a-zA-Z0-9_\.]+\??)\b{}".format("".join(regex_suffixes))

    return RegexToken("<generic_name>", re.compile(regex))


GenericName                                 = _CreateGenericName()


del _CreateGenericName
