# ----------------------------------------------------------------------
# |
# |  SimpleExpressionTrait.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-05 12:13:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SimpleExpressionTrait object"""

import os

from dataclasses import dataclass

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# TODO: This is probably safe to remove
@dataclass(frozen=True, repr=False)
class SimpleExpressionTrait(object):
    """Expression that can be evaluated without any external context"""
    pass
