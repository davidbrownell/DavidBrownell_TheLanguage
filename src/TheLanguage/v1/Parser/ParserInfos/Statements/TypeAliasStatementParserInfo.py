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

from typing import Dict, List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import (
        ParserInfo,
        ParserInfoType,
        ScopeFlag,
        StatementParserInfo,
        TranslationUnitRegion,
    )

    from .Traits.NamedStatementTrait import NamedStatementTrait
    from .Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ..Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo
    from ..Common.VisibilityModifier import VisibilityModifier, InvalidProtectedError

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Statements.ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ...Error import Error, ErrorException


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeAliasStatementParserInfo(
    TemplatedStatementTrait,
    NamedStatementTrait,
    StatementParserInfo,
):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class ResolvedType(ExpressionParserInfo.ResolvedType):
        # ----------------------------------------------------------------------
        @Interface.override
        def ResolveOne(self) -> ExpressionParserInfo.ResolvedType:
            assert isinstance(self.parser_info, TypeAliasStatementParserInfo), self.parser_info
            return self.parser_info.type.resolved_type__

        # ----------------------------------------------------------------------
        @Interface.override
        def Resolve(self) -> ExpressionParserInfo.ResolvedType:
            return self.ResolveOne().Resolve()

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    parent_class_capabilities: Optional[ClassCapabilities]

    constraints: Optional[ConstraintParametersParserInfo]
    type: ExpressionParserInfo

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.Standard,        # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, parser_info_type, regions, visibility_param, templates_param):
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
                + TemplatedStatementTrait.RegionlessAttributesArgs()
            ,
            validate=False,
            **{
                **{
                    "parent_class_capabilities": lambda value: None if value is None else value.name,
                },
                **NamedStatementTrait.ObjectReprImplBaseInitKwargs(),
                **TemplatedStatementTrait.ObjectReprImplBaseInitKwargs(),
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
        TemplatedStatementTrait.__post_init__(self, templates_param)

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
            self.type.InitializeAsType(
                self.parser_info_type__,
                is_instantiated_type=False,
            )
        except ErrorException as ex:
            errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetValidScopes() -> Dict[ParserInfoType, ScopeFlag]:
        return {
            ParserInfoType.Standard: ScopeFlag.Root | ScopeFlag.Class | ScopeFlag.Function,
        }

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsNameOrdered(
        scope_flag: ScopeFlag,
    ) -> bool:
        return bool(scope_flag & ScopeFlag.Function)

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
