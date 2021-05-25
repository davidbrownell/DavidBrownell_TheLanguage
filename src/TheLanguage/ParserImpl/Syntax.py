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
from rop import read_only_properties
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
    from .RepeatStatement import RepeatStatement
    from .StandardStatement import NamedStandardStatement, StandardStatement
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
SetSyntaxStatement                          = NamedStandardStatement(
    "Set Syntax Statement",
    [
        # __with __syntax=1.0:
        #     ...
        #
        RegexToken("__with", re.compile(r"(?P<value>__with)")),
        RegexToken("__syntax", re.compile(r"(?P<value>__syntax)")),
        RegexToken("<assign>", re.compile(r"(?P<value>=)")),
        RegexToken("semantic version", _simple_semantic_version_regex),
        RegexToken(":", re.compile(r"(?P<value>:)")),
        NewlineToken(),
        IndentToken(),
        RepeatStatement(
            StandardStatement(
                [
                    DynamicStatements.Statements,
                ],
            ),
            1,
            None,
        ),
        DedentToken(),
    ],
)

def _GenerateSetSyntaxStatementContentFromResult(node):
    assert len(node.Children) == 9

    # Repeat Statement
    for child in node.Children[7].Children:
        assert isinstance(child.Type, StandardStatement), child
        assert len(child.Children) == 1, child.Children

        child = child.Children[0]

        assert child.Type == DynamicStatements.Statements
        assert len(child.Children) == 1, child.Children

        yield child.Children[0]


SetSyntaxStatement.GenerateContentFromResult            = _GenerateSetSyntaxStatementContentFromResult


# ----------------------------------------------------------------------
@read_only_properties(
    "_observer",
    "DefaultVersion",
    "Syntaxes",
)
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
            assert len(results) >= 4, len(results)
            assert results[3].Token.Name == "semantic version"

            regex_match = results[3].Value.Match
            semver_string = "{}.{}.{}".format(
                regex_match.group("major"),
                regex_match.group("minor"),
                regex_match.group("patch") or "0",
            )

            statement_info = self.Syntaxes.get(SemVer(semver_string), None)
            if statement_info is None:
                raise SyntaxInvalidVersionError(
                    results[3].Iter.Line,
                    results[2].Iter.Column + ((results[3].Whitespace[1] - results[3].Whitespace[0]) if results[3].Whitespace else 0),
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
