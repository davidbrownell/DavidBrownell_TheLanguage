# ----------------------------------------------------------------------
# |
# |  FuncOrTypeExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-22 08:02:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncOrTypeExpressionParserInfo object"""

import os

from typing import List, Optional

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
        ParserInfoType,
    )

    from ..Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
    from ..Common.MutabilityModifier import MutabilityModifier
    from ..Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo

    from ...Error import CreateError, Error, ErrorException

    from ...MiniLanguage.Types.CustomType import CustomType
    from ...MiniLanguage.Types.Type import Type as MiniLanguageType

    # Convenience imports
    from ...MiniLanguage.Types.BooleanType import BooleanType               # pylint: disable=unused-import
    from ...MiniLanguage.Types.CharacterType import CharacterType           # pylint: disable=unused-import
    from ...MiniLanguage.Types.IntegerType import IntegerType               # pylint: disable=unused-import
    from ...MiniLanguage.Types.NoneType import NoneType                     # pylint: disable=unused-import
    from ...MiniLanguage.Types.NumberType import NumberType                 # pylint: disable=unused-import
    from ...MiniLanguage.Types.StringType import StringType                 # pylint: disable=unused-import


# ----------------------------------------------------------------------
InvalidCompileTimeTypeError                 = CreateError(
    "Invalid compile-time type (configuration)",
)

InvalidCompileTimeTemplatesError            = CreateError(
    "Compile-time types may not define template arguments",
)

InvalidCompileTimeConstraintsError          = CreateError(
    "Compile-time types may not define constraint arguments",
)

InvalidCompileTimeMutabilityError           = CreateError(
    "Compile-time types may not have a mutability modifier",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncOrTypeExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    value: MiniLanguageType
    templates: Optional[TemplateArgumentsParserInfo]
    constraints: Optional[ConstraintArgumentsParserInfo]
    mutability_modifier: Optional[MutabilityModifier]

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(FuncOrTypeExpressionParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=[
                "templates",
                "constraints",
            ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateAsConfigurationType(self) -> None:
        errors: List[Error] = []

        if isinstance(self.value, CustomType):
            errors.append(
                InvalidCompileTimeTypeError.Create(
                    region=self.regions__.value,
                ),
            )

        errors += self._GenerateCompileTimeValidationErrors()

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateAsCustomizationType(self) -> None:
        errors: List[Error] = []

        errors += self._GenerateCompileTimeValidationErrors()

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateAsStandardType(self) -> None:
        raise NotImplementedError("TODO")  # TODO

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        details = []

        if self.templates:
            details.append(("templates", self.templates))
        if self.constraints:
            details.append(("constraints", self.constraints))

        return self._AcceptImpl(
            visitor,
            details,
            children=None,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _GenerateCompileTimeValidationErrors(self) -> List[Error]:
        errors: List[Error] = []

        if self.templates is not None:
            errors.append(
                InvalidCompileTimeTemplatesError.Create(
                    region=self.templates.regions__.self__,
                ),
            )

        if self.constraints is not None:
            errors.append(
                InvalidCompileTimeConstraintsError.Create(
                    region=self.constraints.regions__.self__,
                ),
            )

        if self.mutability_modifier is not None:
            errors.append(
                InvalidCompileTimeMutabilityError.Create(
                    region=self.regions__.mutability_modifier,
                ),
            )

        return errors
