# ----------------------------------------------------------------------
# |
# |  AllGrammars.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-29 09:02:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Loads all the Grammars"""

import importlib
import os
import sys
import threading

from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Grammars.GrammarInfo import (
        AST,
        DynamicPhrasesInfo,
        DynamicPhrasesType,
        GetParentStatementNode as GetParentStatementNodeImpl,
        GrammarPhrase,
        ImportGrammarPhrase,
        Phrase,
    )

    from .Lexer.Lexer import (
        Lex as LexImpl,
        LexObserver,
        Prune as PruneImpl,
    )

    from .Lexer.SyntaxObserverDecorator import (
        Configurations,
        RegexToken,
        SemVer,
        TranslationUnitsLexerObserver,
    )

    from .Parser.Parser import (
        Parse as ParseImpl,
        ParserInfo,
        RootParserInfo,
        Verify as VerifyImpl,
    )

    from .Targets.Target import Target


# ----------------------------------------------------------------------
Grammars: Dict[SemVer, DynamicPhrasesInfo]              = OrderedDict()
GrammarPhraseLookup: Dict[Phrase, GrammarPhrase]        = OrderedDict()
GrammarCommentToken: Optional[RegexToken]               = None


# ----------------------------------------------------------------------
def _LoadDynamicContentFromFile(
    filename: str,
    module_comment_attribute_name: Optional[str]=None,
    module_phrases_attribute_name: Optional[str]=None,
) -> DynamicPhrasesInfo:
    global GrammarCommentToken

    assert os.path.isfile(filename), filename

    dirname, basename = os.path.split(filename)
    basename = os.path.splitext(basename)[0]

    sys.path.insert(0, dirname)
    with CallOnExit(lambda: sys.path.pop(0)):
        mod = importlib.import_module(basename)

        # Get the comment token
        grammar_comment = getattr(mod, module_comment_attribute_name or "GrammarCommentToken", None)
        assert grammar_comment is not None

        assert GrammarCommentToken is None or grammar_comment.Regex.pattern == GrammarCommentToken.Regex.pattern, (grammar_comment.Regex.patter, GrammarCommentToken.Regex.pattern)
        GrammarCommentToken = grammar_comment

        # Get the phrases
        grammar_phrases = getattr(mod, module_phrases_attribute_name or "GrammarPhrases", None)
        assert grammar_phrases is not None

        # Organize the phrases
        name_lookup: Set[str] = set()
        dynamic_phrases: Dict[DynamicPhrasesType, List[Phrase]] = {}

        for grammar_phrase in grammar_phrases:
            # Ensure that phrase names are unique
            assert grammar_phrase.Phrase.Name not in name_lookup, grammar_phrase.Phrase.Name
            name_lookup.add(grammar_phrase.Phrase.Name)

            # Add the phrase
            dynamic_phrases.setdefault(grammar_phrase.Type, []).append(grammar_phrase.Phrase)

            # Add the phrase lookup
            assert grammar_phrase.Phrase not in GrammarPhraseLookup, grammar_phrase.Phrase
            GrammarPhraseLookup[grammar_phrase.Phrase] = grammar_phrase

        del sys.modules[basename]

        # pylint: disable=too-many-function-args
        return DynamicPhrasesInfo(
            dynamic_phrases,
            AllowParentTraversal=False,
        )


# ----------------------------------------------------------------------
Grammars[SemVer("0.0.1")]                   = _LoadDynamicContentFromFile(os.path.join(_script_dir, "Grammars", "v0_0_1", "All.py"))


# ----------------------------------------------------------------------
assert Grammars
assert GrammarPhraseLookup
assert GrammarCommentToken is not None

del _LoadDynamicContentFromFile

# TODO: Right now, much of the functionality is concerned with processing the dicts. Remove that functionality
#       from those files and only do it here.


