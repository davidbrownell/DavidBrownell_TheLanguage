# ----------------------------------------------------------------------
# |
# |  UnaryCompileExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 15:03:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UnaryCompileExpression object"""

import os

from enum import auto, Enum
from typing import Any, Dict

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .CompileExpressionPhrase import CompileExpressionPhrase, CompileType
    from ...CompileTypes.Boolean import Boolean


# ----------------------------------------------------------------------
class OperatorType(Enum):
    Not                                     = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class UnaryCompileExpression(CompileExpressionPhrase):
    operator: OperatorType
    expression: CompileExpressionPhrase

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(UnaryCompileExpression, self).__post_init__(regions)

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, CompileType],
    ) -> CompileExpressionPhrase.EvalResult:
        result = self.expression.Eval(args, type_overloads)

        if self.operator == OperatorType.Not:
            return CompileExpressionPhrase.EvalResult(
                not result.type.ToBool(result.value),
                Boolean(),
                None,
            )

        assert False, self.operator  # pragma: no cover

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        value = self.expression.ToString(args)

        if self.operator == OperatorType.Not:
            return "not {}".format(value)

        assert False, self.operator  # pragma: no cover
