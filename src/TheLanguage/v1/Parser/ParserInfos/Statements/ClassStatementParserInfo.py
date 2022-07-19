# ----------------------------------------------------------------------
# |
# |  ClassStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-01 10:42:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassStatementParserInfo object"""

import itertools
import os
import threading

from enum import auto, Enum, Flag
from typing import Any, Callable, cast, Dict, Generator, List, Optional, Set, Tuple, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment.DoesNotExist import DoesNotExist
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ConcreteClass import ConcreteClass

    from .StatementParserInfo import (
        ParserInfo,
        ParserInfoType,
        ScopeFlag,
        StatementParserInfo,
        TranslationUnitRegion,
    )

    from .Traits.ConstrainedStatementTrait import ConstrainedStatementTrait
    from .Traits.NewNamespaceScopedStatementTrait import NewNamespaceScopedStatementTrait
    from .Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Common.ClassModifier import ClassModifier
    from ..Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
    from ..Common.ConstraintParametersParserInfo import ConstraintParameterParserInfo
    from ..Common.MethodHierarchyModifier import MethodHierarchyModifier
    from ..Common.MutabilityModifier import MutabilityModifier
    from ..Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo
    from ..Common.TemplateParametersParserInfo import ResolvedTemplateArguments
    from ..Common.VisibilityModifier import VisibilityModifier, InvalidProtectedError

    from ..EntityResolver import EntityResolver

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from ..Traits.NamedTrait import NamedTrait
    from ..Types import ClassType, Type

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
CycleDetectedError                          = CreateError(
    "An inheritance cycle was detected with '{name}'",
    name=str,
)

StatementsRequiredError                     = CreateError(
    "Statements are required",
)

InvalidReservedNameError                    = CreateError(
    "The name '{name}' is reserved",
    name=str,
)

# TODO: Use this
DuplicateUsingStatementError                = CreateError(
    "A using statement for '{class_name}' and '{type_name}' has already been defined",
    class_name=str,
    type_name=str,
    prev_region=TranslationUnitRegion,
)

# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementDependencyParserInfo(ParserInfo):
    """Dependency of a class"""

    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    visibility: Optional[VisibilityModifier]            # Note that instances may be created with this value as None,
                                                        # but a default will be provided once the instance is associated
                                                        # with a ClassStatement instance.
    type: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(ClassStatementDependencyParserInfo, self).__init__(
            ParserInfoType.Standard,
            regions,
            **{
                "regionless_attributes": ["type", ],
            },
        )

        # Validate
        errors: List[Error] = []

        try:
            self.type.InitializeAsType(
                self.parser_info_type__,
                is_instantiated_type=False,
            )
        except ErrorException as ex:
            errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "type", self.type  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementParserInfo(
    ConstrainedStatementTrait,
    TemplatedStatementTrait,
    NewNamespaceScopedStatementTrait,
    StatementParserInfo,
):
    """\
    Statement that defines a class-like object. The capabilities provided during instantiation
    control many aspects of what is an isn't valid for a particular class type (e.g. class vs.
    struct vs. interface).
    """

    # ----------------------------------------------------------------------
    parent_class_capabilities: Optional[ClassCapabilities]
    class_capabilities: ClassCapabilities

    class_modifier_param: InitVar[Optional[ClassModifier]]
    class_modifier: ClassModifier           = field(init=False)

    documentation: Optional[str]

    extends: Optional[List[ClassStatementDependencyParserInfo]]
    implements: Optional[List[ClassStatementDependencyParserInfo]]
    uses: Optional[List[ClassStatementDependencyParserInfo]]

    constructor_visibility_param: InitVar[Optional[VisibilityModifier]]
    constructor_visibility: VisibilityModifier          = field(init=False)

    is_abstract: Optional[bool]
    is_final: Optional[bool]

    self_referencing_type_names: Optional[List[str]]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.Standard,        # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        parser_info_type,
        regions,
        visibility_param,
        templates_param,
        constraints_param,
        class_modifier_param,
        constructor_visibility_param,
    ):
        StatementParserInfo.__post_init__(
            self,
            parser_info_type,
            regions,
            **{
                **{
                    **NewNamespaceScopedStatementTrait.ObjectReprImplBaseInitKwargs(),
                    **TemplatedStatementTrait.ObjectReprImplBaseInitKwargs(),
                    **ConstrainedStatementTrait.ObjectReprImplBaseInitKwargs(),
                    **{
                        "parent_class_capabilities": lambda value: None if value is None else value.name,
                        "class_capabilities": lambda value: value.name,
                    },
                },
                **{
                    "regionless_attributes": [
                        "parent_class_capabilities",
                        "class_capabilities",
                        "self_referencing_type_names",
                    ]
                        + NewNamespaceScopedStatementTrait.RegionlessAttributesArgs()
                        + TemplatedStatementTrait.RegionlessAttributesArgs()
                        + ConstrainedStatementTrait.RegionlessAttributesArgs()
                    ,
                    "finalize": False,
                },
            },
        )

        self._InitTraits(
            allow_duplicate_names=True,
            allow_name_to_be_duplicated=False,
        )

        # Set defaults
        if visibility_param is None:
            if self.parent_class_capabilities is not None:
                visibility_param = self.parent_class_capabilities.default_nested_class_visibility
            else:
                visibility_param = self.class_capabilities.default_visibility

            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        NewNamespaceScopedStatementTrait.__post_init__(self, visibility_param)
        TemplatedStatementTrait.__post_init__(self, templates_param)
        ConstrainedStatementTrait.__post_init__(self, constraints_param)

        if class_modifier_param is None:
            class_modifier_param = self.class_capabilities.default_class_modifier
            object.__setattr__(self.regions__, "class_modifier", self.regions__.self__)

        object.__setattr__(self, "class_modifier", class_modifier_param)

        if constructor_visibility_param is None:
            constructor_visibility_param = VisibilityModifier.public
            object.__setattr__(self.regions__, "constructor_visibility", self.regions__.self__)

        object.__setattr__(self, "constructor_visibility", constructor_visibility_param)

        for dependencies, default_visibility in [
            (self.extends, self.class_capabilities.default_extends_visibility),
            (self.implements, self.class_capabilities.default_implements_visibility),
            (self.uses, self.class_capabilities.default_uses_visibility),
        ]:
            if dependencies is None:
                continue

            for dependency in dependencies:
                if dependency.visibility is None:
                    object.__setattr__(dependency, "visibility", default_visibility)
                    object.__setattr__(dependency.regions__, "visibility", dependency.regions__.self__)

        self._Finalize()

        # Validate
        errors: List[Error] = []

        try:
            self.class_capabilities.ValidateClassStatementCapabilities(
                self,
                has_parent_class=self.parent_class_capabilities is not None,
            )
        except ErrorException as ex:
            errors += ex.errors

        if self.parent_class_capabilities is not None:
            try:
                self.parent_class_capabilities.ValidateNestedClassStatementCapabilities(self)
            except ErrorException as ex:
                errors += ex.errors

        else:
            if self.visibility == VisibilityModifier.protected:
                errors.append(
                    InvalidProtectedError.Create(
                        region=self.regions__.visibility,
                    ),
                )

        if self.statements is None:
            errors.append(
                StatementsRequiredError.Create(
                    region=self.regions__.self__,
                ),
            )

        else:
            # Ensure that the class or any of its named statements are the same as the self-referencing type names
            if self.self_referencing_type_names is not None:
                for statement in itertools.chain([self, ], self.statements):
                    if not isinstance(statement, NamedTrait):
                        continue

                    if statement.name in self.self_referencing_type_names:
                        errors.append(
                            InvalidReservedNameError.Create(
                                region=statement.regions__.name,
                                name=statement.name,
                            ),
                        )

        # TODO: Create default special methods as necessary
        # TODO: Create a static 'Create' method if one does not already exist

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetValidScopes() -> Dict[ParserInfoType, ScopeFlag]:
        return {
            ParserInfoType.Standard: ScopeFlag.Root | ScopeFlag.Class | ScopeFlag.Function,
        }

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsNameOrdered(
        scope_flag: ScopeFlag,
    ) -> bool:
        return bool(scope_flag & ScopeFlag.Function)

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        # TODO: The functionality for templates and constraints should eventually live in the traits class
        if self.templates:
            yield "templates", self.templates  # type: ignore

        if self.constraints:
            yield "constraints", self.constraints  # type: ignore

        if self.extends:
            yield "extends", self.extends  # type: ignore

        if self.implements:
            yield "implements", self.implements  # type: ignore

        if self.uses:
            yield "uses", self.uses  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConcreteType(
        self,
        entity_resolver: EntityResolver,
    ) -> ClassType:
        return ClassType(self, ConcreteClass.Create(self, entity_resolver))

    # ----------------------------------------------------------------------
    @Interface.override
    def _GetUniqueId(self) -> Tuple[Any, ...]:
        assert self.templates is None
        assert self.constraints is None
        assert self.extends is None
        assert self.implements is None
        assert self.uses is None

        return ()
