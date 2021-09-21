# ----------------------------------------------------------------------
# |
# |  Parse.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-20 21:06:37
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

import os

from concurrent.futures import ThreadPoolExecutor
from typing import cast, Callable, Dict, List, Optional, Union

from semantic_version import Version as SemVer

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Grammars.GrammarPhrase import GrammarPhrase
    from ..Lexer.TranslationUnitsLexer import (
        DynamicPhrasesInfo,
        Leaf,
        Node,
        Phrase,
        RootNode,
    )


# ----------------------------------------------------------------------
def Parse(
    grammars: Dict[SemVer, DynamicPhrasesInfo],
    grammar_phrase_lookup: Dict[Phrase, GrammarPhrase],
    roots: Dict[str, RootNode],
    *,
    max_num_threads: Optional[int]=None,
):
    validator = _Validator(grammars, grammar_phrase_lookup)

    single_threaded = max_num_threads == 1 or len(roots) == 1

    if single_threaded:
        for k, v in roots.items():
            validator.ValidateRoot(k, v)

    else:
        with ThreadPoolExecutor(
            max_workers=max_num_threads,
        ) as executor:
            futures = [
                executor.submit(lambda k=k, v=v: validator.ValidateRoot(k, v))
                for k, v in roots.items()
            ]

            [future.result() for future in futures]


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _Validator(object):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        grammars: Dict[SemVer, DynamicPhrasesInfo],
        grammar_phrase_lookup: Dict[Phrase, GrammarPhrase],
    ):
        self._grammars                      = grammars
        self._grammar_phase_lookup          = grammar_phrase_lookup

    # ----------------------------------------------------------------------
    def ValidateRoot(
        self,
        fully_qualified_name: str,
        root: RootNode,
    ):
        try:
            funcs: List[Callable[[], None]] = []

            for child in root.Children:
                funcs += self.ValidateNode(child)

            for func in reversed(funcs):
                func()

        except Exception as ex:
            if not hasattr(ex, "FullyQualifiedName"):
                object.__setattr__(ex, "FullyQualifiedName", fully_qualified_name)

            raise

    # ----------------------------------------------------------------------
    def ValidateNode(
        self,
        node: Union[Leaf, Node],
    ) -> List[Callable[[], None]]:

        funcs: List[Callable[[], None]] = []

        if isinstance(node.Type, Phrase):
            grammar_phrase = self._grammar_phase_lookup.get(node.Type, None)
            if grammar_phrase is not None:
                result = grammar_phrase.ExtractParserInfo(cast(Node, node))
                if result is not None:
                    assert isinstance(result, GrammarPhrase.ExtractParserInfoResult), result

                    if result.PostExtractFunc is not None:
                        funcs.append(result.PostExtractFunc)

                    if not result.AllowChildTraversal:
                        return funcs

        for child in getattr(node, "Children", []):
            funcs += self.ValidateNode(child)

        return funcs
