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
    from .ClassStatementParserInfo import ClassStatementParserInfo

    from .StatementParserInfo import StatementParserInfo

    from ..Common.ClassModifier import ClassModifier as ClassModifierType
    from ..Common.FunctionParametersParserInfo import FunctionParametersParserInfo
    from ..Common.MethodModifier import MethodModifier as MethodModifierType
    from ..Common.TemplateParametersParserInfo import TemplateParametersParserInfo
    from ..Common.VisibilityModifier import VisibilityModifier
    from ..Common.VisitorTools import StackHelper

    from ..Names.VariableNameParserInfo import VariableNameParserInfo
    from ..Types.TypeParserInfo import TypeParserInfo

    from ..Error import Error

    # Convenience Imports
    from .ClassStatementParserInfo import (
        InvalidMemberClassModifierError,
        InvalidMemberMutableModifierError,
        InvalidMemberVisibilityError,
    )


# ----------------------------------------------------------------------
class OperatorType(Enum):
    # TODO: I don't think that these are complete

    # Compile-time
    EvalTemplates                           = auto()
    EvalConstraints                         = auto()
    IsConvertibleTo                         = auto()

    # Foundational
    ToBool                                  = auto()
    ToString                                = auto()
    Repr                                    = auto()
    Clone                                   = auto()
    Serialize                               = auto()
    Deserialize                             = auto()

    # Instance Instantiation
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
    LessOrEqual                             = auto()
    Greater                                 = auto()
    GreaterOrEqual                          = auto()

    # Logical
    And                                     = auto()
    Or                                      = auto()
    Not                                     = auto()

    # Mathematical
    Add                                     = auto()
    Subtract                                = auto()
    Multiply                                = auto()
    Power                                   = auto()
    Divide                                  = auto()
    DivideFloor                             = auto()
    Modulo                                  = auto()
    Positive                                = auto()
    Negative                                = auto()

    AddInplace                              = auto()
    SubtractInplace                         = auto()
    MultiplyInplace                         = auto()
    PowerInplace                            = auto()
    DivideInplace                           = auto()
    DivideFloorInplace                      = auto()
    ModuloInplace                           = auto()

    # Bit Manipulation
    BitShiftLeft                            = auto()
    BitShiftRight                           = auto()
    BitAnd                                  = auto()
    BitOr                                   = auto()
    BitXor                                  = auto()
    BitFlip                                 = auto()

    BitShiftLeftInplace                     = auto()
    BitShiftRightInplace                    = auto()
    BitAndInplace                           = auto()
    BitOrInplace                            = auto()
    BitXorInplace                           = auto()


COMPILE_TIME_OPERATORS                      = [
    OperatorType.EvalTemplates,
    OperatorType.EvalConstraints,
    OperatorType.IsConvertibleTo,
]


