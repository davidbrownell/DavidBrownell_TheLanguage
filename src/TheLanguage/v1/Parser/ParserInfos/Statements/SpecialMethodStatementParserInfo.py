# ----------------------------------------------------------------------
# |
# |  SpecialMethodStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-18 15:28:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SpecialMethodStatementParserInfo object"""

import os

from enum import auto, Enum
from typing import Dict, List, Optional

from dataclasses import dataclass

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
        ScopeFlag,
        StatementParserInfo,
        TranslationUnitRegion,
    )

    from .Traits.NewNamespaceScopedStatementTrait import NewNamespaceScopedStatementTrait

    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Common.VisibilityModifier import VisibilityModifier

    from ...Parser import (
        CreateError,
        Error,
        ErrorException,
    )


# ----------------------------------------------------------------------
NoClassError                                = CreateError(
    "Special methods may only be defined within a class-like object",
)

StatementsRequiredError                     = CreateError(
    "Statements are required",
)

InvalidCompileTimeStatementError            = CreateError(
    "Invalid compile-time statement",
)


# ----------------------------------------------------------------------
class SpecialMethodType(Enum):
    #                                                       Description                                         Default Behavior                Is Exceptional  Signature
    #                                                       --------------------------------------------        --------------------------      --------------  ---------------------------------
    EvalTemplates               = auto()                    # Custom functionality invoked at compile time      Noop                            N/A             __EvalTemplates!__()  # Uses `Enforce!`
                                                            # to ensure that the template arguments are
                                                            # valid.

    EvalConstraints             = auto()                    # Custom functionality invoked at compile time      Noop                            N/A             __EvalConstraints!__()  # Uses `Enforce!`
                                                            # to ensure that the constraint arguments are
                                                            # valid.

    Convert                     = auto()                    # Custom functionality invoked at compile time      No seamless conversions         N/A             __EvalConvertible!__()  # Uses `Enforce!`; `other` is name of other type
                                                            # to determine if a type with one set of            are allowed.
                                                            # constraints can be converted seamlessly to
                                                            # a different set of constraints.

    Validate                    = auto()                    # Validates an instance of an object                Noop                            Yes             __Validate?__()
                                                            # (invoked before bases are validated).

    ValidateFinal               = auto()                    # Validates an instance of an object                Noop                            Yes             __ValidateFinal?__()
                                                            # (invoked after bases are validated).

    Destroy                     = auto()                    # Called when an instance is being destroyed        Noop                            No              __Destroy__()
                                                            # (invoked before bases are destroyed).

    DestroyFinal                = auto()                    # Called when an instance is being destroyed        Noop                            No              __DestroyFinal__()
                                                            # (invoked after bases are destroyed).

    PrepareFinalize             = auto()                    # Called when an instance is being finalized        Impl based on attr flags        Yes             __PrepareFinalize?__()
    Finalize                    = auto()                    # Called when an instance is being finalized        Impl based on attr flags        No              __Finalize__()

    # ----------------------------------------------------------------------
    def IsCompileTimeMethod(self) -> bool:
        return self in [
            SpecialMethodType.EvalTemplates,
            SpecialMethodType.EvalConstraints,
            SpecialMethodType.Convert,
        ]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class SpecialMethodStatementParserInfo(
    NewNamespaceScopedStatementTrait,
    StatementParserInfo,
):
    # ----------------------------------------------------------------------
    parent_class_capabilities: ClassCapabilities

    special_method_type: SpecialMethodType

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        statements: List[StatementParserInfo],
        parent_class_capabilities: Optional[ClassCapabilities],
        name: SpecialMethodType,
        *args,
        **kwargs,
    ):
        if name.IsCompileTimeMethod():
            parser_info_type = ParserInfoType.TypeCustomization
        else:
            parser_info_type = ParserInfoType.Standard

        return cls(  # pylint: disable=too-many-function-args
            parser_info_type,               # type: ignore
            regions,                        # type: ignore
            str(name),
            VisibilityModifier.private,     # type: ignore
            statements,                     # type: ignore
            parent_class_capabilities,      # type: ignore
            name,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, parser_info_type, regions, visibility_param):
        StatementParserInfo.__post_init__(
            self,
            parser_info_type,
            regions,
            **{
                **NewNamespaceScopedStatementTrait.ObjectReprImplBaseInitKwargs(),
                **{
                    "finalize": False,
                    "regionless_attributes": [
                        "visibility",               # Value is hard coded during creation
                        "parent_class_capabilities",
                        "special_method_type",      # Value is calculated
                    ]
                        + NewNamespaceScopedStatementTrait.RegionlessAttributesArgs()
                    ,
                    "parent_class_capabilities": lambda value: value.name,
                    "special_method_type": None,
                },

            },
        )

        self._InitTraits(
            allow_duplicate_names=False,
            allow_name_to_be_duplicated=False,
        )

        NewNamespaceScopedStatementTrait.__post_init__(self, visibility_param)

        self._Finalize()

        # Validate
        errors: List[Error] = []

        if self.parent_class_capabilities is None:
            errors.append(
                NoClassError.Create(
                    region=self.regions__.self__,
                ),
            )

        if not self.statements:
            errors.append(
                StatementsRequiredError.Create(
                    region=self.regions__.self__,
                ),
            )
        elif self.parser_info_type__.IsCompileTime():
            for statement in self.statements:
                if not statement.parser_info_type__.IsCompileTime():
                    errors.append(
                        InvalidCompileTimeStatementError.Create(
                            region=statement.regions__.self__,
                        ),
                    )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetValidScopes() -> Dict[ParserInfoType, ScopeFlag]:
        return {
            ParserInfoType.TypeCustomization: ScopeFlag.Class,
            ParserInfoType.Standard: ScopeFlag.Class,
        }

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsNameOrdered(*args, **kwargs) -> bool:
        return False
