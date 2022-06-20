# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-29 17:02:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationStatementParserInfo object"""

import os

from typing import Dict, List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfo, ParserInfoType, ScopeFlag, StatementParserInfo, TranslationUnitRegion
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncInvocationStatementParserInfo(StatementParserInfo):
    # ----------------------------------------------------------------------
    expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        expression: ExpressionParserInfo,
        *args,
        **kwargs,
    ):
        return cls(
            expression.parser_info_type__,  # type: ignore
            regions,                        # type: ignore
            expression,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(FuncInvocationStatementParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=["expression", ],
        )

        # Validate
        self.expression.InitializeAsExpression()

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetValidScopes() -> Dict[ParserInfoType, ScopeFlag]:
        return {
            ParserInfoType.Configuration: ScopeFlag.Root | ScopeFlag.Class | ScopeFlag.Function,
            ParserInfoType.TypeCustomization: ScopeFlag.Class | ScopeFlag.Function,
            ParserInfoType.Standard: ScopeFlag.Function,
        }

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "expression", self.expression  # type: ignore
