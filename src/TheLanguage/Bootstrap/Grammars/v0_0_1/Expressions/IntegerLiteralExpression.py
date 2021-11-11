# ----------------------------------------------------------------------
# |
# |  IntegerLiteralExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-25 09:41:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IntegerLiteralExpression object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.IntLiteralExpressionImpl import IntLiteralExpressionImpl
    from ...GrammarInfo import DynamicPhrasesType


# ----------------------------------------------------------------------
class IntegerLiteralExpression(IntLiteralExpressionImpl):
    """\
    An integer value.

    Examples:
        1
        123
        -1
        +45678
    """

    PHRASE_NAME                             = "Integer Literal Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(IntegerLiteralExpression, self).__init__(
            self.PHRASE_NAME,
            DynamicPhrasesType.Expressions,
        )