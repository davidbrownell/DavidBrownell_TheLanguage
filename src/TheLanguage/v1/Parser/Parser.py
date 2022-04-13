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
    from .Error import CreateError, Error, ErrorException, Region
    from .Phrase import Phrase, RootPhrase

    from ..Lexer.Lexer import AST, Phrase as LexerPhrase


# ----------------------------------------------------------------------
DuplicateDocInfoError                       = CreateError(
    "Documentation information has already been provided",
)


# ----------------------------------------------------------------------
class ParseObserver(Interface.Interface):
    # ----------------------------------------------------------------------
    ExtractParserPhraseReturnType           = Union[
        None,
        Phrase,
        List[Error],
        Callable[
            [],
            Union[
                Phrase,
                List[Error],
            ]
        ],
    ]

    @staticmethod
    @Interface.abstractmethod
    def ExtractParserPhrase(
        node: AST.Node,
    ) -> "ParseObserver.ExtractParserPhraseReturnType":
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    ExtractPotentialDocInfoReturnType       = Union[
        None,
        Tuple[Union[AST.Leaf, AST.Node], str],
        List[Error],
    ]

    @staticmethod
    @Interface.abstractmethod
    def ExtractPotentialDocInfo(
        node: Union[AST.Leaf, AST.Node],
    ) -> "ParseObserver.ExtractPotentialDocInfoReturnType":
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
def Parse(
    roots: Dict[str, AST.Node],
    observer: ParseObserver,
    *,
    max_num_threads: Optional[int]=None,
) -> Optional[
    Dict[str, Union[RootPhrase, List[Error]]]
]:
    # ----------------------------------------------------------------------
    def CreateAndExtract(
        fully_qualified_name: str,  # pylint: disable=unused-argument
        root: AST.Node,
    ) -> Optional[Union[RootPhrase, List[Error]]]:
        errors: List[Error] = []

        callback_funcs: List[Tuple[AST.Node, Callable[[], Any]]] = []

        for node in root.Enum(nodes_only=True):
            assert isinstance(node, AST.Node), node

            try:
                result = observer.ExtractParserPhrase(node)

                if result is None:
                    continue
                elif callable(result):
                    callback_funcs.append((node, result))
                elif isinstance(result, list):
                    errors += result
                elif isinstance(result, Phrase):
                    _SetPhrase(node, result)
                else:
                    assert False, result  # pragma: no cover

            except ErrorException as ex:
                errors += ex.errors

        for node, callback in reversed(callback_funcs):
            try:
                result = callback()

                if isinstance(result, list):
                    errors += result
                elif isinstance(result, Phrase):
                    _SetPhrase(node, result)
                else:
                    assert False, result  # pragma: no cover

            except ErrorException as ex:
                errors += ex.errors

        # Extract the root information
        existing_doc_info: Optional[Tuple[Union[AST.Leaf, AST.Node], str]] = None
        statements: List[Phrase] = []

        for child in root.children:
            try:
                result = observer.ExtractPotentialDocInfo(child)

                if result is not None:
                    if isinstance(result, list):
                        errors += result
                    elif isinstance(result, tuple):
                        if existing_doc_info is not None:
                            errors.append(
                                DuplicateDocInfoError(
                                    region=CreateRegion(result[0]),
                                ),
                            )
                        else:
                            existing_doc_info = result
                    else:
                        assert False, result  # pragma: no cover

            except ErrorException as ex:
                errors += ex.errors

            if isinstance(child, AST.Node):
                phrase = _ExtractPhrase(child)
                if phrase is not None:
                    statements.append(phrase)

        if errors:
            return errors

        if existing_doc_info is None:
            docstring_node = None
            docstring_info = None
        else:
            docstring_node, docstring_info = existing_doc_info

        try:
            return RootPhrase.Create(
                CreateRegions(root, root, docstring_node),
                statements or None,
                docstring_info,
            )
        except ErrorException as ex:
            return ex.errors

    # ----------------------------------------------------------------------

    return _Execute(
        roots,
        CreateAndExtract,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
def Validate(
    roots: Dict[str, RootPhrase],
    *,
    max_num_threads: Optional[int]=None,
) -> Optional[
    Dict[str, Union[RootPhrase, List[Error]]]
]:
    return roots  # type: ignore

    # TODO: # Extract names
    # TODO:
    # TODO: # ----------------------------------------------------------------------
    # TODO: def ValidateNames(
    # TODO:     fully_qualified_name: str,  # pylint: disable=unused-argument
    # TODO:     root: RootPhrase,
    # TODO: ) -> _NamespaceVisitor.ReturnType:
    # TODO:     visitor = _NamespaceVisitor()
    # TODO:
    # TODO:     root.Accept(visitor)
    # TODO:
    # TODO:     return visitor.root
    # TODO:
    # TODO: # ----------------------------------------------------------------------
    # TODO:
    # TODO: namespace_values = _Execute(
    # TODO:     roots,
    # TODO:     ValidateNames,
    # TODO:     max_num_threads=max_num_threads,
    # TODO: )
    # TODO:
    # TODO: if namespace_values is None:
    # TODO:     return None
    # TODO:
    # TODO: if any(diagnostics.errors for (_, diagnostics) in roots.values()):
    # TODO:     return roots
    # TODO:
    # TODO: # TODO: Validate types
    # TODO:
    # TODO: return roots


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
        return Region.Create(node.begin.ToLocation(), node.end.ToLocation())
    elif isinstance(node, (AST.Leaf, AST.Node)):
        if node.iter_range is None:
            return None

        return Region.Create(node.iter_range.begin.ToLocation(), node.iter_range.end.ToLocation())
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
    def __init__(self):
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
