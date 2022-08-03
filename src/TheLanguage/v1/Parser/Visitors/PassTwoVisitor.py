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
from typing import Callable, cast, Dict, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Namespaces import Namespace, ParsedNamespace

    from .Types.RootTypes import RootConcreteType
    from .Types.TypeResolver import TypeResolver

    from ..Error import Error, ErrorException

    from ..ParserInfos.ParserInfo import CompileTimeInfo

    from ..ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo

    from ..ParserInfos.Types.ConcreteType import ConcreteType


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

            compile_time_info: List[Dict[str, CompileTimeInfo]] = [mini_language_configuration_values, ]

            # Create a concrete root resolvers for each translation unit
            root_resolvers: Dict[Tuple[str, str], TypeResolver] = {}
            root_types: Dict[Tuple[str, str], RootConcreteType] = {}

            for translation_unit, namespace in translation_unit_namespaces.items():
                type_resolver = TypeResolver(
                    None,
                    namespace,
                    fundamental_types_namespace,
                    compile_time_info,
                    None,
                )

                assert isinstance(namespace.parser_info, RootStatementParserInfo), namespace.parser_info
                root_type = RootConcreteType(type_resolver, namespace.parser_info)

                root_resolvers[translation_unit] = type_resolver
                root_types[translation_unit] = root_type

            for root_resolver in root_resolvers.values():
                root_resolver.Finalize(root_resolvers)

            # Pre-populate the execute results so that we don't need to update via a lock
            execute_results: Dict[
                Tuple[str, str],
                Optional[PassTwoVisitor.Executor._ExecuteResult],  # pylint: disable=protected-access
            ] = {translation_unit: None for translation_unit in translation_unit_namespaces.keys()}

            self._root_types                            = root_types
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

            for postprocess_step in PassTwoVisitor.Executor._PostprocessStep:  # pylint: disable=unused-variable,protected-access
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

            root_type = self._root_types[translation_unit]

            # Pre-populate the postprocess funcs
            postprocess_funcs: List[List[Callable[[], None]]] = []

            for _ in range(len(PassTwoVisitor.Executor._PostprocessStep)):  # pylint: disable=protected-access
                postprocess_funcs.append([])

            # Process all of the top-level types that are default initializable
            added_postprocess_func = False

            for generic_type in root_type.EnumGenericTypes():
                if not generic_type.is_default_initializable:
                    continue

                try:
                    concrete_type = generic_type.CreateDefaultConcreteType()

                    # ----------------------------------------------------------------------
                    def FinalizeImpl(
                        state: ConcreteType.State,
                        concrete_type=concrete_type,
                    ) -> None:
                        concrete_type.Finalize(state)

                    # ----------------------------------------------------------------------

                    PostprocessStep = PassTwoVisitor.Executor._PostprocessStep  # pylint: disable=protected-access

                    postprocess_funcs[PostprocessStep.RootFinalizePass1.value].append(lambda: FinalizeImpl(ConcreteType.State.FinalizedPass1))
                    postprocess_funcs[PostprocessStep.RootFinalizePass2.value].append(lambda: FinalizeImpl(ConcreteType.State.FinalizedPass2))

                    if concrete_type.is_default_initializable:
                        # ----------------------------------------------------------------------
                        def NoneWrappedCreateConstrainedType(
                            concrete_type=concrete_type,
                        ):
                            concrete_type.CreateDefaultConstrainedType()

                        # ----------------------------------------------------------------------

                        # Note that this must be a lambda so that the func properly captures `concrete_type`
                        postprocess_funcs[PostprocessStep.RootCreateConstrainedType.value].append(lambda: NoneWrappedCreateConstrainedType())  # pylint: disable=unnecessary-lambda

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
