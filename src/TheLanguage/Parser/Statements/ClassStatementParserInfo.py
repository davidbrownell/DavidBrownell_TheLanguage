# ----------------------------------------------------------------------
# |
# |  ClassStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-07 14:58:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassDependencyParserInfo and ClassStatementParserInfo objects"""

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

    from ..ParserError import ParserError
    from ..ParserInfo import ParserInfo, Region


# ----------------------------------------------------------------------
class ClassType(Enum):
    """\
    |-----------------------------------------------------------------------------------------------------------------------|
    | VISIBILITY                                                                                                            |
    |-----------|--------------------|----------------------------|---------------------------|-----------------------------|
    |   Type    | Default Visibility |    Allowed Visibilities    | Default Member Visibility | Allowed Member Visibilities |
    |-----------|--------------------|----------------------------|---------------------------|-----------------------------|
    | Class     |      private       | public, protected, private |          private          | public, protected, private  |
    | Enum      |      private       | public, protected, private |          public           | public  protected, private  |
    | Exception |      public        |          public            |          public           | public, protected, private  |
    | Interface |      private       | public, protected, private |          public           | public, protected, private  |
    | Mixin     |      private       | public, protected, private |          private          | public, protected, private  |
    | Primitive |      private       | public, protected, private |          public           | public, protected, private  |
    | Struct    |      private       |          private           |          public           | public, protected, private  |
    | Trait     |      private       | public, protected, private |          public           | public, protected, private  |
    |-----------|--------------------|----------------------------|---------------------------|-----------------------------|


    |--------------------------------------------------------------|
    | CLASS MODIFIERS                                              |
    |-----------|------------------------|-------------------------|
    |   Type    | Default Class Modifier | Allowed Class Modifiers |
    |-----------|------------------------|-------------------------|
    | Class     |       immutable        |    mutable, immutable   |
    | Enum      |       immutable        |    mutable, immutable   |
    | Exception |       immutable        |        immutable        |
    | Interface |       immutable        |    mutable, immutable   |
    | Mixin     |       immutable        |    mutable, immutable   |
    | Primitive |       immutable        |    mutable, immutable   |
    | Struct    |        mutable         |         mutable         |
    | Trait     |       immutable        |    mutable, immutable   |
    |-----------|------------------------|-------------------------|


    |-------------------------------------------------------------------------------------------------|
    | METHODS                                                                                         |
    |-----------|---------------------|----------------------|----------------------------------------|
    |   Type    | Default Method Type | Allowed Method Types |               Notes                    |
    |-----------|---------------------|----------------------|----------------------------------------|
    | Class     |      standard       |                      |                                        |
    | Enum      |      standard       |                      |                                        |
    | Exception |      standard       |                      |                                        |
    | Interface |      abstract       |  -deferred, -static  |                                        |
    | Mixin     |      standard       |                      | 'abstract' is resolved at compile-time |
    | Primitive |      deferred       |      +deferred       | Implementation is resolved by target   |
    | Struct    |      standard       |                      |                                        |
    | Trait     |      abstract       |  -deferred, -static  | 'abstract' is resolved at compile-time |
    |-----------|---------------------|----------------------|----------------------------------------|


    |---------------------------------------------------------------------------------------|
    | DEPENDENCIES (Bases)                                                                  |
    |-----------|-------|------|-----------|-----------|-------|-----------|--------|-------|
    |   Type    | Class | Enum | Exception | Interface | Mixin | Primitive | Struct | Trait |
    |-----------|-------|------|-----------|-----------|-------|-----------|--------|-------|
    | Class     |   X   |      |           |           |       |           |        |       |
    | Enum      |       |      |           |           |       |           |        |       |
    | Exception |       |      |     X     |           |       |           |        |       |
    | Interface |       |      |           |           |       |           |        |       |
    | Mixin     |       |      |           |           |   X   |           |        |       |
    | Primitive |       |      |           |           |       |           |        |       |
    | Struct    |       |      |           |           |       |           |    X   |       |
    | Trait     |       |      |           |           |       |           |        |       |
    |-----------|-------|------|-----------|-----------|-------|-----------|--------|-------|


    |---------------------------------------------------------------------------------------|
    | DEPENDENCIES (Implements)                                                             |
    |-----------|-------|------|-----------|-----------|-------|-----------|--------|-------|
    |   Type    | Class | Enum | Exception | Interface | Mixin | Primitive | Struct | Trait |
    |-----------|-------|------|-----------|-----------|-------|-----------|--------|-------|
    | Class     |       |      |           |     X     |       |           |        |   X   |
    | Enum      |       |      |           |           |       |           |        |       |
    | Exception |       |      |           |     X     |       |           |        |   X   |
    | Interface |       |      |           |     X     |       |           |        |       |
    | Mixin     |       |      |           |           |       |           |        |       |
    | Primitive |       |      |           |           |       |           |        |       |
    | Struct    |       |      |           |           |       |           |        |       |
    | Trait     |       |      |           |           |       |           |        |   X   |
    |-----------|-------|------|-----------|-----------|-------|-----------|--------|-------|


    TODO: This needs some work:

    |---------------------------------------------------------------------------------------|
    | DEPENDENCIES (Uses)                                                                   |
    |-----------|-------|------|-----------|-----------|-------|-----------|--------|-------|
    |   Type    | Class | Enum | Exception | Interface | Mixin | Primitive | Struct | Trait |
    |-----------|-------|------|-----------|-----------|-------|-----------|--------|-------|
    | Class     |       |      |           |           |   X   |           |        |       |
    | Enum      |       |      |           |           |       |           |        |       |
    | Exception |       |      |           |           |   X   |           |        |       |
    | Interface |       |      |           |           |       |           |        |       |
    | Mixin     |       |      |           |           |   X   |           |        |       |
    | Primitive |       |      |           |           |       |           |        |       |
    | Struct    |       |      |           |           |   ?   |           |        |       |
    | Trait     |       |      |           |           |       |           |        |       |
    |-----------|-------|------|-----------|-----------|-------|-----------|--------|-------|

    """


    Class                                   = "class"
    Enum                                    = "enum"
    Exception                               = "exception"
    Interface                               = "interface"
    Mixin                                   = "mixin"
    Primitive                               = "primitive"
    Struct                                  = "struct"
    # TODO: Trait                                   = "trait"

    # TODO: Enum doesn't seem to fit here

