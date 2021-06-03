# ----------------------------------------------------------------------
# |
# |  Statements.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-23 19:38:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains statements used in this grammar version"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ImportStatement import ImportStatement
    from . import StringStatements
    from .VerticalWhitespaceStatement import VerticalWhitespaceStatement

# ----------------------------------------------------------------------
Statements                                  = [
    ImportStatement(".TheLanguage"), # TODO: Fix this once there is a known value

    StringStatements.TripleStringStatement(),
    StringStatements.TripleFormatStringStatement(),
    StringStatements.SimpleStringStatement(),
    StringStatements.SimpleFormatStringStatement(),

    VerticalWhitespaceStatement(),
]
