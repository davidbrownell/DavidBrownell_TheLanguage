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
from typing import Any, Callable, cast, Dict, List, Optional, Tuple, TypeVar, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Error import CreateError, Error, ErrorException, Region
    from .Helpers import MiniLanguageHelpers
    from .NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from .MiniLanguage.Types.BooleanType import BooleanType                 # pylint: disable=unused-import
    from .MiniLanguage.Types.CharacterType import CharacterType             # pylint: disable=unused-import
    from .MiniLanguage.Types.IntegerType import IntegerType                 # pylint: disable=unused-import
    from .MiniLanguage.Types.NoneType import NoneType                       # pylint: disable=unused-import
    from .MiniLanguage.Types.NumberType import NumberType                   # pylint: disable=unused-import
    from .MiniLanguage.Types.StringType import StringType                   # pylint: disable=unused-import
    from .MiniLanguage.Types.Type import Type as MiniLanguageType
    from .MiniLanguage.Types.VariantType import VariantType                 # pylint: disable=unused-import

    from .ParserInfos.ParserInfo import ParserInfo, RootParserInfo

    from .Visitors.PassOneVisitor.Visitor import Visitor as PassOneVisitor

    from ..Lexer.Lexer import AST, Phrase as LexPhrase


# ----------------------------------------------------------------------
DuplicateDocInfoError                       = CreateError(
    "Documentation information has already been provided",
)

ActiveErrorError                            = CreateError(
    "Active errors prevent further validation",
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
    ExtractPotentialDocInfoReturnType       = Optional[
        Tuple[
            Union[AST.Leaf, AST.Node],
            str,
        ]
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

                if isinstance(child, AST.Node):
                    parser_info = _ExtractParserInfo(child)
                    if parser_info is not None:
                        statements.append(parser_info)

            except ErrorException as ex:
                errors += ex.errors

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
    configuration_values: Dict[str, Tuple[MiniLanguageType, Any]],
    *,
    max_num_threads: Optional[int]=None,
) -> Optional[
    Dict[str, Union[RootParserInfo, List[Error]]]
]:
    mini_language_configuration_values = {
        k: MiniLanguageHelpers.CompileTimeInfo(v[0], v[1], None)
        for k, v in configuration_values.items()
    }

    # ----------------------------------------------------------------------
    def ExtractErrorsFromResults(
        results: Dict[str, Any],
    ) -> Optional[Dict[str, List[Error]]]:
        error_results = {}

        for k, v in results.items():
            if isinstance(v, list) and v and isinstance(v[0], Error):
                error_results[k] = v

        return error_results or None

    # ----------------------------------------------------------------------
    def ExecutePassOne(
        fully_qualified_name: str,  # pylint: disable=unused-argument
        root: RootParserInfo,
    ) -> Union[
        Tuple[ParsedNamespaceInfo, PassOneVisitor.PostprocessFuncsType],
        List[Error],
    ]:
        visitor = PassOneVisitor(mini_language_configuration_values)

        root.Accept(visitor)

        if visitor.errors:
            return visitor.errors

        return visitor.namespace_info, visitor.postprocess_funcs

    # ----------------------------------------------------------------------

    results = _Execute(
        roots,
        ExecutePassOne,
        max_num_threads=max_num_threads,
    )

    if results is None:
        return None

    # Check for errors
    error_data = ExtractErrorsFromResults(results)
    if error_data is not None:
        return error_data  # type: ignore

    # Create a complete namespace and extract postprocess funcs
    global_namespace = NamespaceInfo(None)

    postprocess_funcs: Dict[str, PassOneVisitor.PostprocessFuncsType] = {}
    pass_one_results: Dict[str, ParsedNamespaceInfo] = {}

    for fully_qualified_name, (namespace_info, these_postprocess_funcs) in cast(
        Dict[str, Tuple[ParsedNamespaceInfo, PassOneVisitor.PostprocessFuncsType]],
        results,
    ).items():
        # Update the global namespace
        name_parts = os.path.splitext(fully_qualified_name)[0]
        name_parts = name_parts.split(os.path.sep)

        namespace = global_namespace

        for part in name_parts[:-1]:
            if part not in namespace.children:
                namespace.children[part] = NamespaceInfo(namespace)

            namespace = namespace.children[part]

        object.__setattr__(namespace_info, "parent", namespace)
        namespace.children[name_parts[-1]] = namespace_info

        # Update the global postprocess funcs
        if these_postprocess_funcs:
            postprocess_funcs[fully_qualified_name] = these_postprocess_funcs

        # Update the results
        pass_one_results[fully_qualified_name] = namespace_info

    error_data = PassOneVisitor.ExecutePostprocessFuncs(postprocess_funcs)
    if error_data:
        return error_data  # type: ignore

    # TODO: Continue

    return roots # type: ignore


# ----------------------------------------------------------------------
def HasParserInfoErrors(
    node: AST.Node,
) -> bool:
    return getattr(node, _PARSER_INFO_ERROR_ATTRIBUTE_NAME, False)


# ----------------------------------------------------------------------
def GetParserInfoNoThrow(
    node: AST.Node,
) -> Optional[ParserInfo]:
    if HasParserInfoErrors(node):
        raise ErrorException(
            ActiveErrorError.Create(
                CreateRegion(node),
            ),
        )

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
