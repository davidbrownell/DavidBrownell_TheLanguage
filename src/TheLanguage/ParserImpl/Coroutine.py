# ----------------------------------------------------------------------
# |
# |  Coroutine.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-05 18:24:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Utilities that help when working with coroutines"""

import os

from enum import auto, Enum
from typing import Any, Iterator, List, Tuple

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
class Status(Enum):
    """Information used to control the execution of a coroutine"""

    Terminate                               = auto()
    Continue                                = auto()
    Yield                                   = auto()

# ----------------------------------------------------------------------
def Execute(
    iterator: Iterator,
) -> Tuple[Any, List[Any]]:
    results = []

    try:
        while True:
            results.append(next(iterator))
    except StopIteration as ex:
        return ex.value, results
