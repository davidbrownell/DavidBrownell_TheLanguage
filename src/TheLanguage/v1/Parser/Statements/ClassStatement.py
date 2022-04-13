# ----------------------------------------------------------------------
# |
# |  ClassStatement.py
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
"""Contains the ClassStatement object"""

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
    from .StatementPhrase import Phrase, Region, StatementPhrase
    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Common.ClassModifier import ClassModifier
    from ..Common.VisibilityModifier import VisibilityModifier

    from ..Types.StandardType import StandardType
    from ..Types.TypePhrase import MutabilityModifierNotAllowedError

    from ...Common.Diagnostics import CreateError, Diagnostics


# ----------------------------------------------------------------------
InvalidVisibilityError                      = CreateError(
    "'{visibility_str}' is not a valid visibility for '{type}' types; valid visibilities are {valid_visibilities_str}",
    type=str,
    visibility=VisibilityModifier,
    valid_visibilities=List[VisibilityModifier],
    visibility_str=str,
    valid_visibilities_str=str,
)

MultipleExtendsError                        = CreateError(
    "'{type}' types may only extend one other type",
    type=str,
)

InvalidDependencyError                      = CreateError(
    "'{type}' types do not support '{desc}' dependencies",
    type=str,
    desc=str,
)

InvalidDependencyVisibilityError            = CreateError(
    "'{type}' types may not {desc} other types via '{visibility_str}' visibility; valid visibilities are {valid_visibilities_str}",
    type=str,
    desc=str,
    visibility=VisibilityModifier,
    valid_visibilities=List[VisibilityModifier],
    visibility_str=str,
    valid_visibilities_str=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementDependency(Phrase):
    """Dependency of a class"""

    diagnostics: InitVar[Diagnostics]
    regions: InitVar[List[Region]]

    visibility: Optional[VisibilityModifier]            # Note that instances may be created with this value as None,
                                                        # but a default will be provided once the instance is associated
                                                        # with a ClassStatement instance.
    type: StandardType

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, diagnostics, regions):
        super(ClassStatementDependency, self).__init__(diagnostics, regions)

        # Validate
        if self.type.mutability_modifier is not None:
            diagnostics.errors.append(
                MutabilityModifierNotAllowedError.Create(
                    region=self.type.regions__.mutability_modifier,
                ),
            )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatement(StatementPhrase):
    """\
    Statement that defines a class-like object. The capabilities provided during instantiation
    control many aspects of what is an isn't valid for a particular class type (e.g. class vs.
    struct vs. interface).
    """

    # ----------------------------------------------------------------------
    introduces_scope__                      = True

    # ----------------------------------------------------------------------

    # TODO: Named tuple as a capability?
    capabilities: ClassCapabilities

    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier          = field(init=False)

    class_modifier_param: InitVar[Optional[ClassModifier]]
    class_modifier: ClassModifier           = field(init=False)

    name: str
    documentation: Optional[str]

    # TODO: templates
    # TODO: constraints

    extends: Optional[List[ClassStatementDependency]]
    implements: Optional[List[ClassStatementDependency]]
    uses: Optional[List[ClassStatementDependency]]

    statements: List[StatementPhrase]

    # ----------------------------------------------------------------------
    def __post_init__(self, diagnostics, regions, visibility_param, class_modifier_param):
        super(ClassStatement, self).__post_init__(
            diagnostics,
            regions,
            regionless_attributes=[
                "capabilities",
            ],
            validate=False,
            capabilities=lambda value: value.name,
        )

        # Set defaults
        if visibility_param is None:
            visibility_param = self.capabilities.default_visibility
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        object.__setattr__(self, "visibility", visibility_param)

        if class_modifier_param is None:
            class_modifier_param = self.capabilities.default_class_modifier
            object.__setattr__(self.regions__, "class_modifier", self.regions__.self__)

        object.__setattr__(self, "class_modifier", class_modifier_param)

        for dependencies, default_visibility in [
            (self.extends, self.capabilities.default_extends_visibility),
            (self.implements, self.capabilities.default_implements_visibility),
            (self.uses, self.capabilities.default_uses_visibility),
        ]:
            if dependencies is None:
                continue

            for dependency in dependencies:
                if dependency.visibility is None:
                    object.__setattr__(dependency, "visibility", default_visibility)
                    object.__setattr__(dependency.regions__, "visibility", self.regions__.self__)

        self.ValidateRegions()

        # Validate
        if self.visibility not in self.capabilities.valid_visibilities:
            diagnostics.errors.append(
                InvalidVisibilityError.Create(
                    region=self.regions__.visibility,
                    type=self.capabilities.name,
                    visibility=self.visibility,
                    valid_visibilities=self.capabilities.valid_visibilities,
                    visibility_str=self.visibility.name,
                    valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.capabilities.valid_visibilities),
                ),
            )

        if self.extends and len(self.extends) > 1:
            diagnostics.errors.append(
                MultipleExtendsError.Create(
                    region=Region.Create(
                        self.extends[1].regions__.self__.begin,
                        self.extends[-1].regions__.self__.end,
                    ),
                    type=self.capabilities.name,
                ),
            )

        for desc, dependencies, default_visibility, valid_visibilities in [
            (
                "extend",
                self.extends,
                self.capabilities.default_extends_visibility,
                self.capabilities.valid_extends_visibilities,
            ),
            (
                "implement",
                self.implements,
                self.capabilities.default_implements_visibility,
                self.capabilities.valid_implements_visibilities,
            ),
            (
                "use",
                self.uses,
                self.capabilities.default_uses_visibility,
                self.capabilities.valid_uses_visibilities,
            ),
        ]:
            if dependencies is None:
                continue

            if default_visibility is None:
                diagnostics.errors.append(
                    InvalidDependencyError.Create(
                        region=Region.Create(
                            dependencies[0].regions__.self__.begin,
                            dependencies[-1].regions__.self__.end,
                        ),
                        type=self.capabilities.name,
                        desc=desc,
                    ),
                )

            for dependency in dependencies:
                if dependency.visibility not in valid_visibilities:
                    diagnostics.errors.append(
                        InvalidDependencyVisibilityError.Create(
                            region=dependency.regions__.visibility,
                            type=self.capabilities.name,
                            desc=desc,
                            visibility=dependency.visibility,
                            valid_visibilities=valid_visibilities,
                            visibility_str=dependency.visibility.name,
                            valid_visibilities_str=", ".join("'{}'".format(v.name) for v in valid_visibilities),
                        ),
                    )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, *args, **kwargs):
        return self._ScopedAcceptImpl(cast(List[Phrase], self.statements), *args, **kwargs)

# TODO: Not valid to have a protected class at root
# TODO: Constructor Visibility
# TODO: Ensure that attributes are valid
# TODO: Is abstract/final
