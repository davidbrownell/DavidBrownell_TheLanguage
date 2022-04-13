# ----------------------------------------------------------------------
# |
# |  PassStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-01 12:29:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PassStatement object"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementPhrase import StatementPhrase


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class PassStatement(StatementPhrase):
    """Noop statement"""

    # ----------------------------------------------------------------------
    def __post_init__(self, diagnostics, regions):
        super(PassStatement, self).__post_init__(diagnostics, regions)
