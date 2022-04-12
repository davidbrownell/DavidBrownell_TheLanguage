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
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Phrase import Phrase, Region, RootPhrase

    from ..Common.Diagnostics import CreateError, Diagnostics
    from ..Lexer.Lexer import AST, Phrase as LexerPhrase


# ----------------------------------------------------------------------
DuplicateDocInfoError                       = CreateError(
    "Documentation information has already been provided",
)


# ----------------------------------------------------------------------
class ParseObserver(Interface.Interface):
    # ----------------------------------------------------------------------
    ExtractParserPhraseReturnType           = Union[
        Phrase,
        Diagnostics,
        Tuple[Phrase, Diagnostics],
        Callable[[], Phrase],
        Callable[[], Diagnostics],
        Callable[[], Tuple[Phrase, Diagnostics]],
    ]

    @staticmethod
    @Interface.abstractmethod
    def ExtractParserPhrase(
        node: AST.Node,
    ) -> "ParseObserver.ExtractParserPhraseReturnType":
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
        Tuple[RootPhrase, Diagnostics],
    ]
]:
    # ----------------------------------------------------------------------
    def CreateAndExtract(
        fully_qualified_name: str,  # pylint: disable=unused-argument
        root: AST.Node,
    ) -> Optional[Tuple[RootPhrase, Diagnostics]]:
        diagnostics = Diagnostics()

        callback_funcs: List[Tuple[AST.Node, Callable[[], Any]]] = []

        for node in root.Enum(nodes_only=True):
            assert isinstance(node, AST.Node), node

            result = observer.ExtractParserPhrase(node)
            if result is None:
                continue

            if callable(result):
                callback_funcs.append((node, result))
                continue

            if isinstance(result, Diagnostics):
                assert result.errors, result
                diagnostics = diagnostics.Combine(result)

                continue

            this_phrase: Optional[Phrase] = None

            if isinstance(result, tuple):
                assert len(result) == 2, result

                this_phrase, this_diagnostics = result

                assert not this_diagnostics.errors, this_diagnostics
                diagnostics = diagnostics.Combine(this_diagnostics)

            elif isinstance(result, Phrase):
                this_phrase = result

            else:
                assert False, result  # pragma: no cover

            assert this_phrase is not None
            _SetPhrase(node, this_phrase)

        for node, callback in reversed(callback_funcs):
            result = callback()

            if isinstance(result, Diagnostics):
                assert result.errors, result
                diagnostics = diagnostics.Combine(result)

                continue

            this_phrase: Optional[Phrase] = None

            if isinstance(result, tuple):
                assert len(result) == 2, result

                this_phrase, this_diagnostics = result

                assert not this_diagnostics.errors, this_diagnostics
                diagnostics = diagnostics.Combine(this_diagnostics)

            elif isinstance(result, Phrase):
                this_phrase = result

            else:
                assert False, result  # pragma: no cover

            assert this_phrase is not None
            _SetPhrase(node, this_phrase)

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

    # ----------------------------------------------------------------------

    return _Execute(
        roots,
        CreateAndExtract,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
def Validate(
    roots: Dict[str, Tuple[RootPhrase, Diagnostics]],
    *,
    max_num_threads: Optional[int]=None,
) -> Optional[Dict[str, Tuple[RootPhrase, Diagnostics]]]:
    # Extract names

    # ----------------------------------------------------------------------
    def ValidateNames(
        fully_qualified_name: str,  # pylint: disable=unused-argument
        input_value: Tuple[RootPhrase, Diagnostics],
    ) -> _NamespaceVisitor.ReturnType:
        root, diagnostics = input_value

        visitor = _NamespaceVisitor(diagnostics)

        root.Accept(visitor)

        return visitor.root

    # ----------------------------------------------------------------------

    namespace_values = _Execute(
        roots,
        ValidateNames,
        max_num_threads=max_num_threads,
    )

    if namespace_values is None:
        return None

    if any(diagnostics.errors for (_, diagnostics) in roots.values()):
        return roots

    # TODO: Validate types

    return roots


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
def CreateRegionNoThrow(
    node: Union[
        None,
        Region,
        LexerPhrase.NormalizedIteratorRange,
        AST.Leaf,
        AST.Node,
    ],
) -> Optional[Region]:
    if node is None:
        return None
    elif isinstance(node, Region):
        return node
    elif isinstance(node, LexerPhrase.NormalizedIteratorRange):
        return node.ToRegion()
    elif isinstance(node, (AST.Leaf, AST.Node)):
        if node.iter_range is None:
            return None

        return node.iter_range.ToRegion()
    else:
        assert False, node  # pragma: no cover


# ----------------------------------------------------------------------
def CreateRegion(
    node: Any,
) -> Region:
    result = CreateRegionNoThrow(node)
    assert result is not None

    return result


# ----------------------------------------------------------------------
def CreateRegions(
    *nodes: Any,
) -> List[Optional[Region]]:
    return [CreateRegionNoThrow(node) for node in nodes]


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


# ----------------------------------------------------------------------
_ExecuteInputType                           = TypeVar("_ExecuteInputType")
_ExecuteOutputType                          = TypeVar("_ExecuteOutputType")


def _Execute(
    inputs: Dict[str, _ExecuteInputType],
    execute_func: Callable[[str, _ExecuteInputType], Optional[_ExecuteOutputType]],
    *,
    max_num_threads: Optional[int]=None,
) -> Optional[Dict[str, _ExecuteOutputType]]:
    # ----------------------------------------------------------------------
    def Execute(
        fully_qualified_name: str,
        input_value: _ExecuteInputType,
    ) -> Optional[_ExecuteOutputType]:
        try:
            return execute_func(fully_qualified_name, input_value)
        except Exception as ex:
            if not hasattr(ex, "fully_qualified_name"):
                object.__setattr__(ex, "full_qualified_name", fully_qualified_name)

            if not hasattr(ex, "traceback"):
                object.__setattr__(ex, "traceback", traceback.format_exc())

            raise

    # ----------------------------------------------------------------------

    results: List[_ExecuteOutputType] = []

    if max_num_threads == 1 or len(inputs) == 1:
        for k, v in inputs.items():
            result = Execute(k, v)
            if result is None:
                return None

            results.append(result)

    else:
        with ThreadPoolExecutor(
            max_workers=max_num_threads,
        ) as executor:
            futures = [
                executor.submit(Execute, k, v)
                for k, v in inputs.items()
            ]

            for future in futures:
                result = future.result()
                if result is None:
                    return None

                results.append(result)

    return {
        fully_qualified_name: result
        for fully_qualified_name, result in zip(inputs.keys(), results)
    }


# ----------------------------------------------------------------------
class _NamespaceVisitor(object):
    # ----------------------------------------------------------------------
    # |  Public Types
    class Node(ObjectReprImplBase):
        # ----------------------------------------------------------------------
        def __init__(
            self,
            phrase: Optional[Phrase],
        ):
            self.phrase                                                     = phrase
            self.namespaces: Dict[str, List["_NamespaceVisitor.Node"]]      = {}
            self.unnamed: List["_NamespaceVisitor.Node"]                    = []

            super(_NamespaceVisitor.Node, self).__init__()

    # ----------------------------------------------------------------------
    ReturnType                              = Dict[str, List["_NamespaceVisitor.Node"]]

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __init__(
        self,
        diagnostics: Diagnostics,
    ):
        self._diagnostics                               = diagnostics
        self._node_stack: List[_NamespaceVisitor.Node]  = [_NamespaceVisitor.Node(None)]

    # ----------------------------------------------------------------------
    @property
    def root(self) -> "_NamespaceVisitor.ReturnType":
        assert len(self._node_stack) == 1, self._node_stack
        assert self._node_stack[0].phrase is None, self._node_stack[0]

        return self._node_stack[0].namespaces

    # ----------------------------------------------------------------------
    def OnEnterScope(
        self,
        phrase: Phrase,
    ) -> None:
        assert phrase.introduces_scope__, phrase

        new_node = _NamespaceVisitor.Node(phrase)

        name = getattr(phrase, "name", None)
        if name is not None:
            self._node_stack[-1].namespaces.setdefault(name, []).append(new_node)
        else:
            self._node_stack[-1].unnamed.append(new_node)

        self._node_stack.append(new_node)

    # ----------------------------------------------------------------------
    def OnExitScope(
        self,
        phrase: Phrase,
    ) -> None:
        assert phrase.introduces_scope__, phrase

        assert self._node_stack, phrase
        self._node_stack.pop()
        assert self._node_stack, phrase

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        attribute: str,
    ) -> Callable[[Phrase], None]:
        return self._NoopMethod

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _NoopMethod(*args, **kwargs):
        return None

    # TODO: ClassStatement
    # TODO: Aliases
    # TODO: Compile-time statements populate parent namespace
