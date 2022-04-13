# ----------------------------------------------------------------------
# |
# |  Error_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-07 08:48:20
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Error.py"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Error import *


# ----------------------------------------------------------------------
MyError                                     = CreateError(
    "The error value is: {value} [{location}]\n",
    value=str,
)


# ----------------------------------------------------------------------
def test_Standard():
    assert str(MyError.Create(value="foo", location=Location.Create(1, 2))) == textwrap.dedent(
        """\
        The error value is: foo [# <class 'v1.Lexer.Location.Location'>
        column: 2
        line: 1
        ]
        """,
    )

    assert str(MyError.Create(value="bar_and_baz", location=Location.Create(100, 200))) == textwrap.dedent(
        """\
        The error value is: bar_and_baz [# <class 'v1.Lexer.Location.Location'>
        column: 200
        line: 100
        ]
        """,
    )
