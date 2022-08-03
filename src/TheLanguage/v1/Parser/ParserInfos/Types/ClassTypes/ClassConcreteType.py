# ----------------------------------------------------------------------
# |
# |  ClassConcreteType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-26 15:17:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassConcreteType object"""

import itertools
import os

from typing import Any, Callable, cast, Dict, Generator, Generic, Iterator, List, Optional, Tuple, TypeVar, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl.ClassContent import ClassContent
    from .Impl.Dependency import Dependency, DependencyLeaf, DependencyNode

    from ..ConcreteType import ConcreteType
    from ..ConstrainedType import ConstrainedType
    from ..GenericType import GenericType
    from ..TypeResolver import TypeResolver

    from ..FuncDefinitionTypes.FuncDefinitionConcreteType import FuncDefinitionConcreteType

    from ...Common.ClassModifier import ClassModifier
    from ...Common.MethodHierarchyModifier import MethodHierarchyModifier
    from ...Common.MutabilityModifier import MutabilityModifier
    from ...Common.VisibilityModifier import VisibilityModifier

    from ...Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo

    from ...Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ...Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ...Statements.ClassUsingStatementParserInfo import ClassUsingStatementParserInfo
    from ...Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo, SpecialMethodType
    from ...Statements.StatementParserInfo import StatementParserInfo
    from ...Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ...Statements.Traits.ConstrainedStatementTrait import ConstrainedStatementTrait

    from ....Error import CreateError, Error, ErrorException

    from ...Traits.NamedTrait import NamedTrait

    from ....TranslationUnitRegion import TranslationUnitRegion


# ----------------------------------------------------------------------
InvalidResolvedDependencyError              = CreateError(
    "Invalid dependency",
)

FinalDependencyError                        = CreateError(
    "The class '{name}' is final and cannot be extended",
    name=str,
    final_class_region=TranslationUnitRegion,
)

MultipleBasesError                          = CreateError(
    "A base has already been provided",
    prev_region=TranslationUnitRegion,
)

DuplicateSpecialMethodError                 = CreateError(
    "This special method has already been defined",
    prev_region=TranslationUnitRegion,
)

InvalidEvalTemplatesMethodError             = CreateError(
    "The EvalTemplates method is not valid for classes without templates",
)

InvalidEvalConstraintsMethodError           = CreateError(
    "The EvalConstraints method is not valid for classes without constraints",
)

InvalidFinalizeMethodError                  = CreateError(
    "Finalize methods are not valid for classes that are not mutable",
)

InvalidAbstractDecorationError              = CreateError(
    "The class is marked as abstract, but no abstract methods were encountered",
)

InvalidFinalDecorationError                 = CreateError(
    "The class is marked as final, but abstract methods were encountered",
)

InvalidMutableDecorationError               = CreateError(
    "The class is marked as mutable, but no mutable methods were found",
)

InvalidOverrideDecorationError              = CreateError(
    "The method is marked as overridable, but no base method matched its signature",
)

InvalidMutableAttributeError                = CreateError(
    "The attribute is marked as mutable but the class is immutable",
    class_region=TranslationUnitRegion,
)

InvalidMutableMethodError                   = CreateError(
    "The method is marked as mutable but the class is immutable",
    class_region=TranslationUnitRegion,
)

FinalMethodOverrideError                    = CreateError(
    "The method '{name}' is marked as final and cannot be overridden",
    name=str,
    base_region=TranslationUnitRegion,
)

OverlappedVirtualRootMethodError            = CreateError(
    "The method '{name}' has overridden an existing method",
    name=str,
    base_region=TranslationUnitRegion,
)

OverlappedWithStaticMethodError             = CreateError(
    "The static method '{name}' has overridden a non-static method",
    name=str,
    base_region=TranslationUnitRegion,
)

OverlappedWithNonStaticMethodError          = CreateError(
    "The non-static method '{name}' has overridden a static method",
    name=str,
    base_region=TranslationUnitRegion,
)

RootOverlappedHierarchyMethodError          = CreateError(
    "The root method '{name}' has overridden a hierarchy method; did you mean 'override'?",
    name=str,
    base_region=TranslationUnitRegion,
)

OverlappedNonHierararchyMethodError         = CreateError(
    "The hierarchy method '{name}' is attempting to override a non-hierarchy method",
    name=str,
    base_region=TranslationUnitRegion,
)

