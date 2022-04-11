# ----------------------------------------------------------------------
# |
# |  ConceptCapabilities.py
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
"""Contains the definition for "concept" class capabilities"""

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
ConceptCapabilities                         = _ClassCapabilities(
    name="Concept",
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
    default_method_modifier=MethodModifier.abstract,
    default_method_visibility=VisibilityModifier.public,
    allow_static_methods=False,
    valid_attribute_visibilities=[],
    valid_attribute_mutabilities=[],
    default_attribute_visibility=None,
    allow_mutable_public_attributes=False,
)
