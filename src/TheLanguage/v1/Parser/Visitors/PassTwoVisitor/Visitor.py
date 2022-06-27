# ----------------------------------------------------------------------
# |
# |  Visitor.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-16 10:19:19
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

from typing import Callable, Dict, Generator, List, Optional, Union, Tuple

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .CommonMixin import CommonMixin
    from .ExpressionsMixin import ExpressionsMixin
    from .StatementsMixin import StatementsMixin

    from .. import MiniLanguageHelpers
    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ...Error import Error, ErrorException

    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo


# ----------------------------------------------------------------------
class Visitor(
    CommonMixin,
    ExpressionsMixin,
    StatementsMixin,
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
            global_namespace: NamespaceInfo,
            fundamental_types_namespace: Optional[NamespaceInfo],
        ):
            self._mini_language_configuration_values    = mini_language_configuration_values
            self._global_namespace                      = global_namespace
            self._fundamental_types_namespace           = fundamental_types_namespace.Flatten() if fundamental_types_namespace is not None else None

            self._execute_results_lock      = threading.Lock()
            self._execute_results: Dict[
                str,                        # Workspace name
                Dict[
                    str,                    # Relative path
                    Visitor.Executor._ExecuteResult  # pylint: disable=protected-access
                ],
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
            yield True, self._ExecuteParallel

            # ----------------------------------------------------------------------
            def PostprocessFunc(
                index: int,
                names: Tuple[str, str],
            ) -> Union[
                bool,
                List[Error],
            ]:
                # No need to lock, as we are reading the immutable set of results
                execute_results = self._execute_results[names[0]][names[1]]

                errors: List[Error] = []

                for func in execute_results.all_postprocess_funcs[index]:
                    try:
                        func()
                    except ErrorException as ex:
                        errors += ex.errors

                return errors or True

            # ----------------------------------------------------------------------

            for postprocess_type in Visitor.PostprocessType:
                yield (
                    postprocess_type not in Visitor.sequential_postprocess_steps,
                    lambda names, root: PostprocessFunc(postprocess_type.value, names),
                )

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        def _ExecuteParallel(
            self,
            names: Tuple[str, str],
            root: RootStatementParserInfo,
        ) -> Union[
            bool,
            List[Error],
        ]:
            # Get this namespace
            this_namespace = self._global_namespace.children[names[0]]

            name_parts = os.path.splitext(names[1])[0]
            name_parts = name_parts.split(".")

            for name_part in name_parts:
                this_namespace = this_namespace.children[name_part]

            assert isinstance(this_namespace, ParsedNamespaceInfo)

            visitor = Visitor(
                self._mini_language_configuration_values,
                self._fundamental_types_namespace,
                this_namespace,
            )

            root.Accept(visitor)

            if visitor._errors:             # pylint: disable=protected-access
                return visitor._errors      # pylint: disable=protected-access

            with self._execute_results_lock:
                self._execute_results.setdefault(names[0], {})[names[1]] = Visitor.Executor._ExecuteResult(  # pylint: disable=protected-access
                    visitor._all_postprocess_funcs,                                                          # pylint: disable=protected-access
                )

            return True

        # ----------------------------------------------------------------------
        # |
        # |  Private Types
        # |
        # ----------------------------------------------------------------------
        @dataclass(frozen=True)
        class _ExecuteResult(object):
            all_postprocess_funcs: List[List[Callable[[], None]]]
