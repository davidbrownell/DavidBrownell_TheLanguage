# ----------------------------------------------------------------------
# |
# |  Errors.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-03-27 13:57:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains errors that are produced during the compilation process"""

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
    def MessageTemplate(self):
        raise Exception("Abstract property")

    # ----------------------------------------------------------------------
    def __init__(self, source, line, column, **kwargs):
        self.Source                         = source
        self.Line                           = line
        self.Column                         = column
        self.Message                        = self.MessageTemplate.format(**kwargs)

    # ----------------------------------------------------------------------
    def __repr__(self):
        return CommonEnvironment.ObjectReprImpl(self)


# ----------------------------------------------------------------------
def CreateErrorClass(message_template):
    # ----------------------------------------------------------------------
    class TheError(Error):
        MessageTemplate                     = Interface.DerivedProperty(message_template)

    # ----------------------------------------------------------------------

    return TheError


# ----------------------------------------------------------------------
MissingMultilineTokenNewlineSuffixError     = CreateErrorClass("This multiline string token must be followed by a newline.")
MissingMultilineStringTerminatorError       = CreateErrorClass("The closing token for this multiline string was not found.")
InvalidMultilineStringPrefixError           = CreateErrorClass("The prefix for this multiline string is not valid; each line must be aligned with the opening token.")
