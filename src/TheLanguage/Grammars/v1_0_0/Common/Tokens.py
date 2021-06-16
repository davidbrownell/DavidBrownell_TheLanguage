# ----------------------------------------------------------------------
# |
# |  Tokens.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-13 12:09:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains common tokens used across multiple statements"""

import os
import re

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....ParserImpl.Token import (
        DedentToken,
        IndentToken,
        NewlineToken,                       # Included as a convenience for other modules; do not remove
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        RegexToken,
    )


# ----------------------------------------------------------------------
# |  General
Dedent                                      = DedentToken()
Indent                                      = IndentToken()
PopIgnoreWhitespaceControl                  = PopIgnoreWhitespaceControlToken()
PushIgnoreWhitespaceControl                 = PushIgnoreWhitespaceControlToken()

Name                                        = RegexToken("<name>", re.compile(r"(?P<value>[A-Za-z_\.][A-Za-z_\.0-9]*)"))
Equal                                       = RegexToken("'='", re.compile(r"\="))
Colon                                       = RegexToken("':'", re.compile(r":"))
Comma                                       = RegexToken("','", re.compile(r","))

LParen                                      = RegexToken("'('", re.compile(r"\("))
RParen                                      = RegexToken("')'", re.compile(r"\)"))

# ----------------------------------------------------------------------
# |  FunctionDeclarationStatement

# Traditional Parameters
FunctionParameterPositionalDelimiter        = RegexToken("'/'", re.compile(r"/"))
FunctionParameterKeywordDelimiter           = RegexToken("'*'", re.compile(r"\*"))

# New Style Parameters
FunctionParameterPositional                 = RegexToken("'pos'", re.compile(r"pos"))
FunctionParameterAny                        = RegexToken("'any'", re.compile(r"any"))
FunctionParameterKeyword                    = RegexToken("'key'", re.compile(r"key"))

# New Style Parameters must be grouped in this order
AllNewStyleParameters                       = [
    FunctionParameterPositional,
    FunctionParameterAny,
    FunctionParameterKeyword,
]

# ----------------------------------------------------------------------
# |  ImportStatement
From                                        = RegexToken("'from'", re.compile(r"from"))
Import                                      = RegexToken("'import'", re.compile(r"import"))
As                                          = RegexToken("'as'", re.compile(r"as"))

Export                                      = RegexToken("'export'", re.compile(r"export"))

# ----------------------------------------------------------------------
# |  PassStatement
Pass                                        = RegexToken("'pass'", re.compile(r"pass"))

# ----------------------------------------------------------------------
# |  VariableDeclarationStatement

#             isolated    shared
#             --------    ------
# mutable:      var        ref
# immutable:    val        view
#
# variables:    var, val, view
# parameters:   isolated, shared, immutable
# methods:      mutable/mut, immutable/const

Var                                         = RegexToken("'var'", re.compile(r"var"))
Ref                                         = RegexToken("'ref'", re.compile(r"ref"))
Val                                         = RegexToken("'val'", re.compile(r"val"))
View                                        = RegexToken("'view'", re.compile(r"view"))

Isolated                                    = RegexToken("'isolated'", re.compile(r"isolated"))
Shared                                      = RegexToken("'shared'", re.compile(r"shared"))

Mutable                                     = RegexToken("'mutable'", re.compile(r"mutable"))
Immutable                                   = RegexToken("'immutable'", re.compile(r"immutable"))
