# ----------------------------------------------------------------------
# |
# |  AST_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 18:18:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for ASI.py"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..AST import *


# ----------------------------------------------------------------------
def test_Node():
    node = Node(
        None,
        IsIgnored=False,
    )

    assert node.Type is None
    assert node.IsIgnored == False
    assert node.Parent is None
    assert node.Children == []
    assert node.IterBegin is None
    assert node.IterEnd is None

    node.FinalInit()

    assert node.IterBegin is None
    assert node.IterEnd is None
