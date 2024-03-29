# ----------------------------------------------------------------------
# |
# |  IfStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-21 14:32:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IfStatementParserInfo and IfStatementClauseParserInfo objects"""

import os

from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import (
        CompileTimeInfo,
        ParserInfo,
        ParserInfoType,
        ScopeFlag,
        StatementParserInfo,
        TranslationUnitRegion,
    )

    from .Traits.ScopedStatementTrait import ScopedStatementTrait

    from ..Common.VisibilityModifier import VisibilityModifier
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ...Common import MiniLanguageHelpers


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatementClauseParserInfo(
    ScopedStatementTrait,
    ParserInfo,
):
    # ----------------------------------------------------------------------
    parser_info_type: InitVar[ParserInfoType]
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    expression: ExpressionParserInfo
    documentation: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        statements: List[StatementParserInfo],
        regions: List[Optional[TranslationUnitRegion]],
        expression: ExpressionParserInfo,
        *args,
        **kwargs,
    ):
        # Duplicate regions for items that we are generating automatically
        assert regions and regions[0] is not None
        regions.insert(0, regions[0])       # name
        regions.insert(0, regions[0])       # visibility

        return cls(  # pylint: disable=too-many-function-args
            "IfStatementClauseParserInfo ({})".format(regions[0].begin.line),
            VisibilityModifier.private,     # type: ignore
            statements,                     # type: ignore
            expression.parser_info_type__,  # type: ignore
            regions,                        # type: ignore
            expression,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, visibility_param, parser_info_type, regions, *args, **kwargs):
        ParserInfo.__init__(
            self,
            parser_info_type,
            regions,
            *args,
            **{
                **kwargs,
                **ScopedStatementTrait.ObjectReprImplBaseInitKwargs(),
                **{
                    "finalize": False,
                    "regionless_attributes": [
                        "expression",
                    ]
                        + ScopedStatementTrait.RegionlessAttributesArgs()
                    ,
                },
            },
        )

        ScopedStatementTrait.__post_init__(self, visibility_param)

        self._Finalize()

        self._InitTraits(
            allow_name_to_be_duplicated=False,
        )

        self.expression.InitializeAsExpression()

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsNameOrdered(*args, **kwargs) -> bool:
        return True

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "expression", self.expression  # type: ignore

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    @Interface.override
    def _InitConfigurationImpl(*args, **kwargs):
        # Nothing to do here
        yield


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatementElseClauseParserInfo(
    ScopedStatementTrait,
    ParserInfo,
):
    # ----------------------------------------------------------------------
    parser_info_type: InitVar[ParserInfoType]
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    documentation: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        statements: List[StatementParserInfo],
        regions: List[Optional[TranslationUnitRegion]],
        *args,
        **kwargs,
    ):
        # Duplicate regions for items that we are generating automatically
        assert regions and regions[0] is not None
        regions.insert(0, regions[0])       # name
        regions.insert(0, regions[0])       # visibility

        return cls(  # pylint: disable=too-many-function-args
            "IfStatementElseClauseParserInfo ({})".format(regions[0].begin.line),
            VisibilityModifier.private,     # type: ignore
            statements,                     # type: ignore
            ParserInfoType.Unknown,         # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, visibility_param, parser_info_type, regions, *args, **kwargs):
        ParserInfo.__init__(
            self,
            parser_info_type,
            regions,
            *args,
            **{
                **kwargs,
                **ScopedStatementTrait.ObjectReprImplBaseInitKwargs(),
                **{
                    "regionless_attributes": ScopedStatementTrait.RegionlessAttributesArgs(),
                    "finalize": False,
                },
            },
        )

        ScopedStatementTrait.__post_init__(self, visibility_param)

        self._Finalize()

        self._InitTraits(
            allow_name_to_be_duplicated=False,
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsNameOrdered(*args, **kwargs) -> bool:
        return True

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    @Interface.override
    def _InitConfigurationImpl(*args, **kwargs):
        # Nothing to do here
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _GetUniqueId() -> Tuple[Any, ...]:
        return ()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatementParserInfo(StatementParserInfo):
    # ----------------------------------------------------------------------
    clauses: List[IfStatementClauseParserInfo]
    else_clause: Optional[IfStatementElseClauseParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        clauses: List[IfStatementClauseParserInfo],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.GetDominantType(*clauses),   # type: ignore
            regions,                                    # type: ignore
            clauses,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(IfStatementParserInfo, self).__post_init__(
            *args,
            **{
                **kwargs,
                **{
                    "regionless_attributes": [
                        "clauses",
                        "else_clause",
                    ],
                },
            },
        )

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
    def _GenerateAcceptChildren(self) -> ParserInfo._GenerateAcceptChildrenResultType:  # pylint: disable=protected-access
        yield from self.clauses  # type: ignore

        if self.else_clause:
            yield self.else_clause  # type: ignore

    # ----------------------------------------------------------------------
    @contextmanager
    @Interface.override
    def _InitConfigurationImpl(
        self,
        configuration_data: Dict[str, CompileTimeInfo],
    ):
        executed_clause = False

        for clause in self.clauses:
            execute_flag = False

            if not executed_clause:
                clause_result = MiniLanguageHelpers.EvalExpression(
                    clause.expression,
                    [configuration_data],
                )

                clause_result = clause_result.type.ToBoolValue(clause_result.value)
                if clause_result:
                    execute_flag = True

            if execute_flag:
                assert executed_clause is False
                executed_clause = True
            else:
                clause.Disable()

        if self.else_clause and executed_clause:
            self.else_clause.Disable()

        yield
