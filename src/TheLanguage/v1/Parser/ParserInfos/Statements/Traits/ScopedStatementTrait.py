# ----------------------------------------------------------------------
# |
# |  ScopedStatementTrait.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-17 12:49:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ScopedStatementTrait object"""

import os

from typing import Any, Dict, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NamedStatementTrait import NamedStatementTrait

    from ..StatementParserInfo import ParserInfo, ParserInfoType, StatementParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ScopedStatementTrait(NamedStatementTrait):
    """Add to a statement when it introduces a new scope"""

    statements: Optional[List[StatementParserInfo]]

    # ----------------------------------------------------------------------
    def __post_init__(self, visibility_param):
        NamedStatementTrait.__post_init__(self, visibility_param)

        if self.statements:
            parser_info_type = self.parser_info_type__  # type: ignore  # pylint: disable=no-member

            if ParserInfoType.IsCompileTime(parser_info_type):
                for statement in self.statements:
                    if statement.parser_info_type__ == ParserInfoType.CompileTimeTemporary:
                        statement.OverrideParserInfoType(parser_info_type)

    # ----------------------------------------------------------------------
    @staticmethod
    def RegionlessAttributesArgs() -> List[str]:
        return [] + NamedStatementTrait.RegionlessAttributesArgs()

    # ----------------------------------------------------------------------
    @staticmethod
    def ObjectReprImplBaseInitKwargs() -> Dict[str, Any]:
        return {
            **NamedStatementTrait.ObjectReprImplBaseInitKwargs(),
        }

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptChildren(self) -> ParserInfo._GenerateAcceptChildrenResultType:  # pylint: disable=protected-access
        if self.statements:
            yield from self.statements  # pylint: disable=not-an-iterable
