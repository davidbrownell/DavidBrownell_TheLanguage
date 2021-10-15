# ----------------------------------------------------------------------
# |
# |  ClassMemberStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 14:43:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains utilities used with class member statements"""

import os

from typing import Optional

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
    from ..Common.VisibilityModifier import VisibilityModifier

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
    class_modifier: InitVar[Optional[ClassModifierType]]

    Visibility: VisibilityModifier          = field(init=False)
    ClassModifier: ClassModifierType        = field(init=False)

    Type: TypeParserInfo
    Name: str

    InitializedValue: Optional[ExpressionParserInfo]

    # TODO: Flags for init, serialization, compare, etc.

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, class_parser_info, visibility, class_modifier):
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

        # ClassModifier
        if class_modifier is None:
            class_modifier = class_parser_info.TypeInfo.DefaultClassModifier
            object.__setattr__(self.Regions__, "ClassModifier", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

        class_parser_info.ValidateMemberClassModifier(class_modifier, self.Regions__.ClassModifier)  # type: ignore && pylint: disable=no-member
        object.__setattr__(self, "ClassModifier", class_modifier)

        if (
            visibility == VisibilityModifier.public
            and class_modifier == ClassModifierType.mutable
            and not class_parser_info.TypeInfo.AllowMutablePublicDataMembers
        ):
            raise PublicMutableDataMembersNotSupportedError(self.Regions__.ClassModifier, class_parser_info.ClassType.value)  # type: ignore && pylint: disable=no-member

        self.Validate()
