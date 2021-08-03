# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 10:22:42
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Common helpers for automated tests in this directory"""

import os
import textwrap

from enum import auto, Flag
from io import StringIO
from typing import cast, Dict, List, Optional, Tuple, Union
from unittest.mock import patch

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....Parse import Parse, Prune, Validate

    from ....Components.AST import RootNode
    from ....TranslationUnitParser import SyntaxInvalidError


# ----------------------------------------------------------------------
class PatchAndExecuteFlag(Flag):
    _prune_flag                             = auto()
    _validate_flag                          = auto()

    Parse                                   = 0
    Prune                                   = _prune_flag
    Validate                                = _prune_flag | _validate_flag


# ----------------------------------------------------------------------
def PatchAndExecute(
    simulated_file_content: Dict[
        str,                                # filename
        str,                                # content
    ],
    fully_qualified_names: List[str],       # List of filenames to parse
    source_roots: List[str],
    flag=PatchAndExecuteFlag.Parse,
    max_num_threads: Optional[int]=None,
    debug_string_on_exception=True,
) -> Union[
    Dict[str, RootNode],
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
        result = Parse(
            fully_qualified_names,
            source_roots,
            max_num_threads=max_num_threads,
        )

        if isinstance(result, list):
            if len(result) == 1:
                if debug_string_on_exception and isinstance(result[0], SyntaxInvalidError):
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
                        ).format(result[0].ToDebugString()),
                    )

                raise result[0]

            return result

        result = cast(Dict[str, RootNode], result)

        assert len(result) == len(simulated_file_content)
        for name in result.keys():
            assert name in simulated_file_content

        if flag & PatchAndExecuteFlag._prune_flag:
            Prune(
                result,
                max_num_threads=max_num_threads,
            )

        if flag & PatchAndExecuteFlag._validate_flag:
            Validate(
                result,
                max_num_threads=max_num_threads,
            )

        return result


# ----------------------------------------------------------------------
def ExecuteEx(
    content: str,
) -> Tuple[str, RootNode]:
    """Runs PatchAndExecute and then returns the string along with the result"""

    result = PatchAndExecute(
        {
            "filename" : content,
        },
        ["filename"],
        [],
        flag=PatchAndExecuteFlag.Validate,
        max_num_threads=1,
    )

    result = result["filename"]

    return str(result), result


# ----------------------------------------------------------------------
def Execute(
    content: str,
) -> str:
    """Runs PatchAndExecute and then returns the string result"""

    return ExecuteEx(content)[0]