FOUNDATIONAL_OPERATORS                      = [
    OperatorType.ToBool,
    OperatorType.ToString,
    OperatorType.Repr,
    OperatorType.Clone,
    OperatorType.Serialize,
    OperatorType.Deserialize,
    OperatorType.Compare,
]


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidFunctionMethodModifierError(Error):
    MethodModifier: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{MethodModifier}' is not supported for functions.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidFunctionClassModifierError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Class modifiers are not supported for functions.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FunctionStatementsRequiredError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Functions must have statements.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DeferredStatementsError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Statements are not expected for deferred functions or methods.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MethodStatementsRequiredError(Error):
    MethodModifier: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Statements are required for '{MethodModifier}' methods.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MethodStatementsUnexpectedError(Error):
    MethodModifier: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Statements are not expected for '{MethodModifier}' methods.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMethodModifierError(Error):
    ClassType: str
    MethodModifier: str
    AllowedMethodModifiers: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{MethodModifier}' is not a supported method type modifier for members of '{ClassType}' types; supported values are '{AllowedMethodModifiers}'.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassModifierError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Class modifiers are not supported for 'static' methods.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncDefinitionStatementParserInfo(StatementParserInfo):
    class_parser_info: InitVar[Optional[ClassStatementParserInfo]]

    visibility: InitVar[Optional[VisibilityModifier]]
    method_modifier: InitVar[Optional[MethodModifierType]]
    class_modifier: InitVar[Optional[ClassModifierType]]

    Visibility: VisibilityModifier                      = field(init=False)
    MethodModifier: MethodModifierType                  = field(init=False)
    ClassModifier: Optional[ClassModifierType]          = field(init=False)

    ReturnType: TypeParserInfo
    Name: Union[str, OperatorType]
    Templates: Optional[TemplateParametersParserInfo]
    CapturedVariables: Optional[List[VariableNameParserInfo]]
    Parameters: Union[bool, FunctionParametersParserInfo]
    Statements: Optional[List[StatementParserInfo]]
    Documentation: Optional[str]

    # Note that these values are bools rather than enum-flags so that we can associated a region
    # with each of them when set.
    IsDeferred: Optional[bool]
    IsGenerator: Optional[bool]
    IsReentrant: Optional[bool]
    IsExceptional: Optional[bool]
    IsScoped: Optional[bool]
    IsAsync: Optional[bool]

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        regions,
        class_parser_info: Optional[ClassStatementParserInfo],
        visibility: Optional[VisibilityModifier],
        method_modifier: Optional[MethodModifierType],
        class_modifier: Optional[ClassModifierType],
    ):
        super(FuncDefinitionStatementParserInfo, self).__post_init__(
            regions,
            should_validate=False,
        )

        assert not isinstance(self.ReturnType, bool) or self.ReturnType is False
        assert not isinstance(self.Parameters, bool) or self.Parameters is False
        assert self.Statements is None or self.Statements

        assert self.IsDeferred is None or self.IsDeferred
        assert self.IsGenerator is None or self.IsGenerator
        assert self.IsReentrant is None or self.IsReentrant
        assert self.IsExceptional is None or self.IsExceptional
        assert self.IsScoped is None or self.IsScoped
        assert self.IsAsync is None or self.IsAsync

        if self.IsDeferred and self.Statements:
            raise DeferredStatementsError(self.Regions__.Statements)  # type: ignore && pylint: disable=no-member

        # Other variables
        if class_parser_info is None:
            # We are looking at a standard function

            # Visibility
            if visibility is None:
                visibility = VisibilityModifier.private
                object.__setattr__(self.Regions__, "Visibility", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

            object.__setattr__(self, "Visibility", visibility)

            # MethodModifier
            if method_modifier is None:
                method_modifier = MethodModifierType.standard
                object.__setattr__(self.Regions__, "MethodModifier", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member
            elif method_modifier != MethodModifierType.standard:
                raise InvalidFunctionMethodModifierError(self.Regions__.MethodModifier, method_modifier.name)  # type: ignore && pylint: disable=no-member

            object.__setattr__(self, "MethodModifier", method_modifier)

            # ClassModifier
            if class_modifier is not None:
                raise InvalidFunctionClassModifierError(self.Regions__.ClassModifier)  # type: ignore && pylint: disable=no-member

            object.__setattr__(self, "ClassModifier", class_modifier)

            # Statements
            if not self.IsDeferred and not self.Statements:
                raise FunctionStatementsRequiredError(self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

        else:
            # We are looking at a method

            # Visibility
            if visibility is None:
                visibility = class_parser_info.TypeInfo.DefaultMemberVisibility
                object.__setattr__(self.Regions__, "Visibility", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

            class_parser_info.ValidateMemberVisibility(visibility, self.Regions__.Visibility)  # type: ignore && pylint: disable=no-member
            object.__setattr__(self, "Visibility", visibility)

            # MethodModifier
            if method_modifier is None:
                method_modifier = class_parser_info.TypeInfo.DefaultMethodModifier
                object.__setattr__(self.Regions__, "MethodModifier", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

            if (
                method_modifier not in class_parser_info.TypeInfo.AllowedMethodModifiers
                and self.Name not in COMPILE_TIME_OPERATORS
            ):
                raise InvalidMethodModifierError(
                    self.Regions__.MethodModifier,  # type: ignore && pylint: disable=no-member
                    class_parser_info.ClassType.value,
                    method_modifier.name,
                    ", ".join(["'{}'".format(e.name) for e in class_parser_info.TypeInfo.AllowedMethodModifiers]),
                )

            object.__setattr__(self, "MethodModifier", method_modifier)

            # ClassModifier
            if method_modifier == MethodModifierType.static:
                if class_modifier is not None:
                    raise InvalidClassModifierError(self.Regions__.ClassModifier)  # type: ignore && pylint: disable=no-member
            else:
                if class_modifier is None:
                    class_modifier = class_parser_info.TypeInfo.DefaultClassModifier
                    object.__setattr__(self.Regions__, "ClassModifier", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

                class_parser_info.ValidateMemberModifier(class_modifier, self.Regions__.ClassModifier)  # type: ignore && pylint: disable=no-member

            object.__setattr__(self, "ClassModifier", class_modifier)

            # Statements
            if self.Statements:
                if (
                    method_modifier == MethodModifierType.abstract
                    and self.Name not in COMPILE_TIME_OPERATORS
                ):
                    assert not self.IsDeferred
                    raise MethodStatementsUnexpectedError(self.Regions__.Statements, method_modifier.name)  # type: ignore && pylint: disable=no-member
            else:
                if method_modifier != MethodModifierType.abstract and not self.IsDeferred:
                    raise MethodStatementsRequiredError(self.Regions__.Self__, method_modifier.name)  # type: ignore && pylint: disable=no-member

        self.Validate()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            with helper["ReturnType"]:
                self.ReturnType.Accept(visitor, helper.stack, *args, **kwargs)

            if self.Templates is not None:
                with helper["Templates"]:
                    self.Templates.Accept(visitor, helper.stack, *args, **kwargs)

            if self.CapturedVariables is not None:
                with helper["CapturedVariables"]:
                    for captured_variable in self.CapturedVariables:
                        captured_variable.Accept(visitor, helper.stack, *args, **kwargs)

            if isinstance(self.Parameters, FunctionParametersParserInfo):
                with helper["Parameters"]:
                    self.Parameters.Accept(visitor, helper.stack, *args, **kwargs)

            if self.Statements is not None:
                with helper["Statements"]:
                    for statement in self.Statements:
                        statement.Accept(visitor, helper.stack, *args, **kwargs)
