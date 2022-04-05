# ----------------------------------------------------------------------
# |
# |  ThreadPool_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 17:57:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for ThreadPool.py"""

import os

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ThreadPool import *


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_Standard():
    import threading

    # ----------------------------------------------------------------------
    async def Identity(value):
        return value

    # ----------------------------------------------------------------------
    async def AddAsync(a, b):
        return await Identity(a) + await Identity(b)

    # ----------------------------------------------------------------------
    async def DoNothing():
        pass

    # ----------------------------------------------------------------------

    pool = CreateThreadPool()

    coro = pool.EnqueueAsync(
        [
            (AddAsync, (1, 2)),
            (AddAsync, (30, 40)),
            (AddAsync, (500, 600)),
            (AddAsync, {"a": 7, "b": 80}),
            (AddAsync, (13,), {"b": 22}),
            DoNothing,
        ],
    )

    results = await coro

    assert results == [3, 70, 1100, 87, 35, None]
