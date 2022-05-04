# ----------------------------------------------------------------------
# |
# |  Errors.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-03 12:38:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains Common Errors"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Parser.Error import CreateError


# ----------------------------------------------------------------------
InvalidCompileTimeNameError                 = CreateError(
    "The {type} name '{name}' is a compile-time name and not valid in this context",
    name=str,
    type=str,
)
