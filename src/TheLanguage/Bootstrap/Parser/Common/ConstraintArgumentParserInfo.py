import os

from typing import Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .VisitorTools import StackHelper
    from ..ParserInfo import ParserInfo
    from ..TemplateDecoratorExpressions.TemplateDecoratorExpressionParserInfo import TemplateDecoratorExpressionParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConstraintArgumentParserInfo(ParserInfo):
    Expression: TemplateDecoratorExpressionParserInfo
    Keyword: Optional[str]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[(self, "Expression")] as helper:
            self.Expression.Accept(visitor, helper.stack, *args, **kwargs)
