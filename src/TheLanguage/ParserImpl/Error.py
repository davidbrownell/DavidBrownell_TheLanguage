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

import CommonEnvironment
from CommonEnvironment import Interface

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
class Error(Exception, Interface.Interface):
    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def MessageTemplate(self) -> str:
        raise Exception("Abstract property")

    # ----------------------------------------------------------------------
    def __init__(
        self,
        line: int,                          # 1-based
        column: int,                        # 1-based
        **kwargs
    ):
        self.Line                           = line
        self.Column                         = column
        self.Message                        = self.MessageTemplate.format(**kwargs)

        for k, v in kwargs.items():
            assert not hasattr(self, k), k
            setattr(self, k, v)

    # ----------------------------------------------------------------------
    def __repr__(self):
        return CommonEnvironment.ObjectReprImpl(
            self,
            include_id=False,
        )

    # ----------------------------------------------------------------------
    def __eq__(self, other):
        return self.__dict__ == other.__dict__


# ----------------------------------------------------------------------
def CreateErrorClass(
    message_template: str,
):
    """Creates an Error class"""

    # ----------------------------------------------------------------------
    class TheError(Error):
        MessageTemplate                     = Interface.DerivedProperty(message_template)

    # ----------------------------------------------------------------------

    return TheError
