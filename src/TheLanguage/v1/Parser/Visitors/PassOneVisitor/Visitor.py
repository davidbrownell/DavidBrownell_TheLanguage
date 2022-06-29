# ----------------------------------------------------------------------
# |
# |  Visitor.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-10 13:19:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Visitor object"""

import os
import threading

from typing import Callable, Dict, Generator, List, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionsMixin import ExpressionsMixin
    from .StatementsMixin import StatementsMixin
    from .ImportStatementMixin import ImportStatementMixin

    from .. import MiniLanguageHelpers
    from ..NamespaceInfo import NamespaceInfo

    from ...Error import Error, ErrorException

    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo


# ----------------------------------------------------------------------
class Visitor(
    ExpressionsMixin,
    StatementsMixin,
    ImportStatementMixin,
):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class Executor(object):
        # ----------------------------------------------------------------------
        def __init__(
            self,
            mini_language_configuration_values: Dict[str, MiniLanguageHelpers.CompileTimeInfo],
        ):
            self._mini_language_configuration_values    = mini_language_configuration_values

            self._global_namespace                      = NamespaceInfo(None, None)

            self._execute_results_lock                  = threading.Lock()
            self._execute_results: Dict[
                str,                        # Workspace name
                Dict[
                    str,                    # Relative path
                    Visitor.Executor._ExecuteResult,  # pylint: disable=protected-access
                ],
            ]                                           = {}

        # ----------------------------------------------------------------------
        @property
        def global_namespace(self) -> NamespaceInfo:
            return self._global_namespace

        # ----------------------------------------------------------------------
        def GenerateFuncs(self) -> Generator[
            Tuple[
                bool,               # is_parallel
                Callable[
                    [
                        Tuple[str, str],
                        RootStatementParserInfo,
                    ],
                    Union[
                        bool,
                        List[Error],
                    ],
                ],
            ],
            None,
            None,
        ]:
            yield True, self._ExecuteParallel

            # Create a complete namespace
            for workspace_name, workspace_items in self._execute_results.items():
                workspace_namespace = NamespaceInfo(workspace_name, self._global_namespace)

                for relative_path, execute_result in workspace_items.items():
                    name_parts = os.path.splitext(relative_path)[0]
                    name_parts = name_parts.split(".")

                    namespace = workspace_namespace

                    for part in name_parts[:-1]:
                        namespace = namespace.GetOrAddChild(part)

                    namespace.AddChild(name_parts[-1], execute_result.namespace)

                self._global_namespace.AddChild(workspace_name, workspace_namespace)

            # Execute all of the postprocess funcs

            # ----------------------------------------------------------------------
            def Impl(
                funcs_attribute: str,
                names: Tuple[str, str],
            ) -> Union[
                bool,
                List[Error],
            ]:
                execute_results = self._execute_results[names[0]][names[1]]

                errors: List[Error] = []

                for func in getattr(execute_results, funcs_attribute):
                    try:
                        func()
                    except ErrorException as ex:
                        errors += ex.errors

                return errors or True

            # ----------------------------------------------------------------------

            for funcs_attribute in [
                "postprocess_funcs",
                "finalize_funcs",
            ]:
                yield False, lambda names, root: Impl(funcs_attribute, names)  # pylint: disable=cell-var-from-loop

        # ----------------------------------------------------------------------
        # |
        # |  Private Types
        # |
        # ----------------------------------------------------------------------
        @dataclass(frozen=True)
        class _ExecuteResult(object):
            namespace: NamespaceInfo
            postprocess_funcs: List[Callable[[], None]]
            finalize_funcs: List[Callable[[], None]]

        # ----------------------------------------------------------------------
        # |
        # |  Private Methods
        # |
        # ----------------------------------------------------------------------
        def _ExecuteParallel(
            self,
            names: Tuple[str, str],
            root: RootStatementParserInfo,
        ) -> Union[
            bool,                   # Doesn't matter what the return value is as long as it looks different than List[Error]
            List[Error],
        ]:
            visitor = Visitor(
                self._mini_language_configuration_values,
                self._global_namespace,
                names,
            )

            root.Accept(visitor)

            if visitor._errors:                 # pylint: disable=protected-access
                return visitor._errors          # pylint: disable=protected-access

            with self._execute_results_lock:
                assert visitor._root_namespace is not None  # pylint: disable=protected-access

                self._execute_results.setdefault(names[0], {})[names[1]] = Visitor.Executor._ExecuteResult(     # pylint: disable=protected-access
                    visitor._root_namespace,                                                                    # pylint: disable=protected-access
                    visitor._postprocess_funcs,                                                                 # pylint: disable=protected-access
                    visitor._finalize_funcs,                                                                    # pylint: disable=protected-access
                )

            return True
