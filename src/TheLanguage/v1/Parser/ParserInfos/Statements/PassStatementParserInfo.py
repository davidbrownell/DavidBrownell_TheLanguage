# ----------------------------------------------------------------------
# |
# |  PassStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-01 12:29:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PassStatementParserInfo object"""

import os

from contextlib import contextmanager
from typing import Any, Dict, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfoType, ScopeFlag, StatementParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class PassStatementParserInfo(StatementParserInfo):
    """Noop statement"""

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetValidScopes() -> Dict[ParserInfoType, ScopeFlag]:
        return {
            ParserInfoType.Configuration: ScopeFlag.Root | ScopeFlag.Class | ScopeFlag.Function,
            ParserInfoType.TypeCustomization: ScopeFlag.Root | ScopeFlag.Class | ScopeFlag.Function,
            ParserInfoType.Standard: ScopeFlag.Class | ScopeFlag.Function,
        }

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @contextmanager
    @Interface.override
    def _InitConfigurationImpl(self, *args, **kwargs):
        # This statement is not interesting
        self.Disable()
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _GetUniqueId() -> Tuple[Any, ...]:
        return ()
