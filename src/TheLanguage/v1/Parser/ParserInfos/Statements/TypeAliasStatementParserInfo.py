# ----------------------------------------------------------------------
# |
# |  TypeAliasStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-19 12:46:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeAliasStatementParserInfo object"""

import os

from typing import List, Optional, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import (
        NamedStatementTrait,
        ParserInfo,
        ParserInfoType,
        ScopeFlag,
        StatementParserInfo,
        TranslationUnitRegion,
    )

    from ..Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo
    from ..Common.TemplateParametersParserInfo import TemplateParametersParserInfo, TemplateTypeParameterParserInfo
    from ..Common.VisibilityModifier import VisibilityModifier, InvalidProtectedError

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Statements.ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ...Error import Error, ErrorException


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeAliasStatementParserInfo(
    NamedStatementTrait,
    StatementParserInfo,
):
    parent_class_capabilities: Optional[ClassCapabilities]

    templates: Optional[TemplateParametersParserInfo]
    constraints: Optional[ConstraintParametersParserInfo]

    type: ExpressionParserInfo

    # Values set during validation
    _type_parser_info__: Optional[ParserInfo]           = field(init=False, default=None)

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        *args,
        **kwargs,
    ):
        return cls(
            ScopeFlag.Root | ScopeFlag.Class | ScopeFlag.Function,
            ParserInfoType.Standard,        # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, parser_info_type, regions, visibility_param):
        StatementParserInfo.__post_init__(
            self,
            parser_info_type,
            regions,
            regionless_attributes=[
                "parent_class_capabilities",
                "templates",
                "constraints",
                "type",
            ]
                + NamedStatementTrait.RegionlessAttributesArgs()
            ,
            validate=False,
            **{
                **{
                    "parent_class_capabilities": lambda value: None if value is None else value.name,
                },
                **NamedStatementTrait.ObjectReprImplBaseInitKwargs(),
            },
        )

        # Set defaults
        if visibility_param is None:
            if self.parent_class_capabilities:
                if self.parent_class_capabilities.default_type_alias_visibility is not None:
                    visibility_param = self.parent_class_capabilities.default_type_alias_visibility
                    object.__setattr__(self.regions__, "visibility", self.regions__.self__)
            else:
                visibility_param = VisibilityModifier.private
                object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        NamedStatementTrait.__post_init__(self, visibility_param)

        self.ValidateRegions()

        # Validate
        errors: List[Error] = []

        if self.parent_class_capabilities is not None:
            self.parent_class_capabilities.ValidateTypeAliasStatementCapabilities(self)
        else:
            if self.visibility == VisibilityModifier.protected:
                errors.append(
                    InvalidProtectedError.Create(
                        region=self.regions__.visibility,
                    ),
                )

        try:
            self.type.ValidateAsType(
                self.parser_info_type__,
                is_instantiated_type=False,
            )
        except ErrorException as ex:
            errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    # The following values are set during validation
    def InitType(
        self,
        type_parser_info: ParserInfo
    ) -> None:
        assert self._type_parser_info__ is None, self._type_parser_info__
        object.__setattr__(self, "_type_parser_info__", type_parser_info)

    # ----------------------------------------------------------------------
    @property
    def type_parser_info__(self) -> ParserInfo:
        assert self._type_parser_info__ is not None
        return self._type_parser_info__

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "type", self.type  # type: ignore

        if self.templates:
            yield "templates", self.templates  # type: ignore

        if self.constraints:
            yield "constraints", self.constraints  # type: ignore
