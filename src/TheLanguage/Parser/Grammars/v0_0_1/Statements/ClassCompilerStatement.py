# ----------------------------------------------------------------------
# |
# |  ClassCompilerStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-03 09:54:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassCompilerStatement object"""

import os

from typing import Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.MultilineStatementBase import MultilineStatementBase
    from ....Phrases.DSL import Leaf, Node


# ----------------------------------------------------------------------
class ClassCompilerStatement(MultilineStatementBase):
    """\
    A statement that contains instructions used during the complication process.

    '<<<!!!'
    <content>
    '!!!>>>'
    """

    PHRASE_NAME                             = "Class Compiler Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ClassCompilerStatement, self).__init__(
            self.PHRASE_NAME,
            "<<<!!!",
            "!!!>>>",
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _ValidateNodeSyntaxImpl(
        self,
        node: Node,
        leaf: Leaf,
        value: str,
    ) -> Optional[bool]:
        # Persist the info
        object.__setattr__(node, "Info", value)
