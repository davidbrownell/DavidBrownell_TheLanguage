# ----------------------------------------------------------------------
# |
# |  ParserError.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-07 22:54:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParserError object"""

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
class ParserError(Exception, Interface.Interface):
    """Base class for all Parse-related errors"""

    Line: int
    Column: int

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Line >= 1, self.Line
        assert self.Column >= 1, self.Column

    # ----------------------------------------------------------------------
    def __str__(self):
        return self.MessageTemplate.format(**self.__dict__)

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def MessageTemplate(self):
        """Template used when generating the exception string"""
        raise Exception("Abstract property")  # pragma: no cover
