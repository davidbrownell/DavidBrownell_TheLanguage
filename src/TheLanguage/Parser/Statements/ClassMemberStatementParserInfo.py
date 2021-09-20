# ----------------------------------------------------------------------
# |
# |  ClassMemberStatementParserInfo.py
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
"""Contains the ClassMemberStatementParserInfo object and exceptions"""

import os

from typing import Optional

from dataclasses import dataclass, field, InitVar

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

    from ..Common.ClassModifier import ClassModifier
    from ..Common.VisibilityModifier import VisibilityModifier
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Types.TypeParserInfo import TypeParserInfo

    from ..ParserError import ParserError


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassMemberError(ParserError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Data member statements must be enclosed within a class-like object.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DataMembersNotSupportedError(ParserError):
    ClassType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Data members are not supported for '{ClassType}' types.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassMemberStatementParserInfo(StatementParserInfo):
    class_lexer_info: InitVar[Optional[ClassStatementParserInfo]]

    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier          = field(init=False)

    Type: TypeParserInfo
    Name: str

    class_modifier: InitVar[Optional[ClassModifier]]
    ClassModifier: ClassModifier            = field(init=False)

    DefaultValue: Optional[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        regions,
        class_lexer_info: ClassStatementParserInfo,
        visibility: Optional[VisibilityModifier],
        class_modifier, # : Optional[ClassModifier],
    ):
        super(ClassMemberStatementParserInfo, self).__post_init__(
            regions,
            should_validate=False,
        )

        if class_lexer_info is None:
            raise InvalidClassMemberError(self.Regions.Self__)  # type: ignore && pylint: disable=no-member

        # Set the default values as necessary
        if not class_lexer_info.TypeInfo.AllowDataMembers:
            raise DataMembersNotSupportedError(self.Regions.Self__, class_lexer_info.ClassType.value)  # type: ignore && pylint: disable=no-member

        # Visibility
        if visibility is None:
            visibility = class_lexer_info.TypeInfo.DefaultMemberVisibility
            object.__setattr__(self.Regions, "Visibility", self.Regions.Self__)  # type: ignore && pylint: disable=no-member

        class_lexer_info.ValidateMemberVisibility(visibility, self.Regions.Visibility)  # type: ignore && pylint: disable=no-member
        object.__setattr__(self, "Visibility", visibility)

        # ClassModifier
        if class_modifier is None:
            class_modifier = class_lexer_info.TypeInfo.DefaultClassModifier
            object.__setattr__(self.Regions, "ClassModifier", self.Regions.Self__)  # type: ignore && pylint: disable=no-member

        class_lexer_info.ValidateMemberClassModifier(class_modifier, self.Regions.ClassModifier)  # type: ignore && pylint: disable=no-member
        object.__setattr__(self, "ClassModifier", class_modifier)

        # Final validation
        self.Validate()
