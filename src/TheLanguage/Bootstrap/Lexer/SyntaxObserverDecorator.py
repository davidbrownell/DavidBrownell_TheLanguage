# ----------------------------------------------------------------------
# |
# |  SyntaxObserverDecorator.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-27 23:06:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that allows the dynamic specification of targeted compiler behavior"""

import os
import re

from enum import Enum
from typing import cast, Dict, List, Optional, Union

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

    from .Components.Token import (
        DedentToken,
        IndentToken,
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        NewlineToken,
        RegexToken,
    )

    from .Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractToken,
        OneOrMorePhraseItem,
        PhraseItem,
    )
    from .Phrases.SequencePhrase import SequencePhrase

    from .TranslationUnitsLexer import (
        AST,
        DynamicPhrasesInfo,
        Observer as TranslationUnitsLexerObserver,
        Phrase,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SyntaxInvalidVersionFormatError(Error):
    InvalidVersion: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The syntax version '{InvalidVersion}' is not a valid version.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SyntaxInvalidVersionError(Error):
    InvalidVersion: SemVer

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The syntax version '{InvalidVersion}' is not recognized.",
    )


# ----------------------------------------------------------------------
SET_PHRASE_NAME                             = "Set Syntax Statement"
CONDITIONAL_PHRASE_NAME                     = "Conditional Syntax Statement"

# ----------------------------------------------------------------------
class Configurations(Enum):
    Debug                                   = "debug"
    ReleaseNoOptimizations                  = "release_noopt"
    Release                                 = "release"

    # TODO: Implement value comparison


# ----------------------------------------------------------------------
class ComparisonOperators(Enum):
    Equal                                   = "=="
    NotEqual                                = "!="
    LessThan                                = "<"
    LessThanOrEqual                         = "<="
    GreaterThan                             = ">"
    GreaterThanOrEqual                      = ">="


# ----------------------------------------------------------------------
class LogicalOperators(Enum):
    And                                     = "and"
    Or                                      = "or"


# ----------------------------------------------------------------------
_statements_phrase_item                     = OneOrMorePhraseItem(
    PhraseItem.Create(
        name="Grammar-Specific Statements",
        item=DynamicPhrasesType.Statements,
    ),
)


_value_token                                = RegexToken.Create(
    "<value>",
    re.compile(r"(?P<value>[a-zA-Z0-9_\-\.]+)\b"),
)


def _CreateWithStatement() -> Phrase:
    # '__with' '__syntax' '=' <value> ':'
    #     <statement>+
    return CreatePhrase(
        name=SET_PHRASE_NAME,
        item=[
            "__with",
            "__syntax",
            "=",
            _value_token,
            ":",
            NewlineToken.Create(),
            IndentToken.Create(),
            _statements_phrase_item,
            DedentToken.Create(),
        ],
    )


def _CreateConditionalStatement() -> Phrase:
    # Note that the following statement is more complicated that what we would prefer, as we aren't relying
    # on the DynamicPhrases capabilities for expressions (as we don't want these expressions to be
    # used in other contexts). The syntax for these statements are relatively straight forward, so
    # this isn't as big of an issues as it would be if we tried to do this with any reasonably sized
    # grammar.

    # This is a stand-alone phrase because it is recursive
    condition_phrase = CreatePhrase(
        name="Condition Phrase",
        item=(
            # <variable_name> <comparison_operator_types> <value>
            PhraseItem.Create(
                name="Comparison",
                item=[
                    # <variable_name>
                    (
                        "__syntax",
                        "__configuration",
                        "__target",
                    ),

                    # <comparison_operator_types>
                    tuple(e.value for e in ComparisonOperators),

                    # <value>
                    _value_token,
                ],
            ),

            # 'not' <condition_phrase>
            PhraseItem.Create(
                name="Not",
                item=[
                    "not",
                    None,
                ],
            ),

            # '(' <condition_phrase> ((<logical_operator_types>) <condition_phrase>)+ ')'
            #
            # The required use of parens to group the clauses is unfortunate, but a byproduct
            # of how simple these statements need to be at this low level.
            #
            PhraseItem.Create(
                name="Logical",
                item=[
                    # '('
                    "(",
                    PushIgnoreWhitespaceControlToken.Create(),

                    # <condition_phrase>
                    None,

                    # (<logical_operator> <condition_phrase>)+
                    OneOrMorePhraseItem(
                        [
                            tuple(e.value for e in LogicalOperators),
                            None,
                        ],
                    ),

                    # ')'
                    PopIgnoreWhitespaceControlToken.Create(),
                    ")",
                ],
            ),
        ),
    )

    # '__if' <condition_phrase> ':'
    #     <statement>+
    return CreatePhrase(
        name=CONDITIONAL_PHRASE_NAME,
        item=[
            "__if",
            condition_phrase,
            ":",
            NewlineToken.Create(),
            IndentToken.Create(),
            _statements_phrase_item,
            DedentToken.Create(),
        ],
    )


# ----------------------------------------------------------------------
_statements                                 = [
    _CreateWithStatement(),
    _CreateConditionalStatement(),
]

del _value_token
del _statements_phrase_item

del _CreateConditionalStatement
del _CreateWithStatement


