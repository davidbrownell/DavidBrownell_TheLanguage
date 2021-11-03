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
    from .VisitorTools import StackHelper
    from ..ParserInfo import ParserInfo
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Types.TypeParserInfo import TypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FunctionParameterTypeParserInfo(ParserInfo):
    Type: TypeParserInfo
    IsVariadic: Optional[bool]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(FunctionParameterTypeParserInfo, self).__post_init__(regions)
        assert self.IsVariadic is None or self.IsVariadic, self

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[(self, "Type")] as helper:
            self.Type.Accept(visitor, helper.stack, *args, **kwargs)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FunctionParameterParserInfo(FunctionParameterTypeParserInfo):
    Name: str
    Default: Optional[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        super(FunctionParameterParserInfo, self)._AcceptImpl(visitor, stack, *args, **kwargs)

        if self.Default is not None:
            with StackHelper(stack)[(self, "Default")] as helper:
                self.Default.Accept(visitor, helper.stack, *args, **kwargs)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FunctionParametersParserInfo(ParserInfo):
    Positional: Optional[List[FunctionParameterParserInfo]]
    Any: Optional[List[FunctionParameterParserInfo]]
    Keyword: Optional[List[FunctionParameterParserInfo]]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(FunctionParametersParserInfo, self).__post_init__(regions)
        assert self.Positional or self.Any or self.Keyword

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            if self.Positional is not None:
                with helper["Positional"]:
                    for item in self.Positional:
                        item.Accept(visitor, stack, *args, **kwargs)

            if self.Any is not None:
                with helper["Any"]:
                    for item in self.Any:
                        item.Accept(visitor, stack, *args, **kwargs)

            if self.Keyword is not None:
                with helper["Keyword"]:
                    for item in self.Keyword:
                        item.Accept(visitor, stack, *args, **kwargs)
