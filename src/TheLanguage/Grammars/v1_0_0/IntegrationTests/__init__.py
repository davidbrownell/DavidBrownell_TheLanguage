# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-11 08:23:22
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Common helper for automted tests in this directory"""

import os
import textwrap

from enum import auto, Flag
from io import StringIO
from typing import Dict, List, Optional
from unittest.mock import patch

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....Parse import Parse, Prune, Validate
    from ....ParserImpl.StatementsParser import SyntaxInvalidError

# ----------------------------------------------------------------------
class PatchAndExecuteFlag(Flag):
    _parse_flag                             = auto()
    _prune_flag                             = auto()
    _validate_flag                          = auto()

    Parse                                   = _parse_flag
    Prune                                   = _parse_flag | _prune_flag
    Validate                                = _parse_flag | _prune_flag | _validate_flag

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
):
    """Patches file system methods invoked by systems under tests and replaces them so that they simulate files via the file content provided"""

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
        if flag & PatchAndExecuteFlag._parse_flag:
            result = Parse(
                fully_qualified_names,
                source_roots,
                max_num_threads=max_num_threads,
            )

            if isinstance(result, list):
                assert len(result) == 1, result

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
                        ).format(result[0].DebugString()),
                    )

                raise result[0]

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
