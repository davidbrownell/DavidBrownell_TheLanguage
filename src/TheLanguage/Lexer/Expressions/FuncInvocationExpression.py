# ----------------------------------------------------------------------
# |
# |  FuncInvocationExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-31 18:35:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationExpression object"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..AST import ExpressionNode

    from ..Common.FuncInvocationNode import (
        FunctionCallType,                               # Not used directly, but here as a convenience to callers
        FuncInvocationNode as _FuncInvocationNode,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FuncInvocationExpression(ExpressionNode, _FuncInvocationNode):
    """\
    TODO: Describe
    """

    pass
