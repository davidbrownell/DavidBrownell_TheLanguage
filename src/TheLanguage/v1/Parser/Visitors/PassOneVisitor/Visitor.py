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

import importlib
import os
import sys
import threading

from contextlib import contextmanager, ExitStack
from typing import Callable, Dict, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import FileSystem

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .CommonMixin import CommonMixin
    from .ExpressionsMixin import ExpressionsMixin
    from .StatementsMixin import StatementsMixin
    from .ImportStatementMixin import ImportStatementMixin

    from .. import MiniLanguageHelpers
    from ..NamespaceInfo import NamespaceInfo

    from ...Error import Error, ErrorException

    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo


# ----------------------------------------------------------------------
class Visitor(
    CommonMixin,
    ExpressionsMixin,
    StatementsMixin,
    ImportStatementMixin,
):
    # ----------------------------------------------------------------------
    @classmethod
    @contextmanager
    def ScopedExecutor(
        cls,
        workspaces: Dict[
            str,
            Dict[
                str,
                RootStatementParserInfo,
            ],
        ],
        mini_language_configuration_values: Dict[str, MiniLanguageHelpers.CompileTimeInfo],
        *,
        include_fundamental_types: bool,
    ):
        global_namespace = NamespaceInfo(None, None)

        with ExitStack() as exit_stack:
            # Add all of the fundamental types to the workspaces. This will be processed to validate
            # types, then removed so that the caller isn't impacted.
            if include_fundamental_types:
                generated_code_directory = os.path.realpath(os.path.join(_script_dir, "..", "..", "FundamentalTypes", "GeneratedCode"))

                fundamental_types: Dict[str, RootStatementParserInfo] = {}

                for generated_filename in FileSystem.WalkFiles(
                    generated_code_directory,
                    include_file_extensions=[".py", ],
                    exclude_file_names=["__init__.py"],
                ):
                    dirname, basename = os.path.split(generated_filename)
                    basename = os.path.splitext(basename)[0]

                    with ExitStack() as mod_exit_stack:
                        sys.path.insert(0, dirname)
                        mod_exit_stack.callback(lambda: sys.path.pop(0))

                        mod = importlib.import_module(basename)

                        assert generated_filename.startswith(generated_code_directory), (generated_filename, generated_code_directory)

                        relative_path = FileSystem.TrimPath(generated_filename, generated_code_directory)
                        relative_path = relative_path.replace(os.path.sep, ".")

                        fundamental_types[relative_path] = getattr(mod, "root_parser_info")

                # Add the fundamental types to the workspaces collection
                assert cls._FUNDAMENTAL_TYPES_ATTRIBUTE_NAME not in workspaces
                workspaces[cls._FUNDAMENTAL_TYPES_ATTRIBUTE_NAME] = fundamental_types

                exit_stack.callback(lambda: workspaces.pop(cls._FUNDAMENTAL_TYPES_ATTRIBUTE_NAME))

            # ----------------------------------------------------------------------
            class Executor(object):
                # ----------------------------------------------------------------------
                def __init__(self):
                    self._execute_results_lock          = threading.Lock()
                    self._execute_results: Dict[
                        str,                            # Workspace name
                        Dict[
                            str,                        # Relative path
                            Executor._ExecuteResult,
                        ],
                    ]                       = {}

                # ----------------------------------------------------------------------
                @property
                def global_namespace(self) -> NamespaceInfo:
                    return global_namespace

                @property
                def fundamental_types_namespace(self) -> Optional[NamespaceInfo]:
                    return global_namespace.children.get(cls._FUNDAMENTAL_TYPES_ATTRIBUTE_NAME, None)  # pylint: disable=protected-access

                # ----------------------------------------------------------------------
                def Execute(
                    self,
                    names: Tuple[str, str],
                    root: RootStatementParserInfo,
                ) -> Union[
                    bool,                   # Doesn't matter what the return value is as long as it looks different than List[Error]
                    List[Error],
                ]:
                    visitor = cls(mini_language_configuration_values, global_namespace, names)

                    root.Accept(visitor)

                    if visitor._errors:                 # pylint: disable=protected-access
                        return visitor._errors          # pylint: disable=protected-access

                    with self._execute_results_lock:
                        assert visitor._root_namespace is not None  # pylint: disable=protected-access

                        self._execute_results.setdefault(names[0], {})[names[1]] = Executor._ExecuteResult(
                            visitor._root_namespace,    # pylint: disable=protected-access
                            visitor._postprocess_funcs, # pylint: disable=protected-access
                            visitor._finalize_funcs,    # pylint: disable=protected-access
                        )

                    return True

                # ----------------------------------------------------------------------
                def ExecutePostprocessFuncs(self) -> Dict[
                    str,
                    Dict[
                        str,
                        List[Error],
                    ],
                ]:
                    # Create a complete namespace
                    for workspace_name, workspace_items in self._execute_results.items():
                        workspace_namespace = NamespaceInfo(workspace_name, global_namespace)

                        for relative_path, execute_result in workspace_items.items():
                            name_parts = os.path.splitext(relative_path)[0]
                            name_parts = name_parts.split(".")

                            namespace = workspace_namespace

                            for part in name_parts[:-1]:
                                namespace = namespace.GetOrAddChild(part)

                            namespace.AddChild(name_parts[-1], execute_result.namespace)

                        global_namespace.AddChild(workspace_name, workspace_namespace)

                    # Execute all of the postprocess funcs
                    for funcs_attribute in [
                        "postprocess_funcs",
                        "finalize_funcs",
                    ]:
                        errors: Dict[
                            str,
                            Dict[
                                str,
                                List[Error],
                            ],
                        ] = {}

                        for workspace_name, workspace_items in self._execute_results.items():
                            workspace_errors: Dict[str, List[Error]] = {}

                            for relative_path, execute_result in workspace_items.items():
                                these_errors: List[Error] = []

                                for func in getattr(execute_result, funcs_attribute):
                                    try:
                                        func()
                                    except ErrorException as ex:
                                        these_errors += ex.errors

                                if these_errors:
                                    workspace_errors[relative_path] = these_errors

                            if workspace_errors:
                                errors[workspace_name] = workspace_errors

                        if errors:
                            return errors

                    # Can't return None here, as that has special meaning for the caller (cancellation)
                    return {}

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

            yield Executor()

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _FUNDAMENTAL_TYPES_ATTRIBUTE_NAME       = "__fundamental_types__"
