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

from typing import Optional, List, Tuple

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
    from .Impl.ClassTypeInfos import TypeInfo, TYPE_INFOS  # <Incorrect: Unused TypeInfo> pylint: disable=W0611

    from ..Common.ClassModifier import ClassModifier as ClassModifierType
    from ..Common.ClassType import ClassType
    from ..Common.VisibilityModifier import VisibilityModifier
    from ..Common.VisitorTools import StackHelper

    from ..Error import Error
    from ..ParserInfo import ParserInfo, Region


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
class ClassStatementDependencyParserInfo(ParserInfo):
    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier          = field(init=False)

    Name: str

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, visibility):  # <Parameters differ> pylint: disable=W0221
        super(ClassStatementDependencyParserInfo, self).__post_init__(
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
    class_modifier: InitVar[Optional[ClassModifierType]]

    Visibility: VisibilityModifier          = field(init=False)
    ClassModifier: ClassModifierType        = field(init=False)

    ClassType: ClassType
    Name: str
    Base: Optional[ClassStatementDependencyParserInfo]
    Implements: Optional[List[ClassStatementDependencyParserInfo]]
    Uses: Optional[List[ClassStatementDependencyParserInfo]]

    type_info: InitVar[Optional[TypeInfo]]  = None  # type: ignore
    TypeInfo: TypeInfo                      = field(init=False)

    # Values constructed during phase 2
    Statements: List[StatementParserInfo]   = field(init=False, default_factory=list)
    Documentation: Optional[str]            = field(init=False, default=None)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, visibility, class_modifier, type_info):  # <Parameters differ> pylint: disable=W0221
        super(ClassStatementParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["TypeInfo"],
            should_validate=False,
            TypeInfo=None,

            # Note that this should not be necessary, but it seems that the dataclass will include
            # this var as part of the class (likely due to the default initialization). Unfortunately,
            # I wasn't able to remove the attribute from the class instance, so suppressing the
            # output is the next best option.
            type_info=None,
        )

        # TypeInfo
        if type_info is None:
            type_info = TYPE_INFOS[self.ClassType]

        object.__setattr__(self, "TypeInfo", type_info)

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
            self.ClassModifier == ClassModifierType.immutable
            and class_modifier == ClassModifierType.mutable
        ):
            raise InvalidMemberMutableModifierError(
                class_modifier_region,
                self.ClassType.value,
                class_modifier.name,
            )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            if self.Base is not None:
                with helper["Base"]:
                    self.Base.Accept(visitor, helper.stack, *args, **kwargs)

            if self.Implements is not None:
                with helper["Implements"]:
                    for dependency in self.Implements:
                        dependency.Accept(visitor, helper.stack, *args, **kwargs)

            if self.Uses is not None:
                with helper["Uses"]:
                    for dependency in self.Uses:
                        dependency.Accept(visitor, helper.stack, *args, **kwargs)

            with helper["Statements"]:
                for statement in self.Statements:  # type: ignore && pylint: disable=not-an-iterable
                    statement.Accept(visitor, helper.stack, *args, **kwargs)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# pylint: disable=line-too-long
# <line too long> pylint: disable=C0301

