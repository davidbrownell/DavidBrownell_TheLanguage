# ----------------------------------------------------------------------
# |
# |  PassTwoVisitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-21 08:27:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PassTwoVisitor object"""

import os

from enum import auto, Enum
from typing import Callable, Dict, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Namespaces import ImportNamespace, Namespace, ParsedNamespace
    from .TypeResolvers.Impl.Resolvers.RootTypeResolver import RootTypeResolver

    from ..Error import Error, ErrorException

    from ..ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from ..ParserInfos.ParserInfo import CompileTimeInfo, ParserInfoType

    from ..ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo

    from ..ParserInfos.Statements.Traits.ConstrainedStatementTrait import ConstrainedStatementTrait
    from ..ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait


# ----------------------------------------------------------------------
class PassTwoVisitor(object):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class Executor(object):
        # ----------------------------------------------------------------------
        # |  Public Methods
        def __init__(
            self,
            mini_language_configuration_values: Dict[str, CompileTimeInfo],
            translation_unit_namespaces: Dict[Tuple[str, str], ParsedNamespace],
            fundamental_types_namespace: Optional[Namespace],
        ):
            # Flatten the fundamental types namespace for easier lookup
            if fundamental_types_namespace:
                fundamental_types_namespace = fundamental_types_namespace.Flatten()

            # Create a concrete resolver for each translation unit
            root_resolvers: Dict[Tuple[str, str], RootTypeResolver] = {}

            for translation_unit, namespace in translation_unit_namespaces.items():
                resolver = RootTypeResolver(
                    namespace,
                    fundamental_types_namespace,
                    [mini_language_configuration_values, ],
                    None,
                )

                root_resolvers[translation_unit] = resolver

            for resolver in root_resolvers.values():
                resolver.Finalize(root_resolvers)

            # Add children to the resolvers now that they have been finalized
            for translation_unit_resolver in root_resolvers.values():
                for child_namespace_or_namespaces in translation_unit_resolver.namespace.EnumChildren():
                    if isinstance(child_namespace_or_namespaces, list):
                        child_namespaces = child_namespace_or_namespaces
                    else:
                        child_namespaces = [child_namespace_or_namespaces, ]

                    for child_namespace in child_namespaces:
                        if isinstance(child_namespace, ImportNamespace):
                            continue

                        assert isinstance(child_namespace, ParsedNamespace), child_namespace
                        translation_unit_resolver.GetOrCreateNestedResolver(child_namespace)

            # Pre-populate the execute results so that we don't need to update via a lock
            execute_results: Dict[
                Tuple[str, str],
                Optional[PassTwoVisitor.Executor._ExecuteResult],  # pylint: disable=protected-access
            ] = {translation_unit: None for translation_unit in translation_unit_namespaces.keys()}

            self._translation_unit_namespaces           = translation_unit_namespaces
            self._root_resolvers                        = root_resolvers

            self._execute_results                       = execute_results

        # ----------------------------------------------------------------------
        def GenerateFuncs(self) -> Generator[
            Tuple[
                bool,                       # is_parallel
                Callable[
                    [
                        Tuple[str, str],
                        RootStatementParserInfo,
                    ],
                    Union[
                        bool,
                        List[Error],
                    ],
                ]
            ],
            None,
            None,
        ]:
            yield True, self._ProcessRootElements

            for postprocess_step in PassTwoVisitor.Executor._PostprocessStep:  # pylint: disable=protected-access
                yield (
                    True,
                    lambda *args, postprocess_step=postprocess_step, **kwargs: self._ExecutePostprocessSteps(
                        *args,
                        **{
                            **kwargs,
                            **{
                                "postprocess_step": postprocess_step,
                            },
                        },
                    ),
                )

        # ----------------------------------------------------------------------
        # |  Private Types
        class _PostprocessStep(Enum):
            # ----------------------------------------------------------------------
            RootFinalizePass1               = 0
            RootFinalizePass2               = auto()
            RootCreateConstrainedType       = auto()

        # ----------------------------------------------------------------------
        @dataclass(frozen=True)
        class _ExecuteResult(object):
            postprocess_funcs: List[List[Callable[[], None]]]

        # ----------------------------------------------------------------------
        # |  Private Methods
        def _ProcessRootElements(
            self,
            translation_unit: Tuple[str, str],
            root: RootStatementParserInfo,
        ) -> Union[bool, List[Error]]:
            errors: List[Error] = []

            translation_unit_namespace = self._translation_unit_namespaces[translation_unit]
            root_resolver = self._root_resolvers[translation_unit]

            postprocess_funcs: List[List[Callable[[], None]]] = []
            added_postprocess_func = False

            for _ in range(len(PassTwoVisitor.Executor._PostprocessStep)):  # pylint: disable=protected-access
                postprocess_funcs.append([])

            for namespace_or_namespaces in translation_unit_namespace.EnumChildren():
                if isinstance(namespace_or_namespaces, list):
                    namespaces = namespace_or_namespaces
                else:
                    namespaces = [namespace_or_namespaces, ]

                for namespace in namespaces:
                    assert isinstance(namespace, ParsedNamespace), namespace

                    if isinstance(namespace, ImportNamespace):
                        continue

                    resolver = root_resolver.GetOrCreateNestedResolver(namespace)

                    if (
                        not isinstance(namespace.parser_info, TemplatedStatementTrait)
                        or (
                            namespace.parser_info.templates is None
                            or namespace.parser_info.templates.is_default_initializable
                        )
                    ):
                        try:
                            concrete_type = resolver.CreateConcreteType(
                                FuncOrTypeExpressionParserInfo.Create(
                                    parser_info_type=ParserInfoType.Standard,
                                    regions=[
                                        namespace.parser_info.regions__.self__,
                                        namespace.parser_info.regions__.name,
                                        None,
                                    ],
                                    value=namespace.parser_info.name,
                                    templates=None,
                                    constraints=None,
                                    mutability_modifier=None,
                                ),
                            )

                            PostprocessStep = PassTwoVisitor.Executor._PostprocessStep  # pylint: disable=protected-access

                            postprocess_funcs[PostprocessStep.RootFinalizePass1.value].append(concrete_type.FinalizePass1)
                            postprocess_funcs[PostprocessStep.RootFinalizePass2.value].append(concrete_type.FinalizePass2)

                            if (
                                not isinstance(namespace.parser_info, ConstrainedStatementTrait)
                                or (
                                    namespace.parser_info.constraints is None
                                    or namespace.parser_info.constraints.is_default_initializable
                                )
                            ):
                                # ----------------------------------------------------------------------
                                def NoneWrapper(
                                    concrete_type=concrete_type,
                                ):
                                    concrete_type.CreateConstrainedType()

                                # ----------------------------------------------------------------------

                                pass # BugBug postprocess_funcs[PostprocessStep.RootCreateConstrainedType.value].append(NoneWrapper)

                            added_postprocess_func = True

                        except ErrorException as ex:
                            errors += ex.errors

            if errors:
                return errors

            if added_postprocess_func:
                self._execute_results[translation_unit] = PassTwoVisitor.Executor._ExecuteResult(postprocess_funcs)  # pylint: disable=protected-access

            return True

        # ----------------------------------------------------------------------
        def _ExecutePostprocessSteps(
            self,
            translation_unit: Tuple[str, str],
            root: RootStatementParserInfo,  # pylint: disable=unused-argument
            postprocess_step: "PassTwoVisitor.Executor._PostprocessStep",
        ) -> Union[bool, List[Error]]:

            execute_result = self._execute_results[translation_unit]
            if execute_result is None:
                return True

            errors: List[Error] = []

            for postprocess_func in execute_result.postprocess_funcs[postprocess_step.value]:
                try:
                    postprocess_func()
                except ErrorException as ex:
                    errors += ex.errors

            return errors or True
