# ----------------------------------------------------------------------
# |
# |  OutputExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-07 16:56:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the OutputExpression object"""

import os

from typing import Any, Dict, List

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Expression import Expression, Type
    from ..Types.NoneType import NoneType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class OutputExpression(Expression):
    messages: List[Expression]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(OutputExpression, self).__init__()
        assert self.messages

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def EvalType() -> Type:
        return NoneType()

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overrides: Dict[str, Type],
    ) -> Expression.EvalResult:
        outputs: List[str] = []

        for message in self.messages:
            output = message.Eval(args, type_overrides)
            output = output.type.ToStringValue(output.value)

            outputs.append(output)

        output = ", ".join(outputs)

        print("TODO", output)

        return Expression.EvalResult(None, NoneType(), None)

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "Output!({})".format(
            ", ".join(message.ToString(args) for message in self.messages),
        )
