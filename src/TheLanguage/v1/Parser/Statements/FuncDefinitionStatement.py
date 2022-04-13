# ----------------------------------------------------------------------
# |
# |  FuncDefinitionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 15:33:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FunDefinitionStatement object"""

import os

from enum import auto, Enum
from typing import cast, List, Optional, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementPhrase import Phrase, StatementPhrase
    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Common.FuncParametersPhrase import (  # pylint: disable=unused-import
        FuncParametersPhrase,
        FuncParametersItemPhrase,           # Convenience import
    )

    from ..Common.MethodModifier import MethodModifier
    from ..Common.MutabilityModifier import MutabilityModifier
    from ..Common.VariableNamePhrase import VariableNamePhrase
    from ..Common.VisibilityModifier import VisibilityModifier

    from ..Types.TypePhrase import MutabilityModifierRequiredError, TypePhrase

    from ...Common.Diagnostics import CreateError, DiagnosticsError, Error


# ----------------------------------------------------------------------
class OperatorType(Enum):
    TODO = auto()


# ----------------------------------------------------------------------
InvalidFunctionMutabilityError              = CreateError(
    "Mutability modifiers are not valid for functions",
)

InvalidFunctionMethodModifierError          = CreateError(
    "Method modifiers are not valid for functions",
)

InvalidFunctionOperatorError                = CreateError(
    "Functions may not be named as operators",
)

InvalidFunctionDeferredStatementsError      = CreateError(
    "Deferred functions should not have any statements",
)

InvalidMethodCapturedVariableError          = CreateError(
    "Methods may not capture variables",
)

InvalidMethodMutabilityError                = CreateError(
    "'{mutability_str}' is not a valid mutability for '{type}' types;' valid mutabilities are {valid_mutabilities_str}",
    type=str,
    mutability=MutabilityModifier,
    valid_mutabilities=List[MutabilityModifier],
    mutability_str=str,
    valid_mutabilities_str=str,
)

InvalidMethodModifierError                  = CreateError(
    "'{modifier_str}' is not a valid modifier for '{type}' types; valid modifiers are {valid_modifiers_str}",
    type=str,
    modifier=MethodModifier,
    valid_modifiers=List[MethodModifier],
    modifier_str=str,
    valid_modifiers_str=str,
)

InvalidMethodAbstractStatementsError        = CreateError(
    "Abstract methods should not have any statements",
)

InvalidMethodStatementsRequiredError        = CreateError(
    "Method statements are required",
)

InvalidVisibilityError                      = CreateError(
    "'{visibility_str}' is not a valid visibility for {type}; valid visibilities are {valid_visibilities_str}",
    type=str,
    visibility=VisibilityModifier,
    valid_visibilities=List[VisibilityModifier],
    visibility_str=str,
    valid_visibilities_str=str,
)

