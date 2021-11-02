import os

from typing import Optional, Union

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
class TemplateArgumentParserInfo(ParserInfo):
    TypeOrExpression: Union[str, TemplateDecoratorExpressionParserInfo]
    Keyword: Optional[str]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        if isinstance(self.TypeOrExpression, TemplateDecoratorExpressionParserInfo):
            with StackHelper(stack)[(self, "TypeOrExpression")] as helper:
                self.TypeOrExpression.Accept(visitor, helper.stack, *args, **kwargs)
