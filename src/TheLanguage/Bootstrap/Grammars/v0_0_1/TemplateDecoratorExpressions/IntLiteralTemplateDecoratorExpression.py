import os

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.IntLiteralExpressionImpl import IntLiteralExpressionImpl

    from ...GrammarInfo import DynamicPhrasesType


# ----------------------------------------------------------------------
class IntLiteralTemplateDecoratorExpression(IntLiteralExpressionImpl):
    """\
    Type declaration.

    <type_name> <modifier>?

    Examples:
        Int
        Int var
    """

    PHRASE_NAME                             = "Int Literal TemplateDecoratorExpression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(IntLiteralTemplateDecoratorExpression, self).__init__(
            self.PHRASE_NAME,
            DynamicPhrasesType.TemplateDecoratorExpressions,
        )
