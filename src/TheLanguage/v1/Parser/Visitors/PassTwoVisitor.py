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

    from .Resolvers.RootResolvers import RootConcreteTypeResolver
    from .Resolvers.Impl.ConcreteTypeResolver import ConcreteTypeResolver

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

            compile_time_info: List[Dict[str, CompileTimeInfo]] = [mini_language_configuration_values, ]

            # Create a concrete root resolvers for each translation unit
            root_resolvers: Dict[Tuple[str, str], RootConcreteTypeResolver] = {}

            for translation_unit, namespace in translation_unit_namespaces.items():
                root_resolvers[translation_unit] = RootConcreteTypeResolver(
                    namespace,
                    fundamental_types_namespace,
                    compile_time_info,
                )

            for root_resolver in root_resolvers.values():
                root_resolver.Finalize(cast(Dict[Tuple[str, str], ConcreteTypeResolver], root_resolvers))

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

            translation_unit_namespace = self._translation_unit_namespaces[translation_unit]
            root_resolver = self._root_resolvers[translation_unit]

            # Prepopulate the postprocess funcs
            postprocess_funcs: List[List[Callable[[], None]]] = []

            for _ in range(len(PassTwoVisitor.Executor._PostprocessStep)):  # pylint: disable=protected-access
                postprocess_funcs.append([])

            # Process all of the top-level types that are default initializable
            added_postprocess_func = False

            for generic_type in root_resolver.EnumGenericTypes():
                if not generic_type.is_default_initializable:
                    continue

                try:
                    concrete_type = generic_type.CreateDefaultConcreteType()

                    PostprocessStep = PassTwoVisitor.Executor._PostprocessStep  # pylint: disable=protected-access

                    postprocess_funcs[PostprocessStep.RootFinalizePass1.value].append(concrete_type.FinalizePass1)
                    postprocess_funcs[PostprocessStep.RootFinalizePass2.value].append(concrete_type.FinalizePass2)

                    # ----------------------------------------------------------------------
                    def NoneWrapper(
                        concrete_type=concrete_type,
                    ):
                        concrete_type.CreateConstrainedType()

                    # ----------------------------------------------------------------------

                    postprocess_funcs[PostprocessStep.RootCreateConstrainedType.value].append(NoneWrapper)

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
