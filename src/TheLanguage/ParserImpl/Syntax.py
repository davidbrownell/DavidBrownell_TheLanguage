# ----------------------------------------------------------------------
# |
# |  Syntax.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-17 09:49:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when working with custom syntaxes"""

import os
import re

from typing import cast, Dict, List, Optional

from dataclasses import dataclass
from semantic_version import Version as SemVer

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Error import Error
    from .StatementDSL import CreateStatement, DynamicStatements, StatementItem
    from .TranslationUnitParser import DynamicStatementInfo

    from .TranslationUnitsParser import (
        NormalizedIterator,
        Observer as TranslationUnitsParserObserver,
        Statement,
    )

    from .Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
        Token,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SyntaxInvalidVersionError(Error):
    InvalidVersion: SemVer

    MessageTemplate                         = Interface.DerivedProperty("The syntax version '{InvalidVersion}' is not valid")


# ----------------------------------------------------------------------
# major and Minor components are required, patch is optional.
_simple_semantic_version_regex              = re.compile(r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)(?:\.(?P<patch>0|[1-9]\d*))?")


# ----------------------------------------------------------------------
# Statement to explicitly set the version of the syntax used to parse the block. This
# is useful to make code written according to an older syntax version available along side
# code written according to the current syntax version.

# __with_syntax=1.0:
#     ...
#
SetSyntaxStatement                          = CreateStatement(
    name="Set Syntax",
    item=[
        RegexToken("'__with_syntax'", re.compile(r"(?P<value>__with_syntax)")),
        RegexToken("'='", re.compile(r"(?P<value>=)")),
        RegexToken("<semantic_version>", _simple_semantic_version_regex),
        RegexToken("':'", re.compile(r"(?P<value>:)")),
        NewlineToken(),
        IndentToken(),
        StatementItem(DynamicStatements.Statements, Arity="+"),
        DedentToken(),
    ],
)


# ----------------------------------------------------------------------
class Observer(TranslationUnitsParserObserver):
    """Processes syntax-related statements; all other statements are processed by the provided observer"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        observer: TranslationUnitsParserObserver,
        syntaxes: Dict[
            SemVer,                         # Syntax Name
            DynamicStatementInfo,           # Syntax Info
        ],
    ):
        assert observer
        assert syntaxes

        max_ver = None
        updated_syntaxes = {}

        for semver, statement_info in syntaxes.items():
            if max_ver is None or semver > max_ver:
                max_ver = semver

            updated_statements = None

            if not any(statement for statement in statement_info.Statements if getattr(statement, "Name", None) == SetSyntaxStatement.Name):
                updated_statements = (SetSyntaxStatement,) + statement_info.Statements

            updated_syntaxes[semver] = statement_info.Clone(
                updated_statements=updated_statements,
                updated_allow_parent_traversal=False,
                updated_name="{} Grammar".format(semver),
            )

        self._observer                      = observer
        self.DefaultVersion                 = max_ver
        self.Syntaxes                       = updated_syntaxes

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.Enqueue(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def LoadContent(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.LoadContent(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def ExtractDynamicStatements(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.ExtractDynamicStatements(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def StartStatement(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.StartStatement(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def EndStatement(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.EndStatement(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnIndentAsync(
        self,
        fully_qualified_name: str,
        data_stack: List[Statement.StandardParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Optional[DynamicStatementInfo]:
        if len(data_stack) > 1 and data_stack[1].Statement == SetSyntaxStatement:
            data = cast(Statement.MultipleStandardParseResultData, data_stack[1].Data)

            # The data should include everything prior to the indentation
            assert len(data.DataItems) == 5, data.DataItems
            data = cast(Statement.StandardParseResultData, data.DataItems[2])
            assert data.Statement.Name == "<semantic_version>", data.Statement.Name

            token_data = cast(Statement.TokenParseResultData, data.Data)

            regex_match = cast(Token.RegexMatch, token_data.Value).Match

            semver = SemVer(
                "{}.{}.{}".format(
                    regex_match.group("major"),
                    regex_match.group("minor"),
                    regex_match.group("patch") or "0",
                ),
            )

            statement_info = self.Syntaxes.get(semver, None)
            if statement_info is None:
                raise SyntaxInvalidVersionError(
                    token_data.IterBefore.Line,
                    token_data.IterBefore.Column,
                    semver,
                )

            return statement_info

        return await self._observer.OnIndentAsync(
            fully_qualified_name,
            data_stack,
            iter_before,
            iter_after,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnDedentAsync(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return await self._observer.OnDedentAsync(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnStatementCompleteAsync(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return await self._observer.OnStatementCompleteAsync(*args, **kwargs)
