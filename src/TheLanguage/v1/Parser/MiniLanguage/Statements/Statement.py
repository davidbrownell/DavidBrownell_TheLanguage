# ----------------------------------------------------------------------
# |
# |  Statement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-17 09:14:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Statement object"""

import os

from typing import Any, Dict, List

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Expressions.Expression import Expression
    from ..Types.Type import Type
    from ...Error import Error, Warning, Info


# ----------------------------------------------------------------------
class Statement(Interface.Interface, ObjectReprImplBase):
    """Abstract base class for all statements"""

    # ----------------------------------------------------------------------
    # |  Public Types
    @dataclass
    class ExecuteResult(object):
        errors: List[Error]
        warnings: List[Warning]
        infos: List[Info]

        should_continue: bool

    # ----------------------------------------------------------------------
    # |  Public Methods
    @staticmethod
    @Interface.abstractmethod
    def Execute(
        args: Dict[str, Any],
        type_overrides: Dict[str, Type],
    ) -> "Statement.ExecuteResult":
        raise Exception("Abstract method")  # pragma: no cover
