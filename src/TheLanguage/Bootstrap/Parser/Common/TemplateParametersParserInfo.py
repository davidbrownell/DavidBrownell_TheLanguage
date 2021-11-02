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
    from ..TemplateDecoratorExpressions.TemplateDecoratorExpressionParserInfo import TemplateDecoratorExpressionParserInfo
    from ..TemplateDecoratorTypes.TemplateDecoratorTypeParserInfo import TemplateDecoratorTypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateParameterParserInfo(ParserInfo):
    Name: str


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateTypeParameterParserInfo(TemplateParameterParserInfo):
    Default: Optional[str]
    IsVariadic: Optional[bool]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(TemplateTypeParameterParserInfo, self).__post_init__(regions)
        assert self.IsVariadic is None or self.IsVariadic


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateDecoratorParameterParserInfo(TemplateParameterParserInfo):
    Type: TemplateDecoratorTypeParserInfo
    Default: Optional[TemplateDecoratorExpressionParserInfo]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            with helper["Type"]:
                self.Type.Accept(visitor, stack, *args, **kwargs)

            if self.Default is not None:
                with helper["Default"]:
                    self.Default.Accept(visitor, stack, *args, **kwargs)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateParametersParserInfo(ParserInfo):
    Positional: Optional[List[TemplateParameterParserInfo]]
    Any: Optional[List[TemplateParameterParserInfo]]
    Keyword: Optional[List[TemplateParameterParserInfo]]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(TemplateParametersParserInfo, self).__post_init__(regions)
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
