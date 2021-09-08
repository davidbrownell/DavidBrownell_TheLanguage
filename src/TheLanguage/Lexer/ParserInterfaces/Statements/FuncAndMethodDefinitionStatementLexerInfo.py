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
from typing import Any, List, Optional, Union

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

    from ..Common.ClassModifier import ClassModifier as ClassModifierType
    from ..Common.VisibilityModifier import VisibilityModifier

    from ...LexerInfo import Error, LexerInfo


# ----------------------------------------------------------------------
class OperatorType(Enum):
    """\
    Note that operators are defined as '__<enum_name>__' such as '__ToBool__',
    '__Compare__", and "__Add__".
    """

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
class InvalidFunctionMethodTypeError(Error):
    MethodType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{MethodType}' is not supported on functions.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidFunctionClassModifierError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Class modifiers are not supported on functions.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FunctionStatementsRequiredError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Functions must have statements.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MethodStatementsRequiredError(Error):
    MethodType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Statements are required for '{MethodType}' methods.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MethodStatementsUnexpectedError(Error):
    MethodType: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Statements are not expected for '{MethodType}' methods.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMethodTypeError(Error):
    ClassType: str
    MethodType: str
    AllowedMethodTypes: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{MethodType}' is not a supported method type modifier for members of '{ClassType}' types; supported values are {AllowedMethodTypes}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassModifierOnStaticError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Class modifiers are not supported on 'static' methods.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncAndMethodDefinitionStatementLexerInfo(LexerInfo):
    class_lexer_info: InitVar[Optional[ClassStatementLexerInfo]]

    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier          = field(init=False)

    method_type: InitVar[Optional[MethodType]]
    MethodType: MethodType          = field(init=False)

    Type: Any # TODO: TypeLexerInfo
    Name: Union[str, OperatorType]

    Parameters: List[Any] # TODO: ExprLexerInfo

    class_modifier: InitVar[Optional[ClassModifierType]]
    ClassModifier: Optional[ClassModifierType]          = field(init=False)

    has_statements: InitVar[bool]

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        class_lexer_info,
        visibility,
        method_type,
        class_modifier,
        has_statements,
    ):
        self.ValidateTokenLookup(
            fields_to_skip=set(["Visibility", "MethodType", "ClassModifier", "IsFunction"]),
        )

        # Set default values and validate as necessary
        if class_lexer_info is None:
            # We are looking at a function
            if visibility is None:
                visibility = VisibilityModifier.private
                self.TokenLookup["Visibility"] = self.TokenLookup["self"]

            if method_type is None:
                method_type = MethodType.standard
                self.TokenLookup["MethodType"] = self.TokenLookup["self"]
            elif method_type != MethodType.standard:
                raise InvalidFunctionMethodTypeError.FromNode(
                    self.TokenLookup["MethodType"],
                    method_type.name,
                )

            if class_modifier is not None:
                raise InvalidFunctionClassModifierError.FromNode(
                    self.TokenLookup["ClassModifier"],
                )

            if not has_statements:
                raise FunctionStatementsRequiredError.FromNode(
                    self.TokenLookup["self"],
                )

        else:
            # We are looking at a method
            if visibility is None:
                visibility = class_lexer_info.TypeInfo.DefaultMemberVisibility
                self.TokenLookup["Visibility"] = self.TokenLookup["self"]

            class_lexer_info.ValidateMemberVisibility(visibility, self.TokenLookup)

            if method_type is None:
                method_type = class_lexer_info.TypeInfo.DefaultMethodType
                self.TokenLookup["MethodType"] = self.TokenLookup["self"]

            if method_type not in class_lexer_info.TypeInfo.AllowedMethodTypes:
                raise InvalidMethodTypeError.FromNode(
                    self.TokenLookup["MethodType"],
                    class_lexer_info.ClassType.value,
                    method_type.name,
                    ", ".join(["'{}'".format(m.name) for m in class_lexer_info.TypeInfo.AllowedMethodTypes]),
                )

            if method_type == MethodType.static:
                if class_modifier is not None:
                    raise InvalidClassModifierOnStaticError.FromNode(
                        self.TokenLookup["ClassModifier"],
                    )
            else:
                if class_modifier is None:
                    class_modifier = class_lexer_info.TypeInfo.DefaultClassModifier
                    self.TokenLookup["ClassModifier"] = self.TokenLookup["self"]

                class_lexer_info.ValidateMemberClassModifier(class_modifier, self.TokenLookup)

            if (
                has_statements
                and method_type in [MethodType.deferred, MethodType.abstract]
            ):
                raise MethodStatementsUnexpectedError.FromNode(
                    self.TokenLookup["self"],
                    method_type.name,
                )

            if (
                not has_statements
                and method_type not in [MethodType.deferred, MethodType.abstract]
            ):
                raise MethodStatementsRequiredError.FromNode(
                    self.TokenLookup["self"],
                    method_type.name,
                )

        # Set the values
        object.__setattr__(self, "Visibility", visibility)
        object.__setattr__(self, "MethodType", method_type)
        object.__setattr__(self, "ClassModifier", class_modifier)

        super(FuncAndMethodDefinitionStatementLexerInfo, self).__post_init__()
