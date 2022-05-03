# ----------------------------------------------------------------------
# |
# |  Visitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-26 08:51:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Visitor object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .CommonMixin import CommonMixin
    from .ExpressionsMixin import ExpressionsMixin
    from .StatementsMixin import StatementsMixin


# ----------------------------------------------------------------------
class Visitor(
    CommonMixin,
    ExpressionsMixin,
    StatementsMixin,
):
    pass
