# ----------------------------------------------------------------------
# |
# |  DocstringStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 16:38:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DocstringStatement object"""

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
    from .Common.AST import Node


# ----------------------------------------------------------------------
@DataclassDefaultValues(
    Type=Node.NodeType.Statement,  # type: ignore
)
@dataclass(frozen=True)
class DocstringStatement(Node):
    """\
    TODO: Comment
    """

    Content: str
