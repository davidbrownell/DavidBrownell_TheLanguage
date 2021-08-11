# ----------------------------------------------------------------------
# |
# |  RecursivePlaceholderPhrase_UnitTest.py
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
"""Unit test for RecursivePlaceholderPhrase.py"""

import os

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..RecursivePlaceholderPhrase import *

    from ...Components.UnitTests import (
        CreateIterator,
        parse_mock,
    )


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_Parse(parse_mock):
    with pytest.raises(Exception) as ex:
        await RecursivePlaceholderPhrase().ParseAsync(
            CreateIterator("test"),
            parse_mock,
        )

    ex = ex.value

    assert str(ex) == "'ParseAsync' should never be called on a RecursivePlaceholderPhrase instance"

# ----------------------------------------------------------------------
def test_PopulateRecursive():
    with pytest.raises(Exception) as ex:
        RecursivePlaceholderPhrase().PopulateRecursive()

    ex = ex.value

    assert str(ex) == "'_PopulateRecursiveImpl' should never be called on a RecursivePlaceholderPhrase instance"
