# ----------------------------------------------------------------------
# |
# |  ClassStatementLexerInfo.py
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
"""Contains the ClassDependencyLexerInfo and ClassStatementLexerInfo objects"""

import os

from enum import auto, Enum
from typing import Dict, Optional, List

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementLexerInfo import StatementLexerData, StatementLexerInfo

    from ..Common.ClassModifier import ClassModifier
    from ..Common.VisibilityModifier import VisibilityModifier

    from ..LexerError import LexerError

    from ..LexerInfo import (
        LexerData,
        LexerRegions,
        LexerInfo,
        Region,
    )


# ----------------------------------------------------------------------
class ClassType(Enum):
    # <Line too long> pylint: disable=C0301
    """\
    |-----------|--------------------|----------------------------|---------------------------|-----------------------------|---------------------|------------------------------------------------------|--------------------------------|------------------------|-------------------------|-------------------------------------|----------------------|-------------------------------------|--------------------------------------------------|--------|-------------|---------|-----------|
    |           | Default Visibility |    Allowed Visibilities    | Default Member Visibility | Allowed Member Visibilities | Default Method Type |               Allowed Method Types                   |    Allow Method Definitions?   | Default Class Modifier | Allowed Class Modifiers | Requires Special Member Definitions | Allows Data Members? | Allows Mutable Public Data Members? |          Can Be Instantiated Directly?           | Bases? | Interfaces? | Mixins? |           |
    |-----------|--------------------|----------------------------|---------------------------|-----------------------------|---------------------|------------------------------------------------------|--------------------------------|------------------------|-------------------------|-------------------------------------|----------------------|-------------------------------------|--------------------------------------------------|--------|-------------|---------|-----------|
    | Primitive |      private       | public, protected, private |          public           |           public            |      deferred       |        deferred, standard (for special members)      | yes (only for special members) |        immutable       |    mutable, immutable   |                 yes                 |          yes         |                 no                  |                       yes                        |   no   |      no     |   no    | Primitive |
    | Class     |      private       | public, protected, private |          private          | public, protected, private  |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |    mutable, immutable   |   no (defaults will be generated)   |          yes         |                 no                  |                       yes                        |   yes  |      yes    |   yes   |     Class |
    | Struct    |      private       |          private           |          public           |           public            |      standard       | standard, static, abstract, virtual, override, final |               yes              |         mutable        |         mutable         |   no (defaults will be generated)   |          yes         |                 yes                 |                       yes                        |   yes  |      no     |   yes   |    Struct |
    | Exception |      public        |          public            |          public           | public, protected, private  |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |        immutable        |   no (defaults will be generated)   |          yes         |                 no                  |                       yes                        |   yes  |      yes    |   yes   | Exception |
    | Enum      |      private       | public, protected, private |          public           |           public            |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |    mutable, immutable   |   no (defaults will be generated)   |          yes         |                 no                  |                       yes                        |   no   |      no     |   no    |      Enum |
    | Interface |      private       | public, protected, private |          public           |           public            |      abstract       |       static, abstract, virtual, override, final     |               yes              |        immutable       |    mutable, immutable   |   no (defaults will be generated)   |          no          |                 no                  |     no (must be implemented by a super class)    |   no   |      yes    |   no    | Interface |
    | Mixin     |      private       | public, protected, private |          private          | public, protected, private  |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |    mutable, immutable   |                 no                  |          yes         |                 no                  | no (functionality is "grafted" into super class) |   yes  |      no     |   yes   |     Mixin |
    |-----------|--------------------|----------------------------|---------------------------|-----------------------------|---------------------|------------------------------------------------------|--------------------------------|------------------------|-------------------------|-------------------------------------|----------------------|-------------------------------------|--------------------------------------------------|--------|-------------|---------|-----------|
    """

    Primitive                               = "primitive"
    Class                                   = "class"
    Struct                                  = "struct"
    Exception                               = "exception"
    Enum                                    = "enum"
    Interface                               = "interface"
    Mixin                                   = "mixin"

    # TODO: Enum doesn't seem to fit here


