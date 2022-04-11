# ----------------------------------------------------------------------
# |
# |  StandardCapabilities.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-03-31 10:04:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the definition for "standard" class capabilities"""

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
        VisibilityModifier,
    )


# ----------------------------------------------------------------------
# The name `StandardCapabilities` is an unfortunate one. The intent is to define
# what a "standard" class is capable of. However, the name "ClassClassCapabilities"
# is a bit awkward.
StandardCapabilities                        = _ClassCapabilities(
    name="Standard",
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
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_extends_visibility=VisibilityModifier.private,
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
        MethodModifier.abstract,
        MethodModifier.override,
        MethodModifier.standard,
        MethodModifier.virtual,
    ],
    valid_method_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    allow_static_methods=True,
    valid_attribute_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    allow_mutable_public_attributes=False,
)