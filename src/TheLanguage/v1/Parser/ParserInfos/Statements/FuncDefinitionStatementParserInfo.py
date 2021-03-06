# ----------------------------------------------------------------------
# |
# |  FuncDefinitionStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 15:33:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FunDefinitionStatementParserInfo object"""

import itertools
import os

from enum import auto, Enum
from typing import cast, List, Optional, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import (
        ParserInfo,
        ParserInfoType,
        Region,
        ScopeFlag,
        StatementParserInfo,
    )

    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Common.FuncParametersParserInfo import (  # pylint: disable=unused-import
        FuncParametersParserInfo,
        FuncParameterParserInfo,            # Convenience import
    )

    from ..Common.MethodModifier import MethodModifier

    from ..Common.MutabilityModifier import MutabilityModifier

    from ..Common.TemplateParametersParserInfo import (  # pylint: disable=unused-import
        TemplateDecoratorParameterParserInfo,           # Convenience import
        TemplateParametersParserInfo,
        TemplateTypeParameterParserInfo,                # Convenience import
    )

    from ..Common.VisibilityModifier import VisibilityModifier, InvalidProtectedError

    from ..Expressions.VariableExpressionParserInfo import (
        ExpressionParserInfo,
        VariableExpressionParserInfo,
    )

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
# TODO: Rename
class OperatorType(Enum):
    #                                       Description                                         Default Behavior                Is Exceptional  Signature
    #                                       --------------------------------------------        --------------------------      --------------  ---------------------------------

    # ----------------------------------------------------------------------
    # Methods required by fundamental types; will be generated for others
    Accept                      = auto()  # Accepts a visitor.                                  visitor.Visit(this)             Yes             public None __Accept?__<VisitorT>(VisitorT ref visitor) <mutability>
    Compare                     = auto()  # Compares 2 instances of the same type.              Member-wise compare.            No              [static] public Integer __Compare__(ThisType immutable this, ThisType immutable other)
    Deserialize                 = auto()  # Deserializes the type from an archive.              Member-wise deserialization.    Yes             [static] public ThisType __Deserialize?__<ArchiveT>(ArchiveT ref archive)
    Serialize                   = auto()  # Serializes the type to an archive.                  Member-wise serialization.      Yes             public None __Serialize?__<ArchiveT>(ArchiveT ref archive) immutable
    Clone                       = auto()  # Clones the instance.                                Member-wise copy.               Yes             public ThisType __Clone?__(<optional member-wise values>) immutable
    ToBool                      = auto()  # Converts the instance to a boolean value.           Member-wise conversion.         No              public Boolean __ToBool__() immutable
    ToString                    = auto()  # Converts the instance to a string.                  Member-wise conversion.         Yes             public String __ToString?__() immutable

    # ----------------------------------------------------------------------
    Call                        = auto()  # TODO: Finish all this stuff                         N/A                             Yes             <visibility> <return_type> __Call?__(<args>) <mutability>
    GetAttribute                = auto()  #                                                     N/A                             Yes             <visibility> (<return_type> | None) __GetAttribute__(String immutable name) <ref|val>
    Index                       = auto()  #                                                     N/A                             No              <visibility> (IntArch | None) __Index__(<args>) <ref|val>
    Iter                        = auto()  #                                                     N/A                             No              <visibility> Iterator<type> __Iter__() <ref|val>
    Cast                        = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __Cast?__<OtherT>() TODO: This needs some work!

    Negative                    = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __Negative?__() immutable
    Positive                    = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __Positive?__() immutable
    BitFlip                     = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __BitFlip?__() immutable

    Divide                      = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __Divide?__(<type> immutable divisor) immutable
    DivideFloor                 = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __DivideFloor?__(<type> immutable divisor) immutable
    Modulo                      = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __Modulo?__(<type> immutable divisor) immutable
    Multiply                    = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __Multiply?__(<type> immutable multiplier) immutable
    Power                       = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __Power?__(<type> immutable exponent) immutable

    Add                         = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __Add?__(<type> immutable value) immutable
    Subtract                    = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __Subtract?__(<type> immutable value) immutable

    BitShiftLeft                = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __BitShiftLeft?__(<type> immutable value) immutable
    BitShiftRight               = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __BitShiftRight?__(<type> immutable value) immutable

    Greater                     = auto()  #                                                     Result based on Compare         No              <visibility> Boolean __Greater__(<type> immutable value) immutable
    GreaterEqual                = auto()  #                                                     Result based on Compare         No              <visibility> Boolean __GreaterEqual__(<type> immutable value) immutable
    Less                        = auto()  #                                                     Result based on Compare         No              <visibility> Boolean __Less__(<type> immutable value) immutable
    LessEqual                   = auto()  #                                                     Result based on Compare         No              <visibility> Boolean __LessEqual__(<type> immutable value) immutable

    Equal                       = auto()  #                                                     Result based on Comapre         No              <visibility> Boolean __Equal__(<type> immutable value) immutable
    NotEqual                    = auto()  #                                                     Result based on Comapre         No              <visibility> Boolean __NotEqual__(<type> immutable value) immutable

    BitAnd                      = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __BitAnd?__(<type> immutable value) immutable

    BitXor                      = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __BitXor?__(<type> immutable value) immutable

    BitOr                       = auto()  #                                                     N/A                             Yes             <visibility> <return_type> __BitOr?__(<type> immutable value) immutable

    Contains                    = auto()  #                                                     N/A                             No              <visibility> Boolean __Contains__(<type> immutable value) immutable
    NotContains                 = auto()  #                                                     N/A                             No              <visibility> Boolean __NotContains__(<type> immutable value) immutable

    Not                         = auto()  #                                                     N/A                             No              <visibility> <return_type> __Not__() immutable

    LogicalAnd                  = auto()  #                                                     N/A                             No              <visibility> <return_type> __LogicalAnd__(<type> immutable value) immutable

    LogicalOr                   = auto()  #                                                     N/A                             No              <visibility> <return_type> __LogicalOr__(<type> immutable value) immutable

    BitFlipInplace              = auto()  #                                                     N/A                             Yes             <visibility> None __BitFlipInplace?__() mutable

    DivideInplace               = auto()  #                                                     N/A                             Yes             <visibility> None __DivideInplace?__(<type> immutable divisor) mutable
    DivideFloorInplace          = auto()  #                                                     N/A                             Yes             <visibility> None __DivideFloorInplace?__(<type> immutable divisor) mutable
    ModuloInplace               = auto()  #                                                     N/A                             Yes             <visibility> None __ModuloInplace?__(<type> immutable divisor) mutable
    MultiplyInplace             = auto()  #                                                     N/A                             Yes             <visibility> None __MultiplyInplace?__(<type> immutable multiplier) mutable
    PowerInplace                = auto()  #                                                     N/A                             Yes             <visibility> None __PowerInplace?__(<type> immutable exponent) mutable

    AddInplace                  = auto()  #                                                     N/A                             Yes             <visibility> None __AddInplace?__(<type> immutable value) mutable
    SubtractInplace             = auto()  #                                                     N/A                             Yes             <visibility> None __SubtractInplace?__(<type> immutable value) mutable

    BitShiftLeftInplace         = auto()  #                                                     N/A                             Yes             <visibility> None __BitShiftLeftInplace?__(<type> immutable value) mutable
    BitShiftRightInplace        = auto()  #                                                     N/A                             Yes             <visibility> None __BitShiftRightInplace?__(<type> immutable value) mutable

    BitAndInplace               = auto()  #                                                     N/A                             Yes             <visibility> None __BitAndInplace?__(<type> immutable value) mutable

    BitXorInplace               = auto()  #                                                     N/A                             Yes             <visibility> None __BitXorInplace?__(<type> immutable value) mutable

    BitOrInplace                = auto()  #                                                     N/A                             Yes             <visibility> None __BitOrInplace?__(<type> immutable value) mutable


