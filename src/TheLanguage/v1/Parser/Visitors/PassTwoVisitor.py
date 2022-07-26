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
import threading

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

    from ..ParserInfos.ParserInfo import CompileTimeInfo

    from ..ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
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

            self._translation_unit_namespaces           = translation_unit_namespaces
            self._root_resolvers                        = root_resolvers

            self._execute_results_lock      = threading.Lock()
            self._execute_results: Dict[
                Tuple[str, str],
                PassTwoVisitor.Executor._ExecuteResult,  # pylint: disable=protected-access
            ]                               = {}

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
            yield True, self._ExecuteDefaultCreation

        # ----------------------------------------------------------------------
        # |  Private Types
        @dataclass(frozen=True)
        class _ExecuteResult(object):
            all_postprocess_funcs: List[List[Callable[[], None]]]

        # ----------------------------------------------------------------------
        # |  Private Methods
        def _ExecuteDefaultCreation(
            self,
            translation_unit: Tuple[str, str],
            root: RootStatementParserInfo,
        ) -> Union[bool, List[Error]]:
            errors: List[Error] = []

            translation_unit_namespace = self._translation_unit_namespaces[translation_unit]
            root_resolver = self._root_resolvers[translation_unit]

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

                    try:
                        resolver.ValidateDefaultInitialization()
                    except ErrorException as ex:
                        errors += ex.errors

            return errors or True
