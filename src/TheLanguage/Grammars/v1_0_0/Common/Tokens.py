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
import textwrap

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
        MultilineRegexToken,                # Included as a convenience for other modules; do not remove
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

Name                                        = RegexToken(
    "<name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Initial char [not a number]             )[A-Za-z_\.](?#
                Alpha numeric, underscore, dot          )[A-Za-z_\.0-9]*(?#
                [optional] Trailing ? for funcs         )\??(?#
            ))""",
        ),
    ),
)

Equal                                       = RegexToken("'='", re.compile(r"\="))
Colon                                       = RegexToken("':'", re.compile(r":"))
Comma                                       = RegexToken("','", re.compile(r","))

LParen                                      = RegexToken("'('", re.compile(r"\("))
RParen                                      = RegexToken("')'", re.compile(r"\)"))

DocString                                   = RegexToken(
    "<docstring>",
    re.compile(
        r'"""\n(?P<value>.+?)\n\s*"""',
        re.DOTALL | re.MULTILINE,
    ),
    is_multiline=True,
)

# ----------------------------------------------------------------------
# |  ClassDeclarationStatement
Class                                       = RegexToken("'class'", re.compile(r"class\b"))
Public                                      = RegexToken("'public'", re.compile(r"public\b"))
Protected                                   = RegexToken("'protected'", re.compile(r"protected\b"))
Private                                     = RegexToken("'private'", re.compile(r"private\b"))
Implements                                  = RegexToken("'implements'", re.compile(r"implements\b"))
Uses                                        = RegexToken("'uses'", re.compile(r"uses\b"))

# ----------------------------------------------------------------------
# |  FunctionDeclarationStatement

# Traditional Parameters
FunctionParameterPositionalDelimiter        = RegexToken("'/'", re.compile(r"/"))
FunctionParameterKeywordDelimiter           = RegexToken("'*'", re.compile(r"\*"))

# New Style Parameters
FunctionParameterPositional                 = RegexToken("'pos'", re.compile(r"pos\b"))
FunctionParameterAny                        = RegexToken("'any'", re.compile(r"any\b"))
FunctionParameterKeyword                    = RegexToken("'key'", re.compile(r"key\b"))

# New Style Parameters must be grouped in this order
AllNewStyleParameters                       = [
    FunctionParameterPositional,
    FunctionParameterAny,
    FunctionParameterKeyword,
]

# ----------------------------------------------------------------------
# |  ImportStatement
From                                        = RegexToken("'from'", re.compile(r"from\b"))
Import                                      = RegexToken("'import'", re.compile(r"import\b"))
As                                          = RegexToken("'as'", re.compile(r"as\b"))

Export                                      = RegexToken("'export'", re.compile(r"export\b"))

# ----------------------------------------------------------------------
# |  PassStatement
Pass                                        = RegexToken("'pass'", re.compile(r"pass\b"))

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

Var                                         = RegexToken("'var'", re.compile(r"var\b"))
Ref                                         = RegexToken("'ref'", re.compile(r"ref\b"))
Val                                         = RegexToken("'val'", re.compile(r"val\b"))
View                                        = RegexToken("'view'", re.compile(r"view\b"))

Isolated                                    = RegexToken("'isolated'", re.compile(r"isolated\b"))
Shared                                      = RegexToken("'shared'", re.compile(r"shared\b"))

Mutable                                     = RegexToken("'mutable'", re.compile(r"mutable\b"))
Immutable                                   = RegexToken("'immutable'", re.compile(r"immutable\b"))
