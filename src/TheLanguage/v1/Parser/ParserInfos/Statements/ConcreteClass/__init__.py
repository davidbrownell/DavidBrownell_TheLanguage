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

    from ...EntityResolver import EntityResolver
    from ...Types import ClassType, ConcreteType, FuncDefinitionType, NoneType, Type, TypeAliasType

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
        concrete_type_factory_func: Callable[[Optional[TemplateArgumentsParserInfo]], ConcreteType]

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class AttributeInfo(object):
        # ----------------------------------------------------------------------
        statement: ClassAttributeStatementParserInfo
        type: Type

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        self._state                         = _InternalState.PreFinalize

        self._base: Optional[ClassType]                                                              = None
        self._special_methods: Optional[Dict[SpecialMethodType, SpecialMethodStatementParserInfo]]   = None

        self._interfaces: Optional[ClassContent[ClassType]]                     = None
        self._concepts: Optional[ClassContent[ClassType]]                       = None

        self._types: Optional[ClassContent[ConcreteClass.TypeInfo]]             = None
        self._attributes: Optional[ClassContent[ConcreteClass.AttributeInfo]]   = None

        self._abstract_methods: Optional[ClassContent[ConcreteClass.TypeInfo]]  = None
        self._methods: Optional[ClassContent[ConcreteClass.TypeInfo]]           = None

    # ----------------------------------------------------------------------
    @property
    def base(self) -> Optional[ClassType]:
        assert self._state == _InternalState.Finalized
        return self._base

    @property
    def special_methods(self) -> Dict[SpecialMethodType, SpecialMethodStatementParserInfo]:
        assert self._state == _InternalState.Finalized
        assert self._special_methods is not None
        return self._special_methods

    @property
    def interfaces(self) -> ClassContent[ClassType]:
        assert self._state == _InternalState.Finalized
        assert self._interfaces is not None
        return self._interfaces

    @property
    def concepts(self) -> ClassContent[ClassType]:
        assert self._state == _InternalState.Finalized
        assert self._concepts is not None
        return self._concepts

    @property
    def types(self) -> ClassContent["ConcreteClass.TypeInfo"]:
        assert self._state == _InternalState.Finalized
        assert self._types is not None
        return self._types

    @property
    def attributes(self) -> ClassContent["ConcreteClass.AttributeInfo"]:
        assert self._state == _InternalState.Finalized
        assert self._attributes is not None
        return self._attributes

    @property
    def abstract_methods(self) -> ClassContent["ConcreteClass.TypeInfo"]:
        assert self._state == _InternalState.Finalized
        assert self._abstract_methods is not None
        return self._abstract_methods

    @property
    def methods(self) -> ClassContent["ConcreteClass.TypeInfo"]:
        assert self._state == _InternalState.Finalized
        assert self._methods is not None
        return self._methods

    # ----------------------------------------------------------------------
    def Finalize(
        self,
        class_parser_info: "ClassStatementParserInfo",
        entity_resolver: EntityResolver,
    ) -> None:
        if self._state == _InternalState.Finalized:
            return
        elif self._state == _InternalState.FinalizingLocalContent:
            # It isn't a problem if items in a class reference itself
            return
        elif self._state == _InternalState.FinalizingDependencies:
            raise ErrorException(
                CircularDependencyError.Create(
                    region=class_parser_info.regions__.self__,
                    name=class_parser_info.name,
                ),
            )

        assert self._state == _InternalState.PreFinalize

        errors: List[Error] = []

        # Organize dependencies
        self._state = _InternalState.FinalizingDependencies

        initial_base: Optional[Tuple["ClassStatementDependencyParserInfo", ClassType]] = None
        initial_mixins: List[Tuple["ClassStatementDependencyParserInfo", ClassType]] = []
        initial_concepts: List[Tuple["ClassStatementDependencyParserInfo", ClassType]] = []
        initial_interfaces: List[Tuple["ClassStatementDependencyParserInfo", ClassType]] = []

        try:
            for dependency_parser_info, class_type in _EnumDependencies(
                class_parser_info,
                entity_resolver,
            ):
                if class_type.parser_info.is_final:
                    errors.append(
                        FinalDependencyError.Create(
                            region=dependency_parser_info.regions__.self__,
                            name=class_type.parser_info.name,
                            final_class_region=class_type.parser_info.regions__.is_final,
                        ),
                    )

                    continue

                if class_type.parser_info.class_capabilities.name == "Mixin":
                    initial_mixins.append((dependency_parser_info, class_type))
                elif class_type.parser_info.class_capabilities.name == "Concept":
                    initial_concepts.append((dependency_parser_info, class_type))
                elif class_type.parser_info.class_capabilities.name == "Interface":
                    initial_interfaces.append((dependency_parser_info, class_type))
                else:
                    if initial_base is not None:
                        errors.append(
                            MultipleBasesError.Create(
                                region=dependency_parser_info.regions__.self__,
                                prev_region=initial_base[0].regions__.self__,  # pylint: disable=unsubscriptable-object
                            ),
                        )

                    initial_base = (dependency_parser_info, class_type)

                try:
                    class_type.Finalize(entity_resolver)
                except ErrorException as ex:
                    errors += ex.errors

        except ErrorException as ex:
            errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # Extract dependency content
        local_content = _BasicContent()
        augmented_content = _BasicContent()
        dependency_content = _BasicContent()

        for dependency_items, attribute_name in [
            (initial_interfaces, "interfaces"),
            (initial_concepts, "concepts"),
        ]:
            if not dependency_items:
                continue

            for dependency_parser_info, class_type in dependency_items:
                local_content.MergeDependencies(
                    dependency_parser_info,
                    getattr(class_type.concrete_class, attribute_name).EnumDependencies(),
                    attribute_name,
                )

        # Augment our data with the data in the dependencies
        for dependency_items, target_content in [
            ([initial_base, ] if initial_base else [], dependency_content),
            (initial_interfaces, dependency_content),
            (initial_concepts, augmented_content),
            (initial_mixins, augmented_content),
        ]:
            if not dependency_items:
                continue

            target_content.Merge(dependency_items)

        # Extract local content
        self._state = _InternalState.FinalizingLocalContent

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

            local_content.attributes.append(
                DependencyLeaf(
                    ConcreteClass.AttributeInfo(
                        statement,
                        entity_resolver.ResolveType(statement.type),
                    ),
                ),
            )

        # ----------------------------------------------------------------------
        def ProcessClass(
            statement: "ClassStatementParserInfo",
        ) -> None:
            local_content.types.append(
                DependencyLeaf(
                    ConcreteClass.TypeInfo(
                        statement,
                        statement.CreateConcreteTypeFactory(entity_resolver),
                    ),
                ),
            )

        # ----------------------------------------------------------------------
        def ProcessMethod(
            statement: FuncDefinitionStatementParserInfo,
        ) -> None:
            # Ensure that the method's mutability agrees with the class's mutability
            if (
                statement.mutability is not None
                and class_parser_info.class_modifier == ClassModifier.immutable
                and MutabilityModifier.IsMutable(statement.mutability)
            ):
                errors.append(
                    InvalidMutableMethodError.Create(
                        region=statement.regions__.mutability,
                        mutability=statement.mutability,
                        mutability_str=statement.mutability.name,
                        class_region=class_parser_info.regions__.class_modifier,
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
                    statement.CreateConcreteTypeFactory(entity_resolver),
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
                if not class_parser_info.templates:
                    errors.append(
                        InvalidEvalTemplatesMethodError.Create(
                            region=statement.regions__.special_method_type,
                        ),
                    )

                    return

                entity_resolver.EvalStatements(statement.statements)

            if (
                statement.special_method_type == SpecialMethodType.EvalConstraints
                and not class_parser_info.constraints
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
                and class_parser_info.class_modifier != ClassModifier.mutable
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
        def ProcessTypeAlias(
            statement: TypeAliasStatementParserInfo,
        ) -> None:
            local_content.types.append(
                DependencyLeaf(
                    ConcreteClass.TypeInfo(
                        statement,
                        statement.CreateConcreteTypeFactory(entity_resolver),
                    ),
                ),
            )

        # ----------------------------------------------------------------------
        def ProcessUsing(
            statement: ClassUsingStatementParserInfo,
        ) -> None:
            assert isinstance(statement.type, BinaryExpressionParserInfo), statement.type
            assert statement.type.operator == BinaryExpressionOperatorType.Access, statement.type.operator

            resolved_left = entity_resolver.ResolveType(statement.type.left_expression)

            # BugBug: Finish this

        # ----------------------------------------------------------------------

        processing_funcs = {
            "ClassAttributeStatementParserInfo": ProcessAttribute,
            "ClassStatementParserInfo": ProcessClass,
            "ClassUsingStatementParserInfo": ProcessUsing,
            "FuncDefinitionStatementParserInfo": ProcessMethod,
            "SpecialMethodStatementParserInfo": ProcessSpecialMethod,
            "TypeAliasStatementParserInfo": ProcessTypeAlias,
        }

        assert class_parser_info.statements is not None

        for statement in class_parser_info.statements:
            if statement.is_disabled__:
                continue

            processing_func = processing_funcs.get(statement.__class__.__name__, None)
            assert processing_func is not None, statement

            processing_func(statement)

        # Issue an error if the class was declared as abstract but no abstract methods were found
        if (
            class_parser_info.is_abstract
            and not (
                local_content.abstract_methods
                or augmented_content.abstract_methods
                or dependency_content.abstract_methods
            )
        ):
            errors.append(
                InvalidAbstractDecorationError.Create(
                    region=class_parser_info.regions__.is_abstract,
                ),
            )

        # Issue an error if the class was declared as final but there are abstract methods
        if (
            class_parser_info.is_final
            and (
                local_content.abstract_methods
                or augmented_content.abstract_methods
                or dependency_content.abstract_methods
            )
        ):
            errors.append(
                InvalidFinalDecorationError.Create(
                    region=class_parser_info.regions__.is_final,
                ),
            )

        # Issue an error if the class was declared as mutable but no mutable methods were found
        if class_parser_info.class_modifier == ClassModifier.mutable:
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
                        region=class_parser_info.regions__.class_modifier,
                    ),
                )

        if errors:
            raise ErrorException(*errors)

        # Commit the data
        if initial_base:
            base = DependencyNode(initial_base[0], DependencyLeaf(initial_base[1]))
        else:
            base = None

        interfaces = ClassContent.Create(
            local_content.interfaces,
            augmented_content.interfaces,
            dependency_content.interfaces,
            lambda class_type: class_type.parser_info.name,
        )

        concepts = ClassContent.Create(
            local_content.concepts,
            augmented_content.concepts,
            dependency_content.concepts,
            lambda class_type: class_type.parser_info.name,
        )

        types = ClassContent.Create(
            local_content.types,
            augmented_content.types,
            dependency_content.types,
            lambda type_info: type_info.statement.name,
        )

        attributes = ClassContent.Create(
            local_content.attributes,
            augmented_content.attributes,
            dependency_content.attributes,
            lambda attribute_info: attribute_info.statement.name,
        )

        # ----------------------------------------------------------------------
        def MethodIdExtractor(
            type_info: ConcreteClass.TypeInfo,
        ) -> Any:
            # BugBug
            return id(type_info.statement)

        # ----------------------------------------------------------------------

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

        self._base = base
        self._special_methods = special_methods
        self._interfaces = interfaces
        self._concepts = concepts
        self._types = types
        self._attributes = attributes
        self._abstract_methods = abstract_methods
        self._methods = methods

        # We're done
        self._state = _InternalState.Finalized


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _InternalState(Enum):
    PreFinalize                             = auto()
    FinalizingDependencies                  = auto()
    FinalizingLocalContent                  = auto()
    Finalized                               = auto()


# ----------------------------------------------------------------------
class _BasicContent(object):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.interfaces: List[Dependency[ClassType]]                        = []
        self.concepts: List[Dependency[ClassType]]                          = []
        self.types: List[Dependency["ConcreteClass.TypeInfo"]]              = []
        self.attributes: List[Dependency["ConcreteClass.AttributeInfo"]]    = []
        self.abstract_methods: List[Dependency["ConcreteClass.TypeInfo"]]   = []
        self.methods: List[Dependency["ConcreteClass.TypeInfo"]]            = []

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
    def Merge(
        self,
        source_items: List[Tuple["ClassStatementDependencyParserInfo", ClassType]],
    ) -> None:
        if not source_items:
            return

        for dependency_parser_info, class_type in source_items:
            for attribute_name in [
                "interfaces",
                "concepts",
                "types",
                "attributes",
                "abstract_methods",
                "methods",
            ]:
                self.MergeDependencies(
                    dependency_parser_info,
                    getattr(class_type.concrete_class, attribute_name).EnumDependencies(),
                    attribute_name,
                )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _EnumDependencies(
    class_parser_info: "ClassStatementParserInfo",
    entity_resolver: EntityResolver,
) -> Generator[
    Tuple[
        "ClassStatementDependencyParserInfo",
        ClassType,
    ],
    None,
    None,
]:
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

        for dependency in dependencies:
            if dependency.is_disabled__:
                continue

            resolved_type = entity_resolver.ResolveType(
                dependency.type,
                resolve_aliases=True,
            )

            if isinstance(resolved_type, NoneType):
                continue

            try:
                dependency_validation_func(dependency, resolved_type)
            except ErrorException as ex:
                errors += ex.errors
                continue

            assert isinstance(resolved_type, ClassType), resolved_type
            yield dependency, resolved_type

    if errors:
        raise ErrorException(*errors)


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