# TODO: Mutability is required for structs, can never be used on members

# ----------------------------------------------------------------------
class MethodType(Enum):
    """\
    Modifies how a method should be consumed
    """

    abstract                                = auto()
    deferred                                = auto()
    final                                   = auto()
    override                                = auto()
    standard                                = auto()
    static                                  = auto()
    virtual                                 = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeInfo(object):
    # Visibility
    DefaultClassVisibility: VisibilityModifier
    AllowedClassVisibilities: List[VisibilityModifier]

    DefaultMemberVisibility: VisibilityModifier
    AllowedMemberVisibilities: List[VisibilityModifier]

    # Class Modifiers
    DefaultClassModifier: ClassModifier
    AllowedClassModifiers: List[ClassModifier]

    # Methods
    DefaultMethodType: MethodType
    AllowedMethodTypes: List[MethodType]

    # TODO: Dependencies

    AllowDataMembers: bool
    AllowMutablePublicDataMembers: bool
    AllowBases: bool
    AllowInterfaces: bool
    AllowMixins: bool

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.DefaultClassVisibility in self.AllowedClassVisibilities
        assert self.DefaultMemberVisibility in self.AllowedMemberVisibilities
        assert self.DefaultClassModifier in self.AllowedClassModifiers
        assert not self.AllowMutablePublicDataMembers or self.AllowDataMembers


# ----------------------------------------------------------------------
_all_visibilities                           = list(VisibilityModifier)
_all_class_modifiers                        = list(ClassModifier)
_non_deferred_method_types                  = [m for m in MethodType if m != MethodType.deferred]

