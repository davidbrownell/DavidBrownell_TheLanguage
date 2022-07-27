# ----------------------------------------------------------------------
# |
# |  GenericClassType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-26 16:30:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GenericClassType object"""

import os

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GenericType import GenericType

    from ...Statements.ClassStatementParserInfo import ClassStatementParserInfo


# ----------------------------------------------------------------------
class GenericClassType(GenericType):
    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> ClassStatementParserInfo:
        assert isinstance(self._parser_info, ClassStatementParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSameType(
        self,
        other: GenericType,
    ) -> bool:
        # BugBug: Do this
        return False