StatementsRequiredError                     = CreateError(
    "{type} statements are required",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncDefinitionStatement(StatementPhrase):
    """Function or method definition"""

    # ----------------------------------------------------------------------
    introduces_scope__                      = True

    # ----------------------------------------------------------------------
    class_capabilities: InitVar[Optional[ClassCapabilities]]

    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier                      = field(init=False)

    mutability_param: InitVar[Optional[MutabilityModifier]]
    mutability: Optional[MutabilityModifier]            = field(init=False)

    method_modifier_param: InitVar[Optional[MethodModifier]]
    method_modifier: Optional[MethodModifier]           = field(init=False)

    return_type: TypePhrase
    name: Union[str, OperatorType]
    documentation: Optional[str]

    # TODO: Templates

    captured_variables: Optional[List[VariableNamePhrase]]
    parameters: Union[bool, FuncParametersPhrase]

    statements: Optional[List[StatementPhrase]]

    is_deferred: Optional[bool]
    is_exceptional: Optional[bool]
    is_generator: Optional[bool]
    is_reentrant: Optional[bool]
    is_scoped: Optional[bool]

    # ----------------------------------------------------------------------
    def __post_init__(self, diagnostics, regions, class_capabilities, visibility_param, mutability_param, method_modifier_param):
        super(FuncDefinitionStatement, self).__post_init__(
            diagnostics,
            regions,
            validate=False,
        )

        # Set defaults
        if class_capabilities is None:
            # We are looking at a function
            valid_method_visibilities = [
                VisibilityModifier.public,
                VisibilityModifier.internal,
                VisibilityModifier.private,
            ]

            default_method_visibility = VisibilityModifier.private

            capabilities_name = "functions"

        else:
            if mutability_param is None:
                mutability_param = class_capabilities.default_method_mutability
                object.__setattr__(self.regions__, "mutability", self.regions__.self__)

            if method_modifier_param is None:
                method_modifier_param = class_capabilities.default_method_modifier
                object.__setattr__(self.regions__, "method_modifier", self.regions__.self__)

            valid_method_visibilities = class_capabilities.valid_method_visibilities
            default_method_visibility = class_capabilities.default_method_visibility

            capabilities_name = "{} methods".format(class_capabilities.name)

        object.__setattr__(self, "mutability", mutability_param)
        object.__setattr__(self, "method_modifier", method_modifier_param)

        if visibility_param is None:
            visibility_param = default_method_visibility
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        object.__setattr__(self, "visibility", visibility_param)

        self.ValidateRegions()

        # Validate
        if self.return_type.mutability_modifier is None:
            diagnostics.errors.append(
                MutabilityModifierRequiredError.Create(
                    region=self.return_type.regions__.self__,
                ),
            )

        if class_capabilities is None:
            if self.mutability is not None:
                diagnostics.errors.append(
                    InvalidFunctionMutabilityError.Create(
                        region=self.regions__.mutability,
                    ),
                )

            if self.method_modifier is not None:
                diagnostics.errors.append(
                    InvalidFunctionMethodModifierError.Create(
                        region=self.regions__.method_modifier,
                    ),
                )

            if not isinstance(self.name, str):
                diagnostics.errors.append(
                    InvalidFunctionOperatorError.Create(
                        region=self.regions__.name,
                    ),
                )

            if not self.is_deferred and not self.statements:
                diagnostics.errors.append(
                    InvalidFunctionDeferredStatementsError.Create(
                        region=self.regions__.self__,
                    ),
                )

        else:
            if self.captured_variables:
                diagnostics.errors.append(
                    InvalidMethodCapturedVariableError.Create(
                        region=self.regions__.captured_variables,
                    ),
                )

            assert self.mutability is not None

            if self.mutability not in class_capabilities.valid_method_mutabilities:
                diagnostics.errors.append(
                    InvalidMethodMutabilityError.Create(
                        region=self.regions__.mutability,
                        type=class_capabilities.name,
                        mutability=self.mutability,
                        valid_mutabilities=class_capabilities.valid_method_mutabilities,
                        mutability_str=self.mutability.name,
                        valid_mutabilities_str=", ".join(["'{}'".format(m.name) for m in class_capabilities.valid_method_mutabilities]),
                    ),
                )

            assert self.method_modifier is not None

            if self.method_modifier not in class_capabilities.valid_method_modifiers:
                diagnostics.errors.append(
                    InvalidMethodModifierError.Create(
                        region=self.regions__.method_modifier,
                        type=class_capabilities.name,
                        modifier=self.method_modifier,
                        valid_modifiers=class_capabilities.valid_method_modifiers,
                        modifier_str=self.method_modifier.name,
                        valid_modifiers_str=", ".join(["'{}'".format(m.name) for m in class_capabilities.valid_method_modifiers]),
                    ),
                )

            if self.method_modifier == MethodModifier.abstract and self.statements:
                diagnostics.errors.append(
                    InvalidMethodAbstractStatementsError.Create(
                        region=self.regions__.statements,
                    ),
                )
            elif self.method_modifier != MethodModifier.abstract and not self.is_deferred and not self.statements:
                diagnostics.errors.append(
                    InvalidMethodStatementsRequiredError.Create(
                        region=self.regions__.self__,
                    ),
                )

        if self.visibility not in valid_method_visibilities:
            diagnostics.errors.append(
                InvalidVisibilityError.Create(
                    region=self.regions__.visibility,
                    type=capabilities_name,
                    visibility=self.visibility,
                    valid_visibilities=valid_method_visibilities,
                    visibility_str=self.visibility.name,
                    valid_visibilities_str=", ".join(["'{}'".format(v.name) for v in valid_method_visibilities]),
                ),
            )

        if self.is_deferred and self.statements:
            diagnostics.errors.append(
                StatementsRequiredError.Create(
                    region=self.regions__.statements,
                    type=capabilities_name,
                ),
            )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, *args, **kwargs):
        return self._ScopedAcceptImpl(cast(List[Phrase], self.statements or []), *args, **kwargs)

# TODO: Is final
