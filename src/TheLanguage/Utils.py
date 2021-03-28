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

from typing import Optional

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
def IsTokenMatch(
    content: str,
    token: str,
    len_content: Optional[int] = None,
    offset: Optional[int] = None,
) -> bool:
    """Returns True if the token matches the content at the current offset"""

    len_content = len_content or len(content)
    offset = offset or 0

    len_token = len(token)

    if offset + len_token >= len_content:
        return False

    for delta in range(len_token):
        if content[offset + delta] != token[delta]:
            return False

    return True
