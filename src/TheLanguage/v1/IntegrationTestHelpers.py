# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 11:40:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Utilities that help when writing integration tests."""

import os
import textwrap

from enum import auto, Flag
from io import StringIO
from typing import cast, Dict, List, Optional, Union
from unittest.mock import patch

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment import FileSystem

from CommonEnvironment.AutomatedTestHelpers import (
    CompareResultsFromFile                  # pylint: disable=unused-import
)

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .AllGrammars import Grammar, GrammarCommentToken, LexObserver, ParseObserver
    from .Lexer.Lexer import AST, Lex, Prune

    from .Parser.Parser import (
        Error as ParserError,
        ErrorException as ParserErrorException,
        Parse,
        Validate,
    )

    from .Parser.ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo

    from .Targets.Python.PythonTarget import PythonTarget


# ----------------------------------------------------------------------
class PatchAndExecuteFlag(Flag):
    prune_flag                              = auto()
    parse_flag                              = auto()
    validate_flag                           = auto()

    Lex                                     = 0
    Prune                                   = prune_flag
    Parse                                   = Prune | parse_flag
    Validate                                = Parse | validate_flag


# ----------------------------------------------------------------------
def PatchAndExecute(
    simulated_file_content: Dict[
        str,                                # workspace
        Dict[
            str,                            # relative path
            str                             # content
        ],
    ],
    flag=PatchAndExecuteFlag.Validate,
    *,
    max_num_threads: Optional[int]=None,
    include_fundamental_types=True,
) -> Union[
    Dict[str, Dict[str, AST.Node]],         # PatchAndExecuteFlag.Lex
    List[Exception],                        # PatchAndExecuteFlag.Lex
    Dict[
        str,
        Dict[
            str,
            Union[
                RootStatementParserInfo,
                List[ParserError],
            ],
        ],
    ],
]:
    """\
    Patches file system methods invoked by systems under tests and replaces them
    so that they simulate files via the file content provided.
    """

    # TODO: We are using too many threads in the pool when not single threaded; remove this clause
    # when that issue has been resolved.
    if max_num_threads is None:
        max_num_threads = 1

    # ----------------------------------------------------------------------
    def IsFile(filename):
        dirname, basename = os.path.split(filename)

        items = simulated_file_content.get(dirname, None)
        if items is None:
            return False

        return basename in items

    # ----------------------------------------------------------------------
    def IsDir(dirname):
        for key in simulated_file_content.keys():
            if dirname == key:
                return True

        return False

    # ----------------------------------------------------------------------
    def Open(filename):
        for workspace_name, items in simulated_file_content.items():
            if not filename.startswith(workspace_name):
                continue

            relative_path = FileSystem.TrimPath(filename, workspace_name)
            return StringIO(items[relative_path])

        assert False, filename

    # ----------------------------------------------------------------------

    with \
        patch("os.path.isfile", side_effect=IsFile), \
        patch("os.path.isdir", side_effect=IsDir), \
        patch("builtins.open", side_effect=Open) \
    :
        inputs: Dict[str, List[str]] = {}

        for workspace_name, workspace_items in simulated_file_content.items():
            inputs[workspace_name] = list(workspace_items.keys())

        results = Lex(
            GrammarCommentToken,
            Grammar,
            inputs,
            LexObserver(list(inputs.keys())),
            max_num_threads=max_num_threads,
        )

        assert results is not None

        if isinstance(results, list):
            if len(results) == 1:
                print(
                    textwrap.dedent(
                        """\
                        # ----------------------------------------------------------------------
                        # ----------------------------------------------------------------------
                        # ----------------------------------------------------------------------
                        {}
                        # ----------------------------------------------------------------------
                        # ----------------------------------------------------------------------
                        # ----------------------------------------------------------------------
                        """,
                    ).format(str(results[0])),
                )

                raise results[0]

            return results

        results = cast(Dict[str, Dict[str, AST.Node]], results)

        if flag & PatchAndExecuteFlag.prune_flag:
            Prune(
                results,
                max_num_threads=max_num_threads,
            )

        if not flag & PatchAndExecuteFlag.parse_flag:
            return results

        results = Parse(
            results,
            ParseObserver(),
            max_num_threads=max_num_threads,
        )

        assert results is not None

        errors: Dict[str, Dict[str, List[ParserError]]] = {}

        for workspace_name, workspace_items in results.items():
            these_errors: Dict[str, List[ParserError]] = {}

            for relative_path, result in workspace_items.items():
                if isinstance(result, list):
                    these_errors[relative_path] = result

            if these_errors:
                errors[workspace_name] = these_errors

        if errors:
            return errors  # type: ignore

        results = cast(Dict[str, Dict[str, RootStatementParserInfo]], results)

        if flag & PatchAndExecuteFlag.validate_flag:
            results = Validate(
                results,
                {}, # TODO
                max_num_threads=max_num_threads,
                include_fundamental_types=include_fundamental_types,
            )

            assert results is not None

            for workspace_name, workspace_items in results.items():
                these_errors: Dict[str, List[ParserError]] = {}

                for relative_path, result in workspace_items.items():
                    if isinstance(result, list):
                        these_errors[relative_path] = result

                if these_errors:
                    errors[workspace_name] = these_errors

            if errors:
                return errors  # type: ignore

            results = cast(Dict[str, Dict[str, RootStatementParserInfo]], results)

        return results  # type: ignore


# ----------------------------------------------------------------------
def ExecuteNode(
    content: str,
    *,
    max_num_threads: Optional[int]=None,
) -> AST.Node:
    result = PatchAndExecute(
        {
            "workspace" : {
                "filename": content,
            },
        },
        flag=PatchAndExecuteFlag.Prune,
        max_num_threads=max_num_threads,
    )

    assert isinstance(result, dict), result
    assert len(result) == 1
    result = result["workspace"]

    assert isinstance(result, dict), result
    assert len(result) == 1, result
    assert "filename" in result

    return cast(AST.Node, result["filename"])


# ----------------------------------------------------------------------
def ExecuteParserInfo(
    content: str,
    *,
    max_num_threads: Optional[int]=None,
    include_fundamental_types=True,
) -> RootStatementParserInfo:
    result = PatchAndExecute(
        {
            "workspace": {
                "filename": content,
            },
        },
        flag=PatchAndExecuteFlag.Validate,
        max_num_threads=max_num_threads,
        include_fundamental_types=include_fundamental_types,
    )

    assert isinstance(result, dict), result
    assert len(result) == 1
    result = result["workspace"]

    assert isinstance(result, dict), result
    assert len(result) == 1, result
    assert "filename" in result

    result = result["filename"]

    if isinstance(result, list):
        raise ParserErrorException(*result)

    return cast(RootStatementParserInfo, result)


# ----------------------------------------------------------------------
def ExecutePythonTarget(
    content: str,
    *,
    max_num_threads: Optional[int]=None,
    include_fundamental_types=True,
) -> str:
    result = PatchAndExecute(
        {
            "workspace": {
                "filename": content,
            },
        },
        flag=PatchAndExecuteFlag.Validate,
        max_num_threads=max_num_threads,
        include_fundamental_types=include_fundamental_types,
    )

    assert isinstance(result, dict), result

    target = PythonTarget(
        cast(Dict[str, Dict[str, RootStatementParserInfo]], result),
        output_dir=None,
    )

    outputs = list(target.EnumOutputs())

    assert len(outputs) == 1
    return outputs[0].content
