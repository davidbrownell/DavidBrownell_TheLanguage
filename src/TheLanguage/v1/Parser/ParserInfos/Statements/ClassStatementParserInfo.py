# ----------------------------------------------------------------------
# |
# |  ClassStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-01 10:42:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassStatementParserInfo object"""

import os

from typing import cast, List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfo, ParserInfoType, Region, ScopeFlag, StatementParserInfo
    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Common.ClassModifier import ClassModifier
    from ..Common.ConstraintParametersParserInfo import ConstraintParameterParserInfo
    from ..Common.TemplateParametersParserInfo import TemplateParametersParserInfo
    from ..Common.VisibilityModifier import VisibilityModifier, InvalidProtectedError

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
MultipleExtendsError                        = CreateError(
    "'{type}' types may only extend one other type",
    type=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementDependencyParserInfo(ParserInfo):
    """Dependency of a class"""

    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    visibility: Optional[VisibilityModifier]            # Note that instances may be created with this value as None,
                                                        # but a default will be provided once the instance is associated
                                                        # with a ClassStatement instance.
    type: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(ClassStatementDependencyParserInfo, self).__init__(
            ParserInfoType.Standard,
            regions,
            regionless_attributes=["type", ],
        )

        # Validate
        errors: List[Error] = []

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
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("type", self.type),
            ],
            children=None,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementParserInfo(StatementParserInfo):
    """\
    Statement that defines a class-like object. The capabilities provided during instantiation
    control many aspects of what is an isn't valid for a particular class type (e.g. class vs.
    struct vs. interface).
    """

    # ----------------------------------------------------------------------
    introduces_scope__                      = True

    # ----------------------------------------------------------------------
    parent_class_capabilities: InitVar[Optional[ClassCapabilities]]

    class_capabilities: ClassCapabilities

    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier          = field(init=False)

    class_modifier_param: InitVar[Optional[ClassModifier]]
    class_modifier: ClassModifier           = field(init=False)

    name: str
    documentation: Optional[str]

    templates: Optional[TemplateParametersParserInfo]
    constraints: Optional[ConstraintParameterParserInfo]

    extends: Optional[List[ClassStatementDependencyParserInfo]]
    implements: Optional[List[ClassStatementDependencyParserInfo]]
    uses: Optional[List[ClassStatementDependencyParserInfo]]

    statements: List[StatementParserInfo]

    constructor_visibility_param: InitVar[Optional[VisibilityModifier]]
    constructor_visibility: VisibilityModifier          = field(init=False)

    is_abstract: Optional[bool]
    is_final: Optional[bool]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
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
    def __post_init__(
        self,
        parser_info_type,
        regions,
        parent_class_capabilities,
        visibility_param,
        class_modifier_param,
        constructor_visibility_param,
    ):
        super(ClassStatementParserInfo, self).__post_init__(
            parser_info_type,
            regions,
            regionless_attributes=[
                "class_capabilities",
                "templates",
                "constraints",
            ],
            validate=False,
            class_capabilities=lambda value: value.name,
        )

        # Set defaults
        if visibility_param is None:
            if parent_class_capabilities is not None:
                visibility_param = parent_class_capabilities.default_nested_class_visibility
            else:
                visibility_param = self.class_capabilities.default_visibility

            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        object.__setattr__(self, "visibility", visibility_param)

        if class_modifier_param is None:
            class_modifier_param = self.class_capabilities.default_class_modifier
            object.__setattr__(self.regions__, "class_modifier", self.regions__.self__)

        object.__setattr__(self, "class_modifier", class_modifier_param)

        if constructor_visibility_param is None:
            constructor_visibility_param = VisibilityModifier.public
            object.__setattr__(self.regions__, "constructor_visibility", self.regions__.self__)

        object.__setattr__(self, "constructor_visibility", constructor_visibility_param)

        for dependencies, default_visibility in [
            (self.extends, self.class_capabilities.default_extends_visibility),
            (self.implements, self.class_capabilities.default_implements_visibility),
            (self.uses, self.class_capabilities.default_uses_visibility),
        ]:
            if dependencies is None:
                continue

            for dependency in dependencies:
                if dependency.visibility is None:
                    object.__setattr__(dependency, "visibility", default_visibility)
                    object.__setattr__(dependency.regions__, "visibility", dependency.regions__.self__)

        self.ValidateRegions()

        # Validate
        errors: List[Error] = []

        if self.extends and len(self.extends) > 1:
            errors.append(
                MultipleExtendsError.Create(
                    region=Region.Create(
                        self.extends[1].regions__.self__.begin,
                        self.extends[-1].regions__.self__.end,
                    ),
                    type=self.class_capabilities.name,
                ),
            )

        try:
            self.class_capabilities.ValidateClassStatementCapabilities(
                self,
                has_parent_class=parent_class_capabilities is not None,
            )
        except ErrorException as ex:
            errors += ex.errors

        if parent_class_capabilities is not None:
            try:
                parent_class_capabilities.ValidateNestedClassStatementCapabilities(self)
            except ErrorException as ex:
                errors += ex.errors

        else:
            if self.visibility == VisibilityModifier.protected:
                errors.append(
                    InvalidProtectedError.Create(
                        region=self.regions__.visibility,
                    ),
                )

        # TODO: Create default special methods as necessary
        # TODO: Create a static 'Create' method if one does not already exist

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
        if self.extends:
            details.append(("extends", self.extends))
        if self.implements:
            details.append(("implements", self.implements))
        if self.uses:
            details.append(("uses", self.uses))

        return self._AcceptImpl(
            visitor,
            details=details,
            children=cast(List[ParserInfo], self.statements),
        )

# TODO: Not valid to have a protected class without a class ancestor
# TODO: Ensure that all contents have mutability values consistent with the class decoration
