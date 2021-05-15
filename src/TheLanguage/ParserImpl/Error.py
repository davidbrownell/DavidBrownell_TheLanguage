# ----------------------------------------------------------------------
# |
# |  Error.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-09 20:25:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Base class for errors"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Error(Exception, Interface.Interface):
    """Error for all Parse-related errors"""

    Line: int
    Column: int

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def MessageTemplate(self):
        """Template used when generating the exception string"""
        raise Exception("Abstract property")  # pragma: no cover

    # ----------------------------------------------------------------------
    def __str__(self):
        return self.MessageTemplate.format(**self.__dict__)
