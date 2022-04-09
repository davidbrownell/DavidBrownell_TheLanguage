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
from typing import cast, Dict, List, Optional, Tuple, Union
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
        Diagnostics,
        Parse,
        Phrase as ParserPhrase,
        RootPhrase as ParserRootPhrase,
    )


# ----------------------------------------------------------------------
class PatchAndExecuteFlag(Flag):
    prune_flag                              = auto()
    parse_flag                              = auto()
    validate_flag                           = auto()

    Lex                                     = 0
    Prune                                   = prune_flag
    Parse                                   = prune_flag | parse_flag


# ----------------------------------------------------------------------
def PatchAndExecute(
    simulated_file_content: Dict[
        str,                                # fully_qualified_name
        str                                 # content
    ],
    source_roots: List[str],
    flag=PatchAndExecuteFlag.Parse,
    *,
    fully_qualified_names: Optional[List[str]]=None,
    max_num_threads: Optional[int]=None,
) -> Union[
    Dict[str, AST.Node],
    List[Exception],
    Dict[str, Tuple[ParserRootPhrase, Diagnostics]],
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

        if flag & PatchAndExecuteFlag.parse_flag:
            result = Parse(
                result,
                ParseObserver(),
                max_num_threads=max_num_threads,
            )

        assert result is not None



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
def ExecuteParserPhrase(
    content: str,
    *,
    max_num_threads: Optional[int]=None,
    with_diagnostics=False,
) -> Union[
    ParserRootPhrase,
    Tuple[ParserRootPhrase, Diagnostics],
]:
    result = PatchAndExecute(
        {
            "filename": content,
        },
        [],
        flag=PatchAndExecuteFlag.Parse,
        max_num_threads=max_num_threads,
    )

    assert isinstance(result, dict), result
    assert len(result) == 1, result
    assert "filename" in result

    result = cast(Tuple[ParserRootPhrase, Diagnostics], result["filename"])

    if with_diagnostics:
        return result

    root, diagnostics = result

    assert not diagnostics, diagnostics

    return root
