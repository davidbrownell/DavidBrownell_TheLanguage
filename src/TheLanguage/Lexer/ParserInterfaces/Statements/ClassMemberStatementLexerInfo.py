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

    from ..Common.ClassModifier import ClassModifier
    from ..Common.VisibilityModifier import VisibilityModifier

    from ...LexerInfo import Error, LexerInfo


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
class ClassMemberStatementLexerInfo(LexerInfo):
    class_lexer_info: InitVar[Optional[ClassStatementLexerInfo]]

    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier          = field(init=False)

    Type: Any # TODO: TypeLexerInfo
    Name: str

    class_modifier: InitVar[Optional[ClassModifier]]
    ClassModifier: ClassModifier            = field(init=False)

    DefaultValue: Optional[Any] # TODO: ExprLexerInfo

    # ----------------------------------------------------------------------
    def __post_init__(self, class_lexer_info, visibility, class_modifier):
        self.ValidateTokenLookup(
            fields_to_skip=set(["Visibility", "ClassModifier"]),
        )

        if class_lexer_info is None:
            raise InvalidClassMemberError.FromNode(
                self.TokenLookup["self"],
            )

        # Set default values and validate as necessary
        if not class_lexer_info.TypeInfo.AllowDataMembers:
            raise DataMembersNotSupportedError.FromNode(
                self.TokenLookup["self"],
                class_lexer_info.ClassType.value,
            )

        if visibility is None:
            visibility = class_lexer_info.TypeInfo.DefaultMemberVisibility
            self.TokenLookup["Visibility"] = self.TokenLookup["self"]

        class_lexer_info.ValidateMemberVisibility(visibility, self.TokenLookup)

        if class_modifier is None:
            class_modifier = class_lexer_info.TypeInfo.DefaultClassModifier
            self.TokenLookup["ClassModifier"] = self.TokenLookup["self"]

        class_lexer_info.ValidateMemberClassModifier(class_modifier, self.TokenLookup)

        if (
            visibility == VisibilityModifier.public
            and class_modifier == ClassModifier.mutable
            and not class_lexer_info.TypeInfo.AllowMutablePublicDataMembers
        ):
            raise PublicMutableDataMembersNotSupportedError.FromNode(
                self.TokenLookup["Visibility"],
                class_lexer_info.ClassType.value,
            )

        # Set the values
        object.__setattr__(self, "Visibility", visibility)
        object.__setattr__(self, "ClassModifier", class_modifier)

        super(ClassMemberStatementLexerInfo, self).__post_init__()
