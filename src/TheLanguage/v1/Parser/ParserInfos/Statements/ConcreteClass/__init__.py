# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-13 08:05:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ConcreteClass object"""

import itertools
import os

from contextlib import ExitStack
from enum import auto, Enum
from typing import Any, Callable, cast, Dict, Generator, Iterable, List, Optional, Tuple, TYPE_CHECKING, Union

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl.ClassContent import ClassContent
    from .Impl.Dependency import Dependency, DependencyLeaf, DependencyNode

    from ..ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ..ClassUsingStatementParserInfo import ClassUsingStatementParserInfo
    from ..FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ..SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo, SpecialMethodType
    from ..StatementParserInfo import StatementParserInfo
    from ..TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ..Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ...EntityResolver import EntityResolver
    from ...Types import ClassType, FuncDefinitionType, NoneType, Type, TypeAliasType

    from ...Common.ClassModifier import ClassModifier
    from ...Common.MethodHierarchyModifier import MethodHierarchyModifier
    from ...Common.MutabilityModifier import MutabilityModifier
    from ...Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo
    from ...Common.VisibilityModifier import VisibilityModifier

    from ...Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo, OperatorType as BinaryExpressionOperatorType

    from ...Traits.NamedTrait import NamedTrait

    from ....Error import CreateError, Error, ErrorException
    from ....TranslationUnitRegion import TranslationUnitRegion

    if TYPE_CHECKING:
        from ..ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo


# ----------------------------------------------------------------------
InvalidResolvedDependencyError              = CreateError(
    "Invalid dependency",
)

