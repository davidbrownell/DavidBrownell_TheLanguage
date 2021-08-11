# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-02 18:09:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functions used across the files in this directory"""

import os

from typing import List, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..MethodDefinitionStatement import MethodDefinitionStatement, MethodType

    from ...AST import StatementNode

    from ...Common import Flags
    from ...Common.FuncDefinitionNode import FuncDefinitionNode


# ----------------------------------------------------------------------
def CreateMethod(
    name: str,
    return_type: str,
    parameters: Optional[List[FuncDefinitionNode.ParameterNode]],
    statements:List[StatementNode],
    is_mutable: bool,
) -> MethodDefinitionStatement:
    return MethodDefinitionStatement(
        SourceRange=None,
        SourceRanges={
            "Name" : None,
            "ReturnType" : None,
            "Statements" : None,
        },
        Flags=Flags.FunctionFlags.Standard,
        Name=name,
        ReturnType=None, # BugBug
        PositionalParameters=None,
        AnyParameters=parameters,
        KeywordParameters=None,
        CapturedVars=None,
        Visibility=Flags.VisibilityType.Public,
        Statements=statements,
        Method=MethodType.Standard,
        InstanceType=Flags.TypeFlags.Mutable if is_mutable else Flags.TypeFlags.Immutable,
    )