# [[[cog
#    import os
#    import sys
#    import textwrap
#
#    import cog
#
#    sys.path.insert(0, os.path.join(os.path.dirname(cog.inFile), "Impl"))
#    from ClassTypeInfos import *
#    del sys.path[0]
#
#    cog.outl(
#        textwrap.dedent(
#            """\
#
#            # ----------------------------------------------------------------------------------------
#            # |                                                                                      |
#            # |  These comments have been auto-generated by Cog. To update this documentation, run:  |
#            # |                                                                                      |
#            # |      cog -r -c -s "  // Generated by Cog" ClassStatementParserInfo.py                |
#            # |                                                                                      |
#            # ----------------------------------------------------------------------------------------
#
#           """,
#        ),
#    )
#
#    cog.outl(CogCreateCompleteTable())
#    cog.outl(CogCreateMembershipTable("Class Visibility", VisibilityModifier, "DefaultClassVisibility", "AllowedClassVisibilities"))
#    cog.outl(CogCreateMembershipTable("Member Visibility", VisibilityModifier, "DefaultMemberVisibility", "AllowedMemberVisibilities"))
#    cog.outl(CogCreateMembershipTable("Allowed Bases", ClassType, None, "AllowedBaseTypes"))
#    cog.outl(CogCreateMembershipTable("Base Visibility", VisibilityModifier, "DefaultBaseVisibility", "AllowedBaseVisibilities"))
#    cog.outl(CogCreateMembershipTable("Allowed Implements", ClassType, None, "AllowedImplementsTypes"))
#    cog.outl(CogCreateMembershipTable("Implements Visibility", VisibilityModifier, "DefaultImplementsVisibility", "AllowedImplementsVisibilities"))
#    cog.outl(CogCreateMembershipTable("Allowed Uses", ClassType, None, "AllowedUsesTypes"))
#    cog.outl(CogCreateMembershipTable("Uses Visibility", VisibilityModifier, "DefaultUsesVisibility", "AllowedUsesVisibilities"))
#    cog.outl(CogCreateMembershipTable("Class Modifier", ClassModifierType, "DefaultClassModifier", "AllowedClassModifiers"))
#    cog.outl(CogCreateMembershipTable("Method Modifier", MethodModifier, "DefaultMethodModifier", "AllowedMethodModifiers"))
#    cog.outl(CogCreateFlagsTable())
#
# ]]]

# ----------------------------------------------------------------------------------------  // Generated by Cog
# |                                                                                      |  // Generated by Cog
# |  These comments have been auto-generated by Cog. To update this documentation, run:  |  // Generated by Cog
# |                                                                                      |  // Generated by Cog
# |      cog -r -c -s "  // Generated by Cog" ClassStatementParserInfo.py                |  // Generated by Cog
# |                                                                                      |  // Generated by Cog
# ----------------------------------------------------------------------------------------  // Generated by Cog


# region All Info  // Generated by Cog
# ===================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================  // Generated by Cog
# ||                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               ||  // Generated by Cog
# ||                                                                                                                                                                                                                                           All Info                                                                                                                                                                                                                                            ||  // Generated by Cog
# ||                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               ||  // Generated by Cog
# ===================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================  // Generated by Cog
# |           |        Class Visibility        |       Member Visibility        |                   Allowed Bases                   |        Base Visibility         |                Allowed Implements                 |     Implements Visibility      |                   Allowed Uses                    |        Uses Visibility         |    Class Modifier     |                       Method Modifier                       | AllowDataMembers | AllowMutablePublicDataMembers |           |  // Generated by Cog
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------  // Generated by Cog
# | Class     | private*  protected   public   | private*  protected   public   | Class  -       -         -       -     -      -   | private*  protected   public   |   -    -       -     Interface   -     -    Trait | private   protected   public*  |   -    -       -         -     Mixin   -      -   | private*  protected   public   | immutable*  mutable   | abstract   final   override   standard*  static   virtual   |        Y         |               -               |     Class |  // Generated by Cog
# | Enum      | private*  protected   public   | private*  protected   public   |   -    -       -         -       -     -      -   |    -          -         -      |   -    -       -     Interface   -     -    Trait |    -          -       public*  |   -    -       -         -       -     -      -   |    -          -         -      | immutable*     -      | abstract   final   override   standard*  static   virtual   |        -         |               -               |      Enum |  // Generated by Cog
# | Exception |    -          -       public*  |    -          -       public*  |   -    -   Exception     -       -     -      -   |    -          -       public*  |   -    -       -     Interface   -     -    Trait |    -          -       public*  |   -    -       -         -     Mixin   -      -   |    -          -       public*  | immutable*     -      | abstract   final   override   standard*  static   virtual   |        Y         |               -               | Exception |  // Generated by Cog
# | Interface | private*  protected   public   | private*  protected   public   |   -    -       -         -       -     -      -   |    -          -         -      |   -    -       -     Interface   -     -    Trait |    -          -       public*  |   -    -       -         -       -     -      -   |    -          -         -      | immutable*  mutable   | abstract*    -     override      -         -      virtual   |        -         |               -               | Interface |  // Generated by Cog
# | Mixin     | private*  protected   public   | private*  protected   public   | Class  -       -         -       -     -      -   | private*  protected   public   |   -    -       -     Interface   -     -    Trait | private   protected   public*  |   -    -       -         -     Mixin   -      -   | private*  protected   public   | immutable*  mutable   | abstract   final   override   standard*  static   virtual   |        Y         |               -               |     Mixin |  // Generated by Cog
# | Struct    | private   protected   public*  | private   protected   public*  |   -    -       -         -       -   Struct   -   |    -          -       public*  |   -    -       -         -       -     -      -   |    -          -         -      |   -    -       -         -       -   Struct   -   |    -          -       public*  | immutable   mutable*  | abstract   final   override   standard*  static   virtual   |        Y         |               Y               |    Struct |  // Generated by Cog
# | Trait     | private*  protected   public   | private*  protected   public   |   -    -       -         -       -     -      -   |    -          -         -      |   -    -       -     Interface   -     -    Trait |    -          -       public*  |   -    -       -         -       -     -      -   |    -          -         -      | immutable*  mutable   | abstract*    -     override      -         -      virtual   |        -         |               -               |     Trait |  // Generated by Cog
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------  // Generated by Cog
# endregion (All Info)  // Generated by Cog


