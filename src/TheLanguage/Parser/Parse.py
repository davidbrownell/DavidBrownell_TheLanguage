# ----------------------------------------------------------------------
# |
# |  Parse.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 14:22:22
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that parses content"""

import asyncio
import os
import importlib
import sys

from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable, cast, Callable, Dict, List, Optional, Set, Union

from semantic_version import Version as SemVer

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Components.ThreadPool import CreateThreadPool

    # TODO: Consider adding if functionality for targets and configuration similar to the Syntax decorator
    from .Syntax import Observer as SyntaxObserver

    from .TranslationUnitsParser import (
        DynamicPhrasesInfo,
        Leaf,
        Node,
        Observer as TranslationUnitsObserver,
        ParseAsync as TranslationUnitsParseAsync,
        Phrase,
        RootNode,
    )

    from ..Grammars.GrammarPhrase import GrammarPhrase, ImportGrammarStatement


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
Grammars[SemVer("0.0.1")]                   = _LoadDynamicPhrasesFromFile(os.path.join(_script_dir, "..", "Grammars", "v0_0_1", "All.py"))


# ----------------------------------------------------------------------
assert GrammarPhraseLookup, "We should have entries for all encountered phrases"
del _LoadDynamicPhrasesFromFile


# ----------------------------------------------------------------------
def Parse(
    fully_qualified_names: List[str],
    source_roots: List[str],
    max_num_threads: Optional[int]=None,
) -> Union[
    None,                                   # Cancellation
    Dict[str, RootNode],                    # Successful results
    List[Exception],                        # Errors
]:
    """\
    Return AST(s) for the given names.

    This information can be used to complete regenerate the original source (which can be valuable for
    writing things like source formatting tools). However, it contains extraneous data that can make
    parsing more difficult (for example, ignored tokens that comments and whitespace remain in the AST).

    The 'Prune' function should be used on the successful result of this function before further
    processing is invoked.
    """

    syntax_observer = SyntaxObserver(
        _ParseObserver(
            source_roots,
            max_num_threads=max_num_threads,
        ),
        Grammars,
    )

    return asyncio.get_event_loop().run_until_complete(
        TranslationUnitsParseAsync(
            fully_qualified_names,
            syntax_observer.Syntaxes[syntax_observer.DefaultVersion],
            syntax_observer,
            single_threaded=max_num_threads == 1,
        ),
    )


# ----------------------------------------------------------------------
def Prune(
    roots: Dict[str, RootNode],
    max_num_threads: Optional[int]=None,
):
    """Removes Leaf nodes that have been explicitly ignored (for easier parsing)"""

    _Execute(
        lambda fqn, node: _Prune(node),
        roots,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
def Validate(
    roots: Dict[str, RootNode],
    max_num_threads: Optional[int]=None,
):
    """Invokes functionality to validate a node and its children in isolation"""

    _Execute(
        _ValidateRoot,
        roots,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _ParseObserver(TranslationUnitsObserver):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        source_roots: List[str],
        max_num_threads: Optional[int]=None,
    ):
        for source_root in source_roots:
            assert os.path.isdir(source_root), source_root

        assert max_num_threads is None or max_num_threads > 0, max_num_threads

        self._is_cancelled                  = False
        self._source_roots                  = source_roots
        self._executor                      = CreateThreadPool(max_workers=max_num_threads)

    # ----------------------------------------------------------------------
    def Cancel(self):
        self._is_cancelled = True

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def LoadContent(
        fully_qualified_name: str,
    ) -> str:
        assert os.path.isfile(fully_qualified_name), fully_qualified_name

        with open(fully_qualified_name) as f:
            content = f.read()

        return content

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(
        self,
        func_infos: List[Phrase.EnqueueAsyncItemType],
    ) -> Awaitable[Any]:
        # pylint: disable=not-callable
        return self._executor.EnqueueAsync(func_infos)  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def ExtractDynamicPhrases(
        self,
        fully_qualified_name: str,
        node: RootNode,
    ) -> DynamicPhrasesInfo:
        # TODO

        # pylint: disable=too-many-function-args
        return DynamicPhrasesInfo([], [], [], [])

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    async def OnIndentAsync(
        fully_qualified_name: str,
        data_stack: List[Phrase.StandardParseResultData],
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Optional[DynamicPhrasesInfo]:
        # Nothing to do here
        return None

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    async def OnDedentAsync(
        fully_qualified_name: str,
        data_stack: List[Phrase.StandardParseResultData],
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> None:
        # Nothing to do here
        return None

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnPhraseCompleteAsync(
        self,
        fully_qualified_name: str,
        phrase: Phrase,
        node: Node,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Union[
        bool,                                           # True to continue processing, False to terminate
        DynamicPhrasesInfo,                             # Dynamic phases (if any) resulting from the parsed phrase
        TranslationUnitsObserver.ImportInfo,            # Import information (if any) resulting from the parsed phrase
    ]:
        try:
            grammar_phrase = GrammarPhraseLookup.get(phrase, None)
        except TypeError:
            grammar_phrase = None

        if grammar_phrase is not None:
            if isinstance(grammar_phrase, ImportGrammarStatement):
                return grammar_phrase.ProcessImportStatement(
                    self._source_roots,
                    fully_qualified_name,
                    node,
                )

        return not self._is_cancelled


# ----------------------------------------------------------------------
def _Execute(
    func: Callable[[str, RootNode], None],
    roots: Dict[str, RootNode],
    max_num_threads: Optional[int]=None,
):
    single_threaded = max_num_threads == 1 or len(roots) == 1

    if single_threaded:
        for k, v in roots.items():
            func(k, v)

    else:
        with ThreadPoolExecutor(
            max_workers=max_num_threads,
        ) as executor:
            futures = [
                executor.submit(lambda k=k, v=v: func(k, v))
                for k, v in roots.items()
            ]

            [future.result() for future in futures]


# ----------------------------------------------------------------------
def _Prune(
    node: Union[RootNode, Node],
):
    child_index = 0

    while child_index < len(node.Children):
        child = node.Children[child_index]

        should_delete = False

        if isinstance(child, Node):
            _Prune(child)

            if not child.Children:
                should_delete = True

        elif isinstance(child, Leaf):
            if child.IsIgnored:
                should_delete = True

        else:
            assert False, child  # pragma: no cover

        if not should_delete:
            child_index += 1
            continue

        del node.Children[child_index]


# ----------------------------------------------------------------------
def _ValidateRoot(
    fully_qualified_name: str,
    root: RootNode,
):
    try:
        funcs: List[Callable[[], None]] = []

        for child in root.Children:
            funcs += _ValidateNode(child)

        for func in reversed(funcs):
            func()

    except Exception as ex:
        if not hasattr(ex, "FullyQualifiedName"):
            object.__setattr__(ex, "FullyQualifiedName", fully_qualified_name)

        raise


# ----------------------------------------------------------------------
def _ValidateNode(
    node: Union[Leaf, Node],
) -> List[Callable[[], None]]:

    funcs: List[Callable[[], None]] = []

    if isinstance(node.Type, Phrase):
        grammar_phrase = GrammarPhraseLookup.get(node.Type, None)
        if grammar_phrase is not None:
            result = grammar_phrase.ExtractLexerInfo(cast(Node, node))
            if result is not None:
                assert isinstance(result, GrammarPhrase.ExtractLexerInfoResult), result

                if result.PostExtractFunc is not None:
                    funcs.append(result.PostExtractFunc)

                if not result.AllowChildTraversal:
                    return funcs

    for child in getattr(node, "Children", []):
        funcs += _ValidateNode(child)

    return funcs
