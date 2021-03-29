# ----------------------------------------------------------------------
# |
# |  Utils.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-03-27 22:31:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains common code used across multiple modules"""

import os

from typing import Optional, Tuple

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
def IsTokenMatch(
    content: str,
    token: str,
    offset: Optional[int] = None,
    len_content: Optional[int] = None,
    len_token: Optional[int] = None,
) -> Tuple[bool, int]:
    """Returns True and the new offset accounting for the number of characters consumed if the token matches the content"""

    offset = offset or 0
    len_content = len_content = len(content)
    len_token = len_token or len(token)

    if offset >= len_content:
        raise Exception("Invalid argument 'offset'")

    if offset + len_token >= len_content:
        return False, offset

    for index in range(len_token):
        if content[offset + index] != token[index]:
            return False, offset

    return True, offset + len_token
