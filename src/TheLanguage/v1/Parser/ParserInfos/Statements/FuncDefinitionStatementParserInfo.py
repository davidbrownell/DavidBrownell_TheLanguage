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

from enum import Enum
from typing import cast, List, Optional, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import (  # pylint: disable=unused-import
        ParserInfo,
        ParserInfoType,                     # Convenience import
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

    from ..Common.VariableNameParserInfo import VariableNameParserInfo
    from ..Common.VisibilityModifier import VisibilityModifier

    from ..Types.TypeParserInfo import (
        InvalidNewMutabilityModifierError,
        MutabilityModifierRequiredError,
        TypeParserInfo,
    )

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
_auto_ctr = itertools.count(1)
_auto = lambda: next(_auto_ctr)


# ----------------------------------------------------------------------
# TODO: Rename
class OperatorType(Enum):
    # ----------------------------------------------------------------------
    # |  Public Types
    @dataclass(frozen=True, repr=False)
    class Value(ObjectReprImplBase):
        value: int
        precedence: int

        # ----------------------------------------------------------------------
        @classmethod
        def Create(cls, *args, **kwargs):
            """\
            This hack avoids pylint warnings associated with invoking dynamically
            generated constructors with too many methods.
            """
            return cls(*args, **kwargs)

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert self.precedence > 0
            ObjectReprImplBase.__init__(self)

    # ----------------------------------------------------------------------
    # |  Public Data
    #                                                       Description                                         Default Behavior                Is Exceptional  Signature
    #                                                       --------------------------------------------        --------------------------      --------------  ---------------------------------

    # ----------------------------------------------------------------------
    # Methods required by fundamental types; will be generated for others
    Accept                      = Value.Create(_auto(), 1)  # Accepts a visitor.                                visitor.Visit(this)             Yes             public None __Accept?__<VisitorT>(VisitorT ref visitor) <mutability>
    Compare                     = Value.Create(_auto(), 1)  # Compares 2 instances of the same type.            Member-wise compare.            No              [static] public Integer __Compare__(ThisType immutable this, ThisType immutable other)
    Deserialize                 = Value.Create(_auto(), 1)  # Deserializes the type from an archive.            Member-wise deserialization.    Yes             [static] public ThisType __Deserialize?__<ArchiveT>(ArchiveT ref archive)
    Serialize                   = Value.Create(_auto(), 1)  # Serializes the type to an archive.                Member-wise serialization.      Yes             public None __Serialize?__<ArchiveT>(ArchiveT ref archive) immutable
    Clone                       = Value.Create(_auto(), 1)  # Clones the instance.                              Member-wise copy.               Yes             public ThisType __Clone?__(<optional member-wise values>) immutable
    ToBool                      = Value.Create(_auto(), 1)  # Converts the instance to a boolean value.         Member-wise conversion.         No              public Boolean __ToBool__() immutable
    ToString                    = Value.Create(_auto(), 1)  # Converts the instance to a string.                Member-wise conversion.         Yes             public String __ToString?__() immutable

    # ----------------------------------------------------------------------
    Call                        = Value.Create(_auto(), 2)  # TODO: Finish all this stuff                       N/A                             Yes             <visibility> <return_type> __Call?__(<args>) <mutability>
    GetAttribute                = Value.Create(_auto(), 2)  #                                                   N/A                             Yes             <visibility> <return_type> __GetAttribute?__(String immutable name) <ref|val>
    Index                       = Value.Create(_auto(), 2)  #                                                   N/A                             Yes             <visibility> <return_type> __Index?__(<args>) <ref|val>
    Iter                        = Value.Create(_auto(), 2)  #                                                   N/A                             Yes             <visibility> Iterator<type> __Iter?__() <ref|val>
    Cast                        = Value.Create(_auto(), 2)  #                                                   N/A                             Yes             <visibility> <return_type> __Cast?__<OtherT>() TODO: This needs some work!

    Negative                    = Value.Create(_auto(), 3)  #                                                   N/A                             Yes             <visibility> <return_type> __Negative?__() immutable
    Positive                    = Value.Create(_auto(), 3)  #                                                   N/A                             Yes             <visibility> <return_type> __Positive?__() immutable
    BitFlip                     = Value.Create(_auto(), 3)  #                                                   N/A                             Yes             <visibility> <return_type> __BitFlip?__() immutable

    Divide                      = Value.Create(_auto(), 4)  #                                                   N/A                             Yes             <visibility> <return_type> __Divide?__(<type> immutable divisor) immutable
    DivideFloor                 = Value.Create(_auto(), 4)  #                                                   N/A                             Yes             <visibility> <return_type> __DivideFloor?__(<type> immutable divisor) immutable
    Modulo                      = Value.Create(_auto(), 4)  #                                                   N/A                             Yes             <visibility> <return_type> __Modulo?__(<type> immutable divisor) immutable
    Multiply                    = Value.Create(_auto(), 4)  #                                                   N/A                             Yes             <visibility> <return_type> __Multiply?__(<type> immutable multiplier) immutable
    Power                       = Value.Create(_auto(), 4)  #                                                   N/A                             Yes             <visibility> <return_type> __Power?__(<type> immutable exponent) immutable

    Add                         = Value.Create(_auto(), 5)  #                                                   N/A                             Yes             <visibility> <return_type> __Add?__(<type> immutable value) immutable
    Subtract                    = Value.Create(_auto(), 5)  #                                                   N/A                             Yes             <visibility> <return_type> __Subtract?__(<type> immutable value) immutable

    BitShiftLeft                = Value.Create(_auto(), 6)  #                                                   N/A                             Yes             <visibility> <return_type> __BitShiftLeft?__(<type> immutable value) immutable
    BitShiftRight               = Value.Create(_auto(), 6)  #                                                   N/A                             Yes             <visibility> <return_type> __BitShiftRight?__(<type> immutable value) immutable

    Greater                     = Value.Create(_auto(), 7)  #                                                   Result based on Compare         No              <visibility> Boolean __Greater__(<type> immutable value) immutable
    GreaterEqual                = Value.Create(_auto(), 7)  #                                                   Result based on Compare         No              <visibility> Boolean __GreaterEqual__(<type> immutable value) immutable
    Less                        = Value.Create(_auto(), 7)  #                                                   Result based on Compare         No              <visibility> Boolean __Less__(<type> immutable value) immutable
    LessEqual                   = Value.Create(_auto(), 7)  #                                                   Result based on Compare         No              <visibility> Boolean __LessEqual__(<type> immutable value) immutable

    Equal                       = Value.Create(_auto(), 8)  #                                                   Result based on Comapre         No              <visibility> Boolean __Equal__(<type> immutable value) immutable
    NotEqual                    = Value.Create(_auto(), 8)  #                                                   Result based on Comapre         No              <visibility> Boolean __NotEqual__(<type> immutable value) immutable

    BitAnd                      = Value.Create(_auto(), 9)  #                                                   N/A                             Yes             <visibility> <return_type> __BitAnd?__(<type> immutable value) immutable

    BitXor                      = Value.Create(_auto(), 10) #                                                   N/A                             Yes             <visibility> <return_type> __BitXor?__(<type> immutable value) immutable

    BitOr                       = Value.Create(_auto(), 11) #                                                   N/A                             Yes             <visibility> <return_type> __BitOr?__(<type> immutable value) immutable

    Contains                    = Value.Create(_auto(), 12) #                                                   N/A                             No              <visibility> Boolean __Contains__(<type> immutable value) immutable
    NotContains                 = Value.Create(_auto(), 12) #                                                   N/A                             No              <visibility> Boolean __NotContains__(<type> immutable value) immutable

    Not                         = Value.Create(_auto(), 13) #                                                   N/A                             No              <visibility> <return_type> __Not__() immutable

    LogicalAnd                  = Value.Create(_auto(), 14) #                                                   N/A                             No              <visibility> <return_type> __LogicalAnd__(<type> immutable value) immutable

    LogicalOr                   = Value.Create(_auto(), 15) #                                                   N/A                             No              <visibility> <return_type> __LogicalOr__(<type> immutable value) immutable

    BitFlipInplace              = Value.Create(_auto(), 16) #                                                   N/A                             Yes             <visibility> None __BitFlipInplace?__() mutable

    DivideInplace               = Value.Create(_auto(), 17) #                                                   N/A                             Yes             <visibility> None __DivideInplace?__(<type> immutable divisor) mutable
    DivideFloorInplace          = Value.Create(_auto(), 17) #                                                   N/A                             Yes             <visibility> None __DivideFloorInplace?__(<type> immutable divisor) mutable
    ModuloInplace               = Value.Create(_auto(), 17) #                                                   N/A                             Yes             <visibility> None __ModuloInplace?__(<type> immutable divisor) mutable
    MultiplyInplace             = Value.Create(_auto(), 17) #                                                   N/A                             Yes             <visibility> None __MultiplyInplace?__(<type> immutable multiplier) mutable
    PowerInplace                = Value.Create(_auto(), 17) #                                                   N/A                             Yes             <visibility> None __PowerInplace?__(<type> immutable exponent) mutable

    AddInplace                  = Value.Create(_auto(), 18) #                                                   N/A                             Yes             <visibility> None __AddInplace?__(<type> immutable value) mutable
    SubtractInplace             = Value.Create(_auto(), 18) #                                                   N/A                             Yes             <visibility> None __SubtractInplace?__(<type> immutable value) mutable

    BitShiftLeftInplace         = Value.Create(_auto(), 19) #                                                   N/A                             Yes             <visibility> None __BitShiftLeftInplace?__(<type> immutable value) mutable
    BitShiftRightInplace        = Value.Create(_auto(), 19) #                                                   N/A                             Yes             <visibility> None __BitShiftRightInplace?__(<type> immutable value) mutable

    BitAndInplace               = Value.Create(_auto(), 20) #                                                   N/A                             Yes             <visibility> None __BitAndInplace?__(<type> immutable value) mutable

    BitXorInplace               = Value.Create(_auto(), 21) #                                                   N/A                             Yes             <visibility> None __BitXorInplace?__(<type> immutable value) mutable

    BitOrInplace                = Value.Create(_auto(), 22) #                                                   N/A                             Yes             <visibility> None __BitOrInplace?__(<type> immutable value) mutable


# ----------------------------------------------------------------------
del _auto
del _auto_ctr


# ----------------------------------------------------------------------
InvalidProtectedVisibilityError             = CreateError(
    "Protected visibility is not valid for functions",
)

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

StatementsRequiredError                     = CreateError(
    "{type} statements are required",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncDefinitionStatementParserInfo(StatementParserInfo):
    """Function or method definition"""

    # ----------------------------------------------------------------------
    introduces_scope__                      = True

    # ----------------------------------------------------------------------
    class_capabilities: InitVar[Optional[ClassCapabilities]]

    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier                      = field(init=False)

    mutability_param: InitVar[Optional[MutabilityModifier]]
    mutability: Optional[MutabilityModifier]            = field(init=False)

    method_modifier_param: InitVar[Optional[MethodModifier]]
    method_modifier: Optional[MethodModifier]           = field(init=False)

    return_type: Optional[TypeParserInfo]
    name: Union[str, OperatorType]
    documentation: Optional[str]

    templates: Optional[TemplateParametersParserInfo]

    captured_variables: Optional[List[VariableNameParserInfo]]
    parameters: Union[bool, FuncParametersParserInfo]

    statements: Optional[List[StatementParserInfo]]

    is_deferred: Optional[bool]
    is_exceptional: Optional[bool]
    is_generator: Optional[bool]
    is_reentrant: Optional[bool]
    is_scoped: Optional[bool]

    # Valid only for methods
    is_static: Optional[bool]

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        parser_info_type,
        regions,
        class_capabilities,
        visibility_param,
        mutability_param,
        method_modifier_param,
    ):
        super(FuncDefinitionStatementParserInfo, self).__post_init__(
            parser_info_type,
            regions,
            regionless_attributes=[
                "return_type",
                "templates",
            ],
            validate=False,
        )

        # Set defaults
        if class_capabilities is None:
            # We are looking at a function
            valid_method_visibilities = [
                VisibilityModifier.public,
                VisibilityModifier.internal,
                VisibilityModifier.private,
            ]

            default_method_visibility = VisibilityModifier.private

            capabilities_name = "functions"

        else:
            if not self.is_static and mutability_param is None and class_capabilities.default_method_mutability is not None:
                mutability_param = class_capabilities.default_method_mutability
                object.__setattr__(self.regions__, "mutability", self.regions__.self__)

            if method_modifier_param is None and class_capabilities.default_method_modifier is not None:
                method_modifier_param = class_capabilities.default_method_modifier
                object.__setattr__(self.regions__, "method_modifier", self.regions__.self__)

            valid_method_visibilities = class_capabilities.valid_method_visibilities

            default_method_visibility = class_capabilities.default_method_visibility
            capabilities_name = "{} methods".format(class_capabilities.name)

        object.__setattr__(self, "mutability", mutability_param)
        object.__setattr__(self, "method_modifier", method_modifier_param)

        if visibility_param is None and default_method_visibility is not None:
            visibility_param = default_method_visibility
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        object.__setattr__(self, "visibility", visibility_param)

        self.ValidateRegions()

        # Validate
        errors: List[Error] = []

        if self.return_type is not None:
            if self.return_type.mutability_modifier is None:
                errors.append(
                    MutabilityModifierRequiredError.Create(
                        region=self.return_type.regions__.self__,
                    ),
                )
            elif (
                self.return_type.mutability_modifier == MutabilityModifier.new
                and (
                    class_capabilities is None or class_capabilities.is_instantiable
                )
            ):
                errors.append(
                    InvalidNewMutabilityModifierError.Create(
                        region=self.return_type.regions__.mutability_modifier,
                    ),
                )

        if class_capabilities is None:
            if self.visibility == VisibilityModifier.protected:
                errors.append(
                    InvalidProtectedVisibilityError.Create(
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

            # TODO: Captures only when nested

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
                assert self.mutability is not None

                if self.mutability not in class_capabilities.valid_method_mutabilities:
                    errors.append(
                        InvalidMethodMutabilityError.Create(
                            region=self.regions__.mutability,
                            type=class_capabilities.name,
                            mutability=self.mutability,
                            valid_mutabilities=class_capabilities.valid_method_mutabilities,
                            mutability_str=self.mutability.name,
                            valid_mutabilities_str=", ".join("'{}'".format(m.name) for m in class_capabilities.valid_method_mutabilities),
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

            if self.method_modifier not in class_capabilities.valid_method_modifiers:
                errors.append(
                    InvalidMethodModifierError.Create(
                        region=self.regions__.method_modifier,
                        type=class_capabilities.name,
                        modifier=self.method_modifier,
                        valid_modifiers=class_capabilities.valid_method_modifiers,
                        modifier_str=self.method_modifier.name,
                        valid_modifiers_str=", ".join("'{}'".format(m.name) for m in class_capabilities.valid_method_modifiers),
                    ),
                )

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

        if self.visibility not in valid_method_visibilities:
            errors.append(
                InvalidVisibilityError.Create(
                    region=self.regions__.visibility,
                    type=capabilities_name,
                    visibility=self.visibility,
                    valid_visibilities=valid_method_visibilities,
                    visibility_str=self.visibility.name,
                    valid_visibilities_str=", ".join("'{}'".format(v.name) for v in valid_method_visibilities),
                ),
            )

        if self.is_deferred and self.statements:
            errors.append(
                StatementsRequiredError.Create(
                    region=self.regions__.statements,
                    type=capabilities_name,
                ),
            )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, *args, **kwargs):
        return self._ScopedAcceptImpl(cast(List[ParserInfo], self.statements or []), *args, **kwargs)
