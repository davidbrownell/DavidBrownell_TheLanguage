# ----------------------------------------------------------------------
# |
# |  ClassStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-08 10:14:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality used when working with class statements"""

import os

from enum import auto, Enum
from typing import Dict, Optional, List, Tuple

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import StatementParserInfo

    from ..Common.ClassModifier import ClassModifier
    from ..Common.VisibilityModifier import VisibilityModifier

    from ..Error import Error
    from ..ParserInfo import ParserInfo, Region


# ----------------------------------------------------------------------
class ClassType(Enum):
    Class                                   = "class"
    Enum                                    = "enum"
    Exception                               = "exception"
    Interface                               = "interface"
    Mixin                                   = "mixin"
    Primitive                               = "primitive"
    Struct                                  = "struct"
    Trait                                   = "trait"


# ----------------------------------------------------------------------
class MethodModifier(Enum):
    """Modifies how a method should be consumed"""

    abstract                                = auto()
    final                                   = auto()
    override                                = auto()
    standard                                = auto()
    static                                  = auto()
    virtual                                 = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeInfo(object):
    # TODO: This needs refinement

    # Visibility
    DefaultClassVisibility: VisibilityModifier
    AllowedClassVisibilities: List[VisibilityModifier]

    DefaultMemberVisibility: VisibilityModifier
    AllowedMemberVisibilities: List[VisibilityModifier]

    # Base
    DefaultBaseVisibility: Optional[VisibilityModifier]
    AllowedBaseVisibilities: List[VisibilityModifier]
    AllowedBaseTypes: List[ClassType]

    # Implements
    DefaultImplementsVisibility: Optional[VisibilityModifier]
    AllowedImplementsVisibilities: List[VisibilityModifier]
    AllowedImplementsTypes: List[ClassType]

    # Uses
    DefaultUsesVisibility: Optional[VisibilityModifier]
    AllowedUsesVisibilities: List[VisibilityModifier]
    AllowedUsesTypes: List[ClassType]

    # Modifiers
    DefaultClassModifier: ClassModifier
    AllowedClassModifiers: List[ClassModifier]

    # Methods
    DefaultMethodModifier: MethodModifier
    AllowedMethodModifiers: List[MethodModifier]

    # Members
    AllowDataMembers: bool
    AllowMutablePublicDataMembers: bool


# ----------------------------------------------------------------------
# |
# |  Create TypeInfo instances for all ClassType values
# |
# ----------------------------------------------------------------------
_all_method_types                           = list(MethodModifier)
_all_modifiers                              = list(ClassModifier)
_all_visibilities                           = list(VisibilityModifier)


TYPE_INFOS: Dict[ClassType, TypeInfo]       = {
    # TODO: This needs to be completed

    # ----------------------------------------------------------------------
    # |  Class
    ClassType.Class: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.private,
        _all_visibilities,

        # Base
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Class],

        # Implements
        VisibilityModifier.public,
        _all_visibilities,
        [ClassType.Interface, ClassType.Trait],

        # Uses
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Mixin],

        # Modifier
        ClassModifier.immutable,
        _all_modifiers,

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    ),

    # ----------------------------------------------------------------------
    # |  Enum
    ClassType.Enum: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.private,
        _all_visibilities,

        # Base
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Class],

        # Implements
        VisibilityModifier.public,
        _all_visibilities,
        [ClassType.Interface, ClassType.Trait],

        # Uses
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Mixin],

        # Modifier
        ClassModifier.immutable,
        _all_modifiers,

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    ),

    # ----------------------------------------------------------------------
    # |  Exception
    ClassType.Exception: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.private,
        _all_visibilities,

        # Base
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Class],

        # Implements
        VisibilityModifier.public,
        _all_visibilities,
        [ClassType.Interface, ClassType.Trait],

        # Uses
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Mixin],

        # Modifier
        ClassModifier.immutable,
        _all_modifiers,

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    ),

    # ----------------------------------------------------------------------
    # |  Interface
    ClassType.Interface: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.private,
        _all_visibilities,

        # Base
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Class],

        # Implements
        VisibilityModifier.public,
        _all_visibilities,
        [ClassType.Interface, ClassType.Trait],

        # Uses
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Mixin],

        # Modifier
        ClassModifier.immutable,
        _all_modifiers,

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    ),

    # ----------------------------------------------------------------------
    # |  Mixin
    ClassType.Mixin: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.private,
        _all_visibilities,

        # Base
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Class],

        # Implements
        VisibilityModifier.public,
        _all_visibilities,
        [ClassType.Interface, ClassType.Trait],

        # Uses
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Mixin],

        # Modifier
        ClassModifier.immutable,
        _all_modifiers,

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    ),

    # ----------------------------------------------------------------------
    # |  Primitive
    ClassType.Primitive: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.private,
        _all_visibilities,

        # Base
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Class],

        # Implements
        VisibilityModifier.public,
        _all_visibilities,
        [ClassType.Interface, ClassType.Trait],

        # Uses
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Mixin],

        # Modifier
        ClassModifier.immutable,
        _all_modifiers,

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    ),

    # ----------------------------------------------------------------------
    # |  Struct
    ClassType.Struct: TypeInfo(
        # Class
        VisibilityModifier.public,
        _all_visibilities,

        # Members
        VisibilityModifier.public,
        _all_visibilities,

        # Base
        VisibilityModifier.public,
        _all_visibilities,
        [ClassType.Struct],

        # Implements
        None,
        [],
        [],

        # Uses
        None,
        [],
        [],

        # Modifier
        ClassModifier.mutable,
        _all_modifiers,

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    ),

    # ----------------------------------------------------------------------
    # |  Trait
    ClassType.Trait: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.private,
        _all_visibilities,

        # Base
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Class],

        # Implements
        VisibilityModifier.public,
        _all_visibilities,
        [ClassType.Interface, ClassType.Trait],

        # Uses
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Mixin],

        # Modifier
        ClassModifier.immutable,
        _all_modifiers,

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    ),
}

