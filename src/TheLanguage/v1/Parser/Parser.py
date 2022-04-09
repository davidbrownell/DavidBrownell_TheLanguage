# ----------------------------------------------------------------------
# |
# |  Parser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 12:49:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Creates and extracts parser information from nodes"""

import os
import traceback

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, cast, Dict, List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Diagnostics import CreateError, Diagnostics, DiagnosticsError
    from .Phrase import Phrase, Region, RootPhrase

    from ..Lexer.Lexer import AST, Phrase as LexerPhrase


# ----------------------------------------------------------------------
DuplicateDocInfoError                       = CreateError(
    "Documentation information has already been provided",
)


# ----------------------------------------------------------------------
class ParseObserver(Interface.Interface):
    # ----------------------------------------------------------------------
    CreateParserPhraseReturnType            = Union[
        bool,
        Phrase,
        Tuple[Phrase, Diagnostics],
        Tuple[Phrase, Callable[[], Optional[Diagnostics]]],
        Tuple[Phrase, Diagnostics, Callable[[], Optional[Diagnostics]]],
    ]

    @staticmethod
    @Interface.abstractmethod
    def CreateParserPhrase(
        node: AST.Node,
    ) -> "ParseObserver.CreateParserPhraseReturnType":
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def GetPotentialDocInfo(
        node: Union[AST.Leaf, AST.Node],
    ) -> Optional[Tuple[AST.Leaf, str]]:
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
def Parse(
    roots: Dict[str, AST.Node],
    observer: ParseObserver,
    *,
    max_num_threads: Optional[int]=None,
) -> Optional[
    Dict[
        str,
        Tuple[RootPhrase, Diagnostics]
    ]
]:
    single_threaded = max_num_threads == 1 or len(roots) == 1

    # ----------------------------------------------------------------------
    def CreateAndExtract(
        fully_qualified_name: str,
        root: AST.Node,
    ) -> Optional[Tuple[RootPhrase, Diagnostics]]:
        try:
            diagnostics = Diagnostics()

            callback_funcs: List[Tuple[AST.Node, Callable[[], Any]]] = []

            for node in root.Enum(nodes_only=True):
                assert isinstance(node, AST.Node), node

                result = observer.CreateParserPhrase(node)

                this_phrase: Optional[Phrase] = None
                this_diagnostics: Optional[Diagnostics] = None
                this_callback: Optional[Callable[[], Any]] = None

                if isinstance(result, bool):
                    if not result:
                        return None

                    continue

                if isinstance(result, Phrase):
                    this_phrase = result

                if isinstance(result, tuple):
                    if len(result) == 2:
                        this_phrase = result[0]

                        if isinstance(result[1], Diagnostics):
                            this_diagnostics = result[1]
                        elif callable(result[1]):
                            this_callback = result[1]
                        else:
                            assert False, result  # pragma: no cover

                    elif len(result) == 3:
                        this_phrase, this_diagnostics, this_callback = result

                    else:
                        assert False, result  # pragma: no cover

                assert this_phrase is not None
                _SetPhrase(node, this_phrase)

                if this_diagnostics is not None:
                    diagnostics = diagnostics.Combine(this_diagnostics)

                if this_callback is not None:
                    callback_funcs.append((node, this_callback))

            for node, callback in reversed(callback_funcs):
                potential_diagnostics = callback()
                if potential_diagnostics is not None:
                    diagnostics.Combine(potential_diagnostics)

            # Extract the root information
            doc_info: Optional[Tuple[AST.Leaf, str]] = None
            statements: List[Phrase] = []

            for child in root.children:
                potential_doc_info = observer.GetPotentialDocInfo(child)
                if potential_doc_info is not None:
                    if doc_info is not None:
                        diagnostics = diagnostics.Combine(
                            Diagnostics(
                                errors=[
                                    DuplicateDocInfoError.Create(
                                        CreateRegions(potential_doc_info[0]),
                                    ),
                                ],
                            ),
                        )
                    else:
                        doc_info = potential_doc_info

                    continue

                if isinstance(child, AST.Node):
                    phrase = _ExtractPhrase(child)
                    if phrase is None:
                        continue

                    statements.append(phrase)

            return (
                RootPhrase.Create(
                    CreateRegions(root, root, None if doc_info is None else doc_info[0]),
                    statements or None,
                    None if doc_info is None else doc_info[1],
                ),
                diagnostics,
            )

        except Exception as ex:
            if not hasattr(ex, "fully_qualified_name"):
                object.__setattr__(ex, "full_qualified_name", fully_qualified_name)

            if not hasattr(ex, "traceback"):
                object.__setattr__(ex, "traceback", traceback.format_exc())

            raise

    # ----------------------------------------------------------------------

    results: List[Optional[Tuple[RootPhrase, Diagnostics]]] = []

    if single_threaded:
        for k, v in roots.items():
            results.append(CreateAndExtract(k, v))

    else:
        with ThreadPoolExecutor(
            max_workers=max_num_threads,
        ) as executor:
            futures = [
                executor.submit(CreateAndExtract, k, v)
                for k, v in roots.items()
            ]

            for future in futures:
                results.append(future.result())

    if any(result is None for result in results):
        return None

    return {
        fully_qualified_name: cast(Tuple[RootPhrase, Diagnostics], result)
        for fully_qualified_name, result in zip(roots.keys(), results)
    }


# ----------------------------------------------------------------------
def GetPhraseNoThrow(
    node: AST.Node,
) -> Optional[Phrase]:
    return  getattr(node, _PHRASE_ATTRIBUTE_NAME, None)


# ----------------------------------------------------------------------
def GetPhrase(
    node: AST.Node,
) -> Phrase:
    result = GetPhraseNoThrow(node)
    assert result is not None

    return result


# ----------------------------------------------------------------------
def CreateRegions(
    *nodes: Union[
        AST.Leaf,
        AST.Node,
        Region,
        LexerPhrase.NormalizedIteratorRange,
        None,
    ],
) -> List[Optional[Region]]:
    results: List[Optional[Region]] = []

    for node in nodes:
        if node is None:
            results.append(None)
        elif isinstance(node, Region):
            results.append(node)
        elif isinstance(node, LexerPhrase.NormalizedIteratorRange):
            results.append(node.ToRegion())
        elif isinstance(node, (AST.Leaf, AST.Node)):
            if node.iter_range is None:
                results.append(None)
            else:
                results.append(node.iter_range.ToRegion())
        else:
            assert False, node  # pragma: no cover

    return results


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
_PHRASE_ATTRIBUTE_NAME                      = "parser_phrase"


# ----------------------------------------------------------------------
def _SetPhrase(
    node: AST.Node,
    phrase: Phrase,
) -> None:
    object.__setattr__(node, _PHRASE_ATTRIBUTE_NAME, phrase)


# ----------------------------------------------------------------------
def _ExtractPhrase(
    node: AST.Node,
) -> Optional[Phrase]:
    phrase = GetPhraseNoThrow(node)
    if phrase is not None:
        return phrase

    child_phrases: List[Phrase] = []

    for child in node.children:
        if isinstance(child, AST.Leaf):
            continue

        child_phrase = _ExtractPhrase(child)
        if child_phrase is not None:
            child_phrases.append(child_phrase)

    if not child_phrases:
        return None

    assert len(child_phrases) == 1, child_phrases
    return child_phrases[0]