# ----------------------------------------------------------------------
InvalidFunctionMutabilityError              = CreateError(
    "Mutability modifiers are not valid for functions",
)

InvalidFunctionMethodModifierError          = CreateError(
    "Method modifiers are not valid for functions",
)

InvalidFunctionOperatorError                = CreateError(
    "Functions may not be named as operators",
)

InvalidFunctionDeferredStatementsError      = CreateError(
    "Deferred functions should not have any statements",
)

InvalidMethodCapturedVariableError          = CreateError(
    "Methods may not capture variables",
)

InvalidStaticMethodMutabilityError          = CreateError(
    "Static methods may not include a mutability modifier",
)

InvalidMethodMutabilityError                = CreateError(
    "'{mutability_str}' is not a valid mutability for '{type}' types;' valid mutabilities are {valid_mutabilities_str}",
    type=str,
    mutability=MutabilityModifier,
    valid_mutabilities=List[MutabilityModifier],
    mutability_str=str,
    valid_mutabilities_str=str,
)

InvalidMethodParameterNameError             = CreateError(
    "The parameter name '{name}' cannot be overridden",
    name=str,
)

InvalidMethodModifierError                  = CreateError(
    "'{modifier_str}' is not a valid modifier for '{type}' types; valid modifiers are {valid_modifiers_str}",
    type=str,
    modifier=MethodModifier,
    valid_modifiers=List[MethodModifier],
    modifier_str=str,
    valid_modifiers_str=str,
)

