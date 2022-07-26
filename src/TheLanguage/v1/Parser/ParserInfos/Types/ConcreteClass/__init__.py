# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-25 11:39:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types that are used when creating concrete classes"""

import itertools
import os

from typing import Any, cast, Dict, List, Optional, Tuple

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl.Dependency import Dependency, DependencyLeaf, DependencyNode

    from ..ConcreteType import ConcreteType
    from ..ConstrainedType import ConstrainedType
    from ..GenericType import GenericType

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
    from ....TranslationUnitRegion import TranslationUnitRegion


# ----------------------------------------------------------------------
InvalidResolvedDependencyError              = CreateError(
    "Invalid dependency",
)

MultipleBasesError                          = CreateError(
    "A base has already been provided",
    prev_region=TranslationUnitRegion,
)


# ----------------------------------------------------------------------
class TypeResolver(Interface.Interface):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def EvalConcreteType(
        parser_info: ExpressionParserInfo,
        *,
        no_finalize=False,
    ) -> ConcreteType:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def CreateGenericType(
        parser_info: StatementParserInfo,
    ) -> GenericType:
        raise Exception("Abstract method")  # pragma: no cover



# ----------------------------------------------------------------------
class ConcreteClass(object):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: ClassStatementParserInfo,
        type_resolver: TypeResolver,
    ):
        self._parser_info                   = parser_info
        self._type_resolver                 = type_resolver

        # The following values are initialized upon creation and are permanent
        self.base_dependency: Optional[DependencyNode[ConcreteType]]        = None
        self.concept_dependencies: List[DependencyNode[ConcreteType]]       = []
        self.interface_dependencies: List[DependencyNode[ConcreteType]]     = []
        self.mixin_dependencies: List[DependencyNode[ConcreteType]]         = []

        self.types: List[DependencyLeaf[GenericType]]                       = []
        self.methods: List[DependencyLeaf[GenericType]]                     = []
        self.special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo]     = {}

        # The following values are initialized upon creation and destroyed after Finalization
        self._attribute_statements: List[ClassAttributeStatementParserInfo] = []
        self._using_statements: List[ClassUsingStatementParserInfo]          = []

        self._Initialize()

    # ----------------------------------------------------------------------
    def FinalizePass1(self) -> None:
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

        pass # BugBug

    # ----------------------------------------------------------------------
    def FinalizePass2(self) -> None:
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

        if errors:
            raise ErrorException(*errors)

        pass # BugBug

    # ----------------------------------------------------------------------
    def CreateConstrainedType(
        self,
        concrete_type: ConcreteType,
    ) -> ConstrainedType:
        assert False, "BugBug: CreateConstrainedType"
        pass # BugBug

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
                self._parser_info.implements,
                self._parser_info.class_capabilities.ValidateImplementsDependency,
            ),
            (
                self._parser_info.uses,
                self._parser_info.class_capabilities.ValidateUsesDependency,
            ),
            (
                self._parser_info.extends,
                self._parser_info.class_capabilities.ValidateExtendsDependency,
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
        types: List[DependencyLeaf[GenericType]] = []
        methods: List[DependencyLeaf[GenericType]] = []
        special_methods: Dict[SpecialMethodType, SpecialMethodStatementParserInfo] = {}

        attribute_statements: List[ClassAttributeStatementParserInfo] = []
        using_statements: List[ClassUsingStatementParserInfo] = []

        assert self._parser_info.statements is not None

        for statement in self._parser_info.statements:
            if statement.is_disabled__:
                continue

            if isinstance(statement, ClassAttributeStatementParserInfo):
                attribute_statements.append(statement)
            elif isinstance(statement, ClassStatementParserInfo):
                types.append(DependencyLeaf(self._type_resolver.CreateGenericType(statement)))
            elif isinstance(statement, ClassUsingStatementParserInfo):
                using_statements.append(statement)
            elif isinstance(statement, FuncDefinitionStatementParserInfo):
                methods.append(DependencyLeaf(self._type_resolver.CreateGenericType(statement)))
            elif isinstance(statement, SpecialMethodStatementParserInfo):
                pass # BugBug
            elif isinstance(statement, TypeAliasStatementParserInfo):
                types.append(DependencyLeaf(self._type_resolver.CreateGenericType(statement)))
            else:
                assert False, statement  # pragma: no cover


        # Commit the results
        self.base_dependency = base[1] if base is not None else None
        self.concept_dependencies = concepts
        self.interface_dependencies = interfaces
        self.mixin_dependencies = mixins

        self.types = types
        self.methods = methods
        self.special_methods = special_methods

        self._attribute_statements = attribute_statements
        self._using_statements = using_statements
