# ----------------------------------------------------------------------
# |
# |  CommonTokens.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-06 08:33:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains tokens used by multiple statements"""

import os
import re

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...ParserImpl.Token import (
        NewlineToken,                       # Included as a convenience for other modules; do not remove
        PopIgnoreWhitespaceControlToken,    # Included as a convenience for other modules; do not remove
        PushIgnoreWhitespaceControlToken,   # Included as a convenience for other modules; do not remove
        RegexToken,
    )


# ----------------------------------------------------------------------
NameToken                                   = RegexToken("<name>", re.compile(r"(?P<value>\*?[A-Za-z0-9_\.]+(?:\.\.\.)?\??)"))
UnderscoreToken                             = RegexToken("'_'", re.compile(r"_"))

ColonToken                                  = RegexToken("':'", re.compile(r":"))
CommaToken                                  = RegexToken("','", re.compile(r","))
EqualToken                                  = RegexToken("'='", re.compile(r"\="))

LParenToken                                 = RegexToken("'('", re.compile(r"\("))
RParenToken                                 = RegexToken("')'", re.compile(r"\)"))
LBracketToken                               = RegexToken("'['", re.compile(r"\["))
RBracketToken                               = RegexToken("']'", re.compile(r"\]"))
LBraceToken                                 = RegexToken("'{'", re.compile(r"{"))
RBraceToken                                 = RegexToken("'}'", re.compile(r"}"))
LAngleToken                                 = RegexToken("'<'", re.compile(r"<"))
RAngleToken                                 = RegexToken("'>'", re.compile(r">"))

FromToken                                   = RegexToken("'from'", re.compile("from"))
ImportToken                                 = RegexToken("'import'", re.compile("import"))
AsToken                                     = RegexToken("'as'", re.compile("as"))

#             isolated    shared
#             --------    ------
# mutable:      var        ref
# immutable:    val        view
#
# variables:    var, val, view
# parameters:   isolated, shared, immutable
# methods:      mutable/mut, immutable/const

VarToken                                    = RegexToken("'var'", re.compile(r"var"))
RefToken                                    = RegexToken("'ref'", re.compile(r"ref"))
ValToken                                    = RegexToken("'val'", re.compile(r"val"))
ViewToken                                   = RegexToken("'view'", re.compile(r"view"))

IsolatedToken                               = RegexToken("'isolated'", re.compile(r"isolated"))
SharedToken                                 = RegexToken("'shared'", re.compile(r"shared"))

MutableToken                                = RegexToken("'mut'", re.compile(r"mut"))
ImmutableToken                              = RegexToken("'const'", re.compile(r"const"))

FunctionToken                               = RegexToken("'func'", re.compile(r"func"))