# ----------------------------------------------------------------------
def Lex(
    cancellation_event: threading.Event,
    configuration: Configurations,
    target: str,
    fully_qualified_names: List[str],
    source_roots: List[str],
    *,
    default_grammar: Optional[SemVer]=None,
    max_num_threads: Optional[int]=None,
) -> Union[
    None,                                   # Cancellation
    Dict[str, AST.Node],                    # Successful results
    List[Exception],                        # Errors
]:
    # ----------------------------------------------------------------------
    @Interface.staticderived
    class Observer(LexObserver):
        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        def OnPhraseComplete(
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
            try:
                grammar_phrase = GrammarPhraseLookup.get(phrase, None)
            except TypeError:
                grammar_phrase = None

            if grammar_phrase is not None:
                if isinstance(grammar_phrase, ImportGrammarPhrase):
                    return grammar_phrase.ProcessImportNode(
                        source_roots,
                        fully_qualified_name,
                        node,
                    )

                result = grammar_phrase.GetDynamicContent(node)

                # TODO: Process result

            return not cancellation_event.is_set()

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        def GetParentStatementNode(
            node: AST.Node,
        ) -> Optional[AST.Node]:
            return GetParentStatementNodeImpl(node)

    # ----------------------------------------------------------------------

    assert GrammarCommentToken is not None

    return LexImpl(
        GrammarCommentToken,
        Grammars,
        configuration,
        target,
        fully_qualified_names,
        source_roots,
        Observer(),
        default_grammar=default_grammar,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
def Prune(
    roots: Dict[str, AST.Node],
    *,
    max_num_threads: Optional[int]=None,
) -> None:
    return PruneImpl(
        roots,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
def Parse(
    cancellation_event: threading.Event,
    roots: Dict[str, AST.Node],
    *,
    max_num_threads: Optional[int]=None,
) -> Union[
    None,
    Dict[str, RootParserInfo],
    List[Exception],
]:
    # ----------------------------------------------------------------------
    def CreateParserInfo(
        node: AST.Node,
    ) -> Union[
        None,
        bool,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        if isinstance(node.Type, Phrase):
            grammar_phrase = GrammarPhraseLookup.get(node.Type, None)
            if grammar_phrase is not None:
                return grammar_phrase.ExtractParserInfo(node)

        if cancellation_event.is_set():
            return False

        return None

    # ----------------------------------------------------------------------

    return ParseImpl(
        roots,
        CreateParserInfo,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
def Validate(
    cancellation_event: threading.Event,
    roots: Dict[str, RootParserInfo],
    *,
    max_num_threads: Optional[int]=None,
) -> Union[
    None,
    Dict[str, RootParserInfo],
    List[Exception],
]:
    # ----------------------------------------------------------------------
    def Invoke(
        fully_qualified_name: str,
        root: RootParserInfo,
    ):
        pass # TODO

    # ----------------------------------------------------------------------

    return _Execute(
        Invoke,
        cancellation_event,
        roots,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
def InvokeTarget(
    cancellation_event: threading.Event,
    roots: Dict[str, RootParserInfo],
    target: Target,
    *,
    max_num_threads: Optional[int]=None,
) -> Union[
    None,
    Dict[str, RootParserInfo],
    List[Exception],
]:
    # ----------------------------------------------------------------------
    def Invoke(
        fully_qualified_name: str,
        root: RootParserInfo,
    ):
        target.Invoke(fully_qualified_name, root)

    # ----------------------------------------------------------------------

    return _Execute(
        Invoke,
        cancellation_event,
        roots,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Execute(
    on_root_parser_info_func: Callable[[str, RootParserInfo], None],
    cancellation_event: threading.Event,
    roots: Dict[str, RootParserInfo],
    *,
    max_num_threads: Optional[int]=None,
) -> Union[
    None,
    Dict[str, RootParserInfo],
    List[Exception],
]:
    single_threaded = max_num_threads == 1 or len(roots) == 1

    errors: List[Exception] = []

    # ----------------------------------------------------------------------
    def Impl(
        fully_qualified_name: str,
        root: RootParserInfo,
    ) -> bool:
        if cancellation_event.is_set():
            return False

        try:
            result = on_root_parser_info_func(fully_qualified_name, root)
            if result is not None:
                assert isinstance(result, RootParserInfo), result
                roots[fully_qualified_name] = result

        except Exception as ex:
            if not hasattr(ex, "FullyQualifiedName"):
                object.__setattr__(ex, "FullyQualifiedName", fully_qualified_name)

            errors.append(ex)

        return True

    # ----------------------------------------------------------------------

    if single_threaded:
        for k, v in roots.items():
            if not Impl(k, v):
                return None

    else:
        with ThreadPoolExecutor(
            max_workers=max_num_threads,
        ) as executor:
            futures = [
                executor.submit(Impl, k, v)
                for k, v in roots.items()
            ]

            return_none = False

            for future in futures:
                if future.result() is False:
                    return_none = True

            if return_none:
                return None

    if errors:
        return errors

    return roots