TYPE_INFOS: Dict[ClassType, "TypeInfo"]     = {
    ClassType.Primitive: TypeInfo(
        VisibilityModifier.private,
        _all_visibilities,

        VisibilityModifier.public,
        [VisibilityModifier.public],

        ClassModifier.immutable,
        _all_class_modifiers,

        MethodType.deferred,
        [MethodType.deferred],

        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
        AllowBases=False,
        AllowInterfaces=False,
        AllowMixins=False,
    ),

    ClassType.Class: TypeInfo(
        VisibilityModifier.private,
        _all_visibilities,

        VisibilityModifier.private,
        _all_visibilities,

        ClassModifier.immutable,
        _all_class_modifiers,

        MethodType.standard,
        _non_deferred_method_types,

        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
        AllowBases=True,
        AllowInterfaces=True,
        AllowMixins=True,
    ),

    ClassType.Struct: TypeInfo(
        VisibilityModifier.private,
        [VisibilityModifier.private],

        VisibilityModifier.public,
        [VisibilityModifier.public],

        ClassModifier.mutable,
        [ClassModifier.mutable],

        MethodType.standard,
        _non_deferred_method_types,

        AllowDataMembers=True,
        AllowMutablePublicDataMembers=True,
        AllowBases=True,
        AllowInterfaces=False,
        AllowMixins=True,
    ),

    ClassType.Exception: TypeInfo(
        VisibilityModifier.public,
        [VisibilityModifier.public],

        VisibilityModifier.public,
        _all_visibilities,

        ClassModifier.immutable,
        [ClassModifier.immutable],

        MethodType.standard,
        _non_deferred_method_types,

        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
        AllowBases=True,
        AllowInterfaces=True,
        AllowMixins=True,
    ),

    ClassType.Enum: TypeInfo(
        VisibilityModifier.private,
        _all_visibilities,

        VisibilityModifier.public,
        [VisibilityModifier.public],

        ClassModifier.immutable,
        _all_class_modifiers,

        MethodType.standard,
        _non_deferred_method_types,

        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
        AllowBases=False,
        AllowInterfaces=False,
        AllowMixins=False,
    ),

    ClassType.Interface: TypeInfo(
        VisibilityModifier.private,
        _all_visibilities,

        VisibilityModifier.public,
        [VisibilityModifier.public],

        ClassModifier.immutable,
        _all_class_modifiers,

        MethodType.abstract,
        [m for m in _non_deferred_method_types if m != MethodType.static],

        AllowDataMembers=False,
        AllowMutablePublicDataMembers=False,
        AllowBases=False,
        AllowInterfaces=True,
        AllowMixins=False,
    ),

    ClassType.Mixin: TypeInfo(
        VisibilityModifier.private,
        _all_visibilities,

        VisibilityModifier.private,
        _all_visibilities,

        ClassModifier.immutable,
        _all_class_modifiers,

        MethodType.standard,
        _non_deferred_method_types,

        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
        AllowBases=True,
        AllowInterfaces=False,
        AllowMixins=True,
    ),
}

