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

from contextlib import contextmanager
from typing import Any, List, Optional, Tuple, Union

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
        ParserInfo,
        ParserInfoType,
    )

    from .Traits.SimpleExpressionTrait import SimpleExpressionTrait

    from ..Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
    from ..Common.MutabilityModifier import MutabilityModifier
    from ..Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo

    from ...Error import CreateError, Error, ErrorException

    from ...MiniLanguage.Expressions.Expression import Expression as MiniLanguageExpression
    from ...MiniLanguage.Types.Type import Type as MiniLanguageType

    # Convenience imports
    from ...MiniLanguage.Expressions.EnforceExpression import EnforceExpression         # pylint: disable=unused-import
    from ...MiniLanguage.Expressions.ErrorExpression import ErrorExpression             # pylint: disable=unused-import
    from ...MiniLanguage.Expressions.IsDefinedExpression import IsDefinedExpression     # pylint: disable=unused-import
    from ...MiniLanguage.Expressions.OutputExpression import OutputExpression           # pylint: disable=unused-import

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

InvalidStandardTypeError                    = CreateError(
    "Compile-time types are not allowed in this context",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncOrTypeExpressionParserInfo(
    SimpleExpressionTrait,
    ExpressionParserInfo,
):
    # ----------------------------------------------------------------------
    value: Union[
        MiniLanguageType,
        MiniLanguageExpression,
        str,
    ]

    templates: Optional[TemplateArgumentsParserInfo]
    constraints: Optional[ConstraintArgumentsParserInfo]
    mutability_modifier: Optional[MutabilityModifier]

    # TODO: Add functionality to indicate that we should not attempt to resolve the type as nested, but instead use global resolution

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        ExpressionParserInfo.__post_init__(
            self,
            *args,
            **{
                **kwargs,
                **{
                    "regionless_attributes": [
                        "templates",
                        "constraints",
                    ],
                },
            },
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def IsType(self) -> Optional[bool]:
        return isinstance(self.value, (str, MiniLanguageType))

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        if self.templates:
            yield "templates", self.templates  # type: ignore

        if self.constraints:
            yield "constraints", self.constraints  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def _InitializeAsTypeImpl(
        self,
        parser_info_type: ParserInfoType,
        *,
        is_instantiated_type: bool=True,
    ) -> None:
        # Validate
        errors: List[Error] = []

        try:
            MutabilityModifier.Validate(self, parser_info_type, is_instantiated_type)
        except ErrorException as ex:
            errors += ex.errors

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
        if parser_info_type.IsCompileTime():
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

        else:
            assert False, parser_info_type  # pragma: no cover

        if errors:
            raise ErrorException(*errors)

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
        assert self.templates is None
        assert self.constraints is None

        return (None, None, )