CircularDependencyError                     = CreateError(
    "A circular dependency was detected with '{name}'",
    name=str,
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

InvalidAbstractDecorationError              = CreateError(
    "The class is marked as abstract, but no abstract methods were encountered",
)

InvalidFinalDecorationError                 = CreateError(
    "The class is marked as final, but abstract methods were encountered",
)

InvalidMutableDecorationError               = CreateError(
    "The class is marked as mutable, but no mutable methods were found",
)

InvalidMutableMethodError                   = CreateError(
    "The class is marked as immutable, but the method is marked as '{mutability_str}'",
    mutability=MutabilityModifier,
    mutability_str=str,
    class_region=TranslationUnitRegion,
)



# BugBug: Insert here

InvalidEvalTemplatesMethodError             = CreateError(
    "The method to evaluate templates may only be used with classes that have templates",
)

InvalidEvalConstraintsMethodError           = CreateError(
    "The method to evaluate constraints may only be used with classes that have constraints",
)

InvalidFinalizeMethodError                  = CreateError(
    "Finalization methods are not valid for classes that are created as finalized",
)

DuplicateSpecialMethodError                 = CreateError(
    "The special method '{name}' has already been defined",
    name=str,
    prev_region=TranslationUnitRegion,
)


# ----------------------------------------------------------------------
class ConcreteClass(object):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class TypeInfo(object):
        # ----------------------------------------------------------------------
        statement: Union["ClassStatementParserInfo", FuncDefinitionStatementParserInfo, TypeAliasStatementParserInfo]
        concrete_type_factory_func: TemplatedStatementTrait.CreateConcreteTypeFactoryResultType
        name_override: Optional[str]        = field(default=None)

        # ----------------------------------------------------------------------
        @property
        def name(self) -> str:
            return self.name_override or self.statement.name

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class AttributeInfo(object):
        # ----------------------------------------------------------------------
        statement: ClassAttributeStatementParserInfo
        type: Type

        # ----------------------------------------------------------------------
        @property
        def name(self) -> str:
            return self.statement.name

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        class_parser_info: "ClassStatementParserInfo",
        entity_resolver: EntityResolver,
    ):
        errors: List[Error] = []

        base: Optional[Tuple["ClassStatementDependencyParserInfo", ClassType]] = None
        concepts: List[Tuple["ClassStatementDependencyParserInfo", ClassType]] = []
        interfaces: List[Tuple["ClassStatementDependencyParserInfo", ClassType]] = []
        mixins: List[Tuple["ClassStatementDependencyParserInfo", ClassType]] = []

        for dependencies, dependency_validation_func in [
            (
                class_parser_info.implements,
                class_parser_info.class_capabilities.ValidateImplementsDependency,
            ),
            (
                class_parser_info.uses,
                class_parser_info.class_capabilities.ValidateUsesDependency,
            ),
            (
                class_parser_info.extends,
                class_parser_info.class_capabilities.ValidateExtendsDependency,
            ),
        ]:
            if dependencies is None:
                continue

            for dependency_parser_info in dependencies:
                if dependency_parser_info.is_disabled__:
                    continue

                try:
                    resolved_type = entity_resolver.ResolveType(
                        dependency_parser_info.type,
                        resolve_aliases=True,
                    )

                    if isinstance(resolved_type, NoneType):
                        continue

                    if type(resolved_type.parser_info).__name__ != "ClassStatementParserInfo":
                        errors.append(
                            InvalidResolvedDependencyError.Create(
                                region=dependency_parser_info.type.regions__.self__,
                            ),
                        )

                        continue

                    dependency_validation_func(
                        dependency_parser_info,
                        resolved_type.parser_info,  # type: ignore
                    )

                    if resolved_type.parser_info.is_final:  # type: ignore
                        errors.append(
                            FinalDependencyError.Create(
                                region=dependency_parser_info.regions__.self__,
                                name=resolved_type.parser_info.name,  # type: ignore
                                final_class_region=resolved_type.parser_info.regions__.is_final,
                            ),
                        )

                        continue

                    assert isinstance(resolved_type, ClassType), resolved_type

                    if resolved_type.parser_info.class_capabilities.name == "Concept":
                        concepts.append((dependency_parser_info, resolved_type))
                    elif resolved_type.parser_info.class_capabilities.name == "Interface":
                        interfaces.append((dependency_parser_info, resolved_type))
                    elif resolved_type.parser_info.class_capabilities.name == "Mixin":
                        mixins.append((dependency_parser_info, resolved_type))
                    else:
                        if base is not None:
                            errors.append(
                                MultipleBasesError.Create(
                                    region=dependency_parser_info.regions__.self__,
                                    prev_region=base[0].regions__.self__,  # pylint: disable=unsubscriptable-object
                                ),
                            )

                            continue

                        base = dependency_parser_info, resolved_type

                except ErrorException as ex:
                    errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        return cls(base, concepts, interfaces, mixins)

    # ----------------------------------------------------------------------
    def __init__(
        self,
        base_dependency: Optional[Tuple["ClassStatementDependencyParserInfo", ClassType]],
        concept_dependencies: List[Tuple["ClassStatementDependencyParserInfo", ClassType]],
        interface_dependencies: List[Tuple["ClassStatementDependencyParserInfo", ClassType]],
        mixin_dependencies: List[Tuple["ClassStatementDependencyParserInfo", ClassType]],
    ):
        self._state                         = _InternalState.PreFinalize

        # The following values are valid until Finalization is complete
        self._base_dependency               = base_dependency
        self._concept_dependencies          = concept_dependencies
        self._interface_dependencies        = interface_dependencies
        self._mixin_dependencies            = mixin_dependencies

        # The following values are initialized during `FinalizePass1`
        self._base: Optional[Dependency[ClassType]]                         = None
        self._concepts: Optional[ClassContent[ClassType]]                   = None
        self._interfaces: Optional[ClassContent[ClassType]]                 = None
        self._types: Optional[ClassContent[ConcreteClass.TypeInfo]]         = None

        # The following values are initialized during `FinalizePass2`
        self._special_methods: Optional[Dict[SpecialMethodType, SpecialMethodStatementParserInfo]]  = None
        self._attributes: Optional[ClassContent[ConcreteClass.AttributeInfo]]   = None
        self._abstract_methods: Optional[ClassContent[ConcreteClass.TypeInfo]]  = None
        self._methods: Optional[ClassContent[ConcreteClass.TypeInfo]]  = None

    # ----------------------------------------------------------------------
    @property
    def base(self) -> Optional[Dependency[ClassType]]:
        assert self._state.value >= _InternalState.FinalizedPass1.value
        return self._base

    @property
    def concepts(self) -> ClassContent[ClassType]:
        assert self._state.value >= _InternalState.FinalizedPass1.value
        assert self._concepts is not None
        return self._concepts

    @property
    def interfaces(self) -> ClassContent[ClassType]:
        assert self._state.value >= _InternalState.FinalizedPass1.value
        assert self._interfaces is not None
        return self._interfaces

    @property
    def types(self) -> ClassContent["ConcreteClass.TypeInfo"]:
        assert self._state.value >= _InternalState.FinalizedPass1.value
        assert self._types is not None
        return self._types

    @property
    def special_methods(self) -> Dict[SpecialMethodType, SpecialMethodStatementParserInfo]:
        assert self._state.value >= _InternalState.FinalizedPass2.value
        assert self._special_methods is not None
        return self._special_methods

    @property
    def attributes(self) -> ClassContent["ConcreteClass.AttributeInfo"]:
        assert self._state.value >= _InternalState.FinalizedPass2.value
        assert self._attributes is not None
        return self._attributes

    @property
    def abstract_methods(self) -> ClassContent["ConcreteClass.TypeInfo"]:
        assert self._state.value >= _InternalState.FinalizedPass2.value
        assert self._abstract_methods is not None
        return self._abstract_methods

    @property
    def methods(self) -> ClassContent["ConcreteClass.TypeInfo"]:
        assert self._state.value >= _InternalState.FinalizedPass2.value
        assert self._methods is not None
        return self._methods

    # ----------------------------------------------------------------------
    def HasTypes(self) -> bool:
        return self._state.value >= _InternalState.FinalizedPass1.value

    # ----------------------------------------------------------------------
    def FinalizePass1(
        self,
        class_type: ClassType,
    ) -> None:
        if self._state == _InternalState.FinalizingPass1:
            raise ErrorException(
                CircularDependencyError.Create(
                    region=class_type.parser_info.regions__.self__,
                    name=class_type.parser_info.name,
                ),
            )

        if self._state.value >= _InternalState.FinalizedPass1.value:
            return

        assert class_type.instantiated_class is not None

        self._state = _InternalState.FinalizingPass1

        with ExitStack() as exit_stack:
            # ----------------------------------------------------------------------
            def ResetStateOnError():
                if self._state != _InternalState.FinalizedPass1:
                    self._state = _InternalState.PreFinalize

            # ----------------------------------------------------------------------

            exit_stack.callback(ResetStateOnError)

            errors: List[Error] = []

            # Finalize the dependencies
            for dependency_info in itertools.chain(
                [self._base_dependency] if self._base_dependency else [],
                self._concept_dependencies,
                self._interface_dependencies,
                self._mixin_dependencies,
            ):
                dependency_class_type = dependency_info[1]

                try:
                    dependency_class_type.FinalizePass1()
                except ErrorException as ex:
                    errors += ex.errors

            if errors:
                raise ErrorException(*errors)

            # Extract the raw type information
            local_content = _Pass1Info()
            augmented_content = _Pass1Info()
            dependency_content = _Pass1Info()

            for dependency_items, attribute_name in [
                (self._concept_dependencies, "concepts"),
                (self._interface_dependencies, "interfaces"),
            ]:
                if not dependency_items:
                    continue

                for dependency_parser_info, dependency_class_type in dependency_items:
                    local_content.MergeDependencies(
                        dependency_parser_info,
                        getattr(dependency_class_type.concrete_class, attribute_name).EnumDependencies(),
                        attribute_name,
                    )

            for dependency_items, target_content in [
                ([self._base_dependency] if self._base_dependency else [], dependency_content),
                (self._concept_dependencies, augmented_content),
                (self._interface_dependencies, dependency_content),
                (self._mixin_dependencies, augmented_content),
            ]:
                if not dependency_items:
                    continue

                target_content.Merge(dependency_items)

            # Prepare the local content

            # ----------------------------------------------------------------------
            def ProcessClass(
                statement: "ClassStatementParserInfo",
            ) -> None:
                local_content.types.append(
                    DependencyLeaf(
                        ConcreteClass.TypeInfo(
                            statement,
                            statement.CreateConcreteTypeFactory(class_type.entity_resolver),
                        ),
                    ),
                )

            # ----------------------------------------------------------------------
            def ProcessTypeAlias(
                statement: TypeAliasStatementParserInfo,
            ) -> None:
                local_content.types.append(
                    DependencyLeaf(
                        ConcreteClass.TypeInfo(
                            statement,
                            statement.CreateConcreteTypeFactory(class_type.entity_resolver),
                        ),
                    ),
                )

            # ----------------------------------------------------------------------

            processing_funcs = {
                "ClassStatementParserInfo": ProcessClass,
                "TypeAliasStatementParserInfo": ProcessTypeAlias,
            }

            assert class_type.parser_info.statements is not None

            for statement in class_type.parser_info.statements:
                if statement.is_disabled__:
                    continue

                processing_func = processing_funcs.get(type(statement).__name__, None)
                if processing_func is not None:
                    processing_func(statement)

            if class_type.parser_info.self_referencing_type_names:
                # ----------------------------------------------------------------------
                def ThisClassTypeFactory(*args, **kwargs) -> ClassType:
                    return class_type

                # ----------------------------------------------------------------------

                for self_referencing_type_name in class_type.parser_info.self_referencing_type_names:
                    local_content.types.append(
                        DependencyLeaf(
                            ConcreteClass.TypeInfo(
                                class_type.instantiated_class.parser_info,
                                ThisClassTypeFactory,
                                self_referencing_type_name,
                            ),
                        ),
                    )

            # Commit the results
            if self._base_dependency:
                base = DependencyNode(
                    self._base_dependency[0],
                    DependencyLeaf(self._base_dependency[1]),
                )
            else:
                base = None

            concepts = ClassContent.Create(
                local_content.concepts,
                augmented_content.concepts,
                dependency_content.concepts,
                lambda type_info: type_info.parser_info.name,
            )

            interfaces = ClassContent.Create(
                local_content.interfaces,
                augmented_content.interfaces,
                dependency_content.interfaces,
                lambda type_info: type_info.parser_info.name,
            )

            types = ClassContent.Create(
                local_content.types,
                augmented_content.types,
                dependency_content.types,
                lambda type_info: type_info.statement.name,
            )

            self._base = base
            self._concepts = concepts
            self._interfaces = interfaces
            self._types = types

            self._state = _InternalState.FinalizedPass1

    # ----------------------------------------------------------------------
    def FinalizePass2(
        self,
        class_type: ClassType,
    ) -> None:
        if self._state.value >= _InternalState.FinalizedPass2.value:
            return

        assert self._state != _InternalState.FinalizingPass2
        self._state = _InternalState.FinalizingPass2

        with ExitStack() as exit_stack:
            # ----------------------------------------------------------------------
            def ResetStateOnError():
                if self._state != _InternalState.FinalizedPass2:
                    self._state = _InternalState(_InternalState.FinalizingPass2.value - 1)

            # ----------------------------------------------------------------------

            exit_stack.callback(ResetStateOnError)

            errors: List[Error] = []

            # Finalize the dependencies
            for dependency_info in itertools.chain(
                [self._base_dependency] if self._base_dependency else [],
                self._concept_dependencies,
                self._interface_dependencies,
                self._mixin_dependencies,
            ):
                dependency_class_type = dependency_info[1]

                try:
                    dependency_class_type.FinalizePass2()
                except ErrorException as ex:
                    errors += ex.errors

            if errors:
                raise ErrorException(*errors)

            local_content = _Pass2Info()
            augmented_content = _Pass2Info()
            dependency_content = _Pass2Info()

            for dependency_items, target_content in [
                ([self._base_dependency] if self._base_dependency else [], dependency_content),
                (self._concept_dependencies, augmented_content),
                (self._interface_dependencies, dependency_content),
                (self._mixin_dependencies, augmented_content),
            ]:
                if not dependency_items:
                    continue

                target_content.Merge(dependency_items)

            # Prepare the local content

            special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo] = {}
            using_statements: List[
                Tuple[
                    VisibilityModifier,
                    ClassType,
                    FuncDefinitionStatementParserInfo,
                ],
            ] = []

            # ----------------------------------------------------------------------
            def ProcessAttribute(
                statement: ClassAttributeStatementParserInfo,
            ) -> None:
                # BugBug: process 'is_override'

                attribute_type = class_type.entity_resolver.ResolveType(statement.type)

                local_content.attributes.append(
                    DependencyLeaf(ConcreteClass.AttributeInfo(statement, attribute_type)),
                )

            # ----------------------------------------------------------------------
            def ProcessMethod(
                statement: FuncDefinitionStatementParserInfo,
            ) -> None:
                # Ensure that the method's mutability agrees with the class's mutability
                if (
                    statement.mutability is not None
                    and class_type.parser_info.class_modifier == ClassModifier.immutable
                    and MutabilityModifier.IsMutable(statement.mutability)
                ):
                    errors.append(
                        InvalidMutableMethodError.Create(
                            region=statement.regions__.mutability,
                            mutability=statement.mutability,
                            mutability_str=statement.mutability.name,
                            class_region=class_type.parser_info.regions__.class_modifier,
                        ),
                    )

                    return

                # Ensure that the hierarchy modifiers agree with the derived methods
                if (
                    statement.method_hierarchy_modifier is not None
                    and statement.method_hierarchy_modifier != MethodHierarchyModifier.standard
                ):
                    pass # BugBug: Do this

                dependency_leaf = DependencyLeaf(
                    ConcreteClass.TypeInfo(
                        statement,
                        statement.CreateConcreteTypeFactory(class_type.entity_resolver),
                    ),
                )

                if statement.method_hierarchy_modifier == MethodHierarchyModifier.abstract:
                    local_content.abstract_methods.append(dependency_leaf)
                else:
                    local_content.methods.append(dependency_leaf)

            # ----------------------------------------------------------------------
            def ProcessSpecialMethod(
                statement: SpecialMethodStatementParserInfo,
            ) -> None:
                # Determine if the special method is valid for the class
                if statement.special_method_type == SpecialMethodType.EvalTemplates:
                    if not class_type.parser_info.templates:
                        errors.append(
                            InvalidEvalTemplatesMethodError.Create(
                                region=statement.regions__.special_method_type,
                            ),
                        )

                        return

                    class_type.entity_resolver.EvalStatements(statement.statements)

                if (
                    statement.special_method_type == SpecialMethodType.EvalConstraints
                    and not class_type.parser_info.constraints
                ):
                    errors.append(
                        InvalidEvalConstraintsMethodError.Create(
                            region=statement.regions__.special_method_type,
                        ),
                    )

                    return

                if (
                    (
                        statement.special_method_type == SpecialMethodType.PrepareFinalize
                        or statement.special_method_type == SpecialMethodType.Finalize
                    )
                    and class_type.parser_info.class_modifier != ClassModifier.mutable
                ):
                    errors.append(
                        InvalidFinalizeMethodError.Create(
                            region=statement.regions__.special_method_type,
                        ),
                    )

                    return

                prev_special_method = special_methods.get(statement.special_method_type, None)
                if prev_special_method is not None:
                    errors.append(
                        DuplicateSpecialMethodError.Create(
                            region=statement.regions__.special_method_type,
                            name=statement.special_method_type,
                            prev_region=prev_special_method.regions__.special_method_type,
                        ),
                    )

                    return

                special_methods[statement.special_method_type] = statement

            # ----------------------------------------------------------------------
            def ProcessUsingStatement(
                statement: ClassUsingStatementParserInfo,
            ) -> None:
                assert isinstance(statement.type, BinaryExpressionParserInfo), statement.type
                assert statement.type.operator == BinaryExpressionOperatorType.Access, statement.type.operator

                resolved_left = class_type.entity_resolver.ResolveType(statement.type.left_expression)

                # BugBug: Finish this

            # ----------------------------------------------------------------------

            processing_funcs = {
                "ClassAttributeStatementParserInfo": ProcessAttribute,
                "FuncDefinitionStatementParserInfo": ProcessMethod,
                "SpecialMethodStatementParserInfo": ProcessSpecialMethod,
                "ClassUsingStatementParserInfo": ProcessUsingStatement,
            }

            assert class_type.parser_info.statements is not None

            for statement in class_type.parser_info.statements:
                if statement.is_disabled__:
                    continue

                processing_func = processing_funcs.get(type(statement).__name__, None)
                if processing_func is not None:
                    processing_func(statement)

            # Issue an error if the class was declared as abstract but no abstract methods were found
            if (
                class_type.parser_info.is_abstract
                and not (
                    local_content.abstract_methods
                    or augmented_content.abstract_methods
                    or dependency_content.abstract_methods
                )
            ):
                errors.append(
                    InvalidAbstractDecorationError.Create(
                        region=class_type.parser_info.regions__.is_abstract,
                    ),
                )

            # Issue an error if the class was declared as final but there are abstract methods
            if (
                class_type.parser_info.is_final
                and (
                    local_content.abstract_methods
                    or augmented_content.abstract_methods
                    or dependency_content.abstract_methods
                )
            ):
                errors.append(
                    InvalidFinalDecorationError.Create(
                        region=class_type.parser_info.regions__.is_final,
                    ),
                )

            # Issue an error if the class was declared as mutable but no mutable methods were found
            if class_type.parser_info.class_modifier == ClassModifier.mutable:
                has_mutable_method = False

                for dependency in itertools.chain(
                    local_content.methods,
                    local_content.abstract_methods,
                    augmented_content.methods,
                    augmented_content.abstract_methods,
                    dependency_content.methods,
                    dependency_content.abstract_methods,
                ):
                    method_info = dependency.ResolveDependencies()[1]
                    assert isinstance(method_info, ConcreteClass.TypeInfo), method_info

                    assert isinstance(method_info.statement, FuncDefinitionStatementParserInfo), method_info.statement

                    if (
                        method_info.statement.mutability is not None
                        and MutabilityModifier.IsMutable(method_info.statement.mutability)
                    ):
                        has_mutable_method = True
                        break

                if not has_mutable_method:
                    errors.append(
                        InvalidMutableDecorationError.Create(
                            region=class_type.parser_info.regions__.class_modifier,
                        ),
                    )

            if errors:
                raise ErrorException(*errors)

            # Commit the results

            # ----------------------------------------------------------------------
            def MethodIdExtractor(
                type_info: ConcreteClass.TypeInfo,
            ) -> Any:
                # BugBug
                return id(type_info.statement)

            # ----------------------------------------------------------------------

            attributes = ClassContent.Create(
                local_content.attributes,
                augmented_content.attributes,
                dependency_content.attributes,
                lambda attribute_info: attribute_info.statement.name,
            )

            abstract_methods = ClassContent.Create(
                local_content.abstract_methods,
                augmented_content.abstract_methods,
                dependency_content.abstract_methods,
                MethodIdExtractor,
            )

            methods = ClassContent.Create(
                local_content.methods,
                augmented_content.methods,
                dependency_content.methods,
                MethodIdExtractor,
                _PostprocessMethodCreateClassContent,
            )

            self._attributes = attributes
            self._abstract_methods = abstract_methods
            self._methods = methods

            self._state = _InternalState.FinalizedPass2

        # Finalization is now complete
        self._Finalize()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _Finalize(self) -> None:
        del self._base_dependency
        del self._concept_dependencies
        del self._interface_dependencies
        del self._mixin_dependencies

        self._state = _InternalState.Finalized


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _InternalState(Enum):
    PreFinalize                             = auto()

    FinalizingPass1                         = auto()
    FinalizedPass1                          = auto()

    FinalizingPass2                         = auto()
    FinalizedPass2                          = auto()

    Finalized                               = auto()