del _non_deferred_method_types
del _all_class_modifiers
del _all_visibilities


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassVisibilityError(ParserError):
    ClassType: str
    Visibility: str
    AllowedVisibilities: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Visibility}' is not a supported visibility for '{ClassType}' types; supported values are {AllowedVisibilities}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassModifierError(ParserError):
    ClassType: str
    Modifier: str
    AllowedModifiers: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' is not a supported modifier for '{ClassType}' types; supported values are {AllowedModifiers}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMemberVisibilityError(ParserError):
    ClassType: str
    Visibility: str
    AllowedVisibilities: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Visibility}' is not a supported visibility for members of '{ClassType}' types; supported values are {AllowedVisibilities}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMemberClassModifierError(ParserError):
    ClassType: str
    Modifier: str
    AllowedModifiers: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' is not a supported modifier for members of '{ClassType}' types; supported values are {AllowedModifiers}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMutableClassModifierError(ParserError):
    ClassType: str
    Modifier: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' is not a valid member modifier for an immutable '{ClassType}' type.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidBaseError(ParserError):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Base classes cannot be used with '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidInterfacesError(ParserError):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Interfaces cannot be used with '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMixinsError(ParserError):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Mixins cannot be used with '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StatementsRequiredError(ParserError):
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
            object.__setattr__(self.Regions, "Visibility", self.Regions.Self__)  # type: ignore && pylint: disable=no-member

        object.__setattr__(self, "Visibility", visibility)

        self.Validate()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementParserInfo(StatementParserInfo):
    # Constructed during Phase 1
    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier          = field(init=False)

    class_modifier: InitVar[Optional[ClassModifier]]
    ClassModifier: ClassModifier            = field(init=False)

    ClassType: ClassType
    Name: str
    Base: Optional[ClassDependencyParserInfo]
    Interfaces: Optional[List[ClassDependencyParserInfo]]
    Mixins: Optional[List[ClassDependencyParserInfo]]

    TypeInfo: TypeInfo                      = field(init=False)

    # Constructed during Phase 2
    Statements: List[StatementParserInfo]    = field(init=False, default_factory=list)
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
            object.__setattr__(self.Regions, "Visibility", self.Regions.Self__)  # type: ignore && pylint: disable=no-member

        if visibility not in type_info.AllowedClassVisibilities:
            raise InvalidClassVisibilityError(
                self.Regions.Visibility,  # type: ignore && pylint: disable=no-member
                self.ClassType.value,
                visibility.name,
                ", ".join(["'{}'".format(v.name) for v in type_info.AllowedClassVisibilities]),
            )

        object.__setattr__(self, "Visibility", visibility)

        # ClassModifier
        if class_modifier is None:
            class_modifier = type_info.DefaultClassModifier
            object.__setattr__(self.Regions, "ClassModifier", self.Regions.Self__)  # type: ignore && pylint: disable=no-member

        if class_modifier not in type_info.AllowedClassModifiers:
            raise InvalidClassModifierError(
                self.Regions.ClassModifier,  # type: ignore && pylint: disable=no-member
                self.ClassType.value,
                class_modifier.name,
                ", ".join(["'{}'".format(m.name) for m in type_info.AllowedClassModifiers]),
            )

        object.__setattr__(self, "ClassModifier", class_modifier)

        # Validate bases, interfaces, and mixins
        if self.Base is not None and not type_info.AllowBases:
            raise InvalidBaseError(self.Regions.Base, self.ClassType.value)  # type: ignore && pylint: disable=no-member

        if self.Interfaces and not type_info.AllowInterfaces:
            raise InvalidInterfacesError(self.Regions.Interfaces, self.ClassType.value)  # type: ignore && pylint: disable=no-member

        if self.Mixins and not type_info.AllowMixins:
            raise InvalidMixinsError(self.Regions.Mixins, self.ClassType.value)  # type: ignore && pylint: disable=no-member

        # Set TypeInfo
        object.__setattr__(self, "TypeInfo", type_info)

    # ----------------------------------------------------------------------
    def FinalConstruct(
        self,
        statements: List[StatementParserInfo],
        documentation: Optional[Tuple[str, Region]],
    ):
        assert not self.Statements

        if not statements:
            raise StatementsRequiredError(
                self.Regions.Statements,  # type: ignore && pylint: disable=no-member
                self.ClassType.value,
            )

        object.__setattr__(self, "Statements", statements)

        if documentation is not None:
            object.__setattr__(self, "Documentation", documentation[0])
            object.__setattr__(self.Regions, "Documentation", documentation[1])

        self.Validate()

    # ----------------------------------------------------------------------
    def ValidateMemberVisibility(
        self,
        visibility: VisibilityModifier,
        visibility_region: Region,
    ):
        assert visibility is not None

        if visibility not in self.TypeInfo.AllowedMemberVisibilities:  # pylint: disable=no-member
            raise InvalidMemberVisibilityError(
                visibility_region,
                self.ClassType.value,
                visibility.name,
                ", ".join(["'{}'".format(v.name) for v in self.TypeInfo.AllowedMemberVisibilities]),  # pylint: disable=no-member
            )

    # ----------------------------------------------------------------------
    def ValidateMemberClassModifier(
        self,
        class_modifier, # : ClassModifier,
        class_modifier_region: Region,
    ):
        assert class_modifier is not None

        if class_modifier not in self.TypeInfo.AllowedClassModifiers:  # pylint: disable=no-member
            raise InvalidMemberClassModifierError(
                class_modifier_region,
                self.ClassType.value,
                class_modifier.name,
                ", ".join(["'{}'".format(m.name) for m in self.TypeInfo.AllowedClassModifiers]),  # pylint: disable=no-member
            )

        if (
            self.ClassModifier == ClassModifier.immutable
            and class_modifier == ClassModifier.mutable
        ):
            raise InvalidMutableClassModifierError(
                class_modifier_region,
                self.ClassType.value,
                class_modifier.name,
            )
