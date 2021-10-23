# ----------------------------------------------------------------------
# |
# |  ParametersParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-07 12:04:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParametersParserInfo and ParameterParserInfo objects"""

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
    from .VisitorTools import StackHelper, VisitType

    from ..Parser import ParserInfo
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Types.TypeParserInfo import TypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParameterParserInfo(ParserInfo):
    Type: TypeParserInfo
    Name: str
    Default: Optional[ExpressionParserInfo]
    IsVarArgs: Optional[bool]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(ParameterParserInfo, self).__post_init__(regions)
        assert self.IsVarArgs is None or self.IsVarArgs, self

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        if visitor.OnParameter(stack, VisitType.Enter, self, *args, **kwargs) is False:
            return

        with StackHelper(stack)[self] as helper:
            with helper["Type"]:
                self.Type.Accept(visitor, helper.stack, *args, **kwargs)

            if self.Default is not None:
                with helper["Default"]:
                    self.Default.Accept(visitor, helper.stack, *args, **kwargs)

        visitor.OnParameter(stack, VisitType.Exit, self, *args, **kwargs)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParametersParserInfo(ParserInfo):
    Positional: Optional[List[ParameterParserInfo]]
    Keyword: Optional[List[ParameterParserInfo]]
    Any: Optional[List[ParameterParserInfo]]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(ParametersParserInfo, self).__post_init__(regions)
        assert self.Positional or self.Keyword or self.Any

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        if visitor.OnParameters(stack, VisitType.Enter, self, *args, **kwargs) is False:
            return

        with StackHelper(stack)[self] as helper:
            if self.Positional is not None:
                with helper["Positional"]:
                    for parameter in self.Positional:
                        parameter.Accept(visitor, helper.stack, *args, **kwargs)

            if self.Keyword is not None:
                with helper["Keyword"]:
                    for parameter in self.Keyword:
                        parameter.Accept(visitor, helper.stack, *args, **kwargs)

            if self.Any is not None:
                with helper["Any"]:
                    for parameter in self.Any:
                        parameter.Accept(visitor, helper.stack, *args, **kwargs)

        visitor.OnParameters(stack, VisitType.Exit, self, *args, **kwargs)
