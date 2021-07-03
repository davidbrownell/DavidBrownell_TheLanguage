# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-28 07:38:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Types and Methods common across unit tests"""

import os

from typing import Any, Dict, Tuple

import pytest

from asynctest import CoroutineMock

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Statement import Statement

    from ...Normalize import Normalize
    from ...NormalizedIterator import NormalizedIterator


# ----------------------------------------------------------------------
@pytest.fixture
def parse_mock():
    mock = CoroutineMock()

    return mock


# ----------------------------------------------------------------------
def CreateIterator(
    content: str,
) -> NormalizedIterator:
    return NormalizedIterator(Normalize(content))


# ----------------------------------------------------------------------
def OnInternalStatementEqual(
    mock_method_call_result: Tuple[
        str,
        Tuple[
            Statement,
            Statement.ParseResultData,
            NormalizedIterator,
            NormalizedIterator,
        ],
        Dict[str, Any],
    ],
    statement: Statement,
    data: Statement.ParseResultData,
    offset_before: int,
    offset_after: int,
):
    assert mock_method_call_result[0] == "OnInternalStatementAsync"
    call_result = mock_method_call_result[1]

    assert statement == call_result[0]
    assert data == call_result[1]
    assert offset_before == call_result[2].Offset
    assert offset_after == call_result[3].Offset