# ----------------------------------------------------------------------
class SyntaxObserverDecorator(TranslationUnitsLexerObserver):
    """Processes all syntax-related statements; all others are forwarded to the provided observer"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        observer: TranslationUnitsLexerObserver,
        grammars: Dict[SemVer, DynamicPhrasesInfo],
        configuration: Configurations,
        target: str,
        default_grammar: Optional[SemVer]=None,
    ):
        assert observer
        assert grammars
        assert all(bool(phrase_info) for phrase_info in grammars.values())
        assert configuration
        assert target

        # Augment the grammars to include the syntax statements and calculate the max version
        updated_grammars: Dict[SemVer, DynamicPhrasesInfo] = {}
        max_ver: Optional[SemVer] = None

        for semver, phrase_info in grammars.items():
            existing_statements = phrase_info.Phrases.get(DynamicPhrasesType.Statements, [])

            # Augment the existing statements with _statements
            existing_statement_names = set(statement.Name for statement in existing_statements)

            updated_statements = []

            for statement in _statements:
                if statement.Name not in existing_statement_names:
                    updated_statements.append(statement)

            updated_statements += existing_statements

            # Update the phrases with this new statement info
            updated_phrases = {}

            for phrase_type, statements in phrase_info.Phrases.items():
                if phrase_type == DynamicPhrasesType.Statements:
                    updated_phrases[phrase_type] = updated_statements
                else:
                    updated_phrases[phrase_type] = statements

            updated_grammars[semver] = phrase_info.Clone(
                new_phrases=updated_phrases,
                new_allow_parent_traversal=False,
                new_name="{} Grammar".format(semver),
            )

            # Calculate the max version
            if max_ver is None or semver > max_ver:
                max_ver = semver

        assert max_ver is not None

        if default_grammar is None:
            default_grammar = max_ver
        else:
            assert default_grammar in updated_grammars, default_grammar

        self.Grammars                       = updated_grammars
        self.DefaultGrammarVersion          = default_grammar
        self.Configuration                  = configuration
        self.Target                         = target

        self._observer                      = observer

        self._should_ignore_stack: List[bool]           = [False]
        self._node_cache: Optional[List[AST.Node]]      = None

    # ----------------------------------------------------------------------
    @Interface.override
    def LoadContent(self, *args, **kwargs):  # pylint: disable=arguments-differ
        return self._observer.LoadContent(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def GetParentStatementNode(self, *args, **kwargs):  # pylint: disable=arguments-differ
        return self._observer.GetParentStatementNode(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(self, *args, **kwargs):  # pylint: disable=arguments-differ
        return self._observer.Enqueue(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def ExtractDynamicPhrases(self, *args, **kwargs):  # pylint: disable=arguments-differ
        return self._observer.ExtractDynamicPhrases(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnPushScopeAsync(
        self,
        fully_qualified_name: str,
        data: Phrase.StandardLexResultData,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Optional[DynamicPhrasesInfo]:

        result: Optional[DynamicPhrasesInfo] = None
        should_ignore = False

        if self._node_cache is not None:
            assert data.Phrase.Parent is not None

            if data.Phrase.Parent.Name == SET_PHRASE_NAME:
                result = self._OnSetPhrase()

            elif data.Phrase.Parent.Name == CONDITIONAL_PHRASE_NAME:
                should_ignore = self._OnConditionalPhrase()

            else:
                assert False, data.Phrase.Parent.Name

            self._node_cache = None

        self._should_ignore_stack.append(should_ignore)

        if result is not None:
            return result

        return await self._observer.OnPushScopeAsync(
            fully_qualified_name,
            data,
            iter_before,
            iter_after,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnPopScopeAsync(self, *args, **kwargs):  # pylint: disable=arguments-differ
        assert self._should_ignore_stack
        self._should_ignore_stack.pop()

        return await self._observer.OnPopScopeAsync(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnPhraseCompleteAsync(
        self,
        fully_qualified_name: str,
        phrase: Phrase,
        node: AST.Node,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Union[
        bool,
        DynamicPhrasesInfo,
        TranslationUnitsLexerObserver.ImportInfo,
    ]:
        if (
            self._node_cache is None
            and isinstance(node, AST.Leaf)
            and phrase.Parent is not None
            and isinstance(phrase.Parent, SequencePhrase)
            and (
                phrase.Parent.Name == SET_PHRASE_NAME
                or phrase.Parent.Name == CONDITIONAL_PHRASE_NAME
            )
        ):
            self._node_cache = []

        if self._node_cache is not None:
            self._node_cache.append(node)

        object.__setattr__(node, "IsIgnored", self._should_ignore_stack[-1])

        return await self._observer.OnPhraseCompleteAsync(
            fully_qualified_name,
            phrase,
            node,
            iter_before,
            iter_after,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _OnSetPhrase(self) -> DynamicPhrasesInfo:
        assert self._node_cache is not None
        assert len(self._node_cache) == 6

        # Get the string value
        version_leaf = cast(AST.Leaf, self._node_cache[3])
        version_value = cast(str, ExtractToken(version_leaf))

        # Get the semantic version value
        try:
            semver = SemVer.coerce(version_value)
        except:
            raise SyntaxInvalidVersionFormatError(
                version_leaf.IterBegin.Line,
                version_leaf.IterBegin.Column,
                version_value,
            )

        phrases_info = self.Grammars.get(semver, None)
        if phrases_info is None:
            raise SyntaxInvalidVersionError(
                version_leaf.IterBegin.Line,
                version_leaf.IterBegin.Column,
                semver,
            )

        return phrases_info

    # ----------------------------------------------------------------------
    def _OnConditionalPhrase(self) -> bool:
        # TODO
        return False
