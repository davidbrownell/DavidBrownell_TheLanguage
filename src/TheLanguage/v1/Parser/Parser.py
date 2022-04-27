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
    from .ParserInfos.ParserInfo import ParserInfo, RootParserInfo
    from ..Lexer.Lexer import AST, Phrase as LexPhrase


# ----------------------------------------------------------------------
DuplicateDocInfoError                       = CreateError(
    "Documentation information has already been provided",
)


# ----------------------------------------------------------------------
class ParseObserver(Interface.Interface):
    # ----------------------------------------------------------------------
    ExtractParserInfoReturnType             = Union[
        None,
        ParserInfo,
        List[Error],
        Callable[
            [],
            Union[
                ParserInfo,
                List[Error],
            ]
        ],
    ]

    @staticmethod
    @Interface.abstractmethod
    def ExtractParserInfo(
        node: AST.Node,
    ) -> "ParseObserver.ExtractParserInfoReturnType":
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
    Dict[str, Union[RootParserInfo, List[Error]]]
]:
    # ----------------------------------------------------------------------
    def CreateAndExtract(
        fully_qualified_name: str,  # pylint: disable=unused-argument
        root: AST.Node,
    ) -> Optional[Union[RootParserInfo, List[Error]]]:
        errors: List[Error] = []

        callback_funcs: List[Tuple[AST.Node, Callable[[], Any]]] = []

        for node in root.Enum(nodes_only=True):
            assert isinstance(node, AST.Node), node

            try:
                result = observer.ExtractParserInfo(node)

                if result is None:
                    continue

                elif callable(result):
                    callback_funcs.append((node, result))

                elif isinstance(result, list):
                    _SetParserInfoErrors(node)
                    errors += result

                elif isinstance(result, ParserInfo):
                    _SetParserInfo(node, result)

                else:
                    assert False, result  # pragma: no cover

            except ErrorException as ex:
                errors += ex.errors

        for node, callback in reversed(callback_funcs):
            try:
                result = callback()

                if isinstance(result, list):
                    _SetParserInfoErrors(node)
                    errors += result

                elif isinstance(result, ParserInfo):
                    _SetParserInfo(node, result)

                else:
                    assert False, result  # pragma: no cover

            except ErrorException as ex:
                errors += ex.errors

        # Extract the root information
        existing_doc_info: Optional[Tuple[Union[AST.Leaf, AST.Node], str]] = None
        statements: List[ParserInfo] = []

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
                parser_info = _ExtractParserInfo(child)
                if parser_info is not None:
                    statements.append(parser_info)

        if errors:
            return errors

        if existing_doc_info is None:
            docstring_node = None
            docstring_info = None
        else:
            docstring_node, docstring_info = existing_doc_info

        try:
            if not statements:
                statements_node = None
                statements = None  # type: ignore
            else:
                statements_node = root

            return RootParserInfo.Create(
                CreateRegions(root, statements_node, docstring_node),
                statements,
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
# TODO: Deferred types
def Validate(
    roots: Dict[str, RootParserInfo],
    *,
    max_num_threads: Optional[int]=None,
) -> Optional[
    Dict[str, Union[RootParserInfo, List[Error]]]
]:
    # Extract names

    # ----------------------------------------------------------------------
    def ExtractNamespaces(
        fully_qualified_name: str,  # pylint: disable=unused-argument
        root: RootParserInfo,
    ) -> _NamespaceVisitor.ReturnType:
        visitor = _NamespaceVisitor()

        root.Accept(visitor)

        result = visitor.root
        return result

    # ----------------------------------------------------------------------

    namespace_values = _Execute(
        roots,
        ExtractNamespaces,
        max_num_threads=max_num_threads,
    )

    if namespace_values is None:
        return None

    # TODO: Validate types

    return roots


# ----------------------------------------------------------------------
def HasParserInfoErrors(
    node: AST.Node,
) -> bool:
    return getattr(node, _PARSER_INFO_ERROR_ATTRIBUTE_NAME, False)


# ----------------------------------------------------------------------
def GetParserInfoNoThrow(
    node: AST.Node,
) -> Optional[ParserInfo]:
    # TODO: All code should check for this condition prior to invoking this method, which might cause the assertion to fire
    assert not HasParserInfoErrors(node)
    return getattr(node, _PARSER_INFO_ATTRIBUTE_NAME, None)


# ----------------------------------------------------------------------
def GetParserInfo(
    node: AST.Node,
) -> ParserInfo:
    result = GetParserInfoNoThrow(node)
    assert result is not None

    return result


# ----------------------------------------------------------------------
def CreateRegionNoThrow(
    node: Union[
        None,
        Region,
        LexPhrase.NormalizedIteratorRange,
        AST.Leaf,
        AST.Node,
    ],
) -> Optional[Region]:
    if node is None:
        return None
    elif isinstance(node, Region):
        return node
    elif isinstance(node, LexPhrase.NormalizedIteratorRange):
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
_PARSER_INFO_ATTRIBUTE_NAME                 = "parser_info"
_PARSER_INFO_ERROR_ATTRIBUTE_NAME           = "_has_parser_info_errors"


# ----------------------------------------------------------------------
def _SetParserInfo(
    node: AST.Node,
    parser_info: ParserInfo,
) -> None:
    object.__setattr__(node, _PARSER_INFO_ATTRIBUTE_NAME, parser_info)


# ----------------------------------------------------------------------
def _SetParserInfoErrors(
    node: AST.Node,
):
    object.__setattr__(node, _PARSER_INFO_ERROR_ATTRIBUTE_NAME, True)


# ----------------------------------------------------------------------
def _ExtractParserInfo(
    node: AST.Node,
) -> Optional[ParserInfo]:
    parser_info = GetParserInfoNoThrow(node)
    if parser_info is not None:
        return parser_info

    child_parser_infos: List[ParserInfo] = []

    for child in node.children:
        if isinstance(child, AST.Leaf):
            continue

        child_parser_info = _ExtractParserInfo(child)
        if child_parser_info is not None:
            child_parser_infos.append(child_parser_info)

    if not child_parser_infos:
        return None

    assert len(child_parser_infos) == 1, child_parser_infos
    return child_parser_infos[0]


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
            parser_info: Optional[ParserInfo],
        ):
            self.parser_info                                                = parser_info
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
        assert self._node_stack[0].parser_info is None, self._node_stack[0]
        assert len(self._node_stack[0].unnamed) == 1, self._node_stack[0].unnamed

        return self._node_stack[0].unnamed[0]

    # ----------------------------------------------------------------------
    def OnEnterScope(
        self,
        parser_info: ParserInfo,
    ) -> None:
        assert parser_info.introduces_scope__, parser_info

        new_node = _NamespaceVisitor.Node(parser_info)

        name = getattr(parser_info, "name", None)
        if name is not None:
            self._node_stack[-1].namespaces.setdefault(name, []).append(new_node)
        else:
            self._node_stack[-1].unnamed.append(new_node)

        self._node_stack.append(new_node)

    # ----------------------------------------------------------------------
    def OnExitScope(
        self,
        parser_info: ParserInfo,
    ) -> None:
        assert parser_info.introduces_scope__, parser_info

        assert self._node_stack, parser_info
        self._node_stack.pop()
        assert self._node_stack, parser_info

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        attribute: str,
    ) -> Callable[[ParserInfo], None]:
        return self._NoopMethod

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _NoopMethod(*args, **kwargs):
        return None

    # TODO: Aliases
    # TODO: Compile-time statements populate parent namespace