# region Class Visibility  // Generated by Cog
#            ==========================================================  // Generated by Cog
#            ||                                                      ||  // Generated by Cog
#            ||                   Class Visibility                   ||  // Generated by Cog
#            ||                                                      ||  // Generated by Cog
#            ==========================================================  // Generated by Cog
#            |           | private  | protected  | public |           |  // Generated by Cog
#            ----------------------------------------------------------  // Generated by Cog
#            | Class     |   Yes*   |    Yes     |  Yes   |     Class |  // Generated by Cog
#            | Enum      |   Yes*   |    Yes     |  Yes   |      Enum |  // Generated by Cog
#            | Exception |    -     |     -      |  Yes*  | Exception |  // Generated by Cog
#            | Interface |   Yes*   |    Yes     |  Yes   | Interface |  // Generated by Cog
#            | Mixin     |   Yes*   |    Yes     |  Yes   |     Mixin |  // Generated by Cog
#            | Struct    |   Yes    |    Yes     |  Yes*  |    Struct |  // Generated by Cog
#            | Trait     |   Yes*   |    Yes     |  Yes   |     Trait |  // Generated by Cog
#            ----------------------------------------------------------  // Generated by Cog
# endregion (Class Visibility)  // Generated by Cog


# region Member Visibility  // Generated by Cog
#            ==========================================================  // Generated by Cog
#            ||                                                      ||  // Generated by Cog
#            ||                  Member Visibility                   ||  // Generated by Cog
#            ||                                                      ||  // Generated by Cog
#            ==========================================================  // Generated by Cog
#            |           | private  | protected  | public |           |  // Generated by Cog
#            ----------------------------------------------------------  // Generated by Cog
#            | Class     |   Yes*   |    Yes     |  Yes   |     Class |  // Generated by Cog
#            | Enum      |   Yes*   |    Yes     |  Yes   |      Enum |  // Generated by Cog
#            | Exception |    -     |     -      |  Yes*  | Exception |  // Generated by Cog
#            | Interface |   Yes*   |    Yes     |  Yes   | Interface |  // Generated by Cog
#            | Mixin     |   Yes*   |    Yes     |  Yes   |     Mixin |  // Generated by Cog
#            | Struct    |   Yes    |    Yes     |  Yes*  |    Struct |  // Generated by Cog
#            | Trait     |   Yes*   |    Yes     |  Yes   |     Trait |  // Generated by Cog
#            ----------------------------------------------------------  // Generated by Cog
# endregion (Member Visibility)  // Generated by Cog


