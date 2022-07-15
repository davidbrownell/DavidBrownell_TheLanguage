# ----------------------------------------------------------------------
# |
# |  ConcreteFuncDefinition.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-13 13:22:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ConcreteFuncDefinition object"""

import os

from typing import TYPE_CHECKING

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..EntityResolver import EntityResolver

    if TYPE_CHECKING:
        from .FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ConcreteFuncDefinition(object):
    # ----------------------------------------------------------------------
    parser_info: "FuncDefinitionStatementParserInfo"

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        func_parser_info: "FuncDefinitionStatementParserInfo",
        entity_resolver: EntityResolver,
    ):
        # BugBug

        return cls(
            func_parser_info,
        )

    # ----------------------------------------------------------------------
    def Finalize(
        self,
        entity_resolver: EntityResolver,
    ) -> None:
        pass # BugBug
