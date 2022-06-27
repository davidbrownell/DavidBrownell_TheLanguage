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

import os
import threading

from enum import auto, Enum
from typing import Any, Dict, Generator, List, Optional, Set, Tuple, Union

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
    from .StatementParserInfo import (
        ParserInfo,
        ParserInfoType,
        ScopeFlag,
        StatementParserInfo,
        TranslationUnitRegion,
    )

    from .ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from .ClassUsingStatementParserInfo import ClassUsingStatementParserInfo
    from .FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo, OperatorType as FuncDefinitionOperatorType
    from .PassStatementParserInfo import PassStatementParserInfo
    from .SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo, SpecialMethodType
    from .TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from .Traits.NewNamespaceScopedStatementTrait import NewNamespaceScopedStatementTrait
    from .Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Common.ClassModifier import ClassModifier
    from ..Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
    from ..Common.ConstraintParametersParserInfo import ConstraintParameterParserInfo
    from ..Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo
    from ..Common.VisibilityModifier import VisibilityModifier, InvalidProtectedError

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
CycleDetectedError                          = CreateError(
    "An inheritance cycle was detected with '{name}'",
    name=str,
)

StatementsRequiredError                     = CreateError(
    "Statements are required",
)

DuplicateSpecialMethodError                 = CreateError(
    "The special method '{name}' has already been defined",
    name=str,
    prev_region=TranslationUnitRegion,
)


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
            regionless_attributes=["type", ],
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
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class InstantiationInfo(object):
        """Information about the class when instantiated with a specific set of valid templates"""

        # ----------------------------------------------------------------------
        # |  Public Types
        AttributesType                      = Dict[
            VisibilityModifier,
            Dict[
                str,
                ClassAttributeStatementParserInfo,
            ],
        ]

        MethodsType                         = Dict[
            VisibilityModifier,
            Dict[
                Union[str, FuncDefinitionOperatorType],
                List[FuncDefinitionStatementParserInfo]
            ]
        ]

        SpecialMethodsType                  = Dict[
            SpecialMethodType,
            SpecialMethodStatementParserInfo,
        ]

        TypesType                           = Dict[
            VisibilityModifier,
            Dict[
                str,
                Union["ClassStatementParserInfo", TypeAliasStatementParserInfo],
            ],
        ]

        # ----------------------------------------------------------------------
        # |  Public Data
        base: Optional["ClassStatementParserInfo"]

        interfaces: Dict[
            VisibilityModifier,
            List["ClassStatementParserInfo"],
        ]

        my_attributes: AttributesType
        my_methods: MethodsType
        my_special_methods: SpecialMethodsType
        my_types: TypesType

        all_types: Dict[
            VisibilityModifier,
            List[Union["ClassStatementParserInfo", TypeAliasStatementParserInfo]],
        ]

        all_methods: Dict[
            VisibilityModifier,
            List[Union[FuncDefinitionStatementParserInfo, SpecialMethodStatementParserInfo]],
        ]

        all_attributes: Dict[
            VisibilityModifier,
            List[ClassAttributeStatementParserInfo],
        ]

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    parent_class_capabilities: Optional[ClassCapabilities]
    class_capabilities: ClassCapabilities

    class_modifier_param: InitVar[Optional[ClassModifier]]
    class_modifier: ClassModifier           = field(init=False)

    documentation: Optional[str]

    constraints: Optional[ConstraintParameterParserInfo]

    extends: Optional[List[ClassStatementDependencyParserInfo]]
    implements: Optional[List[ClassStatementDependencyParserInfo]]
    uses: Optional[List[ClassStatementDependencyParserInfo]]

    constructor_visibility_param: InitVar[Optional[VisibilityModifier]]
    constructor_visibility: VisibilityModifier          = field(init=False)

    is_abstract: Optional[bool]
    is_final: Optional[bool]

    # Values set after calls to `Initialize`
    _initialize_result: Union[
        DoesNotExist,                       # Not initialized
        None,                               # In the process of initializing
        bool,                               # Successful/Unsuccessful initialization
    ]                                       = field(init=False, default=DoesNotExist.instance)

    _instantiation_info_lock: threading.Lock            = field(init=False, default_factory=threading.Lock)
    _instantiation_info: Dict[
        Any, # TODO: Not sure how to represent this yet
        "ClassStatementParserInfo.InstantiationInfo"
    ]                                                   = field(init=False, default_factory=dict)

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
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
        class_modifier_param,
        constructor_visibility_param,
    ):
        StatementParserInfo.__post_init__(
            self,
            parser_info_type,
            regions,
            validate=False,
            regionless_attributes=[
                "parent_class_capabilities",
                "class_capabilities",
                "constraints",
            ]
                + NewNamespaceScopedStatementTrait.RegionlessAttributesArgs()
                + TemplatedStatementTrait.RegionlessAttributesArgs()
            ,
            **{
                **{
                    "parent_class_capabilities": lambda value: None if value is None else value.name,
                    "class_capabilities": lambda value: value.name,
                },
                **NewNamespaceScopedStatementTrait.ObjectReprImplBaseInitKwargs(),
                **TemplatedStatementTrait.ObjectReprImplBaseInitKwargs(),
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

        self.ValidateRegions()

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
    @Interface.override
    def GenerateDynamicTypeNames(self) -> Generator[str, None, None]:
        yield "ThisType"

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsNameOrdered(
        scope_flag: ScopeFlag,
    ) -> bool:
        return bool(scope_flag & ScopeFlag.Function)

    # ----------------------------------------------------------------------
    def Initialize(self) -> bool:
        if self._initialize_result is None:
            raise ErrorException(
                CycleDetectedError.Create(
                    region=self.regions__.self__,
                    name=self.name,
                ),
            )

        if isinstance(self._initialize_result, bool):
            return self._initialize_result

        object.__setattr__(self, "_initialize_result", None)
        initialize_result = True

        try:
            for dependency_type, dependency, resolved_dependency in self._EnumDependencies(None):
                if resolved_dependency.Initialize() is False:
                    initialize_result = False
                    break

            if not self.templates or self.templates.default_initializable:  # pylint: disable=no-member
                self.Validate(None)

        except ErrorException:
            initialize_result = False
            raise

        finally:
            object.__setattr__(self, "_initialize_result", initialize_result)

        return initialize_result

    # ----------------------------------------------------------------------
    def Validate(
        self,
        template_arguments_parser_info: Optional[TemplateArgumentsParserInfo],
    ) -> None:
        if template_arguments_parser_info is not None:
            raise NotImplementedError("TODO: Templates")

        if self.templates is not None:
            raise NotImplementedError("TODO: Templates with defaults")

        errors: List[Error] = []

        # Collect information about the statements associated with this class
        my_attributes: ClassStatementParserInfo.InstantiationInfo.AttributesType = {}
        my_methods: ClassStatementParserInfo.InstantiationInfo.MethodsType = {}
        my_special_methods: ClassStatementParserInfo.InstantiationInfo.SpecialMethodsType = {}
        my_types: ClassStatementParserInfo.InstantiationInfo.TypesType = {}
        using_statements: List[ClassUsingStatementParserInfo] = []
        is_abstract = False
        is_deferred = False

        assert self.statements is not None

        for statement in self.statements:
            # BugBug: import statement?
            if isinstance(statement, ClassAttributeStatementParserInfo):
                my_attributes.setdefault(statement.visibility, {})[statement.name] = statement

            elif isinstance(statement, ClassStatementParserInfo):
                my_types.setdefault(statement.visibility, {})[statement.name] = statement

            elif isinstance(statement, ClassUsingStatementParserInfo):
                using_statements.append(statement)

            elif isinstance(statement, FuncDefinitionStatementParserInfo):
                is_abstract = is_abstract or statement.is_abstract
                is_deferred = is_deferred or statement.is_deferred

                my_methods.setdefault(
                    statement.visibility,
                    {},
                ).setdefault(statement.name, []).append(statement)

            elif isinstance(statement, PassStatementParserInfo):
                # Nothing to do here
                pass

            elif isinstance(statement, SpecialMethodStatementParserInfo):
                assert statement.visibility is VisibilityModifier.private, statement.visibility

                prev_method = my_special_methods.get(statement.special_method_type, None)
                if prev_method is not None:
                    errors.append(
                        DuplicateSpecialMethodError.Create(
                            region=statement.regions__.self__,
                            prev_region=prev_method.regions__.self__,
                            name=statement.special_method_type.value,
                        ),
                    )

                my_special_methods[statement.special_method_type] = statement

            elif isinstance(statement, TypeAliasStatementParserInfo):
                my_types.setdefault(statement.visibility, {})[statement.name] = statement

            else:
                assert False, statement  # pragma: no cover

        # Collect information about the dependencies
        base: Optional[Tuple[VisibilityModifier, ClassStatementParserInfo]] = None
        mixins: List[Tuple[VisibilityModifier, ClassStatementParserInfo]] = []
        interfaces: List[Tuple[VisibilityModifier, ClassStatementParserInfo]] = []
        concepts: List[Tuple[VisibilityModifier, ClassStatementParserInfo]] = []

        for dependency_type, dependency, resolved_dependency in self._EnumDependencies(
            template_arguments_parser_info,
        ):
            assert dependency.visibility is not None

            instantiation_info = resolved_dependency.GetInstantiationInfo(None)

            if dependency_type == self.__class__._DependencyType.Extends:  # pylint: disable=protected-access
                assert base is None, base
                base = dependency.visibility, resolved_dependency
            elif dependency_type == self.__class__._DependencyType.Uses:  # pylint: disable=protected-access
                mixins.append((dependency.visibility, resolved_dependency))
            elif dependency_type == self.__class__._DependencyType.Implements:  # pylint: disable=protected-access
                if resolved_dependency.class_capabilities.name == "Concept":
                    concepts.append((dependency.visibility, resolved_dependency))
                elif resolved_dependency.class_capabilities.name == "Interface":
                    interfaces.append((dependency.visibility, resolved_dependency))
                else:
                    assert False, resolved_dependency.class_capabilities.name  # pragma: no cover
            else:
                assert False, dependency_type  # pragma: no cover

        # BugBug: Collect my information
        # BugBug: Squash
        # BugBug: Validate
        # BugBug: Populate defaults

        # BugBUg: TODO:
        #       is_deferred
        #       is_instantiatable
        #       Validate method modifiers match class modifier

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    def GetInstantiationInfo(
        self,
        template_arguments_parser_info: Optional[TemplateArgumentsParserInfo],
    ) -> "ClassStatementParserInfo.InstantiationInfo":
        pass # BugBug
        return None

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    class _DependencyType(Enum):
        Extends                             = auto()
        Uses                                = auto()
        Implements                          = auto()

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
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
    def _EnumDependencies(
        self,
        template_arguments_parser_info: Optional[TemplateArgumentsParserInfo],
    ) -> Generator[
        Tuple[
            "ClassStatementParserInfo._DependencyType",
            ClassStatementDependencyParserInfo,
            "ClassStatementParserInfo",
        ],
        None,
        None,
    ]:
        for dependency_type, dependencies in [
            (self.__class__._DependencyType.Extends, self.extends or []),        # pylint: disable=protected-access
            (self.__class__._DependencyType.Uses, self.uses or []),              # pylint: disable=protected-access
            (self.__class__._DependencyType.Implements, self.implements or []),  # pylint: disable=protected-access
        ]:
            for dependency in dependencies:
                if dependency.is_disabled__:
                    continue

                yield (
                    dependency_type,
                    dependency,
                    dependency.type.resolved_type__.Resolve().parser_info,
                )

# TODO: Ensure that all contents have mutability values consistent with the class decoration
