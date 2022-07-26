# ----------------------------------------------------------------------
# |
# |  TypeAliasType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-22 14:01:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains alias-related types"""

import os

from typing import Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ConcreteType import ConcreteType
    from .ConstrainedType import ConstrainedType

    from ..Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConcreteTypeAliasType(ConcreteType):
    # ----------------------------------------------------------------------
    concrete_reference: ConcreteType

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        self.concrete_reference.FinalizePass1()

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        self.concrete_reference.FinalizePass2()

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(
        self,
        constraint_arguments_parser_info: Optional[ConstraintArgumentsParserInfo],
    ) -> "ConstrainedTypeAliasType":
        return ConstrainedTypeAliasType(
            self,
            self.concrete_reference.CreateConstrainedType(constraint_arguments_parser_info),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConstrainedTypeAliasType(ConstrainedType):
    # ----------------------------------------------------------------------
    concrete_reference: ConstrainedType