assert len(TYPE_INFOS) == len(ClassType)

del _all_visibilities
del _all_modifiers
del _all_method_types


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassVisibilityError(Error):
    ClassType: str
    Visibility: str
    AllowedVisibilities: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Visibility}' is not a supported visibility for '{ClassType}' types; supported values are {AllowedVisibilities}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassModifierError(Error):
    ClassType: str
    Modifier: str
    AllowedModifiers: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' is not a supported modifier for '{ClassType}' types; supported values are {AllowedModifiers}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidBaseError(Error):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Base-types cannot be used with '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidBaseVisibilityError(Error):
    ClassType: str
    Visibility: str
    AllowedVisibilities: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Visibility}' is not a supported visibility for bases of '{ClassType}' types; supported values are {AllowedVisibilities}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidBaseTypeError(Error):
    ClassType: str
    Type: str
    AllowedTypes: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Type}' types may not be used as bases for '{ClassType}' types; supported values are {AllowedTypes}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidImplementsError(Error):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Implements-types cannot be used with '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidImplementsVisibilityError(Error):
    ClassType: str
    Visibility: str
    AllowedVisibilities: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Visibility}' is not a supported visibility for types implemented by '{ClassType}' types; supported values are {AllowedVisibilities}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidImplementsTypeError(Error):
    ClassType: str
    Type: str
    AllowedTypes: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Type}' types may not be used as implements for '{ClassType}' types; supported values are {AllowedTypes}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidUsesError(Error):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Uses-types cannot be used with '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidUsesVisibilityError(Error):
    ClassType: str
    Visibility: str
    AllowedVisibilities: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Visibility}' is not a supported visibility for types used by '{ClassType}' types; supported values are {AllowedVisibilities}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidUsesTypeError(Error):
    ClassType: str
    Type: str
    AllowedTypes: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Type}' types may not be an uses type for '{ClassType}' types; supported values are {AllowedTypes}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMemberVisibilityError(Error):
    ClassType: str
    Visibility: str
    AllowedVisibilities: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Visibility}' is not a supported visibility for members of '{ClassType}' types; supported values are {AllowedVisibilities}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMemberClassModifierError(Error):
    ClassType: str
    Modifier: str
    AllowedModifiers: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' is not a supported modifier for members of '{ClassType}' types; supported values are {AllowedModifiers}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMemberMutableModifierError(Error):
    ClassType: str
    Modifier: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' is not a valid member modifier for an immutable '{ClassType}' type.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StatementsRequiredError(Error):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Statements are reqired for '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassDependencyParserInfo(ParserInfo):
    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier          = field(init=False)

    Name: str

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, visibility):
        super(ClassDependencyParserInfo, self).__post_init__(
            regions,
            should_validate=False,
        )

        # Visibility
        if visibility is None:
            visibility = VisibilityModifier.private
            object.__setattr__(self.Regions__, "Visibility", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

        object.__setattr__(self, "Visibility", visibility)

        self.Validate()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementParserInfo(StatementParserInfo):

    # Values constructed during phase 1
    visibility: InitVar[Optional[VisibilityModifier]]
    class_modifier: InitVar[Optional[ClassModifier]]

    Visibility: VisibilityModifier          = field(init=False)
    ClassModifier: ClassModifier            = field(init=False)

    ClassType: ClassType
    Name: str
    Base: Optional[ClassDependencyParserInfo]
    Implements: Optional[List[ClassDependencyParserInfo]]
    Uses: Optional[List[ClassDependencyParserInfo]]

    TypeInfo: TypeInfo                      = field(init=False)

    # Values constructed during phase 2
    Statements: List[StatementParserInfo]   = field(init=False, default_factory=list)
    Documentation: Optional[str]            = field(init=False, default=None)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, visibility, class_modifier):
        super(ClassStatementParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["TypeInfo"],
            should_validate=False,
            TypeInfo=None,
        )

        type_info = TYPE_INFOS[self.ClassType]

        # Visibility
        if visibility is None:
            visibility = type_info.DefaultClassVisibility
            object.__setattr__(self.Regions__, "Visibility", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

        if visibility not in type_info.AllowedClassVisibilities:
            raise InvalidClassVisibilityError(
                self.Regions__.Visibility,  # type: ignore && pylint: disable=no-member
                self.ClassType.value,
                visibility.name,
                ", ".join(["'{}'".format(e.name) for e in type_info.AllowedClassVisibilities]),
            )

        object.__setattr__(self, "Visibility", visibility)

        # ClassModifier
        if class_modifier is None:
            class_modifier = type_info.DefaultClassModifier
            object.__setattr__(self.Regions__, "ClassModifier", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

        if class_modifier not in type_info.AllowedClassModifiers:
            raise InvalidClassModifierError(
                self.Regions__.ClassModifier,  # type: ignore && pylint: disable=no-member
                self.ClassType.value,
                class_modifier.name,
                ", ".join(["'{}'".format(e.name) for e in type_info.AllowedClassModifiers]),
            )

        object.__setattr__(self, "ClassModifier", class_modifier)

        # Bases, Implements, and Uses
        if self.Base is not None:
            if not type_info.AllowedBaseTypes:
                raise InvalidBaseError(
                    self.Regions__.Base,  # type: ignore && pylint: disable=no-member
                    self.ClassType.value,
                )

            if self.Base.Visibility not in type_info.AllowedBaseVisibilities:
                raise InvalidBaseVisibilityError(
                    self.Base.Regions__.Visibility,  # type: ignore && pylint: disable=no-member
                    self.ClassType.value,
                    self.Base.Visibility.name,
                    ", ".join(["'{}'".format(e.name) for e in type_info.AllowedBaseVisibilities]),
                )

        if self.Implements is not None:
            if not type_info.AllowedImplementsTypes:
                raise InvalidImplementsError(
                    self.Regions__.Implements,  # type: ignore && pylint: disable=no-member
                    self.ClassType.value,
                )

            assert self.Implements

            for dependency in self.Implements:
                if dependency.Visibility not in type_info.AllowedImplementsVisibilities:
                    raise InvalidImplementsVisibilityError(
                        dependency.Regions__.Visibility,  # type: ignore && pylint: disable=no-member
                        self.ClassType.value,
                        dependency.Visibility.name,
                        ", ".join(["'{}'".format(e.name) for e in type_info.AllowedImplementsVisibilities]),
                    )

        if self.Uses is not None:
            if not type_info.AllowedUsesTypes:
                raise InvalidUsesError(
                    self.Regions__.Uses,  # type: ignore && pylint: disable=no-member
                    self.ClassType.value,
                )

            assert self.Uses

            for dependency in self.Uses:
                if dependency.Visibility not in type_info.AllowedUsesVisibilities:
                    raise InvalidUsesVisibilityError(
                        dependency.Regions__.Visibility,  # type: ignore && pylint: disable=no-member
                        self.ClassType.value,
                        dependency.Visibility.name,
                        ", ".join(["'{}'".format(e.name) for e in type_info.AllowedUsesVisibilities]),
                    )

        # Set TypeInfo
        object.__setattr__(self, "TypeInfo", type_info)

    # ----------------------------------------------------------------------
    def FinalConstruct(
        self,
        statements: List[StatementParserInfo],
        documentation: Optional[Tuple[str, Region]],
    ) -> None:
        assert not self.Statements
        assert self.Documentation is None

        if not statements:
            raise StatementsRequiredError(
                self.Regions__.Statements,  # type: ignore && pylint: disable=no-member
                self.ClassType.value,
            )

        object.__setattr__(self, "Statements", statements)

        if documentation is not None:
            object.__setattr__(self, "Documentation", documentation[0])
            object.__setattr__(self.Regions__, "Documentation", documentation[1])

        self.Validate()

    # ----------------------------------------------------------------------
    def ValidateMemberVisibility(
        self,
        visibility: VisibilityModifier,
        visibility_region: Region,
    ) -> None:
        assert visibility is not None

        if visibility not in self.TypeInfo.AllowedMemberVisibilities:  # type: ignore && pylint: disable=no-member
            raise InvalidMemberVisibilityError(
                visibility_region,
                self.ClassType.value,
                visibility.name,
                ", ".join(["'{}'".format(e.name) for e in self.TypeInfo.AllowedMemberVisibilities]),  # type: ignore && pylint: disable=no-member
            )

    # ----------------------------------------------------------------------
    def ValidateMemberClassModifier(
        self,
        class_modifier, # : ClassModifier,
        class_modifier_region: Region,
    ) -> None:
        assert class_modifier is not None

        if class_modifier not in self.TypeInfo.AllowedClassModifiers:  # type: ignore && pylint: disable=no-member
            raise InvalidMemberClassModifierError(
                class_modifier_region,
                self.ClassType.value,
                class_modifier.name,
                ", ".join(["'{}'".format(e.name) for e in self.TypeInfo.AllowedClassModifiers]),  # type: ignore && pylint: disable=no-member
            )

        if (
            self.ClassModifier == ClassModifier.immutable
            and class_modifier == ClassModifier.mutable
        ):
            raise InvalidMemberMutableModifierError(
                class_modifier_region,
                self.ClassType.value,
                class_modifier.name,
            )
