# ----------------------------------------------------------------------
# |
# |  Node_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-29 09:57:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for Node.py"""

import os
import textwrap

from unittest.mock import Mock

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..AST import *


# ----------------------------------------------------------------------
def test_Standard():
    node = Node(
        SourceRange(
            SourceLocation("Filename1", 1, 1, 0),
            SourceLocation("Filename1", 1, 40, 40),
        ),
        {
            "one" : SourceRange(
                SourceLocation("Filename1", 10, 20, 30),
                SourceLocation("Filename1", 10, 25, 35),
            ),
            "two" : SourceRange(
                SourceLocation("Filename1", 10, 20, 30),
                SourceLocation("Filename1", 10, 30, 40),
            ),
        },
    )

    assert str(node) == textwrap.dedent(
        """\
        Parent       : None
        SourceRange  : End   : Column   : 40
                               Filename : Filename1
                               Line     : 1
                               Offset   : 40
                       Start : Column   : 1
                               Filename : Filename1
                               Line     : 1
                               Offset   : 0
        SourceRanges : one : End   : Column   : 25
                                     Filename : Filename1
                                     Line     : 10
                                     Offset   : 35
                             Start : Column   : 20
                                     Filename : Filename1
                                     Line     : 10
                                     Offset   : 30
                       two : End   : Column   : 30
                                     Filename : Filename1
                                     Line     : 10
                                     Offset   : 40
                             Start : Column   : 20
                                     Filename : Filename1
                                     Line     : 10
                                     Offset   : 30
        """,
    )
