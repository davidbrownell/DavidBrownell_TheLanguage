# ----------------------------------------------------------------------
# |
# |  InterfaceCapabilities.py
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
"""Contains the definition for "interface" class capabilities"""

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
InterfaceCapabilities                       = _ClassCapabilities(
    name="Interface",
    default_class_modifier=ClassModifier.immutable,
    valid_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        # No private, as what does it mean to be a private and support runtime polymorphism;
        # probably looking for a "concept" instead.
    ],
    default_visibility=VisibilityModifier.protected,
    valid_extends_visibilities=[
        VisibilityModifier.public,
    ],
    default_extends_visibility=VisibilityModifier.public,
    valid_implements_types=[],
    valid_implements_visibilities=[],
    default_implements_visibility=None,
    valid_uses_types=[],
    valid_uses_visibilities=[],
    default_uses_visibility=None,
    valid_method_modifiers=[
        MethodModifier.abstract,
    ],
    valid_method_visibilities=[
        VisibilityModifier.public,
    ],
    allow_static_methods=False,
    valid_attribute_visibilities=[],
    allow_mutable_public_attributes=False,
)
