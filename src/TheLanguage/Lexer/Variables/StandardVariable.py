# ----------------------------------------------------------------------
# |
# |  StandardVariable.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-02 13:06:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardVariable object"""

import os

from typing import List

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..AST import VariableNode


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StandardVariable(VariableNode):
    """\
    TODO: Document
    """

    Name: str

    # ----------------------------------------------------------------------
    @Interface.override
    def VarNames(self) -> List[str]:
        return [self.Name]
