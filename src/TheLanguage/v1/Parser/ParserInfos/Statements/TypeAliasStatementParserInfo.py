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

from typing import List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfoType, Region, StatementParserInfo

    from ..Common.ConstraintParametersParserInfo import ConstraintParameterParserInfo
    from ..Common.TemplateParametersParserInfo import TemplateParametersParserInfo
    from ..Common.VisibilityModifier import VisibilityModifier, InvalidProtectedError

    from ..Statements.ClassCapabilities.ClassCapabilities import ClassCapabilities
    from ..Types.TypeParserInfo import TypeParserInfo

    from ...Error import Error, ErrorException


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeAliasStatementParserInfo(StatementParserInfo):
    parent_class_capabilities: Optional[ClassCapabilities]

    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier          = field(init=False)

    name: str

    templates: Optional[TemplateParametersParserInfo]
    constraints: Optional[ConstraintParameterParserInfo]

    type: TypeParserInfo

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.CompileTimeType, # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, parser_info_type, regions, visibility_param):
        super(TypeAliasStatementParserInfo, self).__post_init__(
            parser_info_type,
            regions,
            regionless_attributes=[
                "parent_class_capabilities",
                "templates",
                "constraints",
                "type",
            ],
            validate=False,
            parent_class_capabilities=lambda value: None if value is None else value.name,
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

        object.__setattr__(self, "visibility", visibility_param)

        self.ValidateRegions()

        # Validate
        errors: List[Error] = []

        if self.parent_class_capabilities is not None:
            errors += self.parent_class_capabilities.ValidateTypeAliasStatementCapabilities(self)
        else:
            if self.visibility == VisibilityModifier.protected:
                errors.append(
                    InvalidProtectedError.Create(
                        region=self.regions__.visibility,
                    ),
                )

        if errors:
            raise ErrorException(*errors)

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
            details=[
                ("type", self.type),
            ] + details,  # type: ignore
            children=None,
        )