InvalidMethodAbstractStatementsError        = CreateError(
    "Abstract methods should not have any statements",
)

InvalidMethodStatementsRequiredError        = CreateError(
    "Method statements are required",
)

InvalidVisibilityError                      = CreateError(
    "'{visibility_str}' is not a valid visibility for {type}; valid visibilities are {valid_visibilities_str}",
    type=str,
    visibility=VisibilityModifier,
    valid_visibilities=List[VisibilityModifier],
    visibility_str=str,
    valid_visibilities_str=str,
)

MutabilityRequiredError                     = CreateError(
    "A mutability modifier is required",
)

StatementsRequiredError                     = CreateError(
    "{type} statements are required",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncDefinitionStatementParserInfo(StatementParserInfo):
    """Function or method definition"""

    # ----------------------------------------------------------------------
    introduces_scope__                      = True
    allow_duplicate_named_items__           = True

    # ----------------------------------------------------------------------
    parent_class_capabilities: Optional[ClassCapabilities]

    parameters: Union[bool, FuncParametersParserInfo]

    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier                      = field(init=False)

    mutability_param: InitVar[Optional[MutabilityModifier]]
    mutability: Optional[MutabilityModifier]            = field(init=False)

    method_modifier_param: InitVar[Optional[MethodModifier]]
    method_modifier: Optional[MethodModifier]           = field(init=False)

    return_type: Optional[ExpressionParserInfo]
    name: Union[str, OperatorType]
    documentation: Optional[str]

    templates: Optional[TemplateParametersParserInfo]

    captured_variables: Optional[List[VariableExpressionParserInfo]]
    statements: Optional[List[StatementParserInfo]]

    is_deferred: Optional[bool]
    is_exceptional: Optional[bool]
    is_generator: Optional[bool]
    is_reentrant: Optional[bool]
    is_scoped: Optional[bool]

    # Valid only for methods
    is_static: Optional[bool]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        parent_class_capabilities: Optional[ClassCapabilities],
        parameters: Union[bool, FuncParametersParserInfo],
        *args,
        **kwargs,
    ):
        if isinstance(parameters, bool):
            parser_info_type = ParserInfoType.Standard
        else:
            parser_info_type = parameters.parser_info_type__

        return cls(  # pylint: disable=too-many-function-args
            ScopeFlag.Root | ScopeFlag.Class | ScopeFlag.Function,
            parser_info_type,               # type: ignore
            regions,                        # type: ignore
            parent_class_capabilities,
            parameters,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        parser_info_type,
        regions,
        visibility_param,
        mutability_param,
        method_modifier_param,
    ):
        super(FuncDefinitionStatementParserInfo, self).__post_init__(
            parser_info_type,
            regions,
            regionless_attributes=[
                "parent_class_capabilities",
                "return_type",
                "templates",
            ],
            validate=False,
            parent_class_capabilities=lambda value: None if value is None else value.name,
        )

        # Set defaults
        if self.parent_class_capabilities is None:
            # We are looking at a function
            if visibility_param is None:
                visibility_param = VisibilityModifier.private
                object.__setattr__(self.regions__, "visibility", self.regions__.self__)

            desc = "functions"

        else:
            if visibility_param is None and self.parent_class_capabilities.default_method_visibility is not None:
                visibility_param = self.parent_class_capabilities.default_method_visibility
                object.__setattr__(self.regions__, "visibility", self.regions__.self__)

            if not self.is_static and mutability_param is None and self.parent_class_capabilities.default_method_mutability is not None:
                mutability_param = self.parent_class_capabilities.default_method_mutability
                object.__setattr__(self.regions__, "mutability", self.regions__.self__)

            if method_modifier_param is None and self.parent_class_capabilities.default_method_modifier is not None:
                method_modifier_param = self.parent_class_capabilities.default_method_modifier
                object.__setattr__(self.regions__, "method_modifier", self.regions__.self__)

            desc = "{} methods".format(self.parent_class_capabilities.name)

        object.__setattr__(self, "visibility", visibility_param)
        object.__setattr__(self, "mutability", mutability_param)
        object.__setattr__(self, "method_modifier", method_modifier_param)

        self.ValidateRegions()

        # Validate
        errors: List[Error] = []

        if self.parent_class_capabilities is None:
            if self.visibility == VisibilityModifier.protected:
                errors.append(
                    InvalidProtectedError.Create(
                        region=self.regions__.visibility,
                    ),
                )

            if self.mutability is not None:
                errors.append(
                    InvalidFunctionMutabilityError.Create(
                        region=self.regions__.mutability,
                    ),
                )

            if self.method_modifier is not None:
                errors.append(
                    InvalidFunctionMethodModifierError.Create(
                        region=self.regions__.method_modifier,
                    ),
                )

            if not isinstance(self.name, str):
                errors.append(
                    InvalidFunctionOperatorError.Create(
                        region=self.regions__.name,
                    ),
                )

            if not self.is_deferred and not self.statements:
                errors.append(
                    InvalidFunctionDeferredStatementsError.Create(
                        region=self.regions__.self__,
                    ),
                )

            # TODO: Captures only when nested with a function

        else:
            if self.captured_variables:
                errors.append(
                    InvalidMethodCapturedVariableError.Create(
                        region=self.regions__.captured_variables,
                    ),
                )

            if self.is_static:
                if self.mutability is not None:
                    errors.append(
                        InvalidStaticMethodMutabilityError.Create(
                            region=self.regions__.mutability,
                        ),
                    )
            else:
                if self.mutability is None:
                    errors.append(
                        MutabilityRequiredError.Create(
                            region=self.regions__.self__,
                        ),
                    )

                # 'this' and 'self' can't be used as parameter names
                if isinstance(self.parameters, FuncParametersParserInfo):
                    for parameter in itertools.chain(
                        self.parameters.positional or [],
                        self.parameters.any or [],
                        self.parameters.keyword or [],
                    ):
                        if parameter.name in ["self", "this"]:
                            errors.append(
                                InvalidMethodParameterNameError.Create(
                                    region=parameter.regions__.name,
                                    name=parameter.name,
                                ),
                            )

            assert self.method_modifier is not None

            if self.method_modifier == MethodModifier.abstract and self.statements:
                errors.append(
                    InvalidMethodAbstractStatementsError.Create(
                        region=self.regions__.statements,
                    ),
                )
            elif self.method_modifier != MethodModifier.abstract and not self.is_deferred and not self.statements:
                errors.append(
                    InvalidMethodStatementsRequiredError.Create(
                        region=self.regions__.self__,
                    ),
                )

            self.parent_class_capabilities.ValidateFuncDefinitionStatementCapabilities(self)

        if self.is_deferred and self.statements:
            errors.append(
                StatementsRequiredError.Create(
                    region=self.regions__.statements,
                    type=desc,
                ),
            )

        if self.return_type is not None:
            try:
                self.return_type.ValidateAsType(self.parser_info_type__)
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        details = []

        if self.return_type:
            details.append(("return_type", self.return_type))
        if self.templates:
            details.append(("templates", self.templates))
        if self.captured_variables:
            details.append(("captured_variables", self.captured_variables))
        if not isinstance(self.parameters, bool):
            details.append(("parameters", self.parameters))

        return self._AcceptImpl(
            visitor,
            details=details,
            children=cast(List[ParserInfo], self.statements) or None,
        )
