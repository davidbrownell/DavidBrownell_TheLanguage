# ----------------------------------------------------------------------
# |
# |  NoneLiteralExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-22 11:01:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NoneLiteralExpression object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.NoneLiteralExpressionImpl import NoneLiteralExpressionImpl
    from ...GrammarInfo import DynamicPhrasesType


# ----------------------------------------------------------------------
class NoneLiteralTemplateDecoratorExpression(NoneLiteralExpressionImpl):
    """\
    None.

    Examples:
        None
    """

    PHRASE_NAME                             = "None Literal TemplateDecoratorExpression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(NoneLiteralTemplateDecoratorExpression, self).__init__(
            self.PHRASE_NAME,
            DynamicPhrasesType.TemplateDecoratorExpressions,
        )
