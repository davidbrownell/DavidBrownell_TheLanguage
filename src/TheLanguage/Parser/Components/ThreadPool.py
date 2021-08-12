# ----------------------------------------------------------------------
# |
# |  ThreadPool.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 01:03:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality to ease the pain for working with asyncio and ThreadPoolExecutor"""

import asyncio
import os

from concurrent.futures import ThreadPoolExecutor
from types import MethodType
from typing import Any, Awaitable, Callable, cast, Dict, List, Tuple, Union

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
EnqueueAsyncItemType                        = Union[
    # function
    Callable[[Any], Awaitable[Any]],

    # function and args
    Tuple[
        Callable[[Any], Awaitable[Any]],
        Union[List[Any], Tuple[Any]],
    ],

    # function and kwargs
    Tuple[
        Callable[[Any], Awaitable[Any]],
        Dict[str, Any],
    ],

    # function, args, kwargs
    Tuple[
        Callable[[Any], Awaitable[Any]],
        Union[List[Any], Tuple[Any]],
        Dict[str, Any],
    ],
]

# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def CreateThreadPool(
    max_workers: int=None,
    thread_name_prefix: str=None,
):
    """Creates a ThreadPoolExecutor with an attached `EnqueueAsync` method"""

    executor = ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix=thread_name_prefix or "",
    )

    executor.EnqueueAsync = MethodType(_EnqueueAsync, executor)  # type: ignore

    return executor


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _EnqueueAsync(
    self,
    func_infos: List[EnqueueAsyncItemType],
) -> Awaitable[Any]:

    coros = [
        asyncio.get_event_loop().run_in_executor(self, lambda fi=fi: _InvokeAsync(fi))
        for fi in func_infos
    ]

    return asyncio.gather(
        *coros,
        return_exceptions=True,
    )


# ----------------------------------------------------------------------
def _InvokeAsync(
    func_info: EnqueueAsyncItemType,
) -> Any:
    if isinstance(func_info, tuple):
        if len(func_info) == 2:
            if isinstance(func_info[1], dict):
                func, kwargs = func_info  # type: ignore
                args = []
            else:
                func, args = func_info  # type: ignore
                kwargs = {}
        elif len(func_info) == 3:
            func, args, kwargs = func_info  # type: ignore
        else:
            assert False, func_info  # pragma: no cover

    else:
        func = func_info
        args = []
        kwargs = {}

    loop = asyncio.new_event_loop()

    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(func(*args, **cast(Dict[str, Any], kwargs)))
    finally:
        loop.close()
