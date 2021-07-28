# ----------------------------------------------------------------------
# |
# |  Tokens.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 09:55:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains tokens used by statements within the grammar"""

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
        NewlineToken,
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        RegexToken,
        Token,
    )

# ----------------------------------------------------------------------
# |  General
Dedent                                      = DedentToken()
Indent                                      = IndentToken()
Newline                                     = NewlineToken()
PopIgnoreWhitespaceControl                  = PopIgnoreWhitespaceControlToken()
PushIgnoreWhitespaceControl                 = PushIgnoreWhitespaceControlToken()

Comment                                     = RegexToken(
    "<comment>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Prefix                      )\#(?#
                Content                     )[^\n]*(?#
            ))""",
        ),
    ),
    is_always_ignored=True,
)

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

# ----------------------------------------------------------------------
# |  FunctionDeclarationStatement


# ----------------------------------------------------------------------
# |  FuncInvocationStatements
# Traditional Parameters
FunctionParameterPositionalDelimiter        = RegexToken("'/'", re.compile(r"/"))
FunctionParameterKeywordDelimiter           = RegexToken("'*'", re.compile(r"\*"))

# New Style Parameters
FunctionParameterPositional                 = RegexToken("'pos'", re.compile(r"pos\b"))
FunctionParameterAny                        = RegexToken("'any'", re.compile(r"any\b"))
FunctionParameterKeyword                    = RegexToken("'key'", re.compile(r"key\b"))

# When declaring a function, new style parameters must be grouped in this order
AllNewStyleParameters                       = [
    FunctionParameterPositional,
    FunctionParameterAny,
    FunctionParameterKeyword,
]

FunctionParameterVarArgsType                = RegexToken("'*'", re.compile(r"\*"))

ArrowedName                                 = RegexToken(
    "<arrowed_name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Arrow                                   )\-\>(?#
                Initial char [not a number or dot]      )[A-Za-z_](?#
                Alpha numeric, underscore, dot          )[A-Za-z_\.0-9]*(?#
                [optional] Trailing ? for funcs         )\??(?#
            ))""",
        ),
    ),
)

DottedName                                  = RegexToken(
    "<dotted_name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Dot                                     )\.(?#
                Initial char [not a number or dot]      )[A-Za-z_](?#
                Alpha numeric, underscore, dot          )[A-Za-z_\.0-9]*(?#
                [optional] Trailing ? for funcs         )\??(?#
            ))""",
        ),
    ),
)

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
# |  VariantType
VariantSep                                  = RegexToken("'|'", re.compile(r"\|"))
