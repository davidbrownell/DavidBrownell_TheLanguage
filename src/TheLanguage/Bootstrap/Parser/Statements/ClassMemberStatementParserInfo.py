import os

from typing import List, Optional

from dataclasses import dataclass, InitVar, field

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ClassStatementParserInfo import ClassStatementParserInfo
    from .StatementParserInfo import StatementParserInfo

    from ..Common.ClassModifier import ClassModifier as ClassModifierType
    from ..Common.ConstraintArgumentParserInfo import ConstraintArgumentParserInfo
    from ..Common.TemplateArgumentParserInfo import TemplateArgumentParserInfo
    from ..Common.TypeModifier import TypeModifier
    from ..Common.VisibilityModifier import VisibilityModifier
    from ..Common.VisitorTools import StackHelper

    from ..Error import Error

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Types.TypeParserInfo import TypeParserInfo

    # Convenience Imports
    from .ClassStatementParserInfo import (
        InvalidMemberClassModifierError,
        InvalidMemberMutableModifierError,
        InvalidMemberVisibilityError,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassMemberError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Data member statements must be enclosed within a class-like object.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DataMembersNotSupportedError(Error):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Data members are not supported for '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class EmptyTypeModifierError(Error):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Type modifiers must be provided for members of '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PublicMutableDataMembersNotSupportedError(Error):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Public mutable data members are not supported for '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassMemberStatementParserInfo(StatementParserInfo):
    class_parser_info: InitVar[Optional[ClassStatementParserInfo]]

    visibility: InitVar[Optional[VisibilityModifier]]

    Visibility: VisibilityModifier          = field(init=False)

    Type: TypeParserInfo
    Name: str

    InitializedValue: Optional[ExpressionParserInfo]

    NoInit: Optional[bool]
    NoSerialize: Optional[bool]
    NoCompare: Optional[bool]

    # TODO: Likely more flags

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, class_parser_info, visibility):
        super(ClassMemberStatementParserInfo, self).__post_init__(
            regions,
            should_validate=False,
        )

        if class_parser_info is None:
            raise InvalidClassMemberError(self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

        if not class_parser_info.TypeInfo.AllowDataMembers:
            raise DataMembersNotSupportedError(self.Regions__.Self__, class_parser_info.ClassType.value)  # type: ignore && pylint: disable=no-member

        # Visibility
        if visibility is None:
            visibility = class_parser_info.TypeInfo.DefaultMemberVisibility
            object.__setattr__(self.Regions__, "Visibility", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

        class_parser_info.ValidateMemberVisibility(visibility, self.Regions__.Visibility)  # type: ignore && pylint: disable=no-member
        object.__setattr__(self, "Visibility", visibility)

        # Type modifier
        type_modifier = self.Type.GetTypeModifier()
        if type_modifier is None:
            raise EmptyTypeModifierError(self.Regions__.Type, class_parser_info.ClassType.value)  # type: ignore && pylint: disable=no-member

        type_modifier, type_modifier_region = type_modifier

        class_parser_info.ValidateMemberModifier(type_modifier, type_modifier_region)

        if (
            visibility == VisibilityModifier.public
            and type_modifier & TypeModifier.mutable
            and not class_parser_info.TypeInfo.AllowMutablePublicDataMembers
        ):
            raise PublicMutableDataMembersNotSupportedError(type_modifier_region, class_parser_info.ClassType.value)  # type: ignore && pylint: disable=no-member

        # Flags
        assert self.NoInit is None or self.NoInit
        assert self.NoSerialize is None or self.NoSerialize
        assert self.NoCompare is None or self.NoCompare

        self.Validate()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            with helper["Type"]:
                self.Type.Accept(visitor, helper.stack, *args, **kwargs)

            if self.InitializedValue is not None:
                with helper["InitializedValue"]:
                    self.InitializedValue.Accept(visitor, helper.stack, *args, **kwargs)
