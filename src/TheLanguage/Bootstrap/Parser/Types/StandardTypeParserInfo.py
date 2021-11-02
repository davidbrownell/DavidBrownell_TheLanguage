import os

from typing import List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeParserInfo import Region, TypeModifier, TypeParserInfo

    from ..Common.ConstraintArgumentParserInfo import ConstraintArgumentParserInfo
    from ..Common.TemplateArgumentParserInfo import TemplateArgumentParserInfo
    from ..Common.VisitorTools import StackHelper


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeParserInfo(TypeParserInfo):
    TypeName: str
    Templates: Optional[List[TemplateArgumentParserInfo]]
    Constraints: Optional[List[ConstraintArgumentParserInfo]]
    Modifier: Optional[TypeModifier]

    # ----------------------------------------------------------------------
    @Interface.override
    def GetTypeModifier(self) -> Optional[Tuple[TypeModifier, Region]]:
        if self.Modifier is None:
            return None

        return (self.Modifier, self.Regions__.Modifier)  # type: ignore && pylint: disable=no-member

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        if self.Templates or self.Constraints:
            with StackHelper(stack)[self] as helper:
                if self.Templates:
                    with helper["Templates"]:
                        for template in self.Templates:
                            template.Accept(visitor, stack, *args, **kwargs)

                if self.Constraints:
                    with helper["Constraints"]:
                        for constraint in self.Constraints:
                            constraint.Accept(visitor, stack, *args, **kwargs)
