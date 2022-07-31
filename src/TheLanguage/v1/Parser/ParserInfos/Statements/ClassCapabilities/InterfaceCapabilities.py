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
        MethodHierarchyModifier,
        MutabilityModifier,
        VisibilityModifier,
    )


# ----------------------------------------------------------------------
InterfaceCapabilities                       = _ClassCapabilities(
    name="Interface",
    is_instantiable=False,
    allow_fundamental=False,
    valid_visibilities=[
        VisibilityModifier.public,
        VisibilityModifier.internal,
        VisibilityModifier.protected,
        # No private, as what does it mean to be a private and support runtime polymorphism;
        # probably looking for a "concept" instead.
    ],
    default_visibility=VisibilityModifier.protected,
    valid_class_modifiers=[
        ClassModifier.immutable,
        ClassModifier.mutable,
    ],
    default_class_modifier=ClassModifier.immutable,
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
    valid_type_alias_visibilities=[
        VisibilityModifier.public,
    ],
    default_type_alias_visibility=VisibilityModifier.public,
    valid_nested_class_types=[
        "Exception",
        "POD",
    ],
    valid_nested_class_visibilities=[
        VisibilityModifier.public,
    ],
    default_nested_class_visibility=VisibilityModifier.public,
    valid_method_hierarchy_modifiers=[
        MethodHierarchyModifier.abstract,
    ],
    default_method_hierarchy_modifier=MethodHierarchyModifier.abstract,
    valid_method_visibilities=[
        VisibilityModifier.public,
    ],
    default_method_visibility=VisibilityModifier.public,
    valid_method_mutabilities=[
        MutabilityModifier.var,
        MutabilityModifier.ref,
        MutabilityModifier.view,
        MutabilityModifier.val,
        MutabilityModifier.immutable,
    ],
    default_method_mutability=None,
    allow_static_methods=True,
    valid_using_visibilities=[],
    default_using_visibility=None,
    valid_attribute_visibilities=[],
    default_attribute_visibility=None,
    valid_attribute_mutabilities=[],
    allow_mutable_public_attributes=False,
)
