# ----------------------------------------------------------------------
# |
# |  FuncAndMethodDefinitionStatementLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-08 11:10:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncAndMethodDefinitionStatementLexerInfo object and exceptions"""

import os

from enum import auto, Enum
from typing import List, Optional, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ClassStatementLexerInfo import ClassStatementLexerInfo, MethodType
    from .StatementLexerInfo import StatementLexerInfo

    from ..Common.ClassModifier import ClassModifier as ClassModifierType
    from ..Common.ParametersLexerInfo import ParameterLexerInfo
    from ..Common.VisibilityModifier import VisibilityModifier
    from ..Types.TypeLexerInfo import TypeLexerInfo

    from ..LexerError import LexerError


# ----------------------------------------------------------------------
class OperatorType(Enum):
    """\
    Note that operators are defined as '__<enum_name>__' such as '__ToBool__',
    '__Compare__", and "__Add__".
    """

    # TODO: I don't think that these are complete

    # Foundational
    ToBool                                  = auto()
    ToString                                = auto()
    Repr                                    = auto()
    Clone                                   = auto()
    Serialize                               = auto()

    Init                                    = auto()
    PostInit                                = auto()

    # Dynamic
    GetAttribute                            = auto()
    Call                                    = auto()
    Cast                                    = auto()
    Index                                   = auto()

    # Container
    Contains                                = auto()
    Length                                  = auto()
    Iter                                    = auto()
    AtEnd                                   = auto()

    # Comparison
    Compare                                 = auto()
    Equal                                   = auto()
    NotEqual                                = auto()
    Less                                    = auto()
    LessEqual                               = auto()
    Greater                                 = auto()
    GreaterEqual                            = auto()

    # Logical
    And                                     = auto()
    Or                                      = auto()
    Not                                     = auto()

    # Mathematical
    Add                                     = auto()
    Subtract                                = auto()
    Multiply                                = auto()
    Divide                                  = auto()
    DivideFloor                             = auto()
    Power                                   = auto()
    Mod                                     = auto()
    Positive                                = auto()
    Negative                                = auto()

    AddInplace                              = auto()
    SubtractInplace                         = auto()
    MultiplyInplace                         = auto()
    DivideInplace                           = auto()
    DivideFloorInplace                      = auto()
    PowerInplace                            = auto()
    ModInplace                              = auto()

    # Bit Manipulation
    ShiftLeft                               = auto()
    ShiftRight                              = auto()
    BitAnd                                  = auto()
    BitOr                                   = auto()
    BitXor                                  = auto()
    BitFlip                                 = auto()

    ShiftLeftInplace                        = auto()
    ShiftRightInplace                       = auto()
    BitAndInplace                           = auto()
    BitOrInplace                            = auto()
    BitXorInplace                           = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidFunctionMethodTypeError(LexerError):
    MethodType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{MethodType}' is not supported for functions.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidFunctionClassModifierError(LexerError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Class modifiers are not supported for functions.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FunctionStatementsRequiredError(LexerError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Functions must have statements.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MethodStatementsRequiredError(LexerError):
    MethodType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Statements are required for '{MethodType}' methods.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MethodStatementsUnexpectedError(LexerError):
    MethodType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Statements are not expected for '{MethodType}' methods.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMethodTypeError(LexerError):
    ClassType: str
    MethodType: str
    AllowedMethodTypes: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{MethodType}' is not a supported method type modifier for members of '{ClassType}' types; supported values are {AllowedMethodTypes}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassModifierOnStaticError(LexerError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Class modifiers are not supported for 'static' methods.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncAndMethodDefinitionStatementLexerInfo(StatementLexerInfo):
    class_lexer_info: InitVar[Optional[ClassStatementLexerInfo]]

    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier                      = field(init=False)

    method_type: InitVar[Optional[MethodType]]
    MethodType: MethodType                              = field(init=False)

    ReturnType: TypeLexerInfo
    Name: Union[str, OperatorType]
    Parameters: Optional[ParameterLexerInfo] # TODO: Update this

    class_modifier: InitVar[Optional[ClassModifierType]]
    ClassModifier: Optional[ClassModifierType]          = field(init=False)

    Statements: Optional[List[StatementLexerInfo]]

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        regions,
        class_lexer_info: ClassStatementLexerInfo,
        visibility: Optional[VisibilityModifier],
        method_type, # : Optional[MethodType],
        class_modifier: Optional[ClassModifierType],
    ):
        super(FuncAndMethodDefinitionStatementLexerInfo, self).__post_init__(
            regions,
            should_validate=False,
        )

        # Set the default values as necessary
        if class_lexer_info is None:
            # Set defaults for a function

            # Visibility
            if visibility is None:
                visibility = VisibilityModifier.private
                object.__setattr__(self.Regions, "Visibility", self.Regions.Self__)  # pylint: disable=no-member

            object.__setattr__(self, "Visibility", visibility)

            # MethodType
            if method_type is None:
                method_type = MethodType.standard
                object.__setattr__(self.Regions, "MethodType", self.Regions.Self__)  # pylint: disable=no-member
            elif method_type != MethodType.standard:
                raise InvalidFunctionMethodTypeError(self.Regions.MethodType, method_type.name)  # pylint: disable=no-member

            object.__setattr__(self, "MethodType", method_type)

            # ClassModifier
            if class_modifier is not None:
                raise InvalidFunctionClassModifierError(self.Regions.ClassModifier)  # pylint: disable=no-member

            object.__setattr__(self, "ClassModifier", class_modifier)

            # Statements
            if not self.Statements:
                raise FunctionStatementsRequiredError(self.Regions.Self__)  # pylint: disable=no-member

        else:
            # Set defaults based on the class type

            # Visibility
            if visibility is None:
                visibility = class_lexer_info.TypeInfo.DefaultMemberVisibility
                object.__setattr__(self.Regions, "Visibility", self.Regions.Self__)  # pylint: disable=no-member

            class_lexer_info.ValidateMemberVisibility(visibility, self.Regions.Visibility)  # pylint: disable=no-member
            object.__setattr__(self, "Visibility", visibility)

            # MethodType
            if method_type is None:
                method_type = class_lexer_info.TypeInfo.DefaultMethodType
                object.__setattr__(self.Regions, "MethodType", self.Regions.Self__)  # pylint: disable=no-member

            if method_type not in class_lexer_info.TypeInfo.AllowedMethodTypes:
                raise InvalidMethodTypeError(
                    self.Regions.MethodType,  # pylint: disable=no-member
                    class_lexer_info.ClassType.value,
                    method_type.name,
                    ", ".join(["'{}'".format(m.name) for m in class_lexer_info.TypeInfo.AllowedMethodTypes]),
                )

            object.__setattr__(self, "MethodType", method_type)

            # ClassModifier
            if method_type == MethodType.static:
                if class_modifier is not None:
                    raise InvalidClassModifierOnStaticError(self.Regions.ClassModifier)  # pylint: disable=no-member
            else:
                if class_modifier is None:
                    class_modifier = class_lexer_info.TypeInfo.DefaultClassModifier
                    object.__setattr__(self.Regions, "ClassModifier", self.Regions.Self__)  # pylint: disable=no-member

                class_lexer_info.ValidateMemberClassModifier(class_modifier, self.Regions.ClassModifier)  # pylint: disable=no-member

            object.__setattr__(self, "ClassModifier", class_modifier)

            # Statements
            if self.Statements and method_type in [MethodType.deferred, MethodType.abstract]:
                raise MethodStatementsUnexpectedError(self.Regions.Self__, method_type.name)  # pylint: disable=no-member

            if (
                self.Statements is None
                and method_type not in [MethodType.deferred, MethodType.abstract]
            ):
                raise MethodStatementsRequiredError(self.Regions.Self__, method_type.name)  # pylint: disable=no-member

        self.Validate()
