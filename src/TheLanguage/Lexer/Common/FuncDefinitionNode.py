# ----------------------------------------------------------------------
# |
# |  FuncDefinitionNode.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-29 10:29:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncDefinitionNode object"""

import os

from typing import List, Optional

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Flags
    from ..AST import Node, ExpressionNode, TypeNode, VariableNode
    from ..Types.FirstClassFunctionType import FirstClassFunctionType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FuncDefinitionNode(Node):
    """\
    TODO: Comment
    """

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ParameterNode(Node):
        """\
        TODO: Comment
        """

        Name: VariableNode
        Type: TypeNode
        DefaultValue: Optional[ExpressionNode]

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    Flags: Flags.FunctionFlags

    Name: str
    ReturnType: Optional[TypeNode]

    PositionalParameters: Optional[List[ParameterNode]]
    AnyParameters: Optional[List[ParameterNode]]
    KeywordParameters: Optional[List[ParameterNode]]

    # TODO: Attributes

    CapturedVars: Optional[List[str]]

    FirstClassFunction: FirstClassFunctionType          = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        # BugBug: Are the captures valid?

        # ----------------------------------------------------------------------
        def ToFirstClassFunctionParameters(
            parameters: Optional[List[FuncDefinitionNode.ParameterNode]],
        ) -> Optional[List[FirstClassFunctionType.ParameterNode]]:
            if parameters is None:
                return None

            return [
                FirstClassFunctionType.ParameterNode(
                    parameter.SourceRange,
                    parameter.SourceRanges,
                    parameter.Type,
                    parameter.DefaultValue,
                )
                for parameter in parameters
            ]

        # ----------------------------------------------------------------------

        object.__setattr__(
            self,
            "FirstClassFunction",
            FirstClassFunctionType(
                self.SourceRange,
                self.SourceRanges,
                self.Flags,
                self.ReturnType,
                ToFirstClassFunctionParameters(self.PositionalParameters),
                ToFirstClassFunctionParameters(self.AnyParameters),
                ToFirstClassFunctionParameters(self.KeywordParameters),
            ),
        )
