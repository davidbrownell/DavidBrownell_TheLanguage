# ----------------------------------------------------------------------
# |
# |  GenericNameExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-11 13:01:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GenericNameExpressionParserInfo object"""

import os

from typing import List, Optional

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

    from ..Common.ConstraintArgumentParserInfo import ConstraintArgumentParserInfo
    from ..Common.TemplateArgumentParserInfo import TemplateArgumentParserInfo
    from ..Common.VisitorTools import StackHelper


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class GenericNameExpressionParserInfo(ExpressionParserInfo):
    Name: str
    Templates: Optional[List[TemplateArgumentParserInfo]]
    Constraints: Optional[List[ConstraintArgumentParserInfo]]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        if self.Templates is not None or self.Constraints is not None:
            with StackHelper(stack)[self] as helper:
                if self.Templates is not None:
                    with helper["Templates"]:
                        for template in self.Templates:
                            template.Accept(visitor, helper.stack, *args, **kwargs)

                if self.Constraints is not None:
                    with helper["Constraints"]:
                        for constraint in self.Constraints:
                            constraint.Accept(visitor, helper.stack, *args, **kwargs)
