# ----------------------------------------------------------------------
# |
# |  ConcreteClass.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-07 07:57:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality helpful when interacting with concrete classes (classes whose template parameters have been associated with template arguments)"""

import itertools
import os

from typing import cast, Dict, Generator, List, Optional, Tuple, TYPE_CHECKING, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .HierarchyInfo import Dependency, DependencyLeaf, DependencyNode
    from .TypeDependencies import TypeDependencies

    from ..ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ..ClassUsingStatementParserInfo import ClassUsingStatementParserInfo
    from ..FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ..SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo, SpecialMethodType
    from ..TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ...Common.ClassModifier import ClassModifier
    from ...Common.MethodHierarchyModifier import MethodHierarchyModifier
    from ...Common.MutabilityModifier import MutabilityModifier
    from ...Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo

    from ...Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ...EntityResolver import EntityResolver
    from ...ParserInfo import CompileTimeInfo
    from ...Types import ClassType, NoneType

    from ....Error import CreateError, Error, ErrorException
    from ....TranslationUnitRegion import TranslationUnitRegion
    from ....Visitors.Namespaces import Namespace

    if TYPE_CHECKING:
        from ..ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo


# ----------------------------------------------------------------------
InvalidDependencyError                      = CreateError(
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

MissingAbstractMethodsError                 = CreateError(
    "The class is marked as abstract, but no abstract methods were encountered",
)

InvalidFinalError                           = CreateError(
    "The class is marked as final, but abstract methods were encountered",
)

InvalidMutableError                         = CreateError(
    "The class is marked as mutable, but no mutable methods were found",
)

InvalidMutableMethodError                   = CreateError(
    "The class is marked as immutable, but the method is marked as '{mutability_str}'",
    mutability=MutabilityModifier,
    mutability_str=str,
    class_region=TranslationUnitRegion,
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

DuplicateSpecialMethodError                 = CreateError(
    "The special method '{name}' has already been defined",
    name=str,
    prev_region=TranslationUnitRegion,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ConcreteClass(object):
    # ----------------------------------------------------------------------
    parser_info: "ClassStatementParserInfo"

    base: Optional[DependencyNode]
    special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo]

    interfaces: TypeDependencies
    concepts: TypeDependencies
    types: TypeDependencies
    attributes: TypeDependencies
    abstract_methods: TypeDependencies
    methods: TypeDependencies

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        class_statement_parser_info: "ClassStatementParserInfo",
        entity_resolver: EntityResolver,
    ):
        errors: List[Error] = []

        base: Optional[DependencyNode] = None

        local_interfaces: List[Dependency] = []
        local_concepts: List[Dependency] = []

        augmented_interfaces: List[Dependency] = []
        augmented_concepts: List[Dependency] = []
        augmented_types: List[Dependency] = []
        augmented_attributes: List[Dependency] = []
        augmented_abstract_methods: List[Dependency] = []
        augmented_methods: List[Dependency] = []

        dependency_interfaces: List[Dependency] = []
        dependency_concepts: List[Dependency] = []
        dependency_types: List[Dependency] = []
        dependency_attributes: List[Dependency] = []
        dependency_abstract_methods: List[Dependency] = []
        dependency_methods: List[Dependency] = []

        for dependency, resolved_entity in cls._EnumDependencies(
            entity_resolver,
            class_statement_parser_info,
        ):
            resolved_parser_info = cast("ClassStatementParserInfo", resolved_entity.parser_info)

            if resolved_parser_info.is_final:
                errors.append(
                    FinalDependencyError.Create(
                        region=dependency.regions__.self__,
                        name=resolved_parser_info.name,
                        final_class_region=resolved_parser_info.regions__.self__,
                    ),
                )
                continue

            assert dependency.visibility is not None

            hierarchy_methods_are_polymorphic: Optional[bool] = None
            target_interfaces: Optional[List[Dependency]] = None
            target_concepts: Optional[List[Dependency]] = None
            target_types: Optional[List[Dependency]] = None
            target_attributes: Optional[List[Dependency]] = None
            target_abstract_methods: Optional[List[Dependency]] = None
            target_methods: Optional[List[Dependency]] = None

            if (
                resolved_parser_info.class_capabilities.name == "Mixin"
                or resolved_parser_info.class_capabilities.name == "Concept"
            ):
                hierarchy_methods_are_polymorphic = False

                target_interfaces = augmented_interfaces
                target_concepts = augmented_concepts
                target_types = augmented_types
                target_attributes = augmented_attributes
                target_abstract_methods = augmented_abstract_methods
                target_methods = augmented_methods

                if resolved_parser_info.class_capabilities.name == "Concept":
                    local_concepts.append(
                        DependencyNode(
                            dependency,
                            DependencyLeaf(resolved_parser_info, resolved_parser_info),
                        ),
                    )

            else:
                hierarchy_methods_are_polymorphic = True

                target_interfaces = dependency_interfaces
                target_concepts = dependency_concepts
                target_types = dependency_types
                target_attributes = dependency_attributes
                target_abstract_methods = dependency_abstract_methods
                target_methods = dependency_methods

                if resolved_parser_info.class_capabilities.name == "Interface":
                    local_interfaces.append(
                        DependencyNode(
                            dependency,
                            DependencyLeaf(resolved_parser_info, resolved_parser_info),
                        ),
                    )

                else:
                    if base is not None:
                        errors.append(
                            MultipleBasesError.Create(
                                region=dependency.regions__.self__,
                                prev_region=base.dependency.regions__.self__,
                            ),
                        )

                        continue

                    base = DependencyNode(
                        dependency,
                        DependencyLeaf(resolved_parser_info, resolved_parser_info),
                    )

            assert hierarchy_methods_are_polymorphic is not None
            assert target_interfaces is not None
            assert target_concepts is not None
            assert target_types is not None
            assert target_attributes is not None
            assert target_abstract_methods is not None
            assert target_methods is not None

            for attribute_name, target in [
                ("interfaces", target_interfaces),
                ("concepts", target_concepts),
                ("types", target_types),
                ("attributes", target_attributes),
                ("abstract_methods", target_abstract_methods if hierarchy_methods_are_polymorphic else target_methods),
                ("methods", target_methods),
            ]:
                for item in getattr(resolved_entity.concrete_class, attribute_name).EnumItems():
                    target.append(DependencyNode(dependency, item))

        # Process the local statements
        special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo] = {}
        local_types: List[Dependency] = []
        local_attributes: List[Dependency] = []
        local_abstract_methods: List[Dependency] = []
        local_methods: List[Dependency] = []

        assert class_statement_parser_info.statements is not None
        for statement in class_statement_parser_info.statements:
            if statement.is_disabled__:
                continue

            if isinstance(statement, ClassAttributeStatementParserInfo):
                # BugBug: Validate is_override
                local_attributes.append(DependencyLeaf(class_statement_parser_info, statement))

            elif statement.__class__.__name__ == "ClassStatementParserInfo":
                local_types.append(DependencyLeaf(class_statement_parser_info, statement))  # type: ignore

            elif isinstance(statement, ClassUsingStatementParserInfo):
                raise NotImplementedError("TODO: ClassUsingStatementParserInfo")

            elif isinstance(statement, FuncDefinitionStatementParserInfo):
                # Ensure that the method's mutability agrees with the class's mutability
                if (
                    statement.mutability is not None
                    and class_statement_parser_info.class_modifier == ClassModifier.immutable
                    and MutabilityModifier.IsMutable(statement.mutability)
                ):
                    errors.append(
                        InvalidMutableMethodError.Create(
                            region=statement.regions__.mutability,
                            mutability=statement.mutability,
                            mutability_str=statement.mutability.name,
                            class_region=class_statement_parser_info.regions__.class_modifier,
                        ),
                    )

                    continue

                # Ensure that the hierarchy modifiers agree with the methods defined in base classes
                if (
                    statement.method_hierarchy_modifier is not None
                    and statement.method_hierarchy_modifier != MethodHierarchyModifier.standard
                ):
                    pass # BugBug: Check hierarchy

                if statement.method_hierarchy_modifier == MethodHierarchyModifier.abstract:
                    local_abstract_methods.append(DependencyLeaf(class_statement_parser_info, statement))
                else:
                    local_methods.append(DependencyLeaf(class_statement_parser_info, statement))

            elif isinstance(statement, SpecialMethodStatementParserInfo):
                # Determine if the special method is valid for the class
                if (
                    statement.special_method_type == SpecialMethodType.EvalTemplates
                    and not class_statement_parser_info.templates
                ):
                    errors.append(
                        InvalidEvalTemplatesMethodError.Create(
                            region=statement.regions__.special_method_type,
                        ),
                    )

                    continue

                if (
                    statement.special_method_type == SpecialMethodType.CompileTimeEvalConstraints
                    and not class_statement_parser_info.constraints
                ):
                    errors.append(
                        InvalidEvalConstraintsMethodError.Create(
                            region=statement.regions__.special_method_type,
                        ),
                    )

                    continue

                if (
                    (
                        statement.special_method_type == SpecialMethodType.PrepareFinalize
                        or statement.special_method_type == SpecialMethodType.Finalize
                    )
                    and class_statement_parser_info.class_modifier == ClassModifier.immutable
                ):
                    errors.append(
                        InvalidFinalizeMethodError.Create(
                            region=statement.regions__.special_method_type,
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
                local_types.append(DependencyLeaf(class_statement_parser_info, statement))

            else:
                assert False, statement

        # Issue an error if the class was declared as abstract but no abstract methods were found
        if class_statement_parser_info.is_abstract and not local_abstract_methods:
            errors.append(
                MissingAbstractMethodsError.Create(
                    region=class_statement_parser_info.regions__.is_abstract,
                ),
            )

        # Issue an error if the class was declared as final but there are still abstract methods
        if (
            class_statement_parser_info.is_final
            and (
                local_abstract_methods
                or augmented_abstract_methods
                or dependency_abstract_methods,
            )
        ):
            errors.append(
                InvalidFinalError.Create(
                    region=class_statement_parser_info.regions__.is_final,
                ),
            )

        # Issue an error if the class was declared as mutable but no mutable methods were found
        if class_statement_parser_info.class_modifier == ClassModifier.mutable:
            has_mutable_method = False

            for dependency_item in itertools.chain(
                local_methods,
                local_abstract_methods,
                augmented_methods,
                augmented_abstract_methods,
                dependency_methods,
                dependency_abstract_methods,
            ):
                method_statement = dependency_item.ResolveHierarchy().statement
                assert isinstance(method_statement, FuncDefinitionStatementParserInfo), method_statement

                if (
                    method_statement.mutability is not None
                    and MutabilityModifier.IsMutable(method_statement.mutability)
                ):
                    has_mutable_method = True
                    break

            if not has_mutable_method:
                errors.append(
                    InvalidMutableError.Create(
                        region=class_statement_parser_info.regions__.class_modifier,
                    ),
                )

        if errors:
            raise ErrorException(*errors)

        # Organize the data

        # ----------------------------------------------------------------------
        def StandardKeyExtractor(
            dependency: Dependency,
        ) -> str:
            return dependency.ResolveHierarchy().statement.name

        # ----------------------------------------------------------------------
        def MethodKeyExtractor(
            dependency: Dependency,
        ):
            parser_info = dependency.ResolveHierarchy().statement

            assert isinstance(parser_info, FuncDefinitionStatementParserInfo), parser_info
            return id(parser_info) # BugBug

        # ----------------------------------------------------------------------
        def PostprocessMethodDependencies(
            local: List[Dependency],
            augmented: List[Dependency],
            inherited: List[Dependency],
        ) -> Tuple[
            List[Dependency],
            List[Dependency],
            List[Dependency],
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

        return cls(
            class_statement_parser_info,
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

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def _EnumDependencies(
        cls,
        entity_resolver: EntityResolver,
        class_statement_parser_info: "ClassStatementParserInfo",
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
                class_statement_parser_info.implements,
                class_statement_parser_info.class_capabilities.ValidateImplementsDependency,
            ),
            (
                class_statement_parser_info.uses,
                class_statement_parser_info.class_capabilities.ValidateUsesDependency,
            ),
            (
                class_statement_parser_info.extends,
                class_statement_parser_info.class_capabilities.ValidateExtendsDependency,
            ),
        ]:
            if dependencies is None:
                continue

            for dependency in dependencies:
                if dependency.is_disabled__:
                    continue

                resolved_entity = entity_resolver.ResolveType(
                    dependency.type,
                    resolve_aliases=True,
                )

                if isinstance(resolved_entity, NoneType):
                    continue

                try:
                    dependency_validation_func(
                        dependency,
                        resolved_entity,
                    )
                except ErrorException as ex:
                    errors += ex.errors
                    continue

                assert isinstance(resolved_entity, ClassType), resolved_entity
                yield dependency, resolved_entity

        if errors:
            raise ErrorException(*errors)
