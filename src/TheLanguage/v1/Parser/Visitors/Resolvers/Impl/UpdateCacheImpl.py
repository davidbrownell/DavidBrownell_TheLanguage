# ----------------------------------------------------------------------
# |
# |  UpdateCacheImpl.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-28 12:56:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that implements a type cache"""

import os
import threading

from contextlib import ExitStack
from typing import Any, Callable, Dict, Optional, TypeVar, Union

import CommonEnvironment
from CommonEnvironment.DoesNotExist import DoesNotExist

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....Error import CreateError, ErrorException # BugBug: Create errors


# ----------------------------------------------------------------------
UpdateCacheImplT                            = TypeVar("UpdateCacheImplT")

# ----------------------------------------------------------------------
def UpdateCacheImpl(
    lock: threading.Lock,
    cache: Dict[Any, Union[threading.Event, UpdateCacheImplT]],
    cache_key: Any,
    create_value_func: Callable[[], UpdateCacheImplT],
) -> UpdateCacheImplT:
    wait_event: Optional[threading.Event] = None
    should_wait: Optional[bool] = None

    with lock:
        cache_result = cache.get(cache_key, DoesNotExist.instance)

        if isinstance(cache_result, DoesNotExist):
            wait_event = threading.Event()
            should_wait = False

            cache[cache_key] = wait_event

        elif isinstance(cache_result, threading.Event):
            wait_event = cache_result
            should_wait = True

        else:
            return cache_result

    assert wait_event is not None
    assert should_wait is not None

    if should_wait:
        wait_event.wait()

        with lock:
            cache_result = cache.get(cache_key, DoesNotExist.instance)

            if isinstance(cache_result, DoesNotExist):
                raise Exception("BugBug: Error somewhere else")

            assert not isinstance(cache_result, threading.Event), cache_result
            return cache_result

    result: Union[DoesNotExist, UpdateCacheImplT] = DoesNotExist.instance

    # ----------------------------------------------------------------------
    def RestoreCacheOnError():
        with lock:
            if isinstance(result, DoesNotExist):
                del cache[cache_key]
            else:
                assert cache[cache_key] is wait_event
                cache[cache_key] = result  # type: ignore

        wait_event.set()

    # ----------------------------------------------------------------------

    with ExitStack() as exit_stack:
        exit_stack.callback(RestoreCacheOnError)

        result = create_value_func()

    assert not isinstance(result, DoesNotExist)
    return result
