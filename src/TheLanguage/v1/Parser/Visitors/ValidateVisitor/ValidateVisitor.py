# ----------------------------------------------------------------------
# |
# |  ValidateVisitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-27 13:42:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ValidateVisitor object"""

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
    from .MiniLanguageMixin import MiniLanguageMixin
    from .StatementsMixin import StatementsMixin
    from .TypesMixin import TypesMixin


# ----------------------------------------------------------------------
class ValidateVisitor(
    CommonMixin,
    ExpressionsMixin,
    MiniLanguageMixin,
    StatementsMixin,
    TypesMixin,
):
    pass
