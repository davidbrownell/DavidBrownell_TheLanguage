# ----------------------------------------------------------------------
# |
# |  QuickRefExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 16:17:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the QuickRefExpression object"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment.DataclassDecorators import DataclassDefaultValues

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.AST import Node


# ----------------------------------------------------------------------
@DataclassDefaultValues(
    Type=Node.NodeType.Expression,  # type: ignore
)
@dataclass(frozen=True)
class QuickRefExpression(Node):
    """\
    TODO: Comment
    """

    Ref: str

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(QuickRefExpression, self).__post_init__()

        # TODO: Validate only used in func invocation where return value is not a ref. Also needs
        #       to match parameter.
