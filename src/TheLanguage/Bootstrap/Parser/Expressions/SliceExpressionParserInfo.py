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
    from .ExpressionParserInfo import ExpressionParserInfo
    from ..Common.VisitorTools import StackHelper


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class SliceExpressionParserInfo(ExpressionParserInfo):
    StartExpression: Optional[ExpressionParserInfo]
    EndExpression: Optional[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(SliceExpressionParserInfo, self).__post_init__(regions)
        assert self.StartExpression is not None or self.EndExpression is not None

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            if self.StartExpression is not None:
                with helper["StartExpression"]:
                    self.StartExpression.Accept(visitor, helper.stack, *args, **kwargs)

            if self.EndExpression is not None:
                with helper["EndExpression"]:
                    self.EndExpression.Accept(visitor, helper.stack, *args, **kwargs)