OverlappedHierarchyMethodError              = CreateError(
    "The non-hierarchy method '{name}' is attempting to override a hierarchy method",
    name=str,
    base_region=TranslationUnitRegion,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class AttributeInfo(object):
    # ----------------------------------------------------------------------
    statement: ClassAttributeStatementParserInfo
    concrete_type: ConcreteType
    mutability_modifier: Optional[MutabilityModifier]


# ----------------------------------------------------------------------
class ClassConcreteType(ConcreteType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        type_resolver: TypeResolver,
        parser_info: ClassStatementParserInfo,
        expression_parser_info: FuncOrTypeExpressionParserInfo,
        resolved_template_arguments_id: Any,
    ):
        super(ClassConcreteType, self).__init__(
            parser_info,
            is_default_initializable=(
                not isinstance(parser_info, ConstrainedStatementTrait)
                or parser_info.constraints is None
                or parser_info.constraints.is_default_initializable
            ),
        )

        self._type_resolver                             = type_resolver
        self._expression_parser_info                    = expression_parser_info if self.is_default_initializable else None
        self._resolved_template_arguments_id            = resolved_template_arguments_id

        errors: List[Error] = []

        # Process the dependencies
        base_dependency_info: Optional[Tuple[ClassStatementDependencyParserInfo, DependencyNode[ConcreteType]]] = None
        concept_dependencies: List[DependencyNode[ConcreteType]] = []
        interface_dependencies: List[DependencyNode[ConcreteType]] = []
        mixin_dependencies: List[DependencyNode[ConcreteType]] = []

        for dependencies, dependency_validation_func in [
            (
                self.parser_info.implements,
                self.parser_info.class_capabilities.ValidateImplementsDependency,
            ),
            (
                self.parser_info.uses,
                self.parser_info.class_capabilities.ValidateUsesDependency,
            ),
            (
                self.parser_info.extends,
                self.parser_info.class_capabilities.ValidateExtendsDependency,
            ),
        ]:
            if dependencies is None:
                continue

            for dependency_parser_info in dependencies:
                try:
                    concrete_type = self._type_resolver.EvalConcreteType(dependency_parser_info.type)[0]
                    resolved_concrete_type = concrete_type.ResolveAliases()

                    resolved_parser_info = resolved_concrete_type.parser_info

                    if isinstance(resolved_parser_info, NoneExpressionParserInfo):
                        continue

                    if not isinstance(resolved_concrete_type, ClassConcreteType):
                        errors.append(
                            InvalidResolvedDependencyError.Create(
                                region=dependency_parser_info.type.regions__.self__,
                            ),
                        )

                        continue

                    assert isinstance(resolved_parser_info, ClassStatementParserInfo), resolved_parser_info

                    if resolved_parser_info.is_final:
                        errors.append(
                            FinalDependencyError.Create(
                                region=dependency_parser_info.regions__.self__,
                                name=resolved_parser_info.name,  # type: ignore
                                final_class_region=resolved_parser_info.regions__.is_final,
                            ),
                        )

                        continue

                    dependency_validation_func(dependency_parser_info, resolved_parser_info)

                    dependency_node = DependencyNode(
                        dependency_parser_info,
                        DependencyLeaf(concrete_type),
                    )

                    if resolved_parser_info.class_capabilities.name == "Concept":
                        concept_dependencies.append(dependency_node)
                    elif resolved_parser_info.class_capabilities.name == "Interface":
                        interface_dependencies.append(dependency_node)
                    elif resolved_parser_info.class_capabilities.name == "Mixin":
                        mixin_dependencies.append(dependency_node)
                    else:
                        if base_dependency_info is not None:
                            errors.append(
                                MultipleBasesError.Create(
                                    region=dependency_parser_info.regions__.self__,
                                    prev_region=base_dependency_info[0].regions__.self__,  # pylint: disable=unsubscriptable-object
                                ),
                            )

                            continue

                        base_dependency_info = (dependency_parser_info, dependency_node)

                except ErrorException as ex:
                    errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        base_dependency = base_dependency_info[1] if base_dependency_info is not None else None

        # Capture the dependency info
        augmented_info = _InitializationInfo()
        dependency_info = _InitializationInfo()

        for dependencies, target_info in [
            ([base_dependency, ] if base_dependency is not None else [], dependency_info),
            (concept_dependencies, augmented_info),
            (interface_dependencies, dependency_info),
            (mixin_dependencies, augmented_info),
        ]:
            target_info.Merge(dependencies)

        # Process the local info
        local_info = _InitializationInfo()

        local_info.concepts += concept_dependencies
        local_info.interfaces += interface_dependencies
        local_info.mixins += mixin_dependencies

        methods: List[GenericType] = []
        attributes: List[ClassAttributeStatementParserInfo] = []
        special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo] = {}
        using_statements: List[ClassUsingStatementParserInfo] = []

        assert self.parser_info.statements is not None

        for statement in self.parser_info.statements:
            if statement.is_disabled__:
                continue

            try:
                if isinstance(statement, ClassAttributeStatementParserInfo):
                    attributes.append(statement)

                elif isinstance(statement, ClassStatementParserInfo):
                    local_info.types.append(
                        DependencyLeaf(self._type_resolver.GetOrCreateNestedGenericType(statement)),
                    )

                elif isinstance(statement, ClassUsingStatementParserInfo):
                    using_statements.append(statement)

                elif isinstance(statement, FuncDefinitionStatementParserInfo):
                    if (
                        statement.mutability_modifier is not None
                        and statement.mutability_modifier.IsMutable()
                        and self.parser_info.class_modifier != ClassModifier.mutable
                    ):
                        errors.append(
                            InvalidMutableMethodError.Create(
                                region=statement.regions__.mutability_modifier,
                                class_region=self.parser_info.regions__.class_modifier,
                            ),
                        )

                        continue

                    methods.append(self._type_resolver.GetOrCreateNestedGenericType(statement))

                elif isinstance(statement, TypeAliasStatementParserInfo):
                    local_info.types.append(
                        DependencyLeaf(self._type_resolver.GetOrCreateNestedGenericType(statement)),
                    )

                elif isinstance(statement, SpecialMethodStatementParserInfo):
                    prev_special_method = special_methods.get(statement.special_method_type, None)
                    if prev_special_method is not None:
                        errors.append(
                            DuplicateSpecialMethodError.Create(
                                region=statement.regions__.self__,
                                prev_region=prev_special_method.regions__.self__,
                            ),
                        )

                        continue

                    if statement.special_method_type == SpecialMethodType.EvalTemplates:
                        if self.parser_info.templates is None:
                            errors.append(
                                InvalidEvalTemplatesMethodError.Create(
                                    region=statement.regions__.self__,
                                ),
                            )

                            continue

                        assert statement.statements is not None

                        self._type_resolver.EvalStatements(statement.statements)

                    if (
                        statement.special_method_type == SpecialMethodType.EvalConstraints
                        and self.parser_info.constraints is None
                    ):
                        errors.append(
                            InvalidEvalConstraintsMethodError.Create(
                                region=statement.regions__.self__,
                            ),
                        )

                        continue

                    if (
                        statement.special_method_type in [SpecialMethodType.PrepareFinalize, SpecialMethodType.Finalize]
                        and self.parser_info.class_modifier != ClassModifier.mutable
                    ):
                        errors.append(
                            InvalidFinalizeMethodError.Create(
                                region=statement.regions__.self__,
                            ),
                        )

                        continue

                    special_methods[statement.special_method_type] = statement

                else:
                    assert False, statement  # pragma: no cover

            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # Prepare the final results
        concepts = ClassContent.Create(
            local_info.concepts,
            augmented_info.concepts,
            dependency_info.concepts,
            lambda concrete_type: concrete_type.parser_info.name,
        )

        interfaces = ClassContent.Create(
            local_info.interfaces,
            augmented_info.interfaces,
            dependency_info.interfaces,
            lambda concrete_type: concrete_type.parser_info.name,
        )

        mixins = ClassContent.Create(
            local_info.mixins,
            augmented_info.mixins,
            dependency_info.mixins,
            lambda concrete_type: concrete_type.parser_info.name,
        )

        types = ClassContent.Create(
            local_info.types,
            augmented_info.types,
            dependency_info.types,
            lambda generic_type: generic_type.parser_info.name,
        )

        # Commit the info
        self.base_dependency: Optional[DependencyNode[ConcreteType]]        = base_dependency
        self.concept_dependencies: List[DependencyNode[ConcreteType]]       = concept_dependencies
        self.interface_dependencies: List[DependencyNode[ConcreteType]]     = interface_dependencies
        self.mixin_dependencies: List[DependencyNode[ConcreteType]]         = mixin_dependencies

        self.concepts: ClassContent[ConcreteType]                           = concepts
        self.interfaces: ClassContent[ConcreteType]                         = interfaces
        self.mixins: ClassContent[ConcreteType]                             = mixins

        self.types: ClassContent[GenericType]                               = types

        # These values are set after FinalizedPass2 is complete
        self._attributes: Optional[ClassContent[AttributeInfo]]             = None
        self._methods: Optional[ClassContent[GenericType]]                  = None

        # These values will be destroyed after finalization is complete
        self._local_methods: List[GenericType]                              = methods
        self._local_attributes: List[ClassAttributeStatementParserInfo]     = attributes
        self._local_using_statements: List[ClassUsingStatementParserInfo]   = using_statements

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> ClassStatementParserInfo:
        assert isinstance(self._parser_info, ClassStatementParserInfo), self._parser_info
        return self._parser_info

    @property
    def attributes(self) -> ClassContent[AttributeInfo]:
        assert self._attributes is not None
        return self._attributes

    @property
    def methods(self) -> ClassContent[GenericType]:
        assert self._methods is not None
        return self._methods

    # ----------------------------------------------------------------------
    @Interface.override
    def IsMatch(
        self,
        other: ConcreteType,
    ) -> bool:
        if other is self:
            return True

        # Handle the corner case where this is a fundamental type and we are in the process
        # of compiling fundamental types.
        if (
            isinstance(other, ClassConcreteType)
            and self.parser_info.unique_id___ == other.parser_info.unique_id___
            and self._resolved_template_arguments_id == other._resolved_template_arguments_id  # pylint: disable=protected-access
        ):
            return True

        return False

    # ----------------------------------------------------------------------
    @Interface.override
    def IsCovariant(
        self,
        other: ConcreteType,
    ) -> bool:
        if not isinstance(other, ClassConcreteType):
            return False

        if other is self:
            return True

        # ----------------------------------------------------------------------
        def EnumDependencies() -> Generator[ClassConcreteType, None, None]:
            for dependencies in [
                other.concepts,
                other.interfaces,
                other.mixins,
            ]:
                for dependency in dependencies.EnumContent():
                    resolved_visibility, resolved_dependency = dependency.ResolveDependencies()
                    if resolved_visibility != VisibilityModifier.public:
                        continue

                    yield resolved_dependency

            # Walk the base hierarchy
            base_dependency = other.base_dependency

            while base_dependency is not None:
                resolved_visibility, resolved_dependency = base_dependency.ResolveDependencies()

                if resolved_visibility != VisibilityModifier.public:
                    break

                assert isinstance(resolved_dependency, ClassConcreteType), resolved_dependency

                yield resolved_dependency

                base_dependency = resolved_dependency.base_dependency

        # ----------------------------------------------------------------------

        for concrete_dependency in EnumDependencies():
            if concrete_dependency is self:
                return True

            if concrete_dependency.parser_info is self.parser_info:
                assert self.parser_info.templates is not None

                # BugBug: Evaluate the resolved templates for covariance

        return False

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        # Cycles here are bad and will produce errors
        errors: List[Error] = []

        # Finalize the dependencies
        for dependency in itertools.chain(
            [self.base_dependency, ] if self.base_dependency else [],
            self.concept_dependencies,
            self.interface_dependencies,
            self.mixin_dependencies,
        ):
            try:
                dependency.ResolveDependencies()[1].Finalize(ConcreteType.State.FinalizedPass1)
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        # Cycles here are ok
        errors: List[Error] = []

        # Finalize the dependencies
        for dependency in itertools.chain(
            [self.base_dependency, ] if self.base_dependency else [],
            self.concept_dependencies,
            self.interface_dependencies,
            self.mixin_dependencies,
        ):
            try:
                dependency.ResolveDependencies()[1].Finalize(ConcreteType.State.FinalizedPass2)
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # Validate the types
        for dependency in self.types.local:
            try:
                generic_type = dependency.ResolveDependencies()[1]

                if not generic_type.is_default_initializable:
                    continue

                (
                    generic_type
                        .CreateDefaultConcreteType()
                        .Finalize(ConcreteType.State.FinalizedPass1)
                )

            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # Capture the dependency info
        augmented_info = _Pass2Info()
        dependency_info = _Pass2Info()

        for dependencies, target_info in [
            ([self.base_dependency, ] if self.base_dependency is not None else [], dependency_info),
            (self.concept_dependencies, augmented_info),
            (self.interface_dependencies, dependency_info),
            (self.mixin_dependencies, augmented_info),
        ]:
            target_info.Merge(dependencies)

        # Process the local info
        local_info = _Pass2Info()

        # Attributes
        for attribute_statement in self._local_attributes:
            try:
                concrete_attribute, mutability_modifier = self._type_resolver.EvalConcreteType(attribute_statement.type)

                assert mutability_modifier is not None
                if (
                    mutability_modifier.IsMutable()
                    and not self.parser_info.class_modifier != ClassModifier.mutable
                ):
                    errors.append(
                        InvalidMutableAttributeError.Create(
                            region=attribute_statement.type.regions__.self__,
                            class_region=self.parser_info.regions__.class_modifier,
                        ),
                    )

                concrete_attribute.Finalize(ConcreteType.State.FinalizedPass2)

                local_info.attributes.append(
                    DependencyLeaf(
                        AttributeInfo(attribute_statement, concrete_attribute, mutability_modifier),
                    ),
                )

            except ErrorException as ex:
                errors += ex.errors

        # Methods
        for generic_method_type in self._local_methods:
            try:
                if generic_method_type.is_default_initializable:
                    concrete_type = generic_method_type.CreateDefaultConcreteType()

                    concrete_type.Finalize(ConcreteType.State.FinalizedPass2)

                local_info.methods.append(DependencyLeaf(generic_method_type))

            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # Prepare the final results
        attributes = ClassContent.Create(
            local_info.attributes,
            augmented_info.attributes,
            dependency_info.attributes,
            lambda attribute_info: attribute_info.statement.name,
            key_collision_is_error=True,
        )

        method_organizer = _MethodOrganizer(self._local_using_statements)

        methods = ClassContent.Create(
            local_info.methods,
            augmented_info.methods,
            dependency_info.methods,
            method_organizer.GetKey,
            method_organizer.PostprocessMethods,
        )

        if self.parser_info.is_abstract and not method_organizer.has_abstract_methods:
            raise ErrorException(
                InvalidAbstractDecorationError.Create(
                    region=self.parser_info.regions__.is_abstract,
                ),
            )

        if self.parser_info.is_final and method_organizer.has_abstract_methods:
            raise ErrorException(
                InvalidFinalDecorationError.Create(
                    region=self.parser_info.regions__.is_final,
                ),
            )

        if self.parser_info.class_modifier == ClassModifier.mutable and not method_organizer.has_mutable_methods:
            raise ErrorException(
                InvalidMutableDecorationError.Create(
                    region=self.parser_info.regions__.class_modifier,
                ),
            )

        # Commit the results
        self._attributes                    = attributes
        self._methods                       = methods

        self._DestroyTemporaryFinalizationAttributes()

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(
        self,
        expression_parser_info: FuncOrTypeExpressionParserInfo,
    ) -> ConstrainedType:
        pass # BugBug

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConstrainedTypeImpl(self) -> ConstrainedType:
        assert self._expression_parser_info is not None
        return self._CreateConstrainedTypeImpl(self._expression_parser_info)

    # ----------------------------------------------------------------------
    def _DestroyTemporaryFinalizationAttributes(self):
        del self._local_methods
        del self._local_attributes
        del self._local_using_statements


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _InfoBase(object):
    # ----------------------------------------------------------------------
    def _MergeImpl(
        self,
        attribute_names: List[str],
        dependency_nodes: List[DependencyNode[ConcreteType]],
    ) -> None:
        if not dependency_nodes:
            return

        for dependency_node in dependency_nodes:
            resolved_dependency = dependency_node.ResolveDependencies()[1]

            resolved_type = resolved_dependency.ResolveAliases()
            assert isinstance(resolved_type, ClassConcreteType), resolved_type

            for attribute_name in attribute_names:
                dest_items = getattr(self, attribute_name)
                source_content = getattr(resolved_type, attribute_name)

                if isinstance(source_content, list):
                    source_items = source_content
                elif isinstance(source_content, ClassContent):
                    source_items = source_content.EnumContent()
                else:
                    assert False, source_content  # pragma: no cover

                for source_item in source_items:  # type: ignore
                    dest_items.append(DependencyNode(dependency_node.dependency, source_item))