# region Allowed Bases  // Generated by Cog
# ==============================================================================================  // Generated by Cog
# ||                                                                                          ||  // Generated by Cog
# ||                                      Allowed Bases                                       ||  // Generated by Cog
# ||                                                                                          ||  // Generated by Cog
# ==============================================================================================  // Generated by Cog
# |           | Class  | Enum | Exception  | Interface  | Mixin  | Struct | Trait  |           |  // Generated by Cog
# ----------------------------------------------------------------------------------------------  // Generated by Cog
# | Class     |  Yes   |  -   |     -      |     -      |   -    |   -    |   -    |     Class |  // Generated by Cog
# | Enum      |   -    |  -   |     -      |     -      |   -    |   -    |   -    |      Enum |  // Generated by Cog
# | Exception |   -    |  -   |    Yes     |     -      |   -    |   -    |   -    | Exception |  // Generated by Cog
# | Interface |   -    |  -   |     -      |     -      |   -    |   -    |   -    | Interface |  // Generated by Cog
# | Mixin     |  Yes   |  -   |     -      |     -      |   -    |   -    |   -    |     Mixin |  // Generated by Cog
# | Struct    |   -    |  -   |     -      |     -      |   -    |  Yes   |   -    |    Struct |  // Generated by Cog
# | Trait     |   -    |  -   |     -      |     -      |   -    |   -    |   -    |     Trait |  // Generated by Cog
# ----------------------------------------------------------------------------------------------  // Generated by Cog
# endregion (Allowed Bases)  // Generated by Cog


# region Base Visibility  // Generated by Cog
#            ==========================================================  // Generated by Cog
#            ||                                                      ||  // Generated by Cog
#            ||                   Base Visibility                    ||  // Generated by Cog
#            ||                                                      ||  // Generated by Cog
#            ==========================================================  // Generated by Cog
#            |           | private  | protected  | public |           |  // Generated by Cog
#            ----------------------------------------------------------  // Generated by Cog
#            | Class     |   Yes*   |    Yes     |  Yes   |     Class |  // Generated by Cog
#            | Enum      |    -     |     -      |   -    |      Enum |  // Generated by Cog
#            | Exception |    -     |     -      |  Yes*  | Exception |  // Generated by Cog
#            | Interface |    -     |     -      |   -    | Interface |  // Generated by Cog
#            | Mixin     |   Yes*   |    Yes     |  Yes   |     Mixin |  // Generated by Cog
#            | Struct    |    -     |     -      |  Yes*  |    Struct |  // Generated by Cog
#            | Trait     |    -     |     -      |   -    |     Trait |  // Generated by Cog
#            ----------------------------------------------------------  // Generated by Cog
# endregion (Base Visibility)  // Generated by Cog


# region Allowed Implements  // Generated by Cog
# ==============================================================================================  // Generated by Cog
# ||                                                                                          ||  // Generated by Cog
# ||                                    Allowed Implements                                    ||  // Generated by Cog
# ||                                                                                          ||  // Generated by Cog
# ==============================================================================================  // Generated by Cog
# |           | Class  | Enum | Exception  | Interface  | Mixin  | Struct | Trait  |           |  // Generated by Cog
# ----------------------------------------------------------------------------------------------  // Generated by Cog
# | Class     |   -    |  -   |     -      |    Yes     |   -    |   -    |  Yes   |     Class |  // Generated by Cog
# | Enum      |   -    |  -   |     -      |    Yes     |   -    |   -    |  Yes   |      Enum |  // Generated by Cog
# | Exception |   -    |  -   |     -      |    Yes     |   -    |   -    |  Yes   | Exception |  // Generated by Cog
# | Interface |   -    |  -   |     -      |    Yes     |   -    |   -    |  Yes   | Interface |  // Generated by Cog
# | Mixin     |   -    |  -   |     -      |    Yes     |   -    |   -    |  Yes   |     Mixin |  // Generated by Cog
# | Struct    |   -    |  -   |     -      |     -      |   -    |   -    |   -    |    Struct |  // Generated by Cog
# | Trait     |   -    |  -   |     -      |    Yes     |   -    |   -    |  Yes   |     Trait |  // Generated by Cog
# ----------------------------------------------------------------------------------------------  // Generated by Cog
# endregion (Allowed Implements)  // Generated by Cog


