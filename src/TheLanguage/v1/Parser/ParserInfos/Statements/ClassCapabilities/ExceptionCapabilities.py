# ----------------------------------------------------------------------
# |
# |  ExceptionCapabilities.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-15 08:54:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ExceptionCapabilities value"""

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
ExceptionCapabilities                       = _ClassCapabilities(
    name="Exception",
    default_class_modifier=ClassModifier.immutable,
    valid_visibilities=[
        VisibilityModifier.public,
    ],
    default_visibility=VisibilityModifier.public,
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
    default_implements_visibility=VisibilityModifier.private,
    valid_uses_types=[
        "Mixin",
    ],
    valid_uses_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_uses_visibility=VisibilityModifier.private,
    valid_method_modifiers=[
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
        MutabilityModifier.val,
    ],
    default_method_mutability=MutabilityModifier.val,
    allow_static_methods=True,
    valid_attribute_visibilities=[
        VisibilityModifier.public,
    ],
    default_attribute_visibility=VisibilityModifier.public,
    valid_attribute_mutabilities=[
        MutabilityModifier.val,
    ],
    allow_mutable_public_attributes=False,
)
