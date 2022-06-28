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
    from ..Common.MethodHierarchyModifier import MethodHierarchyModifier
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

# TODO: Use this
DuplicateUsingStatementError                = CreateError(
    "A using statement for '{class_name}' and '{type_name}' has already been defined",
    class_name=str,
    type_name=str,
    prev_region=TranslationUnitRegion,
)

InvalidDependencyError                      = CreateError(
    "Invalid dependency",
)

InvalidEvalTemplatesMethodError             = CreateError(
    "The method to evaluate templates may only be used with classes that have templates",
)

InvalidEvalConstraintsMethodError           = CreateError(
    "The method to evaluate constraints may only be used with classes that have constraints",
)

InvalidFinalizeMethodError                  = CreateError(
    "Finalization methods are not valid for classes that are created as finalized",
)

FinalDependencyError                        = CreateError(
    "The class '{name}' is final and cannot be extended",
    name=str,
    final_class_region=TranslationUnitRegion,
)

MissingAbstractMethodsError                 = CreateError(
    "The class is marked as abstract, but no abstract methods were encountered",
)

InvalidFinalError                           = CreateError(
    "The class is marked as final, but abstract methods were encountered",
)


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeDependency(object):
    # ----------------------------------------------------------------------
    # |  Public Types
    NonDependencyParserInfoType              = Union[
        ClassAttributeStatementParserInfo,
        "ClassStatementParserInfo",
        FuncDefinitionStatementParserInfo,
        TypeAliasStatementParserInfo,
    ]

    # ----------------------------------------------------------------------
    # |  Public Data
    visibility: VisibilityModifier
    dependency_parser_info: Union["ClassStatementDependencyParserInfo", "ClassStatementParserInfo"]

    next_or_parser_info: Union[
        "TypeDependency",
        NonDependencyParserInfoType,
    ]

    # ----------------------------------------------------------------------
    # |  Public Methods
    def EnumDependencies(self) -> Generator["TypeDependency", None, None]:
        yield self

        if isinstance(self.next_or_parser_info, TypeDependency):
            yield from self.next_or_parser_info.EnumDependencies()

    # ----------------------------------------------------------------------
    def Resolve(self) -> "TypeDependency.NonDependencyParserInfoType":
        *_, recent_type_dependency = self.EnumDependencies()

        assert not isinstance(recent_type_dependency.next_or_parser_info, TypeDependency), recent_type_dependency.next_or_parser_info.next_or_parser_info
        return recent_type_dependency.next_or_parser_info


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeDependencies(object):
    # ----------------------------------------------------------------------
    local: List[TypeDependency]
    augmented: List[TypeDependency]
    inherited: List[TypeDependency]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        local: List[TypeDependency],
        augmented: List[TypeDependency],
        inherited: List[TypeDependency],
        get_key_func: Callable[[TypeDependency], Any],
        postprocess_func: Optional[
            Callable[
                [
                    List[TypeDependency],
                    List[TypeDependency],
                    List[TypeDependency],
                ],
                Tuple[
                    List[TypeDependency],
                    List[TypeDependency],
                    List[TypeDependency],
                ],
            ]
        ]=None,
    ):
        lookup = set()

        local = cls._FilterCreateList(local, get_key_func, lookup)
        augmented = cls._FilterCreateList(augmented, get_key_func, lookup)
        inherited = cls._FilterCreateList(inherited, get_key_func, lookup)

        if postprocess_func:
            local, augmented, inherited = postprocess_func(local, augmented, inherited)

        return cls(local, augmented, inherited)

    # ----------------------------------------------------------------------
    def Enum(
        self,
        inherited_visibility: VisibilityModifier,
        *,
        process_private_items: bool,
    ) -> Generator[
        Tuple[
            VisibilityModifier,
            TypeDependency
        ],
        None,
        None,
    ]:
        for dependency in itertools.chain(self.local, self.augmented, self.inherited):
            effective_visibility = VisibilityModifier(
                min(inherited_visibility.value, dependency.visibility.value),
            )

            if effective_visibility == VisibilityModifier.private and not process_private_items:
                continue

            yield effective_visibility, dependency

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _FilterCreateList(
        items: List[TypeDependency],
        get_key_func: Callable[[TypeDependency], Any],
        lookup: Set[Any],
    ) -> List[TypeDependency]:
        results: List[TypeDependency] = []

        for item in items:
            key = get_key_func(item)

            if key in lookup:
                continue

            results.append(item)
            lookup.add(key)

        return results


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ConcreteTypeInfo(object):
    """Information about a concrete instantiation of a type (taking templates into account)"""

    # ----------------------------------------------------------------------
    # |  Public Types
    AttributesType                          = Dict[
        str,                                # name
        Dict[
            VisibilityModifier,
            TypeDependency
        ],
    ]

    # ----------------------------------------------------------------------
    # BugBug: This Enum feels strange here; not sure how to think about this with
    #       `TypeDependencies`
    class EnumType(Flag):
        local                               = auto()
        augmented                           = auto()
        inherited                           = auto()

        Local                               = local
        Augmented                           = local | augmented
        All                                 = local | augmented | inherited

    # ----------------------------------------------------------------------
    # |  Public Data
    base: Optional[TypeDependency]
    special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo]

    interfaces: TypeDependencies
    concepts: TypeDependencies
    types: TypeDependencies
    attributes: TypeDependencies
    abstract_methods: TypeDependencies
    methods: TypeDependencies



    # BugBug: Following are dependent upon method type
    # BugBug: name, visibility
    # BugBug local_attributes: Dict[str, TypeDependency]
    # BugBug local_methods: Dict[str, TypeDependency]
    # BugBug
    # BugBug all_attributes: Dict[str, List[TypeDependency]]
    # BugBug all_methods: Dict[str, List[TypeDependency]]


    # BugBug: Method to extrapolate by method type




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

    _concrete_types_lock: threading.Lock    = field(init=False, default_factory=threading.Lock)
    _concrete_types: List[
        Tuple[
            Optional[TemplateArgumentsParserInfo],
            "ConcreteTypeInfo",
        ]
    ]                                                   = field(init=False, default_factory=list)

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
            for dependency, resolved_dependency in self._EnumDependencies(None):
                if resolved_dependency.Initialize() is False:
                    initialize_result = False
                    break

            if not self.templates or self.templates.default_initializable:  # pylint: disable=no-member
                self.GetOrCreateConcreteTypeInfo(None)

        except ErrorException:
            initialize_result = False
            raise

        finally:
            object.__setattr__(self, "_initialize_result", initialize_result)

        return initialize_result

    # ----------------------------------------------------------------------
    def GetOrCreateConcreteTypeInfo(
        self,
        template_arguments_parser_info: Optional[TemplateArgumentsParserInfo],
    ) -> "ConcreteTypeInfo":
        if template_arguments_parser_info is None:
            is_match_func = lambda template_arguments: template_arguments is None
        else:
            is_match_func = lambda template_arguments: template_arguments is not None and template_arguments == template_arguments_parser_info

        with cast(threading.Lock, self._concrete_types_lock):  # pylint: disable=not-context-manager
            for template_arguments, potential_concrete_type in self._concrete_types:  # pylint: disable=not-an-iterable
                if is_match_func(template_arguments):
                    return potential_concrete_type

        if template_arguments_parser_info is not None:
            raise NotImplementedError("TODO: Templates")

        if self.templates is not None:
            raise NotImplementedError("TODO: Templates with defaults")

        errors: List[Error] = []

        base: Optional[TypeDependency] = None

        local_interfaces: List[TypeDependency] = []
        local_concepts: List[TypeDependency] = []

        augmented_interfaces: List[TypeDependency] = []
        augmented_concepts: List[TypeDependency] = []
        augmented_types: List[TypeDependency] = []
        augmented_attributes: List[TypeDependency] = []
        augmented_abstract_methods: List[TypeDependency] = []
        augmented_methods: List[TypeDependency] = []

        dependency_interfaces: List[TypeDependency] = []
        dependency_concepts: List[TypeDependency] = []
        dependency_types: List[TypeDependency] = []
        dependency_attributes: List[TypeDependency] = []
        dependency_abstract_methods: List[TypeDependency] = []
        dependency_methods: List[TypeDependency] = []

        for dependency, resolved_dependency in self._EnumDependencies(
            None, # TODO
        ):
            if resolved_dependency.is_final:
                errors.append(
                    FinalDependencyError.Create(
                        region=dependency.type.regions__.self__,
                        name=resolved_dependency.name,
                        final_class_region=resolved_dependency.regions__.self__,
                    ),
                )
                continue

            assert dependency.visibility is not None

            hierarchy_methods_are_polymorphic = True

            interfaces_target: Optional[List[TypeDependency]] = None
            concepts_target: Optional[List[TypeDependency]] = None
            types_target: Optional[List[TypeDependency]] = None
            attributes_target: Optional[List[TypeDependency]] = None
            abstract_methods_target: Optional[List[TypeDependency]] = None
            methods_target: Optional[List[TypeDependency]] = None

            if (
                resolved_dependency.class_capabilities.name == "Mixin"
                or resolved_dependency.class_capabilities.name == "Concept",
            ):
                hierarchy_methods_are_polymorphic = False

                interfaces_target = augmented_interfaces
                concepts_target = augmented_concepts
                types_target = augmented_types
                attributes_target = augmented_attributes
                abstract_methods_target = augmented_abstract_methods
                methods_target = augmented_methods

                if resolved_dependency.class_capabilities.name == "Concept":
                    local_concepts.append(
                        TypeDependency(
                            dependency.visibility,
                            dependency,
                            resolved_dependency,
                        ),
                    )

            else:
                interfaces_target = dependency_interfaces
                concepts_target = dependency_concepts
                types_target = dependency_types
                attributes_target = dependency_attributes
                abstract_methods_target = dependency_abstract_methods
                methods_target = dependency_methods

                if resolved_dependency.class_capabilities.name == "Interface":
                    local_interfaces.append(
                        TypeDependency(
                            dependency.visibility,
                            dependency,
                            resolved_dependency,
                        ),
                    )
                else:
                    assert base is None, base

                    base = TypeDependency(
                        dependency.visibility,
                        dependency,
                        resolved_dependency,
                    )

            assert interfaces_target is not None
            assert concepts_target is not None
            assert abstract_methods_target is not None
            assert types_target is not None
            assert attributes_target is not None
            assert methods_target is not None

            # Process the dependency
            concrete_type_info = resolved_dependency.GetOrCreateConcreteTypeInfo(
                None, # TODO
            )

            for attribute_name, target, process_private_items in [
                ("interfaces", interfaces_target, False),
                ("concepts", concepts_target, False),
                ("types", types_target, False),
                ("attributes", attributes_target, False),
                ("abstract_methods", abstract_methods_target, True),
                ("methods", methods_target, False),
            ]:
                for type_dependency_visibility, type_dependency in getattr(concrete_type_info, attribute_name).Enum(
                    dependency.visibility,
                    process_private_items=process_private_items,
                ):
                    target.append(
                        TypeDependency(
                            type_dependency_visibility,
                            dependency,
                            type_dependency,
                        ),
                    )

        # Process the local statements
        special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo] = {}
        local_types: List[TypeDependency] = []
        local_attributes: List[TypeDependency] = []
        local_abstract_methods: List[TypeDependency] = []
        local_methods: List[TypeDependency] = []

        assert self.statements is not None
        for statement in self.statements:
            if statement.is_disabled__:
                continue

            if isinstance(statement, ClassAttributeStatementParserInfo):
                local_attributes.append(
                    TypeDependency(
                        statement.visibility,
                        self,
                        statement,
                    ),
                )

            elif isinstance(statement, ClassStatementParserInfo):
                local_types.append(
                    TypeDependency(
                        statement.visibility,
                        self,
                        statement,
                    ),
                )

            elif isinstance(statement, ClassUsingStatementParserInfo):
                pass # BugBug

            elif isinstance(statement, FuncDefinitionStatementParserInfo):
                if statement.method_hierarchy_modifier == MethodHierarchyModifier.abstract:
                    local_abstract_methods.append(
                        TypeDependency(
                            statement.visibility,
                            self,
                            statement,
                        ),
                    )

                else:
                    local_methods.append(
                        TypeDependency(
                            statement.visibility,
                            self,
                            statement,
                        ),
                    )

            elif isinstance(statement, SpecialMethodStatementParserInfo):
                if (
                    statement.special_method_type == SpecialMethodType.CompileTimeEvalTemplates
                    and not self.templates
                ):
                    errors.append(
                        InvalidEvalTemplatesMethodError.Create(
                            region=statement.regions__.self__,
                        ),
                    )
                    continue

                if (
                    statement.special_method_type == SpecialMethodType.CompileTimeEvalConstraints
                    and not self.constraints
                ):
                    errors.append(
                        InvalidEvalConstraintsMethodError.Create(
                            region=statement.regions__.self__,
                        ),
                    )
                    continue

                if (
                    (
                        statement.special_method_type == SpecialMethodType.PrepareFinalize
                        or statement.special_method_type == SpecialMethodType.Finalize
                    )
                    and self.class_modifier == ClassModifier.immutable
                ):
                    errors.append(
                        InvalidFinalizeMethodError.Create(
                            region=statement.regions__.self__,
                        ),
                    )
                    continue

                prev_special_method = special_methods.get(statement.special_method_type, None)
                if prev_special_method is not None:
                    errors.append(
                        DuplicateSpecialMethodError.Create(
                            region=statement.regions__.special_method_type,
                            name=statement.special_method_type,
                            prev_region=prev_special_method.regions__.special_method_type,
                        ),
                    )
                    continue

                special_methods[statement.special_method_type] = statement

            elif isinstance(statement, TypeAliasStatementParserInfo):
                local_types.append(
                    TypeDependency(
                        statement.visibility,
                        self,
                        statement,
                    ),
                )

            else:
                assert False, statement  # pragma: no cover

        if self.is_abstract and not local_abstract_methods:
            errors.append(
                MissingAbstractMethodsError.Create(
                    region=self.regions__.is_abstract,
                ),
            )

        if (
            self.is_final
            and (
                local_abstract_methods
                or augmented_abstract_methods
                or dependency_abstract_methods
            )
        ):
            errors.append(
                InvalidFinalError.Create(
                    region=self.regions__.is_final,
                ),
            )

        # BugBug: Check for method hierarchy errors
        # BugBug: Check for mutabilty errors


        if errors:
            raise ErrorException(*errors)

        # ----------------------------------------------------------------------
        def StandardKeyExtractor(
            dependency: TypeDependency,
        ) -> str:
            return dependency.Resolve().name

        # ----------------------------------------------------------------------
        def MethodKeyExtractor(
            dependency: TypeDependency,
        ):
            resolved_dependency = dependency.Resolve()
            assert isinstance(resolved_dependency, FuncDefinitionStatementParserInfo), resolved_dependency

            return resolved_dependency.GetOverrideId()

        # ----------------------------------------------------------------------
        def PostprocessMethodDependencies(
            local: List[TypeDependency],
            augmented: List[TypeDependency],
            inherited: List[TypeDependency],
        ) -> Tuple[
            List[TypeDependency],
            List[TypeDependency],
            List[TypeDependency],
        ]:
            # BugBug
            return local, augmented, inherited

        # ----------------------------------------------------------------------

        abstract_methods = TypeDependencies.Create(
            local_abstract_methods,
            augmented_abstract_methods,
            dependency_abstract_methods,
            MethodKeyExtractor,
        )

        methods = TypeDependencies.Create(
            local_methods,
            augmented_methods,
            dependency_methods,
            MethodKeyExtractor,
            PostprocessMethodDependencies,
        )

        result = ConcreteTypeInfo(
            base,
            special_methods,
            TypeDependencies.Create(
                local_interfaces,
                augmented_interfaces,
                dependency_interfaces,
                StandardKeyExtractor,
            ),
            TypeDependencies.Create(
                local_concepts,
                augmented_concepts,
                dependency_concepts,
                StandardKeyExtractor,
            ),
            TypeDependencies.Create(
                local_types,
                augmented_types,
                dependency_types,
                StandardKeyExtractor,
            ),
            TypeDependencies.Create(
                local_attributes,
                augmented_attributes,
                dependency_attributes,
                StandardKeyExtractor,
            ),
            abstract_methods,
            methods,
        )

        # Cache the result
        with cast(threading.Lock, self._concrete_types_lock):  # pylint: disable=not-context-manager
            self._concrete_types.append((template_arguments_parser_info, result))  # pylint: disable=no-member

        return result

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
            ClassStatementDependencyParserInfo,
            "ClassStatementParserInfo",
        ],
        None,
        None,
    ]:
        for dependency in itertools.chain(
            (self.implements or []),        # pylint: disable=protected-access
            (self.uses or []),              # pylint: disable=protected-access
            (self.extends or []),           # pylint: disable=protected-access
        ):
            if dependency.is_disabled__:
                continue

            resolved_parser_info = dependency.type.resolved_type__.Resolve().parser_info

            if not isinstance(resolved_parser_info, ClassStatementParserInfo):
                raise ErrorException(
                    InvalidDependencyError.Create(
                        region=dependency.regions__.self__,
                    ),
                )

            yield dependency, resolved_parser_info
