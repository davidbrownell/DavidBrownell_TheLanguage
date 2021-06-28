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

from concurrent.futures import ThreadPoolExecutor
from typing import Tuple
from unittest.mock import Mock

import pytest

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
    mock = Mock()

    mock._executor = ThreadPoolExecutor()
    mock.Enqueue = lambda funcs: [mock._executor.submit(func) for func in funcs]

    return mock


# ----------------------------------------------------------------------
def CreateIterator(
    content: str,
) -> NormalizedIterator:
    return NormalizedIterator(Normalize(content))


# ----------------------------------------------------------------------
def OnInternalStatementEqual(
    mock_method_call_result: Tuple[Statement, Statement.ParseResultData, NormalizedIterator, NormalizedIterator],
    statement: Statement,
    data: Statement.ParseResultData,
    offset_before: int,
    offset_after: int,
):
    assert statement == mock_method_call_result[0]
    assert data == mock_method_call_result[1]
    assert offset_before == mock_method_call_result[2].Offset
    assert offset_after == mock_method_call_result[3].Offset
