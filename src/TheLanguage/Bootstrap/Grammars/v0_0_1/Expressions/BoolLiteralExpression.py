# ----------------------------------------------------------------------
# |
# |  BoolLiteralExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-25 09:22:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BoolLiteralExpression object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.BoolLiteralExpressionImpl import BoolLiteralExpressionImpl
    from ...GrammarInfo import DynamicPhrasesType


# ----------------------------------------------------------------------
class BoolLiteralExpression(BoolLiteralExpressionImpl):
    """\
    A boolean value.

    Examples:
        True
        False
    """

    PHRASE_NAME                             = "Bool Literal Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(BoolLiteralExpression, self).__init__(
            self.PHRASE_NAME,
            DynamicPhrasesType.Expressions,
        )