# ----------------------------------------------------------------------
# |
# |  PassStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 17:09:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for PassStatement.py"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Execute
    from ..CommentStatement import *


# ----------------------------------------------------------------------
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Pass
                    'pass' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='pass'>>> ws:None [1, 1 -> 1, 5]
        """,
    )
