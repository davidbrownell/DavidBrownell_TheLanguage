# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-29 09:52:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality common to all integration tests"""

import os
import textwrap
import threading

from enum import auto, Flag
from io import StringIO
from typing import cast, Dict, List, Optional, Union
from unittest.mock import patch

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import CompareResultsFromFile   # This is imported as a convenience

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..AllGrammars import AST, Configurations, Lex, Prune, Parse
    from ..Lexer.TranslationUnitLexer import SyntaxInvalidError
    from ..Parser.ParserInfo import ParserInfo


# ----------------------------------------------------------------------
class PatchAndExecuteFlag(Flag):
    prune_flag                              = auto()
    parse_flag                              = auto()

    Lex                                     = 0
    Prune                                   = prune_flag
    Parse                                   = prune_flag | parse_flag


# ----------------------------------------------------------------------
def PatchAndExecute(
    simulated_file_content: Dict[
        str,                                # Fully Qualified Name (aka filename)
        str,                                # Content
    ],
    fully_qualified_names: List[str],
    source_roots: List[str],
    flag=PatchAndExecuteFlag.Parse,
    *,
    configuration: Optional[Configurations]=None,
    target: Optional[str]=None,
    max_num_threads: Optional[int]=None,
    debug_string_on_exception=True,
) -> Union[
    Dict[str, AST.Node],                    # when flag == PatchAndExecuteFlag.Lex or PatchAndExecuteFlag.Prune
    Dict[str, ParserInfo],                  # when flag == PatchAndExecuteFlag.Parse
    List[Exception],
]:
    """\
    Patches file system methods invoked by systems under tests and replaces them
    so that they simulate files via the file content provided.
    """

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
        cancellation_event = threading.Event()

        result = Lex(
            cancellation_event,
            configuration or Configurations.Debug,
            target or "Standard",
            fully_qualified_names,
            source_roots,
            max_num_threads=max_num_threads,
        )
        assert result is not None

        if not isinstance(result, list):
            result = cast(Dict[str, AST.Node], result)

            if flag & PatchAndExecuteFlag.prune_flag:
                Prune(
                    result,
                    max_num_threads=max_num_threads,
                )

            if flag & PatchAndExecuteFlag.parse_flag:
                result = Parse(
                    cancellation_event,
                    result,
                    max_num_threads=max_num_threads,
                )

            assert result is not None

        if isinstance(result, list):
            if len(result) == 1:
                if debug_string_on_exception:
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


# ----------------------------------------------------------------------
def Execute(
    content: str,
    flag: PatchAndExecuteFlag=PatchAndExecuteFlag.Parse,
    *,
    configuration: Optional[Configurations]=None,
    target: Optional[str]=None,
    max_num_threads: Optional[int]=None,
) -> ParserInfo:
    result = PatchAndExecute(
        {
            "filename" : content,
        },
        ["filename"],
        [],
        flag,
        configuration=configuration,
        target=target,
        # TODO: We are using too many threads in the pool when not single threaded
        # max_num_threads=max_num_threads,
        max_num_threads=1,
    )

    assert isinstance(result, dict), result
    assert len(result) == 1, result
    assert "filename" in result, result

    return cast(ParserInfo, result["filename"])
