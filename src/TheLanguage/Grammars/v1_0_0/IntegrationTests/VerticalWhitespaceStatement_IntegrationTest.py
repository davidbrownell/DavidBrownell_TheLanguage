# ----------------------------------------------------------------------
# |
# |  VerticalWhitespaceStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 17:14:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for VerticalWhitespaceStatement.py"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import PatchAndExecute, PatchAndExecuteFlag
    from ..CommentStatement import *


# ----------------------------------------------------------------------
def Execute(content: str) -> str:
    result = PatchAndExecute(
        {
            "filename" : content,
        },
        ["filename"],
        [],
        flag=PatchAndExecuteFlag.Validate,
        # max_num_threads=1,
    )

    return str(result["filename"])


# ----------------------------------------------------------------------
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            StatementAboveVerticalWhitespace()

            StatementBelowVerticalWhitespace()
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 32), match='StatementAboveVerticalWhitespace'>>> ws:None [1, 1 -> 1, 33]
                    '(' <<Regex: <_sre.SRE_Match object; span=(32, 33), match='('>>> ws:None [1, 33 -> 1, 34]
                    ')' <<Regex: <_sre.SRE_Match object; span=(33, 34), match=')'>>> ws:None [1, 34 -> 1, 35]
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(36, 68), match='StatementBelowVerticalWhitespace'>>> ws:None [3, 1 -> 3, 33]
                    '(' <<Regex: <_sre.SRE_Match object; span=(68, 69), match='('>>> ws:None [3, 33 -> 3, 34]
                    ')' <<Regex: <_sre.SRE_Match object; span=(69, 70), match=')'>>> ws:None [3, 34 -> 3, 35]
        """,
    )
