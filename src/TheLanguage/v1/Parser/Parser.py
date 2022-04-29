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
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

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
    from .Visitors.ValidateVisitor.ValidateVisitor import ValidateVisitor

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
        Callable[
            [],
            ParserInfo,
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

                elif isinstance(result, ParserInfo):
                    _SetParserInfo(node, result)

                else:
                    assert False, result  # pragma: no cover

            except ErrorException as ex:
                _SetParserInfoErrors(node)
                errors += ex.errors

        for node, callback in reversed(callback_funcs):
            try:
                result = callback()

                if isinstance(result, ParserInfo):
                    _SetParserInfo(node, result)

                else:
                    assert False, result  # pragma: no cover

            except ErrorException as ex:
                _SetParserInfoErrors(node)
                errors += ex.errors

        # Extract the root information
        existing_doc_info: Optional[Tuple[Union[AST.Leaf, AST.Node], str]] = None
        statements: List[ParserInfo] = []

        for child in root.children:
            try:
                result = observer.ExtractPotentialDocInfo(child)

                if result is not None:
                    if isinstance(result, tuple):
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
def Validate(
    roots: Dict[str, RootParserInfo],
    compile_time_values: Dict[
        str,
        Tuple[Type, Any],
    ],
    *,
    max_num_threads: Optional[int]=None,
) -> Optional[
    Dict[str, Union[RootParserInfo, List[Error]]]
]:
    # TODO: Add functionality for deferred processing

    # ----------------------------------------------------------------------
    def Execute(
        fully_qualified_name: str,  # pylint: disable=unused-argument
        root: RootParserInfo,
    ) -> Union[
        RootParserInfo,
        List[Error],
    ]:
        visitor = ValidateVisitor(compile_time_values)

        root.Accept(visitor)

        # TODO: Handle warnings and infos

        if visitor.errors:
            return visitor.errors

        return root

    # ----------------------------------------------------------------------

    results = _Execute(
        roots,
        Execute,
        max_num_threads=max_num_threads,
    )

    return results


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
