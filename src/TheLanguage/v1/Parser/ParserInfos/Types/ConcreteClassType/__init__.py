# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-22 21:58:57
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

from typing import Any, cast, Dict, List, Optional, Tuple, Union

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
    from ..GenericType import GenericType

    from ....ParserInfos.Common.MutabilityModifier import MutabilityModifier

    from ....ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ....ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo

    from ....ParserInfos.Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ....ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ....ParserInfos.Statements.ClassUsingStatementParserInfo import ClassUsingStatementParserInfo
    from ....ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ....ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo, SpecialMethodType
    from ....ParserInfos.Statements.StatementParserInfo import StatementParserInfo
    from ....ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ....Error import CreateError, Error, ErrorException
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
class TypeInfo(object):
    # ----------------------------------------------------------------------
    statement: Union[ClassStatementParserInfo, FuncDefinitionStatementParserInfo, TypeAliasStatementParserInfo]
    generic_type: GenericType


# ----------------------------------------------------------------------
@dataclass(eq=False)
class ConcreteClassType(ConcreteType):
    # ----------------------------------------------------------------------
    base_dependency: Optional[DependencyNode[ConcreteType]]                 = field(init=False, default=None)
    concept_dependencies: List[DependencyNode[ConcreteType]]                = field(init=False, default_factory=list)
    interface_dependencies: List[DependencyNode[ConcreteType]]              = field(init=False, default_factory=list)
    mixin_dependencies: List[DependencyNode[ConcreteType]]                  = field(init=False, default_factory=list)

    # The following values are valid until Finalized
    _alias_statements: List[TypeAliasStatementParserInfo]
    _attribute_statements: List[ClassAttributeStatementParserInfo]          = field(init=False, default_factory=list)
    _class_statements: List[ClassStatementParserInfo]                       = field(init=False, default_factory=list)
    _func_statements: List[FuncDefinitionStatementParserInfo]               = field(init=False, default_factory=list)
    _special_method_statements: List[SpecialMethodStatementParserInfo]      = field(init=False, default_factory=list)
    _using_statements: List[ClassUsingStatementParserInfo]                  = field(init=False, default_factory=list)

    # The following values are valid after FinalizePass1
    _concepts: Optional[ClassContent[ConcreteType]]     = field(init=False, default=None)
    _interfaces: Optional[ClassContent[ConcreteType]]   = field(init=False, default=None)
    _mixins: Optional[ClassContent[ConcreteType]]       = field(init=False, default=None)
    _types: Optional[ClassContent[TypeInfo]]            = field(init=False, default=None)

    # The following values are valid after FinalizePass2
    _attributes: Optional[ClassContent[TypeInfo]]                                           = field(init=False, default=None)
    _abstract_methods: Optional[ClassContent[TypeInfo]]                                     = field(init=False, default=None)
    _methods: Optional[ClassContent[TypeInfo]]                                              = field(init=False, default=None)
    _special_methods: Optional[Dict[SpecialMethodType, SpecialMethodStatementParserInfo]]   = field(init=False, default=None)

    # ----------------------------------------------------------------------
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

    @property
    def attributes(self) -> ClassContent[TypeInfo]:
        assert self.state.value >= ConcreteType.State.FinalizedPass2.value
        assert self._attributes is not None
        return self._attributes

    @property
    def abstract_methods(self) -> ClassContent[TypeInfo]:
        assert self.state.value >= ConcreteType.State.FinalizedPass2.value
        assert self._abstract_methods is not None
        return self._abstract_methods

    @property
    def methods(self) -> ClassContent[TypeInfo]:
        assert self.state.value >= ConcreteType.State.FinalizedPass2.value
        assert self._methods is not None
        return self._methods

    @property
    def special_methods(self) -> Dict[SpecialMethodType, SpecialMethodStatementParserInfo]:
        assert self.state.value >= ConcreteType.State.FinalizedPass2.value
        assert self._special_methods is not None
        return self._special_methods

    # ----------------------------------------------------------------------
    def __post_init__(self):
        errors: List[Error] = []

        class_parser_info = self.generic_type.definition_parser_info

        assert isinstance(class_parser_info, ClassStatementParserInfo), class_parser_info

        # Extract the dependencies
        base: Optional[Tuple[ClassStatementDependencyParserInfo, DependencyNode[ConcreteType]]]     = None
        concepts: List[DependencyNode[ConcreteType]]                                                = []
        interfaces: List[DependencyNode[ConcreteType]]                                              = []
        mixins: List[DependencyNode[ConcreteType]]                                                  = []

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
                    generic_type = self._EvalType(dependency_parser_info.type)
                    resolved_generic_type = generic_type.ResolveAliases()

                    resolved_parser_info = resolved_generic_type.definition_parser_info

                    if isinstance(resolved_parser_info, NoneExpressionParserInfo):
                        continue

                    if not isinstance(resolved_parser_info, ClassStatementParserInfo):
                        errors.append(
                            InvalidResolvedDependencyError.Create(
                                region=dependency_parser_info.type.regions__.self__,
                            ),
                        )

                        continue

                    dependency_validation_func(dependency_parser_info, resolved_parser_info)

                    dependency_node = DependencyNode(
                        dependency_parser_info,
                        DependencyLeaf(generic_type.CreateConcreteType()),
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
                                    prev_region=base[0].regions__.self__,
                                ),
                            )

                            continue

                        base = (dependency_parser_info, dependency_node)

                except ErrorException as ex:
                    errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # Process the local statements
        statements: Dict[Any, List[StatementParserInfo]] = {
            TypeAliasStatementParserInfo: [],
            ClassAttributeStatementParserInfo: [],
            ClassStatementParserInfo: [],
            ClassUsingStatementParserInfo: [],
            FuncDefinitionStatementParserInfo: [],
            SpecialMethodStatementParserInfo: [],
        }

        assert class_parser_info.statements is not None

        for statement in class_parser_info.statements:
            if statement.is_disabled__:
                continue

            dest = statements.get(type(statement), None)
            assert dest is not None, statement

            dest.append(statement)

        # Commit the results
        self.base_dependency = base[1] if base is not None else None
        self.concept_dependencies = concepts
        self.interface_dependencies = interfaces
        self.mixin_dependencies = mixins

        self._alias_statements = cast(List[TypeAliasStatementParserInfo], statements[TypeAliasStatementParserInfo])
        self._attribute_statements = cast(List[ClassAttributeStatementParserInfo], statements[ClassAttributeStatementParserInfo])
        self._class_statements = cast(List[ClassStatementParserInfo], statements[ClassStatementParserInfo])
        self._func_statements = cast(List[FuncDefinitionStatementParserInfo], statements[FuncDefinitionStatementParserInfo])
        self._special_method_statements = cast(List[SpecialMethodStatementParserInfo], statements[SpecialMethodStatementParserInfo])
        self._using_statements = cast(List[ClassUsingStatementParserInfo], statements[ClassUsingStatementParserInfo])

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(
        self,
    ) -> None:
        errors: List[Error] = []

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

        local_info = _Pass1Info()

        local_info.concepts += self.concept_dependencies
        local_info.interfaces += self.interface_dependencies
        local_info.mixins += self.mixin_dependencies

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

        # Prepare nested types
        for statement in itertools.chain(self._class_statements, self._alias_statements):
            local_info.types.append(
                DependencyLeaf(
                    TypeInfo(statement, self._CreateNestedType(statement)),
                ),
            )

        # Prepare the final results
        concepts = ClassContent.Create(
            local_info.concepts,
            augmented_info.concepts,
            dependency_info.concepts,
            lambda concrete_type: concrete_type.generic_type.definition_parser_info.name,  # type: ignore
        )

        interfaces = ClassContent.Create(
            local_info.interfaces,
            augmented_info.interfaces,
            dependency_info.interfaces,
            lambda concrete_type: concrete_type.generic_type.definition_parser_info.name,  # type: ignore
        )

        mixins = ClassContent.Create(
            local_info.mixins,
            augmented_info.mixins,
            dependency_info.mixins,
            lambda concrete_type: concrete_type.generic_type.definition_parser_info.name,  # type: ignore
        )

        types = ClassContent.Create(
            local_info.types,
            augmented_info.types,
            dependency_info.types,
            lambda type_info: type_info.statement.name,
        )

        # Commit the results
        self._concepts = concepts
        self._interfaces = interfaces
        self._mixins = mixins
        self._types = types

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(
        self,
    ) -> None:
        errors: List[Error] = []

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

        if errors:
            raise ErrorException(*errors)

        local_info = _Pass2Info()
        augmented_info = _Pass2Info()
        dependency_info = _Pass2Info()

        # BugBug

    # ----------------------------------------------------------------------
    def _PostFinalizeCleanup(self) -> None:
        del self._alias_statements
        del self._attribute_statements
        del self._class_statements
        del self._func_statements
        del self._special_method_statements
        del self._using_statements

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _EvalType(
        parser_info: ExpressionParserInfo,
    ) -> GenericType:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateNestedType(
        parser_info: Union[ClassStatementParserInfo, FuncDefinitionStatementParserInfo, TypeAliasStatementParserInfo],
    ) -> GenericType:
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _Pass1Info(object):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.concepts: List[Dependency[ConcreteType]]   = []
        self.interfaces: List[Dependency[ConcreteType]] = []
        self.mixins: List[Dependency[ConcreteType]]     = []
        self.types: List[Dependency[TypeInfo]]          = []

    # ----------------------------------------------------------------------
    def Merge(
        self,
        dependencies: List[DependencyNode[ConcreteType]],
    ) -> None:
        for dependency in dependencies:
            visibility, concrete_type = dependency.ResolveDependencies()
            assert visibility is not None

            resolved_concrete_type = concrete_type.ResolveAliases()

            for attribute_name in [
                "concepts",
                "interfaces",
                "mixins",
                "types",
            ]:
                dest_items = getattr(self, attribute_name)
                source_items = getattr(resolved_concrete_type, attribute_name)

                for source_item in source_items:
                    dest_items.append(DependencyNode(dependency.dependency, source_item))


# ----------------------------------------------------------------------
class _Pass2Info(object):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.attributes: List[Dependency[TypeInfo]]                         = []
        self.abstract_methods: List[Dependency[TypeInfo]]                   = []
        self.methods: List[Dependency[TypeInfo]]                            = []

    # ----------------------------------------------------------------------
    def Merge(
        self,
        concrete_classes: Iterable[Dependency[ConcreteType]],
    ) -> None:
        pass # BugBug
