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

from typing import Dict, Optional

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
    from .MultifileParser import Observer as MultifileParserObserver
    from .Statement import DynamicStatements, Statement
    from .StatementsParser import DynamicStatementInfo

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
SetSyntaxStatement                          = Statement(
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
class Observer(MultifileParserObserver):
    """Processes syntax-related statements; all other statements are processed by the provided observer"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        observer: MultifileParserObserver,
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

            if not any(statement for statement in statement_info.statements if getattr(statement, "Name", None) == SetSyntaxStatement.Name):
                updated_statements = [SetSyntaxStatement] + statement_info.statements

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
    def ExtractDynamicStatementInfo(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.ExtractDynamicStatementInfo(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.Enqueue(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnIndent(
        self,
        fully_qualified_name: str,
        statement: Statement,
        results: Statement.ParseResultItemsType,
    ) -> Optional[DynamicStatementInfo]:
        if statement == SetSyntaxStatement:
            assert len(results) >= 3, len(results)
            assert results[2].Token.Name == "<semantic_version>"

            regex_match = results[2].Value.Match
            semver_string = "{}.{}.{}".format(
                regex_match.group("major"),
                regex_match.group("minor"),
                regex_match.group("patch") or "0",
            )

            statement_info = self.Syntaxes.get(SemVer(semver_string), None)
            if statement_info is None:
                raise SyntaxInvalidVersionError(
                    results[2].IterBefore.Line,
                    results[2].IterBefore.Column,
                    semver_string,
                )

            return statement_info

        return self._observer.OnIndent(fully_qualified_name, statement, results)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnDedent(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.OnDedent(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnStatementComplete(self, *args, **kwargs):  # <Parameters differ> pylint: disable=W0221
        return self._observer.OnStatementComplete(*args, **kwargs)
