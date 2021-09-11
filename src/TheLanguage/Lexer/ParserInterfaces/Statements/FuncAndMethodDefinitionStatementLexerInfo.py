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
    from .StatementLexerInfo import StatementLexerData, StatementLexerInfo

    from ..Common.ClassModifier import ClassModifier as ClassModifierType
    from ..Common.VisibilityModifier import VisibilityModifier
    from ..Expressions.ExpressionLexerInfo import ExpressionLexerInfo
    from ..Types.TypeLexerInfo import TypeLexerInfo

    from ...LexerError import LexerError
    from ...LexerInfo import LexerRegions, Region


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
class FuncAndMethodDefinitionStatementLexerData(StatementLexerData):
    Visibility: VisibilityModifier
    MethodType: MethodType
    ReturnType: TypeLexerInfo
    Name: Union[str, OperatorType]
    Parameters: List[Any]
    ClassModifier: Optional[ClassModifierType]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert isinstance(self.Name, OperatorType) or self.Name
        super(FuncAndMethodDefinitionStatementLexerData, self).__post_init__()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncAndMethodDefinitionStatementLexerRegions(LexerRegions):
    Visibility: Region
    MethodType: Region
    ReturnType: Region
    Name: Region
    Parameters: Region
    ClassModifier: Optional[Region]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncAndMethodDefinitionStatementLexerInfo(StatementLexerInfo):
    Data: FuncAndMethodDefinitionStatementLexerData     = field(init=False)
    Regions: FuncAndMethodDefinitionStatementLexerRegions

    class_lexer_info: InitVar[Optional[ClassStatementLexerInfo]]

    visibility: InitVar[Optional[VisibilityModifier]]
    method_type: InitVar[Optional[MethodType]]
    return_type: InitVar[TypeLexerInfo]
    name: InitVar[str]
    parameters: InitVar[ExpressionLexerInfo]
    class_modifier: InitVar[Optional[ClassModifierType]]
    has_statements: InitVar[bool]

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        class_lexer_info,
        visibility,
        method_type,
        return_type,
        name,
        parameters,
        class_modifier,
        has_statements,
    ):
        # Set default values and validate as necessary
        if class_lexer_info is None:
            # We are looking at a function
            if visibility is None:
                visibility = VisibilityModifier.private
                object.__setattr__(self.Regions, "Visibility", self.Regions.Self__)

            if method_type is None:
                method_type = MethodType.standard
                object.__setattr__(self.Regions, "MethodType", self.Regions.Self__)

            elif method_type != MethodType.standard:
                raise InvalidFunctionMethodTypeError(self.Regions.MethodType, method_type.name)

            if class_modifier is not None:
                assert self.Regions.ClassModifier is not None
                raise InvalidFunctionClassModifierError(self.Regions.ClassModifier)

            if not has_statements:
                raise FunctionStatementsRequiredError(self.Regions.Self__)

        else:
            # We are looking at a method
            if visibility is None:
                visibility = class_lexer_info.Data.TypeInfo.DefaultMemberVisibility
                object.__setattr__(self.Regions, "Visibility", self.Regions.Self__)

            class_lexer_info.Data.ValidateMemberVisibility(visibility, self.Regions.Visibility)

            if method_type is None:
                method_type = class_lexer_info.Data.TypeInfo.DefaultMethodType
                object.__setattr__(self.Regions, "MethodType", self.Regions.Self__)

            if method_type not in class_lexer_info.Data.TypeInfo.AllowedMethodTypes:
                raise InvalidMethodTypeError(
                    self.Regions.MethodType,
                    class_lexer_info.Data.ClassType.value,
                    method_type.name,
                    ", ".join(["'{}'".format(m.name) for m in class_lexer_info.Data.TypeInfo.AllowedMethodTypes]),
                )

            if method_type == MethodType.static:
                if class_modifier is not None:
                    assert self.Regions.ClassModifier is not None
                    raise InvalidClassModifierOnStaticError(self.Regions.ClassModifier)
            else:
                if class_modifier is None:
                    class_modifier = class_lexer_info.Data.TypeInfo.DefaultClassModifier
                    object.__setattr__(self.Regions, "ClassModifier", self.Regions.Self__)

                class_lexer_info.Data.ValidateMemberClassModifier(class_modifier, self.Regions.ClassModifier)

            if (
                has_statements
                and method_type in [MethodType.deferred, MethodType.abstract]
            ):
                raise MethodStatementsUnexpectedError(self.Regions.Self__, method_type.name)

            if (
                not has_statements
                and method_type not in [MethodType.deferred, MethodType.abstract]
            ):
                raise MethodStatementsRequiredError(self.Regions.Self__, method_type.name)

        # Set the values
        object.__setattr__(
            self,
            "Data",
            # pylint: disable=too-many-function-args
            FuncAndMethodDefinitionStatementLexerData(
                visibility,
                method_type,
                return_type,
                name,
                parameters,
                class_modifier,
            ),
        )

        super(FuncAndMethodDefinitionStatementLexerInfo, self).__post_init__()
