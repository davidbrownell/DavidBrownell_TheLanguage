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
from typing import Any, Callable, cast, Dict, Generator, Generic, Iterable, List, Optional, Tuple, TYPE_CHECKING, TypeVar, Union

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

    from ..ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ..ClassUsingStatementParserInfo import ClassUsingStatementParserInfo
    from ..FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ..SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo, SpecialMethodType
    from ..StatementParserInfo import StatementParserInfo
    from ..TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ..Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ...Types.ConcreteType import ConcreteType
    from ...Types.ConstrainedType import ConstrainedType
    from ...Types.GenericType import GenericType

    from ...Common.ClassModifier import ClassModifier
    from ...Common.MethodHierarchyModifier import MethodHierarchyModifier
    from ...Common.MutabilityModifier import MutabilityModifier
    from ...Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo
    from ...Common.VisibilityModifier import VisibilityModifier

    from ...Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo, OperatorType as BinaryExpressionOperatorType
    from ...Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo

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
class TypeResolver(Interface.Interface):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def EvalType(
        parser_info: ExpressionParserInfo,
    ) -> GenericType:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def CreateGenericTypeResolver(
        parser_info: Union["ClassStatementParserInfo", FuncDefinitionStatementParserInfo, TypeAliasStatementParserInfo],
    ) -> Any:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def EvalStatements(
        statements: Optional[List[StatementParserInfo]],
    ) -> None:
        raise Exception("Abstract method")  # pragma: no cover


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
        concrete_type_factory_func: Any # BugBug: TemplatedStatementTrait.CreateConcreteTypeFactoryResultType
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
    def __init__(
        self,
        class_parser_info: "ClassStatementParserInfo",
        type_resolver: TypeResolver,
    ):
        self._type_resolver                 = type_resolver
        self._state                         = _InternalState.PreFinalize

        # The following values are valid while state < _InternalState.Finalized
        self._base: Optional[DependencyNode[ConcreteType]]                  = None
        self._concepts: List[DependencyNode[ConcreteType]]                  = []
        self._interfaces: List[DependencyNode[ConcreteType]]                = []
        self._mixins: List[DependencyNode[ConcreteType]]                    = []

        # Organize the initial dependencies
        base: Optional[Tuple[ClassStatementParserInfo, DependencyNode[ConcreteType]]]   = None
        concepts: List[Dependency[ConcreteType]]                                    = []
        interfaces: List[Dependency[ConcreteType]]                                  = []
        mixins: List[Dependency[ConcreteType]]                                      = []

        errors: List[Error] = []

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
                try:
                    resolved_type = type_resolver.EvalType(dependency_parser_info.type)
                    fully_resolved_type = resolved_type.ResolveAliases()

                    parser_info = fully_resolved_type.definition_parser_info

                    if isinstance(parser_info, NoneExpressionParserInfo):
                        continue

                    if type(parser_info).__name__ != "ClassStatementDependencyParserInfo":
                        errors.append(
                            InvalidResolvedDependencyError.Create(
                                region=dependency_parser_info.type.regions__.self__,
                            ),
                        )

                        continue

                    dependency_validation_func(dependency_parser_info, parser_info)  # type: ignore

                    if parser_info.is_final:  # type: ignore
                        errors.append(
                            FinalDependencyError.Create(
                                region=dependency_parser_info.regions__.self__,
                                name=parser_info.name,  # type: ignore
                                final_class_region=parser_info.regions__.is_final,
                            ),
                        )

                        continue

                    concrete_type = resolved_type.CreateConcreteType()

                    dependency_node = DependencyNode(
                        dependency_parser_info,
                        DependencyLeaf(concrete_type),
                    )

                    if parser_info.class_capabilities.name == "Concept":  # type: ignore
                        concepts.append(dependency_node)
                    elif parser_info.class_capabilities.name == "Interface":  # type: ignore
                        interfaces.append(dependency_node)
                    elif parser_info.class_capabilities.name == "Mixin":  # type: ignore
                        mixins.append(dependency_node)
                    else:
                        if base is not None:
                            errors.append(
                                MultipleBasesError.Create(
                                    region=dependency_parser_info.regions__.self__,
                                    prev_region=base[0].regions__.self__,
                                ),
                            )

                            continue

                        base = (dependency_parser_info, dependency_node)

                except ErrorException as ex:
                    errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # Commit the results
        self._base = base[1] if base else None
        self._concepts = concepts
        self._interfaces = interfaces
        self._mixins = mixins

    # ----------------------------------------------------------------------
    def FinalizePass1(
        self,
        class_parser_info: "ClassStatementParserInfo",
    ) -> None:
        if self._state == _InternalState.FinalizingPass1:
            raise ErrorException(
                CircularDependencyError.Create(
                    region=class_parser_info.regions__.self__,
                    name=class_parser_info.name,
                ),
            )

        if self._state.value >= _InternalState.FinalizedPass1.value:
            return

        self._state = _InternalState.FinalizingPass1

        with ExitStack() as exit_stack:
            # ----------------------------------------------------------------------
            def RestoreStateOnError():
                if self._state != _InternalState.FinalizedPass1:
                    self._state = _InternalState(_InternalState.FinalizingPass1.value - 1)

            # ----------------------------------------------------------------------

            exit_stack.callback(RestoreStateOnError)

            errors: List[Error] = []

            # Finalize the dependencies
            for dependency in itertools.chain(
                [self._base, ] if self._base else [],
                self._concepts,
                self._interfaces,
                self._mixins,
            ):
                try:
                    dependency.ResolveDependencies()[1].FinalizePass1()
                except ErrorException as ex:
                    errors += ex.errors

            if errors:
                raise ErrorException(*errors)

            # Extract type definitions
            local_content = _Pass1Info()

            local_content.concepts += self._concepts
            local_content.interfaces += self._interfaces
            local_content.mixins += self._mixins

            augmented_content = _Pass1Info()
            dependency_content = _Pass1Info()

            for dependency_nodes, target_content in [
                ([self._base, ] if self._base else [], dependency_content),
                (self._concepts, augmented_content),
                (self._interfaces, dependency_content),
                (self._mixins, augmented_content),
            ]:
                if not dependency_nodes:
                    continue

                target_content.Merge(dependency_nodes)

            # BugBug

            self._state = _InternalState.FinalizedPass1

    # ----------------------------------------------------------------------
    def FinalizePass2(
        self,
        class_parser_info: "ClassStatementParserInfo",
    ) -> None:
        if self._state.value >= _InternalState.FinalizingPass2.value:
            return

        self._state = _InternalState.FinalizingPass2

        with ExitStack() as exit_stack:
            # ----------------------------------------------------------------------
            def RestoreStateOnError():
                if self._state != _InternalState.FinalizedPass2:
                    self._state = _InternalState(_InternalState.FinalizingPass2.value - 1)

            # ----------------------------------------------------------------------

            exit_stack.callback(RestoreStateOnError)

            errors: List[Error] = []

            # Finalize the dependencies
            for dependency in itertools.chain(
                [self._base, ] if self._base else [],
                self._concepts,
                self._interfaces,
                self._mixins,
            ):
                try:
                    dependency.ResolveDependencies()[1].FinalizePass2()
                except ErrorException as ex:
                    errors += ex.errors

            if errors:
                raise ErrorException(*errors)

            # BugBug

            self._state = _InternalState.FinalizedPass2

        # BugBug: Validate any contained types if default initializable

        # We are officially done
        self._state = _InternalState.Finalized

    # BugBug # ----------------------------------------------------------------------
    # BugBug def __init__(
    # BugBug     self,
    # BugBug     type_resolver: TypeResolver,
    # BugBug     base_dependency: Optional[Tuple["ClassStatementDependencyParserInfo", GenericType]],
    # BugBug     concept_dependencies: List[Tuple["ClassStatementDependencyParserInfo", GenericType]],
    # BugBug     interface_dependencies: List[Tuple["ClassStatementDependencyParserInfo", GenericType]],
    # BugBug     mixin_dependencies: List[Tuple["ClassStatementDependencyParserInfo", GenericType]],
    # BugBug ):
    # BugBug     self._type_resolver                 = type_resolver
    # BugBug     self._state                         = _InternalState.PreFinalize
    # BugBug
    # BugBug     # The following values are valid while state < _InternalState.FinalizedPass1
    # BugBug     self._base_dependency               = base_dependency
    # BugBug     self._concept_dependencies          = concept_dependencies
    # BugBug     self._interface_dependencies        = interface_dependencies
    # BugBug     self._mixin_dependencies            = mixin_dependencies
    # BugBug
    # BugBug     # The following values are initialized during `FinalizePass1`
    # BugBug     self._base: Optional[Dependency[ConcreteClassType]]                 = None
    # BugBug     self._concepts: Optional[ClassContent[ConcreteClassType]]           = None
    # BugBug     self._interfaces: Optional[ClassContent[ConcreteClassType]]         = None
    # BugBug     self._mixins: Optional[ClassContent[ConcreteClassType]]             = None
    # BugBug     self._types: Optional[ClassContent[ConcreteClass.TypeInfo]]         = None
    # BugBug
    # BugBug     # The following values are initialized during `FinalizePass2`
    # BugBug     self._attributes: Optional[ClassContent[ConcreteClass.AttributeInfo]]                       = None
    # BugBug     self._abstract_methods: Optional[ClassContent[ConcreteClass.TypeInfo]]                      = None
    # BugBug     self._methods: Optional[ClassContent[ConcreteClass.TypeInfo]]                               = None
    # BugBug     self._special_methods: Optional[Dict[SpecialMethodType, SpecialMethodStatementParserInfo]]  = None

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
    def mixins(self) -> ClassContent[ClassType]:
        assert self._state.value >= _InternalState.FinalizedPass1.value
        assert self._mixins is not None
        return self._mixins

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
    def FinalizePass1_BugBug(
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
                (self._mixin_dependencies, "mixins"),
            ]:
                if not dependency_items:
                    continue

                for dependency_parser_info, dependency_class_type in dependency_items:
                    local_content.MergeDependencies(
                        dependency_parser_info,
                        getattr(dependency_class_type.concrete_class, attribute_name),
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
                            self._type_resolver.CreateGenericTypeResolver(statement),
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
                            self._type_resolver.CreateGenericTypeResolver(statement),
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
                    try:
                        processing_func(statement)
                    except ErrorException as ex:
                        errors += ex.errors

            if errors:
                raise ErrorException(*errors)

            if class_type.parser_info.self_referencing_type_names:
                # ----------------------------------------------------------------------
                def ThisClassTypeFactory(*args, **kwargs) -> ClassType:
                    return class_type

                # ----------------------------------------------------------------------

                for self_referencing_type_name in class_type.parser_info.self_referencing_type_names:
                    local_content.types.append(
                        DependencyLeaf(
                            ConcreteClass.TypeInfo(
                                class_type.parser_info,
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

            mixins = ClassContent.Create(
                local_content.mixins,
                augmented_content.mixins,
                dependency_content.mixins,
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
            self._mixins = mixins
            self._types = types

            self._state = _InternalState.FinalizedPass1

            del self._base_dependency
            del self._concept_dependencies
            del self._interface_dependencies
            del self._mixin_dependencies

    # ----------------------------------------------------------------------
    def FinalizePass2_BugBug(
        self,
        class_type: ClassType,
    ) -> None:
        if self._state.value >= _InternalState.FinalizedPass2.value:
            return

        print("BugBug (check)", class_type.parser_info.name, id(class_type), class_type.parser_info.translation_unit__)

        if self._state.value == _InternalState.FinalizingPass2.value:
            # This can happen when a type relies on itself (via a type alias)
            # or the type relies on a type that relies on this one (this is
            # common with fundamental types). Either way, it is safe to bail
            # because we are not evaluating the contents of the types themselves
            # at this point.
            return

        print("BugBug *******", class_type.parser_info.name, id(class_type), class_type.parser_info.translation_unit__)

        errors: List[Error] = []

        self._state = _InternalState.FinalizingPass2

        # ----------------------------------------------------------------------
        def ResetStateOnError():
            if self._state.value == _InternalState.FinalizingPass2.value:
                self._state = _InternalState(_InternalState.FinalizingPass2.value - 1)

        # ----------------------------------------------------------------------

        with ExitStack() as exit_stack:
            exit_stack.callback(ResetStateOnError)

            # Finalize the dependencies
            for dependencies in [
                [self.base, ] if self.base else [],
                self.concepts.EnumContent(),
                self.interfaces.EnumContent(),
                self.mixins.EnumContent(),
            ]:
                for dependency in dependencies:
                    try:
                        dependency.ResolveDependencies()[1].FinalizePass2()
                    except ErrorException as ex:
                        errors += ex.errors

            if errors:
                raise ErrorException(*errors)

            # Merge the dependencies with the information that will be a part of this class
            local_content = _Pass2Info()
            augmented_content = _Pass2Info()
            dependency_content = _Pass2Info()

            for dependencies, target_content in [
                ([self.base, ] if self.base else [], dependency_content),
                (self.concepts.EnumContent(), augmented_content),
                (self.interfaces.EnumContent(), dependency_content),
                (self.mixins.EnumContent(), augmented_content),
            ]:
                try:
                    target_content.Merge(dependencies)
                except ErrorException as ex:
                    errors += ex.errors

            if errors:
                raise ErrorException(*errors)

            # BugBug: Should types be finalized?

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

                attribute_type = self._type_resolver.EvalType(statement.type)

                local_content.attributes.append(
                    DependencyLeaf(ConcreteClass.AttributeInfo(statement, attribute_type)),
                )

            # ----------------------------------------------------------------------
            def ProcessMethod(
                statement: FuncDefinitionStatementParserInfo,
            ) -> None:
                if class_type.parser_info.name == "Str" and statement.name == "OperatorType.Index":
                    BugBug = 10

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
                        self._type_resolver.CreateGenericTypeResolver(statement),
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

                    self._type_resolver.EvalStatements(statement.statements)

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

                resolved_left = self._type_resolver.EvalType(statement.type.left_expression)

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
                if processing_func is None:
                    continue

                try:
                    processing_func(statement)
                except ErrorException as ex:
                    errors += ex.errors

            if errors:
                raise ErrorException(*errors)

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
            self._special_methods = special_methods

            assert self._state == _InternalState.FinalizingPass2, self._state
            self._state = _InternalState.FinalizedPass2

        # Processing is complete
        self._state = _InternalState.Finalized

# BugBug
# BugBug
# BugBug
# BugBug             # Finalize the types created in pass 1
# BugBug
# BugBug             # Create the dependency iterators
# BugBug             dependencies: List[List[Tuple["ClassStatementDependencyParserInfo", ClassType]]] = [
# BugBug                 [self._base_dependency, ] if self._base_dependency else [],
# BugBug                 self._concept_dependencies,
# BugBug                 self._interface_dependencies,
# BugBug                 self._mixin_dependencies,
# BugBug             ]
# BugBug
# BugBug             # Finalize the dependencies (BugBug: Remove this in favor of the captured content)
# BugBug             for dependency_parser_info, dependency_class in itertools.chain(*dependencies):  # pylint: disable=unused-variable
# BugBug                 try:
# BugBug                     dependency_class.FinalizePass2()
# BugBug                 except ErrorException as ex:
# BugBug                     errors += ex.errors
# BugBug
# BugBug             if errors or self._state != _InternalState.FinalizingPass2:
# BugBug                 return
# BugBug
# BugBug             # Finalize the content created in pass 1
# BugBug             # BugBug
# BugBug
# BugBug             # Merge the content
# BugBug             local_content = _Pass2Info()
# BugBug             augmented_content = _Pass2Info()
# BugBug             dependency_content = _Pass2Info()
# BugBug
# BugBug             for dependency_items, target_content in zip(
# BugBug                 dependencies,
# BugBug                 [
# BugBug                     dependency_content, # base
# BugBug                     augmented_content,  # concepts
# BugBug                     dependency_content, # interfaces
# BugBug                     augmented_content,  # mixins
# BugBug                 ],
# BugBug             ):
# BugBug                 if not dependency_items:
# BugBug                     continue
# BugBug
# BugBug                 target_content.Merge(dependency_items)
# BugBug
# BugBug             if errors or self._state != _InternalState.FinalizingPass2:
# BugBug                 return
# BugBug
# BugBug             # Prepare the local content
# BugBug
# BugBug             special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo] = {}
# BugBug             using_statements: List[
# BugBug                 Tuple[
# BugBug                     VisibilityModifier,
# BugBug                     ClassType,
# BugBug                     FuncDefinitionStatementParserInfo,
# BugBug                 ],
# BugBug             ] = []
# BugBug
# BugBug             # ----------------------------------------------------------------------
# BugBug             def ProcessAttribute(
# BugBug                 statement: ClassAttributeStatementParserInfo,
# BugBug             ) -> None:
# BugBug                 # BugBug: process 'is_override'
# BugBug
# BugBug                 attribute_type = self._type_resolver.EvalType(statement.type)
# BugBug
# BugBug                 local_content.attributes.append(
# BugBug                     DependencyLeaf(ConcreteClass.AttributeInfo(statement, attribute_type)),
# BugBug                 )
# BugBug
# BugBug             # ----------------------------------------------------------------------
# BugBug             def ProcessMethod(
# BugBug                 statement: FuncDefinitionStatementParserInfo,
# BugBug             ) -> None:
# BugBug                 # Ensure that the method's mutability agrees with the class's mutability
# BugBug                 if (
# BugBug                     statement.mutability is not None
# BugBug                     and class_type.parser_info.class_modifier == ClassModifier.immutable
# BugBug                     and MutabilityModifier.IsMutable(statement.mutability)
# BugBug                 ):
# BugBug                     errors.append(
# BugBug                         InvalidMutableMethodError.Create(
# BugBug                             region=statement.regions__.mutability,
# BugBug                             mutability=statement.mutability,
# BugBug                             mutability_str=statement.mutability.name,
# BugBug                             class_region=class_type.parser_info.regions__.class_modifier,
# BugBug                         ),
# BugBug                     )
# BugBug
# BugBug                     return
# BugBug
# BugBug                 # Ensure that the hierarchy modifiers agree with the derived methods
# BugBug                 if (
# BugBug                     statement.method_hierarchy_modifier is not None
# BugBug                     and statement.method_hierarchy_modifier != MethodHierarchyModifier.standard
# BugBug                 ):
# BugBug                     pass # BugBug: Do this
# BugBug
# BugBug                 dependency_leaf = DependencyLeaf(
# BugBug                     ConcreteClass.TypeInfo(
# BugBug                         statement,
# BugBug                         self._type_resolver.CreateGenericTypeResolver(statement),
# BugBug                     ),
# BugBug                 )
# BugBug
# BugBug                 if statement.method_hierarchy_modifier == MethodHierarchyModifier.abstract:
# BugBug                     local_content.abstract_methods.append(dependency_leaf)
# BugBug                 else:
# BugBug                     local_content.methods.append(dependency_leaf)
# BugBug
# BugBug             # ----------------------------------------------------------------------
# BugBug             def ProcessSpecialMethod(
# BugBug                 statement: SpecialMethodStatementParserInfo,
# BugBug             ) -> None:
# BugBug                 # Determine if the special method is valid for the class
# BugBug                 if statement.special_method_type == SpecialMethodType.EvalTemplates:
# BugBug                     if not class_type.parser_info.templates:
# BugBug                         errors.append(
# BugBug                             InvalidEvalTemplatesMethodError.Create(
# BugBug                                 region=statement.regions__.special_method_type,
# BugBug                             ),
# BugBug                         )
# BugBug
# BugBug                         return
# BugBug
# BugBug                     self._type_resolver.EvalStatements(statement.statements)
# BugBug
# BugBug                 if (
# BugBug                     statement.special_method_type == SpecialMethodType.EvalConstraints
# BugBug                     and not class_type.parser_info.constraints
# BugBug                 ):
# BugBug                     errors.append(
# BugBug                         InvalidEvalConstraintsMethodError.Create(
# BugBug                             region=statement.regions__.special_method_type,
# BugBug                         ),
# BugBug                     )
# BugBug
# BugBug                     return
# BugBug
# BugBug                 if (
# BugBug                     (
# BugBug                         statement.special_method_type == SpecialMethodType.PrepareFinalize
# BugBug                         or statement.special_method_type == SpecialMethodType.Finalize
# BugBug                     )
# BugBug                     and class_type.parser_info.class_modifier != ClassModifier.mutable
# BugBug                 ):
# BugBug                     errors.append(
# BugBug                         InvalidFinalizeMethodError.Create(
# BugBug                             region=statement.regions__.special_method_type,
# BugBug                         ),
# BugBug                     )
# BugBug
# BugBug                     return
# BugBug
# BugBug                 prev_special_method = special_methods.get(statement.special_method_type, None)
# BugBug                 if prev_special_method is not None:
# BugBug                     errors.append(
# BugBug                         DuplicateSpecialMethodError.Create(
# BugBug                             region=statement.regions__.special_method_type,
# BugBug                             name=statement.special_method_type,
# BugBug                             prev_region=prev_special_method.regions__.special_method_type,
# BugBug                         ),
# BugBug                     )
# BugBug
# BugBug                     return
# BugBug
# BugBug                 special_methods[statement.special_method_type] = statement
# BugBug
# BugBug             # ----------------------------------------------------------------------
# BugBug             def ProcessUsingStatement(
# BugBug                 statement: ClassUsingStatementParserInfo,
# BugBug             ) -> None:
# BugBug                 assert isinstance(statement.type, BinaryExpressionParserInfo), statement.type
# BugBug                 assert statement.type.operator == BinaryExpressionOperatorType.Access, statement.type.operator
# BugBug
# BugBug                 resolved_left = self._type_resolver.EvalType(statement.type.left_expression)
# BugBug
# BugBug                 # BugBug: Finish this
# BugBug
# BugBug             # ----------------------------------------------------------------------
# BugBug
# BugBug             processing_funcs = {
# BugBug                 "ClassAttributeStatementParserInfo": ProcessAttribute,
# BugBug                 "FuncDefinitionStatementParserInfo": ProcessMethod,
# BugBug                 "SpecialMethodStatementParserInfo": ProcessSpecialMethod,
# BugBug                 "ClassUsingStatementParserInfo": ProcessUsingStatement,
# BugBug             }
# BugBug
# BugBug             assert class_type.parser_info.statements is not None
# BugBug             for statement in class_type.parser_info.statements:
# BugBug                 if statement.is_disabled__:
# BugBug                     continue
# BugBug
# BugBug                 processing_func = processing_funcs.get(type(statement).__name__, None)
# BugBug                 if processing_func is None:
# BugBug                     continue
# BugBug
# BugBug                 try:
# BugBug                     processing_func(statement)
# BugBug                 except ErrorException as ex:
# BugBug                     errors += ex.errors
# BugBug
# BugBug             if errors or self._state != _InternalState.FinalizingPass2:
# BugBug                 return
# BugBug
# BugBug             # Issue an error if the class was declared as abstract but no abstract methods were found
# BugBug             if (
# BugBug                 class_type.parser_info.is_abstract
# BugBug                 and not (
# BugBug                     local_content.abstract_methods
# BugBug                     or augmented_content.abstract_methods
# BugBug                     or dependency_content.abstract_methods
# BugBug                 )
# BugBug             ):
# BugBug                 errors.append(
# BugBug                     InvalidAbstractDecorationError.Create(
# BugBug                         region=class_type.parser_info.regions__.is_abstract,
# BugBug                     ),
# BugBug                 )
# BugBug
# BugBug             # Issue an error if the class was declared as final but there are abstract methods
# BugBug             if (
# BugBug                 class_type.parser_info.is_final
# BugBug                 and (
# BugBug                     local_content.abstract_methods
# BugBug                     or augmented_content.abstract_methods
# BugBug                     or dependency_content.abstract_methods
# BugBug                 )
# BugBug             ):
# BugBug                 errors.append(
# BugBug                     InvalidFinalDecorationError.Create(
# BugBug                         region=class_type.parser_info.regions__.is_final,
# BugBug                     ),
# BugBug                 )
# BugBug
# BugBug             # Issue an error if the class was declared as mutable but no mutable methods were found
# BugBug             if class_type.parser_info.class_modifier == ClassModifier.mutable:
# BugBug                 has_mutable_method = False
# BugBug
# BugBug                 for dependency in itertools.chain(
# BugBug                     local_content.methods,
# BugBug                     local_content.abstract_methods,
# BugBug                     augmented_content.methods,
# BugBug                     augmented_content.abstract_methods,
# BugBug                     dependency_content.methods,
# BugBug                     dependency_content.abstract_methods,
# BugBug                 ):
# BugBug                     method_info = dependency.ResolveDependencies()[1]
# BugBug                     assert isinstance(method_info, ConcreteClass.TypeInfo), method_info
# BugBug
# BugBug                     assert isinstance(method_info.statement, FuncDefinitionStatementParserInfo), method_info.statement
# BugBug
# BugBug                     if (
# BugBug                         method_info.statement.mutability is not None
# BugBug                         and MutabilityModifier.IsMutable(method_info.statement.mutability)
# BugBug                     ):
# BugBug                         has_mutable_method = True
# BugBug                         break
# BugBug
# BugBug                 if not has_mutable_method:
# BugBug                     errors.append(
# BugBug                         InvalidMutableDecorationError.Create(
# BugBug                             region=class_type.parser_info.regions__.class_modifier,
# BugBug                         ),
# BugBug                     )
# BugBug
# BugBug             # Commit the results
# BugBug
# BugBug             # ----------------------------------------------------------------------
# BugBug             def MethodIdExtractor(
# BugBug                 type_info: ConcreteClass.TypeInfo,
# BugBug             ) -> Any:
# BugBug                 # BugBug
# BugBug                 return id(type_info.statement)
# BugBug
# BugBug             # ----------------------------------------------------------------------
# BugBug
# BugBug             attributes = ClassContent.Create(
# BugBug                 local_content.attributes,
# BugBug                 augmented_content.attributes,
# BugBug                 dependency_content.attributes,
# BugBug                 lambda attribute_info: attribute_info.statement.name,
# BugBug             )
# BugBug
# BugBug             abstract_methods = ClassContent.Create(
# BugBug                 local_content.abstract_methods,
# BugBug                 augmented_content.abstract_methods,
# BugBug                 dependency_content.abstract_methods,
# BugBug                 MethodIdExtractor,
# BugBug             )
# BugBug
# BugBug             methods = ClassContent.Create(
# BugBug                 local_content.methods,
# BugBug                 augmented_content.methods,
# BugBug                 dependency_content.methods,
# BugBug                 MethodIdExtractor,
# BugBug                 _PostprocessMethodCreateClassContent,
# BugBug             )
# BugBug
# BugBug             self._attributes = attributes
# BugBug             self._abstract_methods = abstract_methods
# BugBug             self._methods = methods
# BugBug
# BugBug             assert not errors
# BugBug
# BugBug             assert self._state == _InternalState.FinalizingPass2, self._state
# BugBug             self._state = _InternalState.FinalizedPass2
# BugBug
# BugBug             should_finalize = True
# BugBug
# BugBug         self._Finalize()


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
class _Pass1Info(object):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.concepts: List[Dependency[ConcreteType]]                       = []
        self.interfaces: List[Dependency[ConcreteType]]                     = []
        self.mixins: List[Dependency[ConcreteType]]                         = []
        self.types: List[Dependency[ConcreteClass.TypeInfo]]                = []

    # ----------------------------------------------------------------------
    def Merge(
        self,
        dependencies: List[DependencyNode[ConcreteType]],
    ) -> None:
        if not dependencies:
            return

        for attribute_name in [
            "concepts",
            "interfaces",
            "mixins",
            "types",
        ]:
            dest_items = getattr(self, attribute_name)

            for dependency in dependencies:
                visibility, concrete_type
                source_items = getattr(





    # ----------------------------------------------------------------------
    def MergeDependencies(
        self,
        dependency_parser_info: "ClassStatementDependencyParserInfo",
        source_items: List[Dependency],
        dest_attribute_name: str,
    ) -> None:
        dest = getattr(self, dest_attribute_name)

        for source_item in source_items:
            dest.append(DependencyNode(dependency_parser_info, source_item))

    # ----------------------------------------------------------------------
    def Merge(
        self,
        source_items: List[DependencyNode[ConcreteType]],
    ) -> None:
        if not source_items:
            return

        for attribute_name in [
            "concepts",
            "interfaces",
            "mixins",
            "types",
        ]:
            for dependency_parser_info, class_type in source_items:
                self.MergeDependencies(
                    dependency_parser_info,
                    getattr(class_type.concrete_class, attribute_name),
                    attribute_name,
                )


# ----------------------------------------------------------------------
class _Pass2Info(object):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.attributes: List[Dependency[ConcreteClass.AttributeInfo]]      = []
        self.abstract_methods: List[Dependency[ConcreteClass.TypeInfo]]     = []
        self.methods: List[Dependency[ConcreteClass.TypeInfo]]              = []

    # ----------------------------------------------------------------------
    def Merge(
        self,
        dependencies_iter: Iterable[Dependency[ClassType]],
    ) -> None:
        for dependency in dependencies_iter:
            dependency_class_type = dependency.ResolveDependencies()[1]

            for attribute_name in [
                "attributes",
                "abstract_methods",
                "methods",
            ]:
                getattr(self, attribute_name).extend(
                    getattr(
                        dependency_class_type.concrete_class,
                        attribute_name,
                    ).EnumContent(),
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
