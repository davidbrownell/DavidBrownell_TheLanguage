# ----------------------------------------------------------------------
# |
# |  LexerError.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-09 15:03:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LexerError object"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .LexerInfo import Region


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class LexerError(Exception, Interface.Interface):
    """Base error for all Lexer-related errors"""

    Region: Region

    # ----------------------------------------------------------------------
    def __str__(self):
        # pylint: disable=no-member
        return self.MessageTemplate.format(**self.__dict__)

    # ----------------------------------------------------------------------
    @Interface.abstractmethod
    def MessageTemplate(self) -> str:
        """Template used when generating the exception string"""
        raise Exception("Abstract method")  # pragma: no cover
