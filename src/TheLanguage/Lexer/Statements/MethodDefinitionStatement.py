# ----------------------------------------------------------------------
# |
# |  MethodDefinitionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 16:40:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MethodDefinitionStatement object"""

import os
from enum import auto, Enum
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
    from ..Common import Flags
    from .FuncDefinitionStatement import FuncDefinitionStatement


# ----------------------------------------------------------------------
class MethodType(Enum):
    """\
    TODO: Comment
    """

    Standard                                = auto()
    Replace                                 = auto()
    Abstract                                = auto()
    Virtual                                 = auto()
    Override                                = auto()
    Final                                   = auto()
    Static                                  = auto()

    # TODO: Static might need New/Replace


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MethodDefinitionStatement(FuncDefinitionStatement):
    """\
    TODO: Comment
    """

    Method: MethodType
    InstanceType: Flags.TypeFlags

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetTypeDescriptions() -> List[str]:
        return ["method"]
