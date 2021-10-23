# ----------------------------------------------------------------------
# |
# |  LiteralParserInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-22 10:12:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for LiteralParserInfo.py"""

import os

from unittest.mock import Mock

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..LiteralParserInfo import *
    from ...Common.AutomatedTests import RegionCreator


# ----------------------------------------------------------------------
def test_Dynamic():
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class MyLiteralParserInfo(LiteralParserInfo):
        Value: str

    # ----------------------------------------------------------------------

    # Validate creation
    region_creator = RegionCreator()

    literal = MyLiteralParserInfo(
        [region_creator(container=True)],  # type: ignore
        "This is a string",
    )

    assert literal.Value == "This is a string"
    assert isinstance(literal.Value, str)
    assert literal.Regions__.Self__ == region_creator[0]

    # Validate visitation
    visitor = Mock()

    literal.Accept(visitor, [])

    assert visitor.OnMyLiteral.call_count == 1
