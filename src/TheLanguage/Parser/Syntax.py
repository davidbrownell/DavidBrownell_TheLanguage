# ----------------------------------------------------------------------
# |
# |  Syntax.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 11:48:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that allows the dynamic specification of custom syntaxes"""

import os
import re

from typing import cast, Dict, List, Optional, Tuple

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
    from .Components.Error import Error
    from .Components.Token import (
        DedentToken,
        IndentToken,
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        NewlineToken,
        RegexToken,
    )

    from .Phrases.DSL import CreatePhrase, DynamicPhrasesType, PhraseItem

    from .TranslationUnitParser import DynamicPhrasesInfo

    from .TranslationUnitsParser import (
        Observer as TranslationUnitsParserObserver,
        Phrase,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SyntaxInvalidVersionFormatError(Error):
    # Note that this is a str rather than a SemVer, as the invalid version may not even be in the
    # correct format
    InvalidVersion: str

    MessageTemplate                         = Interface.DerivedProperty("The syntax version '{InvalidVersion}' is not a valid version")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SyntaxInvalidVersionError(Error):
    InvalidVersion: SemVer

    MessageTemplate                         = Interface.DerivedProperty("The syntax version '{InvalidVersion}' is not recognized")


# ----------------------------------------------------------------------
def _CreateSyntaxStatements():
    version_token = RegexToken("<semantic_version>", re.compile(r"(?P<value>[a-zA-Z0-9_\-\.]+)\b"))

    statements_phrase = PhraseItem(
        DynamicPhrasesType.Statements,
        arity="+",
    )

    # '__with' '__syntax' '=' <version> ':'
    #     <statement>+
    set_syntax_statement = CreatePhrase(
        name="Set Syntax",
        item=[
            "__with",
            "__syntax",
            "=",
            version_token,
            ":",
            NewlineToken(),
            IndentToken(),
            statements_phrase,
            DedentToken(),
        ],
    )

    # Note that this statement is more complicated that what we would prefer, as we aren't relying
    # on the DynamicPhrases capabilities for expressions (as we don't want these expressions to be
    # used in other contextes). The syntax for these statements are relatively straight forward, so
    # this isn't as big of an issues as it would be if we tried to do this with any reasonably sized
    # grammar.

    # This is a stand-alone phrase because it is recursive
    condition_phrase = CreatePhrase(
        name="Condition Phrase",
        item=(
            # '__syntax' ('=='|'!='|'<'|'<='|'>'|'>=') <version>
            PhraseItem(
                name="Comparison",
                item=[
                    "__syntax",
                    ("==", "!=", "<", "<=", ">", ">="),
                    version_token,
                ],
            ),

            # 'not' <condition_phrase>
            PhraseItem(
                name="Not",
                item=["not", None],
            ),

            # '(' <condition_phrase> ('and'|'or' <condition_phrase>)+ ')'
            #
            #  The use of parens to group the clauses is unfortunately, but a byproduct of the simplicity
            # of these statements. Hopefully, this functionality isn't used much and this is an
            # acceptable tradeoff.
            #
            PhraseItem(
                name="Logical",
                item=[
                    # '('
                    '(',
                    PushIgnoreWhitespaceControlToken(),

                    # <condition_phrase>
                    None,

                    # ('and'|'or' <condition_phrase>)+
                    PhraseItem(
                        item=[
                            ("and", "or"),
                            None,
                        ],
                        arity="+",
                    ),

                    # ')'
                    PopIgnoreWhitespaceControlToken(),
                    ')',
                ],
            ),
        ),
    )

    # '__if' <condition_phrase> ':'
    #     <statement>+
    if_syntax_statement = CreatePhrase(
        name="If Syntax",
        item=[
            "__if",
            condition_phrase,
            ":",
            NewlineToken(),
            IndentToken(),
            statements_phrase,
            DedentToken(),
        ],
    )

    return [
        set_syntax_statement,
        if_syntax_statement,
    ]


_syntax_statements                          = _CreateSyntaxStatements()
del _CreateSyntaxStatements


# ----------------------------------------------------------------------
class Observer(TranslationUnitsParserObserver):
    """Processes all syntax-related statements; all others are forwarded to the provided observer"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        observer: TranslationUnitsParserObserver,
        syntaxes: Dict[
            SemVer,
            DynamicPhrasesInfo,
        ],
    ):
        assert observer
        assert syntaxes

        max_ver: Optional[SemVer] = None
        updated_syntaxes = {}

        for semver, phrases_info in syntaxes.items():
            if max_ver is None or semver > max_ver:
                max_ver = semver

            updated_statements = phrases_info.Statements

            for syntax_statement in _syntax_statements:
                if not any(statement for statement in phrases_info.Statements if getattr(statement, "Name", None) == syntax_statement.Name):
                    updated_statements = [syntax_statement] + updated_statements

            updated_syntaxes[semver] = phrases_info.Clone(
                updated_statements=updated_statements,
                updated_allow_parent_traversal=False,
                updated_name="{} Grammar".format(semver),
            )

        assert max_ver is not None

        self._observer                      = observer

        self.DefaultVersion                 = max_ver
        self.Syntaxes                       = updated_syntaxes

    # ----------------------------------------------------------------------
    @Interface.override
    def LoadContent(self, *args, **kwargs):  # <parameters differ> pylint: disable=W0221
        return self._observer.LoadContent(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(self, *args, **kwargs):  # <parameters differ> pylint: disable=W0221
        return self._observer.Enqueue(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def ExtractDynamicPhrases(self, *args, **kwargs):  # <parameters differ> pylint: disable=W0221
        return self._observer.ExtractDynamicPhrases(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnIndentAsync(
        self,
        fully_qualified_name: str,
        data_stack: List[Phrase.StandardParseResultData],
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Optional[DynamicPhrasesInfo]:
        # Process the statement once we have encountered the corresponding indent
        if len(data_stack) > 1 and data_stack[1].Phrase in _syntax_statements:
            statement = data_stack[1].Phrase

            if statement.Name == "Set Syntax":
                assert data_stack[1].Data
                return self._SetSyntax(data_stack[1].Data)

            elif statement.Name == "If Syntax":
                pass # TODO

            else:
                assert False, statement  # pragma: no cover

        return await self._observer.OnIndentAsync(
            fully_qualified_name,
            data_stack,
            iter_before,
            iter_after,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnDedentAsync(self, *args, **kwargs):  # <parameters differ> pylint: disable=W0221
        return await self._observer.OnDedentAsync(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnPhraseCompleteAsync(self, *args, **kwargs):  # <parameters differ> pylint: disable=W0221
        return await self._observer.OnPhraseCompleteAsync(*args, **kwargs)


    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _SetSyntax(
        self,
        data: Phrase.ParseResultData,
    ) -> DynamicPhrasesInfo:
        data = cast(Phrase.MultipleStandardParseResultData, data)

        # The data will include everything prior to the indentation
        assert len(data.DataItems) == 6, data.DataItems

        # Extract the version
        version_data = data.DataItems[3]
        assert version_data

        version, version_data = self._GetVersion(version_data)

        phrases_info = self.Syntaxes.get(version, None)
        if phrases_info is None:
            raise SyntaxInvalidVersionError(
                version_data.IterBefore.Line,
                version_data.IterBefore.Column,
                version,
            )

        return phrases_info

    # ----------------------------------------------------------------------
    @staticmethod
    def _GetVersion(
        data: Phrase.ParseResultData,
    ) -> Tuple[SemVer, Phrase.TokenParseResultData]:
        data = cast(Phrase.StandardParseResultData, data)
        assert data.Phrase.Name == "<semantic_version>", data.Phrase.name

        token_data = cast(Phrase.TokenParseResultData, data.Data)
        token_value = cast(RegexToken.MatchResult, token_data.Value).Match.group("value")

        try:
            return SemVer.coerce(token_value), token_data
        except ValueError:
            raise SyntaxInvalidVersionFormatError(
                token_data.IterBefore.Line,
                token_data.IterBefore.Column,
                token_value,
            )
