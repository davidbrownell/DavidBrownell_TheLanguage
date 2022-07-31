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
        MethodHierarchyModifier,
        MutabilityModifier,
        VisibilityModifier,
    )


# ----------------------------------------------------------------------
# The name `StandardCapabilities` is an unfortunate one. The intent is to define
# what a "standard" class is capable of. However, the name "ClassClassCapabilities"
# is a bit awkward.
StandardCapabilities                        = _ClassCapabilities(
    name="Standard",
    is_instantiable=True,
    allow_fundamental=True,
    valid_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_visibility=VisibilityModifier.private,
    valid_class_modifiers=[
        ClassModifier.immutable,
        ClassModifier.mutable,
    ],
    default_class_modifier=ClassModifier.immutable,
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
    valid_type_alias_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_type_alias_visibility=VisibilityModifier.private,
    valid_nested_class_types=[
        "Exception",
        "POD",
        "Standard",
    ],
    valid_nested_class_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_nested_class_visibility=VisibilityModifier.private,
    valid_method_hierarchy_modifiers=[
        MethodHierarchyModifier.abstract,
        MethodHierarchyModifier.final,
        MethodHierarchyModifier.override,
        MethodHierarchyModifier.standard,
        MethodHierarchyModifier.virtual,
    ],
    default_method_hierarchy_modifier=MethodHierarchyModifier.standard,
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
        MutabilityModifier.view,
        MutabilityModifier.val,
        MutabilityModifier.immutable,
    ],
    default_method_mutability=None,
    allow_static_methods=True,
    valid_using_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_using_visibility=VisibilityModifier.private,
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