# region Implements Visibility  // Generated by Cog
#            ==========================================================  // Generated by Cog
#            ||                                                      ||  // Generated by Cog
#            ||                Implements Visibility                 ||  // Generated by Cog
#            ||                                                      ||  // Generated by Cog
#            ==========================================================  // Generated by Cog
#            |           | private  | protected  | public |           |  // Generated by Cog
#            ----------------------------------------------------------  // Generated by Cog
#            | Class     |   Yes    |    Yes     |  Yes*  |     Class |  // Generated by Cog
#            | Enum      |    -     |     -      |  Yes*  |      Enum |  // Generated by Cog
#            | Exception |    -     |     -      |  Yes*  | Exception |  // Generated by Cog
#            | Interface |    -     |     -      |  Yes*  | Interface |  // Generated by Cog
#            | Mixin     |   Yes    |    Yes     |  Yes*  |     Mixin |  // Generated by Cog
#            | Struct    |    -     |     -      |   -    |    Struct |  // Generated by Cog
#            | Trait     |    -     |     -      |  Yes*  |     Trait |  // Generated by Cog
#            ----------------------------------------------------------  // Generated by Cog
# endregion (Implements Visibility)  // Generated by Cog


# region Allowed Uses  // Generated by Cog
# ==============================================================================================  // Generated by Cog
# ||                                                                                          ||  // Generated by Cog
# ||                                       Allowed Uses                                       ||  // Generated by Cog
# ||                                                                                          ||  // Generated by Cog
# ==============================================================================================  // Generated by Cog
# |           | Class  | Enum | Exception  | Interface  | Mixin  | Struct | Trait  |           |  // Generated by Cog
# ----------------------------------------------------------------------------------------------  // Generated by Cog
# | Class     |   -    |  -   |     -      |     -      |  Yes   |   -    |   -    |     Class |  // Generated by Cog
# | Enum      |   -    |  -   |     -      |     -      |   -    |   -    |   -    |      Enum |  // Generated by Cog
# | Exception |   -    |  -   |     -      |     -      |  Yes   |   -    |   -    | Exception |  // Generated by Cog
# | Interface |   -    |  -   |     -      |     -      |   -    |   -    |   -    | Interface |  // Generated by Cog
# | Mixin     |   -    |  -   |     -      |     -      |  Yes   |   -    |   -    |     Mixin |  // Generated by Cog
# | Struct    |   -    |  -   |     -      |     -      |   -    |  Yes   |   -    |    Struct |  // Generated by Cog
# | Trait     |   -    |  -   |     -      |     -      |   -    |   -    |   -    |     Trait |  // Generated by Cog
# ----------------------------------------------------------------------------------------------  // Generated by Cog
# endregion (Allowed Uses)  // Generated by Cog


# region Uses Visibility  // Generated by Cog
#            ==========================================================  // Generated by Cog
#            ||                                                      ||  // Generated by Cog
#            ||                   Uses Visibility                    ||  // Generated by Cog
#            ||                                                      ||  // Generated by Cog
#            ==========================================================  // Generated by Cog
#            |           | private  | protected  | public |           |  // Generated by Cog
#            ----------------------------------------------------------  // Generated by Cog
#            | Class     |   Yes*   |    Yes     |  Yes   |     Class |  // Generated by Cog
#            | Enum      |    -     |     -      |   -    |      Enum |  // Generated by Cog
#            | Exception |    -     |     -      |  Yes*  | Exception |  // Generated by Cog
#            | Interface |    -     |     -      |   -    | Interface |  // Generated by Cog
#            | Mixin     |   Yes*   |    Yes     |  Yes   |     Mixin |  // Generated by Cog
#            | Struct    |    -     |     -      |  Yes*  |    Struct |  // Generated by Cog
#            | Trait     |    -     |     -      |   -    |     Trait |  // Generated by Cog
#            ----------------------------------------------------------  // Generated by Cog
# endregion (Uses Visibility)  // Generated by Cog


