# ----------------------------------------------------------------------
# |
# |  VariableExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 15:06:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableExpressionParserInfo object"""

import os

from contextlib import contextmanager
from typing import Any, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import (  # pylint: disable=unused-import
        ExpressionParserInfo,
        ParserInfoType,                     # convenience import
    )

    from .Traits.SimpleExpressionTrait import SimpleExpressionTrait


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableExpressionParserInfo(
    SimpleExpressionTrait,
    ExpressionParserInfo,
):
    # ----------------------------------------------------------------------
    name: str

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    @Interface.override
    def _InitConfigurationImpl(*args, **kwargs):  # pylint: disable=unused-argument
        # Nothing to do here
        yield

    # ----------------------------------------------------------------------
    @Interface.override
    def _GetUniqueId(self) -> Tuple[Any, ...]:
        return (self.name, )
