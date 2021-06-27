# ----------------------------------------------------------------------
# |
# |  ClassDeclarationStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-17 08:18:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for ClassDeclarationStatement.py"""

import os
import textwrap

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Execute
    from ..FuncDeclarationStatement import *


# ----------------------------------------------------------------------
def test_SingleCustomStatement():
    assert Execute(
        textwrap.dedent(
            """\
            class Basic:
                <<<!!!
                    '[' <expression> (',' <expression>)* ','? ']'

                    def Lower(node):
                        # There isn't anything here right now.
                        # Keep the blank line below to verify parsing
                        # works as expected.

                        return node
                !!!>>>
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Expected Output>
        """,
    )
