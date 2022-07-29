# ----------------------------------------------------------------------
# |
# |  SelfReferenceExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-29 13:01:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SelfReferenceExpressionParserInfo object"""

import os

from typing import Any, List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfoType
    from .FuncOrTypeExpressionParserInfo import InvalidCompileTimeMutabilityModifierError, InvalidStandardMutabilityModifierError, MutabilityModifierRequiredError

    from .Traits.SimpleExpressionTrait import SimpleExpressionTrait

    from ..Common.MutabilityModifier import MutabilityModifier

    from ...Error import Error, ErrorException


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class SelfReferenceExpressionParserInfo(
    SimpleExpressionTrait,
    ExpressionParserInfo,
):
    # ----------------------------------------------------------------------
    mutability_modifier: Optional[MutabilityModifier] = None

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.Standard,  # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsType() -> Optional[bool]:
        return True

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _InitializeAsTypeImpl(
        self,
        parser_info_type: ParserInfoType,
        *,
        is_instantiated_type: Optional[bool]=True,
    ) -> None:
        # Validate

        errors: List[Error] = []

        if is_instantiated_type and self.mutability_modifier is None:
            errors.append(
                MutabilityModifierRequiredError.Create(
                    regions=self.regions__.self__,
                ),
            )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _GetUniqueId() -> Tuple[Any, ...]:
        return ()
