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

from enum import Enum
from typing import Dict, Optional, List, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.ClassModifier import ClassModifier
    from ..Common.VisibilityModifier import VisibilityModifier
    from ...LexerInfo import Error, LexerInfo

    from ....Parser.Components.AST import Leaf, Node


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
class InvalidMutableClassModifierError(Error):
    ClassName: str
    ClassType: str
    Modifier: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' is not a valid member modifier for '{ClassName}', which is an immutable '{ClassType}' type.",
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

    # TODO: DefaultMethodType: MethodType
    # TODO: AllowedMethodTypes: List[MethodType]

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

TYPE_INFOS: Dict[ClassType, "TypeInfo"]     = {
    ClassType.Primitive: TypeInfo(
        VisibilityModifier.private,
        _all_visibilities,

        VisibilityModifier.public,
        [VisibilityModifier.public],

        ClassModifier.immutable,
        _all_class_modifiers,

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

        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
        AllowBases=True,
        AllowInterfaces=False,
        AllowMixins=True,
    ),
}

del _all_class_modifiers
del _all_visibilities


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassDependencyLexerInfo(LexerInfo):
    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier          = field(init=False)

    Name: str

    # ----------------------------------------------------------------------
    def __post_init__(self, visibility):
        # Set default values and validate as necessary
        if visibility is None:
            visibility = VisibilityModifier.private
            self.TokenLookup["Visibility"] = self.TokenLookup["self"]

        # Set the values
        object.__setattr__(self, "Visibility", visibility)

        super(ClassDependencyLexerInfo, self).__post_init__()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementLexerInfo(LexerInfo):
    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier          = field(init=False)

    class_modifier: InitVar[Optional[ClassModifier]]
    ClassModifier: ClassModifier            = field(init=False)

    ClassType: ClassType
    Name: str
    Base: Optional[ClassDependencyLexerInfo]
    Interfaces: List[ClassDependencyLexerInfo]
    Mixins: List[ClassDependencyLexerInfo]

    TypeInfo: TypeInfo                      = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self, visibility, class_modifier):
        type_info = TYPE_INFOS[self.ClassType]

        # Set default values and validate as necessary
        if visibility is None:
            visibility = type_info.DefaultClassVisibility
            self.TokenLookup["Visibility"] = self.TokenLookup["self"]

        if visibility not in type_info.AllowedClassVisibilities:
            raise InvalidClassVisibilityError.FromNode(
                self.TokenLookup["Visibility"],
                self.ClassType.value,
                visibility.name,
                ", ".join(["'{}'".format(v.name) for v in type_info.AllowedClassVisibilities]),
            )

        if class_modifier is None:
            class_modifier = type_info.DefaultClassModifier
            self.TokenLookup["ClassModifier"] = self.TokenLookup["self"]

        if class_modifier not in type_info.AllowedClassModifiers:
            raise InvalidClassModifierError.FromNode(
                self.TokenLookup["ClassModifier"],
                self.ClassType.value,
                class_modifier.name,
                ", ".join(["'{}'".format(m.name) for m in type_info.AllowedClassModifiers]),
            )

        # Set the values
        object.__setattr__(self, "TypeInfo", type_info)
        object.__setattr__(self, "Visibility", visibility)
        object.__setattr__(self, "ClassModifier", class_modifier)

        super(ClassStatementLexerInfo, self).__post_init__(
            TypeInfo=None,
        )

    # ----------------------------------------------------------------------
    def ValidateMemberVisibility(
        self,
        visibility: VisibilityModifier,
        token_lookup: Dict[str, Union[Leaf, Node]],
        token_lookup_key_name="Visibility",
    ):
        assert visibility is not None

        if visibility not in self.TypeInfo.AllowedMemberVisibilities:
            raise InvalidMemberVisibilityError.FromNode(
                token_lookup[token_lookup_key_name],
                self.ClassType.value,
                visibility.name,
                ", ".join(["'{}'".format(v) for v in self.TypeInfo.AllowedMemberVisibilities]),
            )

    # ----------------------------------------------------------------------
    def ValidateMemberClassModifier(
        self,
        class_modifier, # : ClassModifier,
        token_lookup: Dict[str, Union[Leaf, Node]],
        token_lookup_key_name="ClassModifier",
    ):
        assert class_modifier is not None

        if class_modifier not in self.TypeInfo.AllowedClassModifiers:
            raise InvalidMemberClassModifierError.FromNode(
                token_lookup[token_lookup_key_name],
                self.ClassType.value,
                class_modifier.name,
                ", ".join(["'{}'".format(m) for m in self.TypeInfo.AllowedClassModifiers]),
            )

        if (
            self.ClassModifier == ClassModifier.immutable
            and class_modifier == ClassModifier.mutable
        ):
            raise InvalidMutableClassModifierError.FromNode(
                token_lookup[token_lookup_key_name],
                self.Name,
                self.ClassType.value,
                class_modifier.name,
            )
