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

# This token is intended to be a generic token that will match every name used in the grammar so that
# we don't see complicated syntax errors when incorrect naming conventions are used. Grammars leveraging
# this token should perform more specific regex matching during their custom validation process.
GenericName                                 = RegexToken("<name>", re.compile(r"(?P<value>[a-zA-Z0-9_\.]+\??)\b"))
