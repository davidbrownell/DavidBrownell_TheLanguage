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
                Initial char [not a number or period]   )[A-Za-z](?#
                Alpha numeric, underscore, dot          )[A-Za-z0-9\._]*(?#
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

# ----------------------------------------------------------------------
# |  PassStatement
Pass                                        = RegexToken("'pass'", re.compile(r"pass\b"))
