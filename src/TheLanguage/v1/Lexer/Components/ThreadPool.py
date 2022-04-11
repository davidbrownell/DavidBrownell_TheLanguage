# ----------------------------------------------------------------------
# |
# |  ThreadPool.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-02 16:47:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
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
from typing import Any, Awaitable, Callable, cast, Dict, List, Optional, Tuple, TypeVar, Union

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
EnqueueFuncInfoType                         = Union[
    Tuple[
        Callable[..., Any],
        List[Any],
        Dict[str, Any],
    ],
    Tuple[
        Callable[..., Any],
        List[Any],
    ],
    Tuple[
        Callable[..., Any],
        Dict[str, Any],
    ],
]

EnqueueFuncInfosType                        = List[EnqueueFuncInfoType]
EnqueueReturnType                           = List["asyncio.Future[Any]"]


# ----------------------------------------------------------------------
EnqueueAsyncFuncInfoReturnType              = Union[
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
    max_workers: Optional[int]=None,
    thread_name_prefix: Optional[str]=None,
) -> ThreadPoolExecutor:
    """Creates a ThreadPoolExecutor with an attached `EnqueueAsync` method"""

    executor = ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix=thread_name_prefix or "",
    )

    executor.Enqueue = MethodType(_Enqueue, executor)  # type: ignore
    executor.EnqueueAsync = MethodType(_EnqueueAsync, executor)  # type: ignore

    return executor


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
_EnqueueFuncInfoReturnType                  = TypeVar("_EnqueueFuncInfoReturnType")

def _Enqueue(
    self: ThreadPoolExecutor,
    func_infos: List[
        Union[
            Tuple[
                Callable[..., _EnqueueFuncInfoReturnType],
                List[Any],
                Dict[str, Any],
            ],
            Tuple[
                Callable[..., _EnqueueFuncInfoReturnType],
                List[Any],
            ],
            Tuple[
                Callable[..., _EnqueueFuncInfoReturnType],
                Dict[str, Any],
            ],
        ]
    ],
) -> List["asyncio.Future[_EnqueueFuncInfoReturnType]"]:
    results: List["asyncio.Future[_EnqueueFuncInfoReturnType]"] = []

    for func_info in func_infos:
        assert isinstance(func_info, tuple), func_info

        if len(func_info) == 3:
            func, args, kwargs = func_info
        elif len(func_info) == 2:
            func = func_info[0]

            if isinstance(func_info[1], list):
                args = func_info[1]
                kwargs = {}
            elif isinstance(func_info[1], dict):
                args = []
                kwargs = func_info[1]
            else:
                assert False, func_info  # pragma: no cover
        else:
            assert False, func_info  # pragma: no cover

        future = self.submit(func, *args, **kwargs)

        results.append(future)  # type: ignore

    return results


# ----------------------------------------------------------------------
def _EnqueueAsync(
    self,
    func_infos: List[EnqueueAsyncFuncInfoReturnType],
) -> Awaitable[Any]:
    coroutines = [
        asyncio.get_event_loop().run_in_executor(self, lambda fi=fi: _InvokeAsync(fi))
        for fi in func_infos
    ]

    return asyncio.gather(
        *coroutines,
        return_exceptions=True,
    )


# ----------------------------------------------------------------------
def _InvokeAsync(
    func_info: EnqueueAsyncFuncInfoReturnType,
) -> Any:
    if isinstance(func_info, tuple):
        if len(func_info) == 3:
            func, args, kwargs = func_info
        elif len(func_info) == 2:
            if isinstance(func_info[1], dict):
                func, kwargs = func_info
                args = []
            else:
                func, args = func_info
                kwargs = {}
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