# ----------------------------------------------------------------------
class _InitializationInfo(_InfoBase):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.concepts: List[Dependency[ConcreteType]]   = []
        self.interfaces: List[Dependency[ConcreteType]] = []
        self.mixins: List[Dependency[ConcreteType]]     = []

        self.types: List[Dependency[GenericType]]       = []

    # ----------------------------------------------------------------------
    def Merge(
        self,
        dependency_nodes: List[DependencyNode[ConcreteType]],
    ) -> None:
        self._MergeImpl(
            [
                "concepts",
                "interfaces",
                "mixins",
                "types",
            ],
            dependency_nodes,
        )


# ----------------------------------------------------------------------
class _Pass2Info(_InfoBase):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.attributes: List[Dependency[AttributeInfo]]                    = []
        self.methods: List[Dependency[GenericType]]                         = []

    # ----------------------------------------------------------------------
    def Merge(
        self,
        dependency_nodes: List[DependencyNode[ConcreteType]],
    ) -> None:
        self._MergeImpl(
            [
                "attributes",
                "methods",
            ],
            dependency_nodes,
        )


# ----------------------------------------------------------------------
_MethodOrganizer_LookingInfo_TypeT          = TypeVar("_MethodOrganizer_LookingInfo_TypeT")


class _MethodOrganizer(object):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        using_statements: List[ClassUsingStatementParserInfo],
    ):
        self._using_statements              = using_statements

        self._errors: List[Error]           = []

        self._is_complete                   = False

        self._has_abstract_methods          = False
        self._has_mutable_methods           = False

        self._standard_method_lookup: Dict[str, List[_MethodOrganizer._LookupInfo[ConcreteType]]]   = {}
        self._template_method_lookup: Dict[str, List[_MethodOrganizer._LookupInfo[GenericType]]]    = {}


    # ----------------------------------------------------------------------
    @property
    def has_abstract_methods(self) -> bool:
        assert self._is_complete is True
        return self._has_abstract_methods

    @property
    def has_mutable_methods(self) -> bool:
        assert self._is_complete is True
        return self._has_mutable_methods

    # ----------------------------------------------------------------------
    def GetKey(
        self,
        generic_type: GenericType,
    ) -> Any:
        if generic_type.parser_info.templates is not None:
            return self._GetTemplateKey(generic_type)

        return self._GetStandardKey(generic_type)

    # ----------------------------------------------------------------------
    def PostprocessMethods(
        self,
        local: List[Dependency[GenericType]],
        augmented: List[Dependency[GenericType]],
        inherited: List[Dependency[GenericType]],
    ) -> Tuple[
        List[Dependency[GenericType]],
        List[Dependency[GenericType]],
        List[Dependency[GenericType]],
    ]:
        # Identify methods marked as override but without anything to override
        for lookup_infos in itertools.chain(
            self._standard_method_lookup.values(),
            self._template_method_lookup.values(),
        ):
            for lookup_info in lookup_infos:
                if (
                    lookup_info.method_type.parser_info.method_hierarchy_modifier == MethodHierarchyModifier.override
                    and lookup_info.was_matched is False
                ):
                    self._errors.append(
                        InvalidOverrideDecorationError.Create(
                            region=lookup_info.method_type.parser_info.regions__.method_hierarchy_modifier,
                        ),
                    )

        if self._errors:
            raise ErrorException(*self._errors)

        # Group the methods using the using statements
        if self._using_statements:
            raise NotImplementedError("Using statements are not implemented yet")

        # BugBug: Do this

        # Check for final errors
        for dependency in itertools.chain(local, augmented, inherited):
            generic_type = dependency.ResolveDependencies()[1]

            assert isinstance(generic_type.parser_info, FuncDefinitionStatementParserInfo), generic_type.parser_info

            if (
                generic_type.parser_info.mutability_modifier is not None
                and generic_type.parser_info.mutability_modifier.IsMutable()
            ):
                self._has_mutable_methods = True
            if generic_type.parser_info.method_hierarchy_modifier == MethodHierarchyModifier.abstract:
                self._has_abstract_methods = True

            if self._has_mutable_methods and self._has_abstract_methods:
                break

        self._is_complete = True

        return local, augmented, inherited

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    @dataclass
    class _LookupInfo(Generic[_MethodOrganizer_LookingInfo_TypeT]):
        method_type: _MethodOrganizer_LookingInfo_TypeT
        was_matched: bool                   = field(init=False, default=False)

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    def _GetTemplateKey(
        self,
        generic_type: GenericType,
    ) -> Any:
        # BugBug: Not processing this correctly right now
        return id(generic_type)

    # ----------------------------------------------------------------------
    def _GetStandardKey(
        self,
        generic_type: GenericType,
    ) -> Any:
        assert generic_type.is_default_initializable, generic_type

        concrete_type = generic_type.CreateDefaultConcreteType()

        lookup_infos = self._standard_method_lookup.setdefault(concrete_type.parser_info.id, [])

        for lookup_info_index, lookup_info in enumerate(lookup_infos):
            if concrete_type.IsMatch(lookup_info.method_type):
                # Ensure that the hierarchy modifiers for both methods are valid
                assert isinstance(lookup_info.method_type.parser_info, FuncDefinitionStatementParserInfo), lookup_info.method_type.parser_info
                derived_parser_info = lookup_info.method_type.parser_info

                if derived_parser_info.resets_hierarchy:
                    assert isinstance(concrete_type.parser_info, FuncDefinitionStatementParserInfo), concrete_type.parser_info
                    base_parser_info = concrete_type.parser_info

                    if (
                        derived_parser_info.method_hierarchy_modifier is not None
                        or base_parser_info.method_hierarchy_modifier is not None
                    ):
                        if derived_parser_info.method_hierarchy_modifier is None:
                            self._errors.append(
                                OverlappedWithStaticMethodError.Create(
                                    region=derived_parser_info.regions__.self__,
                                    name=derived_parser_info.name,
                                    base_region=base_parser_info.regions__.method_hierarchy_modifier,
                                ),
                            )
                        elif base_parser_info.method_hierarchy_modifier is None:
                            self._errors.append(
                                OverlappedWithNonStaticMethodError.Create(
                                    region=derived_parser_info.regions__.method_hierarchy_modifier,
                                    name=derived_parser_info.name,
                                    base_region=base_parser_info.regions__.self__,
                                ),
                            )
                        elif base_parser_info.method_hierarchy_modifier == MethodHierarchyModifier.final:
                            self._errors.append(
                                FinalMethodOverrideError.Create(
                                    region=derived_parser_info.regions__.self__,
                                    name=derived_parser_info.name,
                                    base_region=base_parser_info.regions__.method_hierarchy_modifier,
                                ),
                            )
                        elif (
                            derived_parser_info.method_hierarchy_modifier.IsVirtualRoot()
                            and base_parser_info.method_hierarchy_modifier.IsHierarchy()
                        ):
                            self._errors.append(
                                RootOverlappedHierarchyMethodError.Create(
                                    region=derived_parser_info.regions__.method_hierarchy_modifier,
                                    name=derived_parser_info.name,
                                    base_region=base_parser_info.regions__.method_hierarchy_modifier,
                                ),
                            )
                        elif derived_parser_info.method_hierarchy_modifier.IsVirtualRoot():
                            self._errors.append(
                                OverlappedVirtualRootMethodError.Create(
                                    region=derived_parser_info.regions__.method_hierarchy_modifier,
                                    name=derived_parser_info.name,
                                    base_region=base_parser_info.regions__.self__,
                                ),
                            )
                        elif (
                            derived_parser_info.method_hierarchy_modifier.IsHierarchy()
                            and not base_parser_info.method_hierarchy_modifier.IsHierarchy()
                        ):
                            self._errors.append(
                                OverlappedNonHierararchyMethodError.Create(
                                    region=derived_parser_info.regions__.method_hierarchy_modifier,
                                    name=derived_parser_info.name,
                                    base_region=base_parser_info.regions__.method_hierarchy_modifier,
                                ),
                            )
                        elif (
                            not derived_parser_info.method_hierarchy_modifier.IsHierarchy()
                            and base_parser_info.method_hierarchy_modifier.IsHierarchy()
                        ):
                            self._errors.append(
                                OverlappedHierarchyMethodError.Create(
                                    region=derived_parser_info.regions__.self__,
                                    name=derived_parser_info.name,
                                    base_region=base_parser_info.regions__.method_hierarchy_modifier,
                                ),
                            )

                lookup_info.was_matched = True

                return concrete_type.parser_info.id, lookup_info_index

        lookup_infos.append(_MethodOrganizer._LookupInfo(concrete_type))

        return concrete_type.parser_info.id, len(lookup_infos) - 1
