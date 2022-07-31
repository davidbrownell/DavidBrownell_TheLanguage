# ----------------------------------------------------------------------
# |
# |  ConcreteClassType.py
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
"""Contains the ConcreteClassType object"""

import itertools
import os

from typing import Any, Callable, Dict, Generator, Iterator, List, Optional, Tuple, Union

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
    from ..GenericTypes import GenericStatementType, GenericType
    from ..TypeResolvers import ConcreteTypeResolver

    from ...Common.ClassModifier import ClassModifier
    from ...Common.MethodHierarchyModifier import MethodHierarchyModifier
    from ...Common.MutabilityModifier import MutabilityModifier

    from ...Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo

    from ...Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ...Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ...Statements.ClassUsingStatementParserInfo import ClassUsingStatementParserInfo
    from ...Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo, SpecialMethodType
    from ...Statements.StatementParserInfo import StatementParserInfo
    from ...Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ....Error import CreateError, Error, ErrorException

    from ....ParserInfos.Traits.NamedTrait import NamedTrait

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


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeInfo(object):
    # ----------------------------------------------------------------------
    generic_type: GenericStatementType
    name_override: Optional[str]            = field(default=None)

    # ----------------------------------------------------------------------
    @property
    def name(self) -> str:
        assert isinstance(self.generic_type.parser_info, NamedTrait), self.generic_type.parser_info
        return self.name_override or self.generic_type.parser_info.name


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class AttributeInfo(object):
    # ----------------------------------------------------------------------
    statement: ClassAttributeStatementParserInfo
    constrained_type: ConstrainedType


