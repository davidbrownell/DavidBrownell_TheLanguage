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

from CommonEnvironment.AutomatedTestHelpers import (
    CompareResultsFromFile                  # This is imported as a convenience  # pylint: disable=unused-import
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
        RootParserInfo,
        Validate,
    )

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
        str,                                # fully_qualified_name
        str                                 # content
    ],
    source_roots: List[str],
    flag=PatchAndExecuteFlag.Validate,
    *,
    fully_qualified_names: Optional[List[str]]=None,
    max_num_threads: Optional[int]=None,
) -> Union[
    Dict[str, AST.Node],                    # PatchAndExecuteFlag.Lex
    List[Exception],                        # PatchAndExecuteFlag.Lex
    Dict[str,                               # PatchAndExecuteFlag.Parse
        Union[
            RootParserInfo,
            List[ParserError],
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
        return filename in simulated_file_content

    # ----------------------------------------------------------------------
    def IsDir(dirname):
        for key in simulated_file_content.keys():
            if dirname == os.path.dirname(key):
                return True

        return False

    # ----------------------------------------------------------------------

    with \
        patch("os.path.isfile", side_effect=IsFile), \
        patch("os.path.isdir", side_effect=IsDir), \
        patch("builtins.open", side_effect=lambda filename: StringIO(simulated_file_content[filename])) \
    :
        result = Lex(
            GrammarCommentToken,
            Grammar,
            fully_qualified_names or list(simulated_file_content.keys()),
            LexObserver(source_roots),
            max_num_threads=max_num_threads,
        )

        assert result is not None

        if isinstance(result, list):
            if len(result) == 1:
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
                    ).format(str(result[0])),
                )

                raise result[0]

            return result

        result = cast(Dict[str, AST.Node], result)

        if flag & PatchAndExecuteFlag.prune_flag:
            Prune(
                result,
                max_num_threads=max_num_threads,
            )

        if not flag & PatchAndExecuteFlag.parse_flag:
            return result

        result = Parse(
            result,
            ParseObserver(),
            max_num_threads=max_num_threads,
        )

        assert result is not None

        roots: Dict[str, RootParserInfo] = {}

        for key, value in result.items():
            if isinstance(value, list):
                return result

            roots[key] = value

        if flag & PatchAndExecuteFlag.validate_flag:
            result = Validate(
                roots,
                max_num_threads=max_num_threads,
            )

            assert result is not None

            # TODO: Check return value

        return result


# ----------------------------------------------------------------------
def ExecuteNode(
    content: str,
    *,
    max_num_threads: Optional[int]=None,
) -> AST.Node:
    result = PatchAndExecute(
        {
            "filename": content,
        },
        [],
        flag=PatchAndExecuteFlag.Prune,
        max_num_threads=max_num_threads,
    )

    assert isinstance(result, dict), result
    assert len(result) == 1, result
    assert "filename" in result

    return cast(AST.Node, result["filename"])


# ----------------------------------------------------------------------
def ExecuteParserInfo(
    content: str,
    *,
    max_num_threads: Optional[int]=None,
) -> RootParserInfo:
    result = PatchAndExecute(
        {
            "filename": content,
        },
        [],
        flag=PatchAndExecuteFlag.Validate,
        max_num_threads=max_num_threads,
    )

    assert isinstance(result, dict), result
    assert len(result) == 1, result
    assert "filename" in result

    result = result["filename"]

    if isinstance(result, list):
        raise ParserErrorException(*result)

    return cast(RootParserInfo, result)


# ----------------------------------------------------------------------
def ExecutePythonTarget(
    content: str,
    *,
    max_num_threads: Optional[int]=None,
) -> str:
    result = ExecuteParserInfo(
        content,
        max_num_threads=max_num_threads,
    )

    target = PythonTarget([])

    target.PreInvoke(["filename"])
    target.Invoke("filename", result)
    target.PostInvoke(["filename"])

    outputs = list(target.EnumOutputs())

    assert len(outputs) == 1
    return outputs[0].content
