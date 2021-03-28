# ----------------------------------------------------------------------
# |
# |  Tokens.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-03-27 22:34:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains common tokens"""

import inspect
import os

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Set these values dynamically at the global namespace so that we can auto-calculate the length
_frame = inspect.stack()[0][0]
_mod = inspect.getmodule(_frame)

for name, token in [
    ("MULTILINE_STRING_TOKEN", '"""'),
    ("COMMENT_TOKEN", "#"),
]:
    setattr(_mod, name, token)
    setattr(_mod, "{}_length".format(name), len(token))

del _mod
del _frame
