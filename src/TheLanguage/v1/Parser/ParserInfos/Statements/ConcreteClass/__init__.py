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

from typing import Any, Dict, Generator, List, Optional, Tuple, TYPE_CHECKING

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
    from ..TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ...EntityResolver import EntityResolver
    from ...Types import ClassType, NoneType

    from ...Common.ClassModifier import ClassModifier
    from ...Common.MethodHierarchyModifier import MethodHierarchyModifier
    from ...Common.MutabilityModifier import MutabilityModifier
    from ...Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo

    from ....Error import CreateError, Error, ErrorException
    from ....TranslationUnitRegion import TranslationUnitRegion

    if TYPE_CHECKING:
        from ..ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo


# ----------------------------------------------------------------------
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
@dataclass(frozen=True)
class ConcreteClass(object):
    # ----------------------------------------------------------------------
    parser_info: "ClassStatementParserInfo"

    base: Optional[DependencyNode]
    special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo]

    interfaces: ClassContent
    concepts: ClassContent
    types: ClassContent
    attributes: ClassContent
    abstract_methods: ClassContent
    methods: ClassContent

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        class_statement_parser_info: "ClassStatementParserInfo",
        entity_resolver: EntityResolver,
    ):
        errors: List[Error] = []

        base: Optional[DependencyNode] = None

        local_contents = _PartialContents()
        augmented_contents = _PartialContents()
        dependency_contents = _PartialContents()

        # Extract information from the dependencies
        for dependency_parser_info, resolved_entity in _EnumDependencies(
            class_statement_parser_info,
            entity_resolver,
        ):
            if resolved_entity.parser_info.is_final:
                errors.append(
                    FinalDependencyError.Create(
                        region=dependency_parser_info.regions__.self__,
                        name=resolved_entity.parser_info.name,
                        final_class_region=resolved_entity.parser_info.regions__.self__,
                    ),
                )
                continue

            assert dependency_parser_info.visibility is not None

            hierarchy_methods_are_polymorphic: Optional[bool] = None
            target_contents: Optional[_PartialContents] = None

            if (
                resolved_entity.parser_info.class_capabilities.name == "Mixin"
                or resolved_entity.parser_info.class_capabilities.name == "Concept"
            ):
                hierarchy_methods_are_polymorphic = False
                target_contents = augmented_contents

                if resolved_entity.parser_info.class_capabilities.name == "Concept":
                    local_contents.concepts.append(  # pylint: disable=no-member
                        DependencyNode(
                            dependency_parser_info,
                            DependencyLeaf(
                                resolved_entity.parser_info,
                                resolved_entity.parser_info,
                            ),
                        ),
                    )

            else:
                hierarchy_methods_are_polymorphic = True
                target_contents = dependency_contents

                if resolved_entity.parser_info.class_capabilities.name == "Interface":
                    local_contents.interfaces.append(  # pylint: disable=no-member
                        DependencyNode(
                            dependency_parser_info,
                            DependencyLeaf(
                                resolved_entity.parser_info,
                                resolved_entity.parser_info,
                            ),
                        ),
                    )

                else:
                    if base is not None:
                        errors.append(
                            MultipleBasesError.Create(
                                region=dependency_parser_info.regions__.self__,
                                prev_region=base.dependency.regions__.self__,
                            ),
                        )

                        continue

                    base = DependencyNode(
                        dependency_parser_info,
                        DependencyLeaf(
                            resolved_entity.parser_info,
                            resolved_entity.parser_info,
                        ),
                    )

            assert hierarchy_methods_are_polymorphic is not None
            assert target_contents is not None

            target_contents.Merge(dependency_parser_info, resolved_entity.concrete_class)

        # Extract information from the class
        special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo] = {}

        # ----------------------------------------------------------------------
        def ProcessAttribute(
            statement: ClassAttributeStatementParserInfo,
        ) -> None:
            # BugBug: Validate is_override
            local_contents.attributes.append(DependencyLeaf(class_statement_parser_info, statement))  # pylint: disable=no-member

        # ----------------------------------------------------------------------
        def ProcessClass(
            statement: "ClassStatementParserInfo",
        ) -> None:
            # BugBug: Need to create this type?
            local_contents.types.append(DependencyLeaf(class_statement_parser_info, statement))  # pylint: disable=no-member

        # ----------------------------------------------------------------------
        def ProcessUsing(
            statement: ClassUsingStatementParserInfo,
        ) -> None:
            raise NotImplementedError("TODO: ClassUsingStatementParserInfo")

        # ----------------------------------------------------------------------
        def ProcessMethod(
            statement: FuncDefinitionStatementParserInfo,
        ) -> None:
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

                return

            # Ensure that the hierarchy modifiers agree with the methods defined in the base classes
            if (
                statement.method_hierarchy_modifier is not None
                and statement.method_hierarchy_modifier != MethodHierarchyModifier.standard
            ):
                pass # BugBug: Do this

            if statement.method_hierarchy_modifier == MethodHierarchyModifier.abstract:
                local_contents.abstract_methods.append(DependencyLeaf(class_statement_parser_info, statement))  # pylint: disable=no-member
            else:
                local_contents.methods.append(DependencyLeaf(class_statement_parser_info, statement))  # pylint: disable=no-member

        # ----------------------------------------------------------------------
        def ProcessSpecialMethod(
            statement: SpecialMethodStatementParserInfo,
        ) -> None:
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

                return

            if (
                statement.special_method_type == SpecialMethodType.EvalConstraints
                and not class_statement_parser_info.constraints
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
                and class_statement_parser_info.class_modifier != ClassModifier.mutable
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
        def ProcessAlias(
            statement: TypeAliasStatementParserInfo,
        ) -> None:
            # BugBug: Need to create this type?
            local_contents.types.append(DependencyLeaf(class_statement_parser_info, statement))  # pylint: disable=no-member

        # ----------------------------------------------------------------------

        processing_funcs = {
            "ClassAttributeStatementParserInfo": ProcessAttribute,
            "ClassStatementParserInfo": ProcessClass,
            "ClassUsingStatementParserInfo": ProcessUsing,
            "FuncDefinitionStatementParserInfo": ProcessMethod,
            "SpecialMethodStatementParserInfo": ProcessSpecialMethod,
            "TypeAliasStatementParserInfo": ProcessAlias,
        }

        assert class_statement_parser_info.statements is not None
        for statement in class_statement_parser_info.statements:
            if statement.is_disabled__:
                continue

            processing_func = processing_funcs.get(statement.__class__.__name__, None)
            assert processing_func is not None, statement

            processing_func(statement)

        # Issue an error if the class was declared as abstract but no abstract methods were found
        if (
            class_statement_parser_info.is_abstract
            and not (
                local_contents.abstract_methods
                or augmented_contents.abstract_methods
                or dependency_contents.abstract_methods
            )
        ):
            errors.append(
                InvalidAbstractDecorationError.Create(
                    region=class_statement_parser_info.regions__.is_abstract,
                ),
            )

        # Issue an error if the class was declared as final but there are abstract methods
        if (
            class_statement_parser_info.is_final
            and (
                local_contents.abstract_methods
                or augmented_contents.abstract_methods
                or dependency_contents.abstract_methods
            )
        ):
            errors.append(
                InvalidFinalDecorationError.Create(
                    region=class_statement_parser_info.regions__.is_final,
                ),
            )

        # Issue an error if the class was declared as mutable but no mutable methods were found
        if class_statement_parser_info.class_modifier == ClassModifier.mutable:
            has_mutable_method = False

            for dependency in itertools.chain(
                local_contents.methods,
                local_contents.abstract_methods,
                augmented_contents.methods,
                augmented_contents.abstract_methods,
                dependency_contents.methods,
                dependency_contents.abstract_methods,
            ):
                method_statement = dependency.ResolveDependencies()[1]
                assert isinstance(method_statement, FuncDefinitionStatementParserInfo), method_statement

                if (
                    method_statement.mutability is not None
                    and MutabilityModifier.IsMutable(method_statement.mutability)
                ):
                    has_mutable_method = True
                    break

            if not has_mutable_method:
                errors.append(
                    InvalidMutableDecorationError.Create(
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
            return dependency.ResolveDependencies()[1].name

        # ----------------------------------------------------------------------
        def MethodKeyExtractor(
            dependency: Dependency,
        ) -> Any:
            method_parser_info = dependency.ResolveDependencies()[1]
            assert isinstance(method_parser_info, FuncDefinitionStatementParserInfo), method_parser_info

            return id(method_parser_info) # BugBug

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

        abstract_methods = ClassContent.Create(
            local_contents.abstract_methods,
            augmented_contents.abstract_methods,
            dependency_contents.abstract_methods,
            MethodKeyExtractor,
        )

        methods = ClassContent.Create(
            local_contents.methods,
            augmented_contents.methods,
            dependency_contents.methods,
            MethodKeyExtractor,
            PostprocessMethodDependencies,
        )

        return cls(
            class_statement_parser_info,
            base,
            special_methods,
            ClassContent.Create(
                local_contents.interfaces,
                augmented_contents.interfaces,
                dependency_contents.interfaces,
                StandardKeyExtractor,
            ),
            ClassContent.Create(
                local_contents.concepts,
                augmented_contents.concepts,
                dependency_contents.concepts,
                StandardKeyExtractor,
            ),
            ClassContent.Create(
                local_contents.types,
                augmented_contents.types,
                dependency_contents.types,
                StandardKeyExtractor,
            ),
            ClassContent.Create(
                local_contents.attributes,
                augmented_contents.attributes,
                dependency_contents.attributes,
                StandardKeyExtractor,
            ),
            abstract_methods,
            methods,
        )

# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _PartialContents(object):
    # ----------------------------------------------------------------------
    interfaces: List[Dependency]            = field(init=False, default_factory=list)
    concepts: List[Dependency]              = field(init=False, default_factory=list)
    types: List[Dependency]                 = field(init=False, default_factory=list)
    attributes: List[Dependency]            = field(init=False, default_factory=list)
    abstract_methods: List[Dependency]      = field(init=False, default_factory=list)
    methods: List[Dependency]               = field(init=False, default_factory=list)

    # ----------------------------------------------------------------------
    def Merge(
        self,
        dependency_parser_info: "ClassStatementDependencyParserInfo",
        source_class: ConcreteClass,
    ) -> None:
        for attribute_name in [
            "interfaces",
            "concepts",
            "types",
            "attributes",
            "abstract_methods",
            "methods",
        ]:
            source = getattr(source_class, attribute_name)
            dest = getattr(self, attribute_name)

            for dependency in source.EnumDependencies():
                dest.append(DependencyNode(dependency_parser_info, dependency))  # pylint: disable=no-member


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
# ----------------------------------------------------------------------
def _EnumDependencies(
    class_statement_parser_info: "ClassStatementParserInfo",
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
