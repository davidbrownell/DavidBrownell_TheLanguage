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
class BoolLiteralTemplateDecoratorExpression(BoolLiteralExpressionImpl):
    """\
    A boolean value.

    Examples:
        True
        False
    """

    PHRASE_NAME                             = "Bool Literal TemplateDecoratorExpression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(BoolLiteralTemplateDecoratorExpression, self).__init__(
            self.PHRASE_NAME,
            DynamicPhrasesType.TemplateDecoratorExpressions,
        )
