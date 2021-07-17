# ----------------------------------------------------------------------
# |
# |  RecursivePlaceholderStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-15 14:11:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for RecursivePlaceholderStatement.py"""

import os

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import (
        CreateIterator,
        parse_mock,
    )

    from ..RecursivePlaceholderStatement import *


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_Parse(parse_mock):
    with pytest.raises(Exception) as ex:
        await RecursivePlaceholderStatement().ParseAsync(
            CreateIterator("test"),
            parse_mock,
        )

    ex = ex.value

    assert str(ex) == "'ParseAsync' should never be called on a RecursivePlaceholderStatement instance"

# ----------------------------------------------------------------------
def test_PopulateRecursive():
    with pytest.raises(Exception) as ex:
        RecursivePlaceholderStatement().PopulateRecursive()

    ex = ex.value

    assert str(ex) == "'_PopulateRecursiveImpl' should never be called on a RecursivePlaceholderStatement instance"
