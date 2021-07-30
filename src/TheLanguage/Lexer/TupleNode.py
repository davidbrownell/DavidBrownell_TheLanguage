# ----------------------------------------------------------------------
# |
# |  TupleNode.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-29 20:34:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleNode object"""

import os

from typing import List

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common.AST import Node


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TupleNode(Node):
    """\
    TODO: Comment
    """

    Elements: List[Node]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        self.ValidateTypes(
            Elements=self.Type,
        )
