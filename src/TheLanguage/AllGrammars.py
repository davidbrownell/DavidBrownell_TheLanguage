# ----------------------------------------------------------------------
# |
# |  AllGrammars.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-20 21:10:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Loads all Grammars"""

import importlib
import os
import sys

from collections import OrderedDict
from typing import Dict, List, Optional, Set

from semantic_version import Version as SemVer

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Grammars.GrammarPhrase import GrammarPhrase

    from .Lexer.Lex import (
        Lex as LexImpl,
        Prune as PruneImpl,
    )

    from .Lexer.TranslationUnitsLexer import (
        DynamicPhrasesInfo,
        Phrase,
        RootNode,
    )

    from .Parser.Parse import Parse as ParseImpl


# ----------------------------------------------------------------------
Grammars: Dict[SemVer, DynamicPhrasesInfo]              = OrderedDict()
GrammarPhraseLookup: Dict[Phrase, GrammarPhrase]        = OrderedDict()


# ----------------------------------------------------------------------
def _LoadDynamicPhrasesFromFile(
    filename: str,
    module_attribute_name: str=None,
) -> DynamicPhrasesInfo:
    assert os.path.isfile(filename), filename

    dirname, basename = os.path.split(filename)
    basename = os.path.splitext(basename)[0]

    sys.path.insert(0, dirname)
    with CallOnExit(lambda: sys.path.pop(0)):
        mod = importlib.import_module(basename)

        grammar_phrases = getattr(mod, module_attribute_name or "GrammarPhrases", None)
        assert grammar_phrases is not None, filename

        expressions: List[Phrase] = []
        names: List[Phrase] = []
        statements: List[Phrase] = []
        types: List[Phrase] = []
        name_lookup: Set[str] = set()

        for grammar_phrase in grammar_phrases:
            if grammar_phrase.TypeValue == GrammarPhrase.Type.Expression:
                expressions.append(grammar_phrase.Phrase)
            elif grammar_phrase.TypeValue == GrammarPhrase.Type.Name:
                names.append(grammar_phrase.Phrase)
            elif grammar_phrase.TypeValue == GrammarPhrase.Type.Statement:
                statements.append(grammar_phrase.Phrase)
            elif grammar_phrase.TypeValue == GrammarPhrase.Type.Type:
                types.append(grammar_phrase.Phrase)
            else:
                assert False, grammar_phrase.TypeValue  # pragma: no cover

            assert grammar_phrase.Phrase not in GrammarPhraseLookup, grammar_phrase.Phrase
            GrammarPhraseLookup[grammar_phrase.Phrase] = grammar_phrase

            # Ensure that phrase names are unique
            assert grammar_phrase.Phrase.Name not in name_lookup, grammar_phrase.Phrase.Name
            name_lookup.add(grammar_phrase.Phrase.Name)

        del sys.modules[basename]

        # pylint: disable=too-many-function-args
        return DynamicPhrasesInfo(
            expressions,
            names,
            statements,
            types,
            AllowParentTraversal=False,
        )


# ----------------------------------------------------------------------
Grammars[SemVer("0.0.1")]                   = _LoadDynamicPhrasesFromFile(os.path.join(_script_dir, "Grammars", "v0_0_1", "All.py"))


# ----------------------------------------------------------------------
assert GrammarPhraseLookup, "We should have entries for all encountered phrases"
del _LoadDynamicPhrasesFromFile


# ----------------------------------------------------------------------
def Lex(
    fully_qualified_names: List[str],
    source_roots: List[str],
    *,
    max_num_threads: Optional[int]=None,
):
    return LexImpl(
        Grammars,
        GrammarPhraseLookup,
        fully_qualified_names,
        source_roots,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
def Prune(
    roots: Dict[str, RootNode],
    *,
    max_num_threads: Optional[int]=None,
):
    return PruneImpl(
        roots,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
def Parse(
    roots: Dict[str, RootNode],
    *,
    max_num_threads: Optional[int]=None,
):
    return ParseImpl(
        Grammars,
        GrammarPhraseLookup,
        roots,
        max_num_threads=max_num_threads,
    )
