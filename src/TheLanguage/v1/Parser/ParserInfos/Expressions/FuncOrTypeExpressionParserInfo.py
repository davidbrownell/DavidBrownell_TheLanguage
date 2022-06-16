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

from typing import List, Optional, Type, Union

from dataclasses import dataclass, field

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
        InvalidExpressionError,
        ParserInfo,
        ParserInfoType,
    )

    from ..Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
    from ..Common.MutabilityModifier import MutabilityModifier
    from ..Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo
    from ..Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo

    from ..Statements.StatementParserInfo import StatementParserInfo

    from ...Error import CreateError, Error, ErrorException

    from ...MiniLanguage.Expressions.Expression import Expression as MiniLanguageExpression
    from ...MiniLanguage.Types.Type import Type as MiniLanguageType

    # Convenience imports
    from ...MiniLanguage.Expressions.EnforceExpression import EnforceExpression         # pylint: disable=unused-import
    from ...MiniLanguage.Expressions.ErrorExpression import ErrorExpression             # pylint: disable=unused-import
    from ...MiniLanguage.Expressions.IsDefinedExpression import IsDefinedExpression     # pylint: disable=unused-import

    from ...MiniLanguage.Types.BooleanType import BooleanType               # pylint: disable=unused-import
    from ...MiniLanguage.Types.CharacterType import CharacterType           # pylint: disable=unused-import
    from ...MiniLanguage.Types.IntegerType import IntegerType               # pylint: disable=unused-import
    from ...MiniLanguage.Types.NoneType import NoneType                     # pylint: disable=unused-import
    from ...MiniLanguage.Types.NumberType import NumberType                 # pylint: disable=unused-import
    from ...MiniLanguage.Types.StringType import StringType                 # pylint: disable=unused-import
    from ...MiniLanguage.Types.VariantType import VariantType               # pylint: disable=unused-import


# ----------------------------------------------------------------------
InvalidCompileTimeTypeError                 = CreateError(
    "'{name}' is not a valid compile-time type",
    name=str,
)

InvalidCompileTimeTemplatesError            = CreateError(
    "Compile-time types may not define template arguments",
)

InvalidCompileTimeConstraintsError          = CreateError(
    "Compile-time types may not define constraint arguments",
)

InvalidCompileTimeMutabilityModifierError   = CreateError(
    "Compile-time types may not have a mutability modifier",
)

MutabilityModifierRequiredError             = CreateError(
    "A mutability modifier is required in this context",
)

InvalidStandardMutabilityModifierError      = CreateError(
    "A mutability modifier is not allowed in this context",
)

InvalidStandardTypeError                    = CreateError(
    "Compile-time types are not allowed in this context",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncOrTypeExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    value: Union[
        MiniLanguageType,
        Type[MiniLanguageExpression],
        str,
    ]

    templates: Optional[TemplateArgumentsParserInfo]
    constraints: Optional[ConstraintArgumentsParserInfo]
    mutability_modifier: Optional[MutabilityModifier]

    # The following values are set during validation
    _value_parser_info: Union[None, StatementParserInfo, TemplateTypeParameterParserInfo]           = field(init=False, default=None)

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(FuncOrTypeExpressionParserInfo, self).__post_init__(
            *args,
            regionless_attributes=[
                "templates",
                "constraints",
            ],
            **{
                "value_parser_info__": None,
                **kwargs,
            },
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def IsType(self) -> Optional[bool]:
        return True

    # ----------------------------------------------------------------------
    @Interface.override
    def InitializeAsType(
        self,
        parser_info_type: ParserInfoType,
        *,
        is_instantiated_type: Optional[bool]=True,
    ) -> None:
        # Validate
        errors: List[Error] = []

        # Checks just for configuration values
        if parser_info_type == ParserInfoType.Configuration:
            if isinstance(self.value, str):
                errors.append(
                    InvalidCompileTimeTypeError.Create(
                        region=self.regions__.value,
                        name=self.value,
                    ),
                )

        # Checks for all compile-time values
        if ParserInfoType.IsCompileTime(parser_info_type):
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
                    InvalidCompileTimeMutabilityModifierError.Create(
                        region=self.regions__.mutability_modifier,
                    ),
                )

        elif (
            parser_info_type == ParserInfoType.Standard
            or parser_info_type == ParserInfoType.Unknown
        ):
            if not isinstance(self.value, str):
                errors.append(
                    InvalidStandardTypeError.Create(
                        region=self.regions__.value,
                    ),
                )

            if is_instantiated_type and self.mutability_modifier is None:
                errors.append(
                    MutabilityModifierRequiredError.Create(
                        region=self.regions__.self__,
                    ),
                )
            elif not is_instantiated_type and self.mutability_modifier is not None:
                errors.append(
                    InvalidStandardMutabilityModifierError.Create(
                        region=self.regions__.mutability_modifier,
                    ),
                )

        else:
            assert False, parser_info_type  # pragma: no cover

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def InitializeAsExpression(self) -> None:
        raise ErrorException(
            InvalidExpressionError.Create(
                self.regions__.self__,
            ),
        )

    # ----------------------------------------------------------------------
    def InitValueParserInfo(
        self,
        parser_info: Union[StatementParserInfo, TemplateTypeParameterParserInfo],
    ) -> None:
        assert self._value_parser_info is None
        object.__setattr__(self, "_value_parser_info", parser_info)

    # ----------------------------------------------------------------------
    @property
    def value_parser_info__(self) -> Union[StatementParserInfo, TemplateTypeParameterParserInfo]:
        assert self._value_parser_info is not None
        return self._value_parser_info

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        if self.templates:
            yield "templates", self.templates  # type: ignore

        if self.constraints:
            yield "constraints", self.constraints  # type: ignore