# ----------------------------------------------------------------------
class ConcreteClassType(ConcreteType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        type_resolver: ConcreteTypeResolver,
        parser_info: ClassStatementParserInfo,
    ):
        super(ConcreteClassType, self).__init__(parser_info)

        self._type_resolver                 = type_resolver

        # The following values are initialized upon creation and are permanent
        self.base_dependency: Optional[DependencyNode[ConcreteType]]        = None
        self.concept_dependencies: List[DependencyNode[ConcreteType]]       = []
        self.interface_dependencies: List[DependencyNode[ConcreteType]]     = []
        self.mixin_dependencies: List[DependencyNode[ConcreteType]]         = []

        self.special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo]     = {}

        # The following values are created on FinalizePass1 and exposed via properties
        self._concepts: Optional[ClassContent[ConcreteType]]                = None
        self._interfaces: Optional[ClassContent[ConcreteType]]              = None
        self._mixins: Optional[ClassContent[ConcreteType]]                  = None
        self._types: Optional[ClassContent[TypeInfo]]                       = None

        # The following values are created during FinalizePass2 and exposed via properties
        self._attributes: Optional[ClassContent[AttributeInfo]]                 = None
        self._methods: Optional[ClassContent[GenericStatementType]]             = None
        self._abstract_methods: Optional[ClassContent[GenericStatementType]]    = None

        # The following values are initialized upon creation and destroyed after Finalization
        self._attribute_statements: List[ClassAttributeStatementParserInfo]                         = []
        self._method_statements: List[FuncDefinitionStatementParserInfo]                            = []
        self._type_statements: List[Union[ClassStatementParserInfo, TypeAliasStatementParserInfo]]  = []
        self._using_statements: List[ClassUsingStatementParserInfo]                                 = []

        self._Initialize()

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> ClassStatementParserInfo:
        assert isinstance(self._parser_info, ClassStatementParserInfo), self._parser_info
        return self._parser_info

    # Valid after FinalizePass1
    @property
    def concepts(self) -> ClassContent[ConcreteType]:
        assert self.state.value >= ConcreteType.State.FinalizedPass1.value
        assert self._concepts is not None
        return self._concepts

    @property
    def interfaces(self) -> ClassContent[ConcreteType]:
        assert self.state.value >= ConcreteType.State.FinalizedPass1.value
        assert self._interfaces is not None
        return self._interfaces

    @property
    def mixins(self) -> ClassContent[ConcreteType]:
        assert self.state.value >= ConcreteType.State.FinalizedPass1.value
        assert self._mixins is not None
        return self._mixins

    @property
    def types(self) -> ClassContent[TypeInfo]:
        assert self.state.value >= ConcreteType.State.FinalizedPass1.value
        assert self._types is not None
        return self._types

    # Valid after FinalizePass2
    @property
    def attributes(self) -> ClassContent[AttributeInfo]:
        assert self.state.value >= ConcreteType.State.FinalizedPass2.value
        assert self._attributes is not None
        return self._attributes

    @property
    def methods(self) -> ClassContent[GenericStatementType]:
        assert self.state.value >= ConcreteType.State.FinalizedPass2.value
        assert self._methods is not None
        return self._methods

    @property
    def abstract_methods(self) -> ClassContent[GenericStatementType]:
        assert self.state.value >= ConcreteType.State.FinalizedPass2.value
        assert self._abstract_methods is not None
        return self._abstract_methods

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _Initialize(self) -> None:
        errors: List[Error] = []

        # Process the dependencies
        base: Optional[Tuple[ClassStatementDependencyParserInfo, DependencyNode[ConcreteType]]] = None
        concepts: List[DependencyNode[ConcreteType]] = []
        interfaces: List[DependencyNode[ConcreteType]] = []
        mixins: List[DependencyNode[ConcreteType]] = []

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
                    concrete_type = self._type_resolver.EvalConcreteType(dependency_parser_info.type)
                    resolved_concrete_type = concrete_type.ResolveAliases()

                    resolved_parser_info = resolved_concrete_type.parser_info

                    if isinstance(resolved_parser_info, NoneExpressionParserInfo):
                        continue

                    if not isinstance(resolved_concrete_type, ConcreteClassType):
                        errors.append(
                            InvalidResolvedDependencyError.Create(
                                region=dependency_parser_info.type.regions__.self__,
                            ),
                        )

                        continue

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
                        concepts.append(dependency_node)
                    elif resolved_parser_info.class_capabilities.name == "Interface":
                        interfaces.append(dependency_node)
                    elif resolved_parser_info.class_capabilities.name == "Mixin":
                        mixins.append(dependency_node)
                    else:
                        if base is not None:
                            errors.append(
                                MultipleBasesError.Create(
                                    region=dependency_parser_info.regions__.self__,
                                    prev_region=base[0].regions__.self__,  # pylint: disable=unsubscriptable-object
                                ),
                            )

                            continue

                        base = (dependency_parser_info, dependency_node)

                except ErrorException as ex:
                    errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # Process the local statements
        special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo] = {}

        attribute_statements: List[ClassAttributeStatementParserInfo] = []
        method_statements: List[FuncDefinitionStatementParserInfo] = []
        type_statements: List[Union[ClassStatementParserInfo, TypeAliasStatementParserInfo]] = []
        using_statements: List[ClassUsingStatementParserInfo] = []

        assert self.parser_info.statements is not None

        for statement in self.parser_info.statements:
            if statement.is_disabled__:
                continue

            try:
                if isinstance(statement, ClassAttributeStatementParserInfo):
                    # BugBug: Check for mutable on immutable class
                    attribute_statements.append(statement)
                elif isinstance(statement, ClassStatementParserInfo):
                    type_statements.append(statement)
                elif isinstance(statement, ClassUsingStatementParserInfo):
                    using_statements.append(statement)
                elif isinstance(statement, FuncDefinitionStatementParserInfo):
                    # BugBug: Check for mutable on immutable class
                    method_statements.append(statement)
                elif isinstance(statement, TypeAliasStatementParserInfo):
                    type_statements.append(statement)
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

        # Commit the results
        self.base_dependency = base[1] if base is not None else None
        self.concept_dependencies = concepts
        self.interface_dependencies = interfaces
        self.mixin_dependencies = mixins

        self.special_methods = special_methods

        self._attribute_statements = attribute_statements
        self._type_statements = type_statements
        self._method_statements = method_statements
        self._using_statements = using_statements

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        errors: List[Error] = []

        # Finalize all dependencies
        for dependency in itertools.chain(
            [self.base_dependency, ] if self.base_dependency else [],
            self.concept_dependencies,
            self.interface_dependencies,
            self.mixin_dependencies,
        ):
            try:
                dependency.ResolveDependencies()[1].FinalizePass1()
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # Capture the dependency info
        augmented_info = _Pass1Info()
        dependency_info = _Pass1Info()

        for dependencies, target_info in [
            ([self.base_dependency, ] if self.base_dependency else [], dependency_info),
            (self.concept_dependencies, augmented_info),
            (self.interface_dependencies, dependency_info),
            (self.mixin_dependencies, augmented_info),
        ]:
            if not dependencies:
                continue

            target_info.Merge(dependencies)

        if errors:
            raise ErrorException(*errors)

        # Extract the local information
        local_info = _Pass1Info()

        local_info.concepts += self.concept_dependencies
        local_info.interfaces += self.interface_dependencies
        local_info.mixins += self.mixin_dependencies

        for statement in self._type_statements:
            local_info.types.append(
                DependencyLeaf(TypeInfo(self._type_resolver.GetOrCreateNestedGenericType(statement))),
            )

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
            lambda type_info: type_info.name,
        )

        # Commit the results
        self._concepts = concepts
        self._interfaces = interfaces
        self._mixins = mixins
        self._types = types

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        errors: List[Error] = []

        # Finalize all dependencies
        for dependency in itertools.chain(
            [self.base_dependency, ] if self.base_dependency else [],
            self.concept_dependencies,
            self.interface_dependencies,
            self.mixin_dependencies,
        ):
            try:
                dependency.ResolveDependencies()[1].FinalizePass2()
            except ErrorException as ex:
                errors += ex.errors

        # Validate the local types
        for dependency in self.types.local:
            try:
                generic_type = dependency.ResolveDependencies()[1].generic_type

                if generic_type.is_default_initializable:
                    generic_type.CreateDefaultConcreteType().Finalize()

            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # Capture the dependency info
        augmented_info = _Pass2Info()
        dependency_info = _Pass2Info()

        for dependencies, target_info in [
            ([self.base_dependency, ] if self.base_dependency else [], dependency_info),
            (self.concept_dependencies, augmented_info),
            (self.interface_dependencies, dependency_info),
            (self.mixin_dependencies, augmented_info),
        ]:
            if not dependencies:
                continue

            target_info.Merge(dependencies)

        if errors:
            raise ErrorException(*errors)

        # Extract the local information
        local_info = _Pass2Info()

        # Attributes
        for attribute_statement in self._attribute_statements:
            try:
                # BugBug: Handle 'is_override'

                concrete_type = self._type_resolver.EvalConcreteType(attribute_statement.type)

                concrete_type.Finalize()

                constrained_type = concrete_type.CreateConstrainedType()

                local_info.attributes.append(
                    DependencyLeaf(
                        AttributeInfo(attribute_statement, constrained_type),
                    ),
                )

            except ErrorException as ex:
                errors += ex.errors

        # Methods
        for method_statement in self._method_statements:
            try:
                generic_type = self._type_resolver.GetOrCreateNestedGenericType(method_statement)

                # BugBug: Handle hierarchy

                dependency_leaf = DependencyLeaf(generic_type)

                if method_statement.method_hierarchy_modifier == MethodHierarchyModifier.abstract:
                    local_info.abstract_methods.append(dependency_leaf)
                else:
                    local_info.methods.append(dependency_leaf)

            except ErrorException as ex:
                errors += ex.errors
                continue

        # Using
        if self._using_statements:
            raise NotImplementedError("Using statements are not implemented yet")

        if errors:
            raise ErrorException(*errors)

        # Issue an error if the class was declared as abstract but no abstract methods were found
        if (
            self.parser_info.is_abstract
            and not (
                local_info.abstract_methods
                or augmented_info.abstract_methods
                or dependency_info.abstract_methods
            )
        ):
            errors.append(
                InvalidAbstractDecorationError.Create(
                    region=self.parser_info.regions__.is_abstract,
                ),
            )

        # Issue an error if the class was declared as final but there are abstract methods
        if (
            self.parser_info.is_final
            and (
                local_info.abstract_methods
                or augmented_info.abstract_methods
                or dependency_info.abstract_methods
            )
        ):
            errors.append(
                InvalidFinalDecorationError.Create(
                    region=self.parser_info.regions__.is_final,
                ),
            )

        # Issue an error if the class was declared as mutable but no mutable methods were found
        if self.parser_info.class_modifier == ClassModifier.mutable:
            has_mutable_method = False

            for dependency in itertools.chain(
                local_info.methods,
                local_info.abstract_methods,
                augmented_info.methods,
                augmented_info.abstract_methods,
                dependency_info.methods,
                dependency_info.abstract_methods,
            ):
                generic_statement_type = dependency.ResolveDependencies()[1]

                assert isinstance(generic_statement_type.parser_info, FuncDefinitionStatementParserInfo), generic_statement_type.parser_info

                if (
                    generic_statement_type.parser_info.mutability_modifier is not None
                    and MutabilityModifier.IsMutable(generic_statement_type.parser_info.mutability_modifier)
                ):
                    has_mutable_method = True
                    break

            if not has_mutable_method:
                errors.append(
                    InvalidMutableDecorationError.Create(
                        region=self.parser_info.regions__.class_modifier,
                    ),
                )

        # Prepare the final results

        attributes = ClassContent.Create(
            local_info.attributes,
            augmented_info.attributes,
            dependency_info.attributes,
            lambda attribute_info: attribute_info.statement.name,
        )

        # ----------------------------------------------------------------------
        def ExtractMethodKey(
            generic_type: GenericStatementType,
        ) -> Any:
            pass # BugBug

        # ----------------------------------------------------------------------
        def PostprocessMethods(
            local: List[Dependency[GenericStatementType]],
            augmented: List[Dependency[GenericStatementType]],
            inherited: List[Dependency[GenericStatementType]],
        ) -> Tuple[
            List[Dependency[GenericStatementType]],
            List[Dependency[GenericStatementType]],
            List[Dependency[GenericStatementType]],
        ]:
            # BugBug
            return local, augmented, inherited

        # ----------------------------------------------------------------------

        methods = ClassContent.Create(
            local_info.methods,
            augmented_info.methods,
            dependency_info.methods,
            ExtractMethodKey,
            PostprocessMethods,
        )

        abstract_methods = ClassContent.Create(
            local_info.abstract_methods,
            augmented_info.abstract_methods,
            dependency_info.abstract_methods,
            ExtractMethodKey,
        )

        # Commit the results
        self._attributes = attributes
        self._methods = methods
        self._abstract_methods = abstract_methods

        self._Finalize()

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(self) -> ConstrainedType:
        pass # BugBug

    # ----------------------------------------------------------------------
    def _Finalize(self):
        del self._attribute_statements
        del self._method_statements
        del self._type_statements
        del self._using_statements


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _InfoBase(object):
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
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
            assert isinstance(resolved_type, ConcreteClassType), resolved_type

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
class _Pass1Info(_InfoBase):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.concepts: List[Dependency[ConcreteType]]                       = []
        self.interfaces: List[Dependency[ConcreteType]]                     = []
        self.mixins: List[Dependency[ConcreteType]]                         = []
        self.types: List[Dependency[TypeInfo]]                              = []

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
        self.methods: List[Dependency[GenericStatementType]]                = []
        self.abstract_methods: List[Dependency[GenericStatementType]]       = []

    # ----------------------------------------------------------------------
    def Merge(
        self,
        dependency_nodes: List[DependencyNode[ConcreteType]],
    ) -> None:
        self._MergeImpl(
            [
                "attributes",
                "methods",
                "abstract_methods",
            ],
            dependency_nodes,
        )
