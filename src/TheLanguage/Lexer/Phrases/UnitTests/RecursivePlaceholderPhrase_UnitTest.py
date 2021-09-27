# ----------------------------------------------------------------------
# |
# |  RecursivePlaceholderPhrase_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-24 15:00:21
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
async def test_Lex(parse_mock):
    with pytest.raises(Exception) as ex:
        await RecursivePlaceholderPhrase().LexAsync(
            ("root", ),
            CreateIterator("test"),
            parse_mock,
        )

    ex = ex.value

    assert str(ex) == "This method should never be called on an instance of this object"

# ----------------------------------------------------------------------
def test_PopulateRecursive():
    with pytest.raises(Exception) as ex:
        RecursivePlaceholderPhrase().PopulateRecursive(None)

    ex = ex.value

    assert str(ex) == "This method should never be called on an instance of this object"
