# ----------------------------------------------------------------------
# |
# |  PODCapabilities.py
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
"""Contains the definition for a Plain-Old-Data (PDO) class capabilities"""

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
PODCapabilities                             = _ClassCapabilities(
    name="POD",
    is_instantiable=True,
    allow_fundamental=False,
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
    valid_extends_visibilities=[],
    default_extends_visibility=None,
    valid_implements_types=[],
    valid_implements_visibilities=[],
    default_implements_visibility=None,
    valid_uses_types=[],
    valid_uses_visibilities=[],
    default_uses_visibility=None,
    valid_type_alias_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.private,
    ],
    default_type_alias_visibility=VisibilityModifier.private,
    valid_nested_class_types=[
        "POD",
    ],
    valid_nested_class_visibilities=[
        VisibilityModifier.public,
    ],
    default_nested_class_visibility=VisibilityModifier.public,
    valid_method_hierarchy_modifiers=[
        MethodHierarchyModifier.standard,
    ],
    default_method_hierarchy_modifier=MethodHierarchyModifier.standard,
    valid_method_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
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
    allow_virtual_root_methods_with_templates=False,
    valid_using_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.protected,
        VisibilityModifier.private,
    ],
    default_using_visibility=VisibilityModifier.private,
    valid_attribute_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.private,
    ],
    default_attribute_visibility=VisibilityModifier.public,
    valid_attribute_mutabilities=[
        MutabilityModifier.var,
        MutabilityModifier.ref,
        MutabilityModifier.view,
        MutabilityModifier.val,
        MutabilityModifier.immutable,
    ],
    allow_mutable_public_attributes=True,
)
