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
