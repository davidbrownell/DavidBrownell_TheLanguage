# ----------------------------------------------------------------------
# |
# |  ClassMemberStatementLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-08 08:10:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassMemberStatementLexerInfo object and exceptions"""

import os

from typing import Any, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ClassStatementLexerInfo import ClassStatementLexerInfo
    from .StatementLexerInfo import StatementLexerData, StatementLexerInfo

    from ..Common.ClassModifier import ClassModifier
    from ..Common.VisibilityModifier import VisibilityModifier
    from ..Expressions.ExpressionLexerInfo import ExpressionLexerInfo
    from ..Types.TypeLexerInfo import TypeLexerInfo

    from ...LexerInfo import LexerRegions, Region
    from ...Components.LexerError import LexerError


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassMemberError(LexerError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Data member statements must be enclosed within a class-like object.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DataMembersNotSupportedError(LexerError):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Data members are not supported for '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PublicMutableDataMembersNotSupportedError(LexerError):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Public mutable data members are not supported for '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassMemberStatementLexerData(StatementLexerData):
    Visibility: VisibilityModifier
    Type: TypeLexerInfo
    Name: str
    ClassModifier: ClassModifier
    DefaultValue: Optional[ExpressionLexerInfo]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassMemberStatementLexerRegions(LexerRegions):
    Visibility: Region
    Type: Region
    Name: Region
    ClassModifier: Region
    DefaultValue: Optional[Region]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassMemberStatementLexerInfo(StatementLexerInfo):
    Data: ClassMemberStatementLexerData                 = field(init=False)
    Regions: ClassMemberStatementLexerRegions

    class_lexer_info: InitVar[Optional[ClassStatementLexerInfo]]

    visibility: InitVar[Optional[VisibilityModifier]]
    the_type: InitVar[TypeLexerInfo]
    name: InitVar[str]
    class_modifier: InitVar[Optional[ClassModifier]]
    default_value: InitVar[Optional[ExpressionLexerInfo]]

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        class_lexer_info,
        visibility,
        the_type,
        name,
        class_modifier,
        default_value,
    ):
        if class_lexer_info is None:
            raise InvalidClassMemberError(self.Regions.Self__)

        # Set default values and validate as necessary
        if not class_lexer_info.Data.TypeInfo.AllowDataMembers:
            raise DataMembersNotSupportedError(self.Regions.Self__, class_lexer_info.Classtype.value)

        if visibility is None:
            visibility = class_lexer_info.Data.TypeInfo.DefaultMemberVisibility
            object.__setattr__(self.Regions, "Visibility", self.Regions.Self__)

        class_lexer_info.Data.ValidateMemberVisibility(visibility, self.Regions.Visibility)

        if class_modifier is None:
            class_modifier = class_lexer_info.Data.TypeInfo.DefaultClassModifier
            object.__setattr__(self.Regions, "ClassModifier", self.Regions.Self__)

        class_lexer_info.Data.ValidateMemberClassModifier(class_modifier, self.Regions.ClassModifier)

        if (
            visibility == VisibilityModifier.public
            and class_modifier == ClassModifier.mutable
            and not class_lexer_info.Data.TypeInfo.AllowMutablePublicDataMembers
        ):
            raise PublicMutableDataMembersNotSupportedError(self.Regions.Visibility, class_lexer_info.ClassType.value)

        # Set the values
        object.__setattr__(
            self,
            "Data",
            # pylint: disable=too-many-function-args
            ClassMemberStatementLexerData(
                visibility,
                the_type,
                name,
                class_modifier,
                default_value,
            ),
        )

        super(ClassMemberStatementLexerInfo, self).__post_init__()
