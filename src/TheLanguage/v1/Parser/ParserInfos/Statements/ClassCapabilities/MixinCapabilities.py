# ----------------------------------------------------------------------
# |
# |  MixinCapabilities.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-03-31 10:23:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the definition for "Mixin" class capabilities"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ClassCapabilities import (
        ClassCapabilities as _ClassCapabilities,
        ClassModifier,
        MethodModifier,
        MutabilityModifier,
        VisibilityModifier,
    )


# ----------------------------------------------------------------------
MixinCapabilities                           = _ClassCapabilities(
    name="Mixin",
    is_instantiable=False,
    default_class_modifier=ClassModifier.immutable,
    valid_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_visibility=VisibilityModifier.private,
    valid_extends_visibilities=[
        VisibilityModifier.public,
    ],
    default_extends_visibility=VisibilityModifier.public,
    valid_implements_types=[
        "Concept",
        "Interface",
    ],
    valid_implements_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_implements_visibility=None,
    valid_uses_types=[
        "Mixin",
    ],
    valid_uses_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_uses_visibility=None,
    valid_method_modifiers=[
        MethodModifier.abstract,
        MethodModifier.final,
        MethodModifier.override,
        MethodModifier.standard,
        MethodModifier.virtual,
    ],
    default_method_modifier=MethodModifier.standard,
    valid_method_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_method_visibility=VisibilityModifier.private,
    valid_method_mutabilities=[
        MutabilityModifier.var,
        MutabilityModifier.ref,
        MutabilityModifier.val,
        MutabilityModifier.mutable,
        MutabilityModifier.immutable,
    ],
    default_method_mutability=None,
    allow_static_methods=True,
    valid_attribute_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_attribute_visibility=VisibilityModifier.private,
    valid_attribute_mutabilities=[
        MutabilityModifier.var,
        MutabilityModifier.val,
    ],
    allow_mutable_public_attributes=False,
)
