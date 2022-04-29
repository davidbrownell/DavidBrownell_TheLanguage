# ----------------------------------------------------------------------
# |
# |  Expression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-15 13:19:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Expression object"""

import os

from typing import Any, Dict, Optional

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
    from ..Types.Type import Type


# ----------------------------------------------------------------------
class Expression(Interface.Interface, ObjectReprImplBase):
    """Abstract base class for all expressions"""

    # ----------------------------------------------------------------------
    # |  Public Types
    @dataclass
    class EvalResult(object):
        value: Any
        type: Type
        name: Optional[str]                 # None if the result is a temporary value

    # ----------------------------------------------------------------------
    # |  Public Methods
    @staticmethod
    @Interface.abstractmethod
    def EvalType() -> Type:
        """Evaluated the type of the expression"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Eval(
        args: Dict[str, Any],
        type_overrides: Dict[str, Type],
    ) -> "Expression.EvalResult":
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ToString(
        args: Dict[str, Any],
    ) -> str:
        raise Exception("Abstract method")  # pragma: no cover