# region Class Modifier  // Generated by Cog
#                =================================================  // Generated by Cog
#                ||                                             ||  // Generated by Cog
#                ||               Class Modifier                ||  // Generated by Cog
#                ||                                             ||  // Generated by Cog
#                =================================================  // Generated by Cog
#                |           | immutable  | mutable  |           |  // Generated by Cog
#                -------------------------------------------------  // Generated by Cog
#                | Class     |    Yes*    |   Yes    |     Class |  // Generated by Cog
#                | Enum      |    Yes*    |    -     |      Enum |  // Generated by Cog
#                | Exception |    Yes*    |    -     | Exception |  // Generated by Cog
#                | Interface |    Yes*    |   Yes    | Interface |  // Generated by Cog
#                | Mixin     |    Yes*    |   Yes    |     Mixin |  // Generated by Cog
#                | Struct    |    Yes     |   Yes*   |    Struct |  // Generated by Cog
#                | Trait     |    Yes*    |   Yes    |     Trait |  // Generated by Cog
#                -------------------------------------------------  // Generated by Cog
# endregion (Class Modifier)  // Generated by Cog


# region Method Modifier  // Generated by Cog
# =======================================================================================  // Generated by Cog
# ||                                                                                   ||  // Generated by Cog
# ||                                  Method Modifier                                  ||  // Generated by Cog
# ||                                                                                   ||  // Generated by Cog
# =======================================================================================  // Generated by Cog
# |           | abstract | final  | override | standard | static | virtual  |           |  // Generated by Cog
# ---------------------------------------------------------------------------------------  // Generated by Cog
# | Class     |   Yes    |  Yes   |   Yes    |   Yes*   |  Yes   |   Yes    |     Class |  // Generated by Cog
# | Enum      |   Yes    |  Yes   |   Yes    |   Yes*   |  Yes   |   Yes    |      Enum |  // Generated by Cog
# | Exception |   Yes    |  Yes   |   Yes    |   Yes*   |  Yes   |   Yes    | Exception |  // Generated by Cog
# | Interface |   Yes*   |   -    |   Yes    |    -     |   -    |   Yes    | Interface |  // Generated by Cog
# | Mixin     |   Yes    |  Yes   |   Yes    |   Yes*   |  Yes   |   Yes    |     Mixin |  // Generated by Cog
# | Struct    |   Yes    |  Yes   |   Yes    |   Yes*   |  Yes   |   Yes    |    Struct |  // Generated by Cog
# | Trait     |   Yes*   |   -    |   Yes    |    -     |   -    |   Yes    |     Trait |  // Generated by Cog
# ---------------------------------------------------------------------------------------  // Generated by Cog
# endregion (Method Modifier)  // Generated by Cog


# region Flags  // Generated by Cog
#   ============================================================================  // Generated by Cog
#   ||                                                                        ||  // Generated by Cog
#   ||                                 Flags                                  ||  // Generated by Cog
#   ||                                                                        ||  // Generated by Cog
#   ============================================================================  // Generated by Cog
#   |           | AllowDataMembers | AllowMutablePublicDataMembers |           |  // Generated by Cog
#   | Class     |        Y         |               -               |     Class |  // Generated by Cog
#   | Enum      |        -         |               -               |      Enum |  // Generated by Cog
#   | Exception |        Y         |               -               | Exception |  // Generated by Cog
#   | Interface |        -         |               -               | Interface |  // Generated by Cog
#   | Mixin     |        Y         |               -               |     Mixin |  // Generated by Cog
#   | Struct    |        Y         |               Y               |    Struct |  // Generated by Cog
#   | Trait     |        -         |               -               |     Trait |  // Generated by Cog
#   ----------------------------------------------------------------------------  // Generated by Cog
# endregion (Flags)  // Generated by Cog

# [[[end]]] (checksum: fcbdaa8d7418a6bc6186d57bccd4654d)
