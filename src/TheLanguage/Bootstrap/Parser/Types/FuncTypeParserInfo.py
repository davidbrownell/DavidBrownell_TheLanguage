import os

from typing import List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeParserInfo import TypeModifier, TypeParserInfo, Region

    from ..Common.FunctionParametersParserInfo import FunctionParameterTypeParserInfo
    from ..Common.VisitorTools import StackHelper


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncTypeParserInfo(TypeParserInfo):
    ReturnType: TypeParserInfo
    Parameters: Union[bool, List[FunctionParameterTypeParserInfo]]

    # TODO: A lot of redundancy with FuncDefinitionStatementParserInfo that should be resolved

    IsGenerator: Optional[bool]
    IsReentrant: Optional[bool]
    IsExceptional: Optional[bool]
    IsScoped: Optional[bool]
    IsAsync: Optional[bool]

    Modifier: Optional[TypeModifier]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(FuncTypeParserInfo, self).__post_init__(regions)

        assert self.IsGenerator is None or self.IsGenerator
        assert self.IsReentrant is None or self.IsReentrant
        assert self.IsExceptional is None or self.IsExceptional
        assert self.IsScoped is None or self.IsScoped
        assert self.IsAsync is None or self.IsAsync

    # ----------------------------------------------------------------------
    @Interface.override
    def GetTypeModifier(self) -> Optional[Tuple[TypeModifier, Region]]:
        """Returns information a TypeModifier associated with the type (if any)"""

        if self.Modifier is None:
            return None

        return (self.Modifier, self.Regions__.Modifier)  # type: ignore && pylint: disable=no-member

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            with helper["ReturnType"]:
                self.ReturnType.Accept(visitor, helper.stack, *args, **kwargs)

            if isinstance(self.Parameters, list):
                with helper["Parameters"]:
                    for parameter in self.Parameters:
                        parameter.Accept(visitor, helper.stack, *args, **kwargs)
