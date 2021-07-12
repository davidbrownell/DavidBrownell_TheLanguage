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

from typing import Dict, List, Optional

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

    from .StatementEx import (
        DynamicStatements,
        NormalizedIterator,
        Statement,
        StatementEx,
    )

    from .TranslationUnitParser import DynamicStatementInfo

    from .TranslationUnitsParser import (
        Node,
        Observer as TranslationUnitsParserObserver,
    )

    from .Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
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
SetSyntaxStatement                          = StatementEx(
    "Set Syntax",
    RegexToken("'__with_syntax'", re.compile(r"(?P<value>__with_syntax)")),
    RegexToken("'='", re.compile(r"(?P<value>=)")),
    RegexToken("<semantic_version>", _simple_semantic_version_regex),
    RegexToken("':'", re.compile(r"(?P<value>:)")),
    NewlineToken(),
    IndentToken(),
    (DynamicStatements.Statements, 1, None),
    DedentToken(),
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
                updated_statements = [SetSyntaxStatement] + statement_info.Statements

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
    def LoadContent(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.LoadContent(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def ExtractDynamicStatements(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.ExtractDynamicStatements(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.Enqueue(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnIndentAsync(
        self,
        fully_qualified_name: str,
        statement: StatementEx,
        data_items: List[Statement.ParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Optional[DynamicStatementInfo]:
        if statement == SetSyntaxStatement:
            assert len(data_items) >= 3, len(data_items)
            assert data_items[2].Statement.Name == "<semantic_version>"

            regex_match = data_items[2].Data.Value.Match
            semver_string = "{}.{}.{}".format(
                regex_match.group("major"),
                regex_match.group("minor"),
                regex_match.group("patch") or "0",
            )

            statement_info = self.Syntaxes.get(SemVer(semver_string), None)
            if statement_info is None:
                raise SyntaxInvalidVersionError(
                    data_items[2].Data.IterBefore.Line,
                    data_items[2].Data.IterBefore.Column,
                    semver_string,
                )

            return statement_info

        return self._observer.OnIndentAsync(
            fully_qualified_name,
            statement,
            data_items,
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
