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

from contextlib import contextmanager, ExitStack
from typing import Callable, Dict, List, Tuple, Union

import CommonEnvironment
from CommonEnvironment import FileSystem

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementsMixin import StatementsMixin
    from .ImportStatementMixin import ImportStatementMixin

    from ...Error import Error, ErrorException
    from ...Helpers import MiniLanguageHelpers
    from ...MiniLanguage.Types.CustomType import CustomType
    from ...NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ...ParserInfos.ParserInfo import RootParserInfo
    from ...ParserInfos.Common.VisibilityModifier import VisibilityModifier
    from ...ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo


# ----------------------------------------------------------------------
class Visitor(
    StatementsMixin,
    ImportStatementMixin,
):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    PositiveExecuteResultType               = Tuple[
        ParsedNamespaceInfo,
        List[
            Tuple[
                Callable[[], None],         # postprocess_func
                Callable[[], None],         # finalize_func
            ],
        ],
    ]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    @contextmanager
    def ScopedExecutor(
        cls,
        workspaces: Dict[
            str,
            Dict[
                str,
                RootParserInfo,
            ],
        ],
        mini_language_configuration_values: Dict[str, MiniLanguageHelpers.CompileTimeInfo],
        *,
        include_fundamental_types: bool,
    ):
        global_namespace = NamespaceInfo(None)

        with ExitStack() as exit_stack:
            # Add all of the fundamental types
            if include_fundamental_types:
                generated_code_directory = os.path.realpath(os.path.join(_script_dir, "..", "..", "FundamentalTypes", "GeneratedCode"))

                fundamental_types: Dict[str, RootParserInfo] = {}

                for generated_filename in FileSystem.WalkFiles(
                    generated_code_directory,
                    include_file_extensions=[".py", ],
                    exclude_file_names=["__init__.py"],
                ):
                    dirname, basename = os.path.split(generated_filename)
                    basename = os.path.splitext(basename)[0]

                    with ExitStack() as exit_stack:
                        sys.path.insert(0, dirname)
                        exit_stack.callback(lambda: sys.path.pop(0))

                        mod = importlib.import_module(basename)

                        assert generated_filename.startswith(generated_code_directory), (generated_filename, generated_code_directory)
                        relative_path = FileSystem.TrimPath(generated_filename, generated_code_directory)

                        fundamental_types[relative_path] = getattr(mod, "root_parser_info")

                assert fundamental_types

                # Add the fundamental types to the workspaces collection
                assert "__fundamental_types__" not in workspaces
                workspaces["__fundamental_types__"] = fundamental_types

                exit_stack.callback(lambda: workspaces.pop("__fundamental_types__"))

            # ----------------------------------------------------------------------
            class Executor(object):
                # ----------------------------------------------------------------------
                @staticmethod
                def Execute(
                    fully_qualifed_name: str,  # pylint: disable=unused-argument
                    root: RootParserInfo,
                ) -> Union[
                    Visitor.PositiveExecuteResultType,
                    List[Error],
                ]:
                    visitor = cls(mini_language_configuration_values)

                    root.Accept(visitor)

                    if visitor._errors:                 # pylint: disable=protected-access
                        return visitor._errors          # pylint: disable=protected-access

                    return visitor._root_namespace_info, visitor._postprocess_funcs  # type: ignore  # pylint: disable=protected-access

                # ----------------------------------------------------------------------
                @staticmethod
                def ExecutePostprocessFuncs(
                    results: Dict[
                        str,
                        Dict[
                            str,
                            Visitor.PositiveExecuteResultType,
                        ],
                    ],
                ) -> Dict[
                    str,
                    Dict[
                        str,
                        List[Error],
                    ],
                ]:
                    # Create a complete namespace and extract postprocess funcs
                    postprocess_func_infos: List[
                        Tuple[
                            str,                                    # workspace name
                            str,                                    # relative path
                            List[
                                Tuple[
                                    Callable[[], None],             # postprocess_func
                                    Callable[[], None],             # finalize_func
                                ],
                            ],
                        ]
                    ] = []

                    for workspace_name, workspace_items in results.items():
                        workspace_namespace = NamespaceInfo(global_namespace)

                        for relative_path, (namespace_info, these_postprocess_funcs) in workspace_items.items():
                            # Update the namespace
                            name_parts = os.path.splitext(relative_path)[0]
                            name_parts = name_parts.split(os.path.sep)

                            namespace = workspace_namespace

                            for part in name_parts[:-1]:
                                if part not in namespace.children:
                                    namespace.children[part] = NamespaceInfo(namespace)

                                namespace = namespace.children[part]

                            object.__setattr__(namespace_info, "parent", namespace)
                            namespace.children[name_parts[-1]] = namespace_info

                            # Update the postprocess_funcs
                            if these_postprocess_funcs:
                                postprocess_func_infos.append((workspace_name, relative_path, these_postprocess_funcs))

                        assert workspace_name not in global_namespace.children
                        global_namespace.children[workspace_name] = workspace_namespace

                    for get_func_func in [
                        lambda this_postprocess_funcs: this_postprocess_funcs[0],       # postprocess_func
                        lambda this_postprocess_funcs: this_postprocess_funcs[1],       # finalize_func
                    ]:
                        errors: Dict[str, Dict[str, List[Error]]] = {}

                        for workspace_name, relative_path, these_postprocess_funcs in postprocess_func_infos:
                            these_errors: List[Error] = []

                            for this_postprocess_funcs in these_postprocess_funcs:
                                try:
                                    get_func_func(this_postprocess_funcs)()
                                except ErrorException as ex:
                                    these_errors += ex.errors

                            if these_errors:
                                errors.setdefault(workspace_name, {})[relative_path] = these_errors

                        if errors:
                            return errors

                    # Can't return None here, as that has special meaning for the caller (cancellation)
                    return {}

            # ----------------------------------------------------------------------

            yield Executor()

            # Add all of the fundamental types to the configuration info
            if include_fundamental_types:
                # ----------------------------------------------------------------------
                def EnumNamespace(
                    namespace: NamespaceInfo,
                ) -> None:
                    for type_name, namespace_info in namespace.children.items():
                        if type_name is None:
                            type_namespaces = namespace_info if isinstance(namespace_info, list) else [namespace_info]

                            for namespace in type_namespaces:
                                assert isinstance(namespace, ParsedNamespaceInfo)
                                assert isinstance(namespace.parser_info, ImportStatementParserInfo)
                                assert namespace.parser_info.visibility != VisibilityModifier.public

                            continue

                        if not isinstance(namespace_info, ParsedNamespaceInfo):
                            EnumNamespace(namespace_info)
                            continue

                        assert isinstance(namespace_info, ParsedNamespaceInfo), namespace_info
                        assert isinstance(type_name, str), type_name
                        assert type_name not in mini_language_configuration_values, type_name

                        # TODO: fullname

                        mini_language_configuration_values[type_name] = MiniLanguageHelpers.CompileTimeInfo(
                            CustomType(type_name),
                            namespace_info,
                            namespace_info.parser_info.regions__.self__,
                        )

                # ----------------------------------------------------------------------

                fundamental_types_namespace = global_namespace.children.get("__fundamental_types__", None)
                if fundamental_types_namespace is not None:
                    EnumNamespace(fundamental_types_namespace)