# ----------------------------------------------------------------------
class _RawInfo(object):
    # ----------------------------------------------------------------------
    def MergeDependencies(
        self,
        dependency_parser_info: "ClassStatementDependencyParserInfo",
        source_items: Iterable[Any],
        dest_attribute_name: str,
    ) -> None:
        dest = getattr(self, dest_attribute_name)

        for source_item in source_items:
            dest.append(DependencyNode(dependency_parser_info, source_item))

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _MergeImpl(
        self,
        attribute_names: List[str],
        source_items: List[Tuple["ClassStatementDependencyParserInfo", ClassType]],
    ) -> None:
        if not source_items:
            return

        for dependency_parser_info, class_type in source_items:
            for attribute_name in attribute_names:
                self.MergeDependencies(
                    dependency_parser_info,
                    getattr(class_type.concrete_class, attribute_name).EnumDependencies(),
                    attribute_name,
                )


# ----------------------------------------------------------------------
class _Pass1Info(_RawInfo):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.concepts: List[Dependency[ClassType]]                          = []
        self.interfaces: List[Dependency[ClassType]]                        = []
        self.types: List[Dependency[ConcreteClass.TypeInfo]]                = []

    # ----------------------------------------------------------------------
    def Merge(
        self,
        source_items: List[Tuple["ClassStatementDependencyParserInfo", ClassType]],
    ) -> None:
        return self._MergeImpl(
            [
                "concepts",
                "interfaces",
                "types",
            ],
            source_items,
        )


# ----------------------------------------------------------------------
class _Pass2Info(_RawInfo):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.attributes: List[Dependency[ConcreteClass.AttributeInfo]]      = []
        self.abstract_methods: List[Dependency[ConcreteClass.TypeInfo]]     = []
        self.methods: List[Dependency[ConcreteClass.TypeInfo]]              = []

    # ----------------------------------------------------------------------
    def Merge(
        self,
        source_items: List[Tuple["ClassStatementDependencyParserInfo", ClassType]],
    ) -> None:
        return self._MergeImpl(
            [
                "attributes",
                "abstract_methods",
                "methods",
            ],
            source_items,
        )


# ----------------------------------------------------------------------
def _PostprocessMethodCreateClassContent(
    local: List[Dependency[ConcreteClass.TypeInfo]],
    augmented: List[Dependency[ConcreteClass.TypeInfo]],
    inherited: List[Dependency[ConcreteClass.TypeInfo]],
) -> Tuple[
    List[Dependency[ConcreteClass.TypeInfo]],
    List[Dependency[ConcreteClass.TypeInfo]],
    List[Dependency[ConcreteClass.TypeInfo]],
]:
    # BugBug
    return local, augmented, inherited