# ----------------------------------------------------------------------
class MethodType(Enum):  # type: ignore
    """\
    Modifies how a method should be consumed
    """

    standard                                = auto()
    deferred                                = auto()
    static                                  = auto()
    abstract                                = auto()
    virtual                                 = auto()
    override                                = auto()
    final                                   = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassVisibilityError(LexerError):
    ClassType: str
    Visibility: str
    AllowedVisibilities: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Visibility}' is not a supported visibility for '{ClassType}' types; supported values are {AllowedVisibilities}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassModifierError(LexerError):
    ClassType: str
    Modifier: str
    AllowedModifiers: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' is not a supported modifier for '{ClassType}' types; supported values are {AllowedModifiers}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMemberVisibilityError(LexerError):
    ClassType: str
    Visibility: str
    AllowedVisibilities: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Visibility}' is not a supported visibility for members of '{ClassType}' types; supported values are {AllowedVisibilities}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMemberClassModifierError(LexerError):
    ClassType: str
    Modifier: str
    AllowedModifiers: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' is not a supported modifier for members of '{ClassType}' types; supported values are {AllowedModifiers}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMutableClassModifierError(LexerError):
    ClassType: str
    Modifier: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' is not a valid member modifier for an immutable '{ClassType}' type.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidBaseError(LexerError):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Base classes cannot be used with '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidInterfacesError(LexerError):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Interfaces cannot be used with '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMixinsError(LexerError):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Mixins cannot be used with '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeInfo(object):
    DefaultClassVisibility: VisibilityModifier
    AllowedClassVisibilities: List[VisibilityModifier]

    DefaultMemberVisibility: VisibilityModifier
    AllowedMemberVisibilities: List[VisibilityModifier]

    DefaultClassModifier: ClassModifier
    AllowedClassModifiers: List[ClassModifier]

    DefaultMethodType: MethodType
    AllowedMethodTypes: List[MethodType]

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
@dataclass(frozen=True, repr=False)
class ClassDependencyLexerData(LexerData):
    Visibility: VisibilityModifier
    Name: str

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Name
        super(ClassDependencyLexerData, self).__post_init__()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassDependencyLexerRegions(LexerRegions):
    Visibility: Region
    Name: Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassDependencyLexerInfo(LexerInfo):
    Data: ClassDependencyLexerData          = field(init=False)
    Regions: ClassDependencyLexerRegions

    visibility: InitVar[Optional[VisibilityModifier]]
    name: InitVar[str]

    # ----------------------------------------------------------------------
    def __post_init__(self, visibility, name):
        # Set default values and validate as necessary
        if visibility is None:
            visibility = VisibilityModifier.private
            object.__setattr__(self.Regions, "Visibility", self.Regions.Self__)

        # pylint: disable=too-many-function-args
        object.__setattr__(
            self,
            "Data",
            ClassDependencyLexerData(visibility, name),
        )

        super(ClassDependencyLexerInfo, self).__post_init__()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementLexerData(StatementLexerData):
    Visibility: VisibilityModifier
    ClassModifier: ClassModifier
    ClassType: ClassType
    Name: str
    Base: Optional[ClassDependencyLexerInfo]
    Interfaces: List[ClassDependencyLexerInfo]
    Mixins: List[ClassDependencyLexerInfo]

    TypeInfo: TypeInfo                      = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        type_info = TYPE_INFOS[self.ClassType]

        assert self.Visibility in type_info.AllowedClassVisibilities
        assert self.ClassModifier in type_info.AllowedClassModifiers
        assert self.Base is None or type_info.AllowBases
        assert not self.Interfaces or type_info.AllowInterfaces
        assert not self.Mixins or type_info.AllowMixins

        object.__setattr__(self, "TypeInfo", type_info)

        super(ClassStatementLexerData, self).__post_init__(
            TypeInfo=None,
        )

    # ----------------------------------------------------------------------
    def ValidateMemberVisibility(
        self,
        visibility: VisibilityModifier,
        visibility_region: Region,
    ):
        assert visibility is not None

        # pylint: disable=no-member
        if visibility not in self.TypeInfo.AllowedMemberVisibilities:
            raise InvalidMemberVisibilityError(
                visibility_region,
                self.ClassType.value,
                visibility.name,
                ", ".join(["'{}'".format(v.name) for v in self.TypeInfo.AllowedMemberVisibilities]),
            )

    # ----------------------------------------------------------------------
    def ValidateMemberClassModifier(
        self,
        class_modifier, # : ClassModifier,
        class_modifier_region: Region,
    ):
        assert class_modifier is not None

        # pylint: disable=no-member
        if class_modifier not in self.TypeInfo.AllowedClassModifiers:
            raise InvalidMemberClassModifierError(
                class_modifier_region,
                self.ClassType.value,
                class_modifier.name,
                ", ".join(["'{}'".format(m.name) for m in self.TypeInfo.AllowedClassModifiers]),
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


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementLexerRegions(LexerRegions):
    Visibility: Region
    ClassModifier: Region
    ClassType: Region
    Name: Region
    Base: Optional[Region]
    Interfaces: Optional[Region]
    Mixins: Optional[Region]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementLexerInfo(StatementLexerInfo):
    Data: ClassStatementLexerData           = field(init=False)
    Regions: ClassStatementLexerRegions

    visibility: InitVar[Optional[VisibilityModifier]]
    class_modifier: InitVar[Optional[ClassModifier]]
    class_type: InitVar[ClassType]
    name: InitVar[str]
    base: InitVar[Optional[ClassDependencyLexerInfo]]
    interfaces: InitVar[List[ClassDependencyLexerInfo]]
    mixins: InitVar[List[ClassDependencyLexerInfo]]

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        visibility,
        class_modifier,
        class_type,
        name,
        base,
        interfaces,
        mixins,
    ):
        type_info = TYPE_INFOS[class_type]

        # Set default values and validate as necessary
        if visibility is None:
            visibility = type_info.DefaultClassVisibility
            object.__setattr__(self.Regions, "Visibility", self.Regions.Self__)

        if visibility not in type_info.AllowedClassVisibilities:
            raise InvalidClassVisibilityError(
                self.Regions.Visibility,
                class_type.value,
                visibility.name,
                ", ".join(["'{}'".format(v.name) for v in type_info.AllowedClassVisibilities]),
            )

        if class_modifier is None:
            class_modifier = type_info.DefaultClassModifier
            object.__setattr__(self.Regions, "ClassModifier", self.Regions.Self__)

        if class_modifier not in type_info.AllowedClassModifiers:
            raise InvalidClassModifierError(
                self.Regions.ClassModifier,
                class_type.value,
                class_modifier.name,
                ", ".join(["'{}'".format(m.name) for m in type_info.AllowedClassModifiers]),
            )

        # Validate bases, interfaces, and mixins
        if base is not None and not type_info.AllowBases:
            assert self.Regions.Base is not None
            raise InvalidBaseError(self.Regions.Base, class_type.value)

        if interfaces and not type_info.AllowInterfaces:
            assert self.Regions.Interfaces is not None
            raise InvalidInterfacesError(self.Regions.Interfaces, class_type.value)

        if mixins and not type_info.AllowMixins:
            assert self.Regions.Mixins is not None
            raise InvalidMixinsError(self.Regions.Mixins, class_type.value)

        # Set the values
        object.__setattr__(
            self,
            "Data",
            # pylint: disable=too-many-function-args
            ClassStatementLexerData(
                visibility,  # type: ignore
                class_modifier,  # type: ignore
                class_type,
                name,
                base,
                interfaces,
                mixins,
            ),
        )
