# ----------------------------------------------------------------------
# |
# |  ClassCapabilities.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-03-31 09:46:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassCapabilities object"""

import os

from dataclasses import dataclass
from typing import List, Optional

import CommonEnvironment
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common.ClassModifier import ClassModifier
    from ...Common.MethodModifier import MethodModifier
    from ...Common.VisibilityModifier import VisibilityModifier


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassCapabilities(ObjectReprImplBase):
    """\
    Classes come in different forms; this class defines capabilities
    that dictate what is and isn't valid for an instance of a class.
    """

    name: str
    default_class_modifier: ClassModifier

    valid_visibilities: List[VisibilityModifier]
    default_visibility: VisibilityModifier

    valid_extends_visibilities: List[VisibilityModifier]
    default_extends_visibility: Optional[VisibilityModifier]

    valid_implements_types: List[str]
    valid_implements_visibilities: List[VisibilityModifier]
    default_implements_visibility: Optional[VisibilityModifier]

    valid_uses_types: List[str]
    valid_uses_visibilities: List[VisibilityModifier]
    default_uses_visibility: Optional[VisibilityModifier]

    valid_method_modifiers: List[MethodModifier]
    valid_method_visibilities: List[VisibilityModifier]
    allow_static_methods: bool

    valid_attribute_visibilities: List[VisibilityModifier]
    allow_mutable_public_attributes: bool

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.valid_visibilities
        assert self.default_visibility in self.valid_visibilities
        assert (self.valid_implements_types and self.valid_implements_visibilities) or (not self.valid_implements_types and not self.valid_implements_visibilities)
        assert (self.valid_uses_types and self.valid_uses_visibilities) or (not self.valid_uses_types and not self.valid_uses_visibilities)
        assert (self.valid_method_modifiers and self.valid_method_visibilities) or (not self.valid_method_modifiers and not self.valid_method_visibilities)
        assert not self.allow_static_methods or self.valid_method_visibilities
        assert not self.allow_mutable_public_attributes or self.valid_attribute_visibilities

        ObjectReprImplBase.__init__(self)
