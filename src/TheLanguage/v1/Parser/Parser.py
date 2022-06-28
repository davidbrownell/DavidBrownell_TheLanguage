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
    from .Error import CreateError, Error, ErrorException, TranslationUnitRegion

    from .MiniLanguage.Types.BooleanType import BooleanType                 # pylint: disable=unused-import
    from .MiniLanguage.Types.CharacterType import CharacterType             # pylint: disable=unused-import
    from .MiniLanguage.Types.IntegerType import IntegerType                 # pylint: disable=unused-import
    from .MiniLanguage.Types.NoneType import NoneType                       # pylint: disable=unused-import
    from .MiniLanguage.Types.NumberType import NumberType                   # pylint: disable=unused-import
    from .MiniLanguage.Types.StringType import StringType                   # pylint: disable=unused-import
    from .MiniLanguage.Types.Type import Type as MiniLanguageType
    from .MiniLanguage.Types.VariantType import VariantType                 # pylint: disable=unused-import

    from .ParserInfos.ParserInfo import ParserInfo
    from .ParserInfos.Statements.RootStatementParserInfo import StatementParserInfo, RootStatementParserInfo

    from .Visitors import MiniLanguageHelpers
    from .Visitors.PassOneVisitor.Visitor import Visitor as PassOneVisitor
    from .Visitors.PassTwoVisitor.Visitor import Visitor as PassTwoVisitor

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
    workspaces: Dict[
        str,                                # workspace name
        Dict[
            str,                            # relative path
            AST.Node,
        ],
    ],
    observer: ParseObserver,
    *,
    max_num_threads: Optional[int]=None,
) -> Optional[
    Dict[
        str,                                # workspace name
        Dict[
            str,                            # relative path
            Union[
                # Unsuccessful result
                List[Error],

                # Successful result
                RootStatementParserInfo,
            ],
        ],
    ]
]:
    # ----------------------------------------------------------------------
    def CreateAndExtract(
        names: Tuple[str, str],  # pylint: disable=unused-argument
        root: AST.Node,
    ) -> Optional[Union[RootStatementParserInfo, List[Error]]]:
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

            return RootStatementParserInfo.Create(
                CreateRegions(root, statements_node, docstring_node),
                names[1],
                cast(List[StatementParserInfo], statements),
                docstring_info,
            )
        except ErrorException as ex:
            return ex.errors

    # ----------------------------------------------------------------------

    return _Execute(
        workspaces,
        CreateAndExtract,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
def ResolveExpressionTypes(
    workspaces: Dict[
        str,                                # workspace root
        Dict[
            str,                            # relative path to file
            RootStatementParserInfo
        ]
    ],
    configuration_values: Dict[str, Tuple[MiniLanguageType, Any]],
    *,
    include_fundamental_types=True,
    max_num_threads: Optional[int]=None,
) -> Optional[
    Dict[
        str,                                # workspace root
        Dict[
            str,                            # relative path to file
            Union[
                RootStatementParserInfo,
                List[Error],
            ],
        ],
    ]
]:
    mini_language_configuration_values = {
        k: MiniLanguageHelpers.CompileTimeInfo(v[0], v[1])
        for k, v in configuration_values.items()
    }

    # ----------------------------------------------------------------------
    # |  Pass 1
    with PassOneVisitor.ScopedExecutor(
        workspaces,
        mini_language_configuration_values,
        include_fundamental_types=include_fundamental_types,
    ) as executor:
        for is_parallel, func in executor.GenerateFuncs():
            results = _Execute(
                workspaces,
                func,
                max_num_threads=max_num_threads if is_parallel else 1,
            )

            if results is None:
                return None

            # Check for errors
            error_data = _ExtractErrorsFromResults(results)
            if error_data is not None:
                return error_data  # type: ignore

        global_namespace = executor.global_namespace
        fundamental_types_namespace = executor.fundamental_types_namespace

    # ----------------------------------------------------------------------
    # |  Pass 2
    executor = PassTwoVisitor.Executor(
        mini_language_configuration_values,
        global_namespace,
        fundamental_types_namespace,
    )

    for is_parallel, func in executor.GenerateFuncs():
        results = _Execute(
            workspaces,
            func,
            max_num_threads=max_num_threads if is_parallel else 1,
        )

        if results is None:
            return None

        error_data = _ExtractErrorsFromResults(results)
        if error_data is not None:
            return error_data  # type: ignore

    return workspaces  # type: ignore


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
        TranslationUnitRegion,
        LexPhrase.NormalizedIteratorRange,
        AST.Leaf,
        AST.Node,
    ],
) -> Optional[TranslationUnitRegion]:
    if node is None:
        return None
    elif isinstance(node, TranslationUnitRegion):
        return node
    elif isinstance(node, LexPhrase.NormalizedIteratorRange):
        return TranslationUnitRegion.Create(node.begin.ToLocation(), node.end.ToLocation())
    elif isinstance(node, (AST.Leaf, AST.Node)):
        if node.iter_range is None:
            return None

        return TranslationUnitRegion.Create(node.iter_range.begin.ToLocation(), node.iter_range.end.ToLocation())
    else:
        assert False, node  # pragma: no cover


# ----------------------------------------------------------------------
def CreateRegion(
    node: Any,
) -> TranslationUnitRegion:
    result = CreateRegionNoThrow(node)
    assert result is not None

    return result


# ----------------------------------------------------------------------
def CreateRegions(
    *nodes: Any,
) -> List[Optional[TranslationUnitRegion]]:
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
    inputs: Dict[
        str,                                # workspace root
        Dict[
            str,                            # relative path
            _ExecuteInputType
        ]
    ],
    execute_func: Callable[[Tuple[str, str], _ExecuteInputType], Optional[_ExecuteOutputType]],
    *,
    max_num_threads: Optional[int]=None,
) -> Optional[
    Dict[
        str,                                # workspace root
        Dict[
            str,                            # relative path
            _ExecuteOutputType
        ]
    ]
]:
    # ----------------------------------------------------------------------
    def Execute(
        names: Tuple[str, str],
        input_value: _ExecuteInputType,
    ) -> Optional[_ExecuteOutputType]:
        try:
            return execute_func(names, input_value)
        except Exception as ex:
            if not hasattr(ex, "fully_qualified_name"):
                object.__setattr__(ex, "full_qualified_name", os.path.join(*names))

            if not hasattr(ex, "traceback"):
                object.__setattr__(ex, "traceback", traceback.format_exc())

            raise

    # ----------------------------------------------------------------------

    # Flatten the inputs
    flattened_inputs: Dict[Tuple[str, str], _ExecuteInputType] = {}

    for workspace_root, workspace_items in inputs.items():
        for relative_path, input_value in workspace_items.items():
            key = (workspace_root, relative_path)

            assert key not in flattened_inputs, key
            flattened_inputs[key] = input_value

    # Execute
    raw_results: List[_ExecuteOutputType] = []

    if max_num_threads == 1 or len(flattened_inputs) == 1:
        for k, v in flattened_inputs.items():
            result = Execute(k, cast(_ExecuteInputType, v))
            if result is None:
                return None

            raw_results.append(result)

    else:
        with ThreadPoolExecutor(
            max_workers=max_num_threads,
        ) as executor:
            futures = [
                executor.submit(Execute, k, cast(_ExecuteInputType, v))
                for k, v in flattened_inputs.items()
            ]

            for future in futures:
                result = future.result()
                if result is None:
                    return None

                raw_results.append(result)

    # Unflatten the results
    results: Dict[
        str,                        # workspace root
        Dict[
            str,                    # relative path
            _ExecuteOutputType
        ]
    ] = {}

    raw_results_iter = iter(raw_results)

    for workspace_root, workspace_items in inputs.items():
        workspace_results: Dict[str, _ExecuteOutputType] = {}

        for relative_path in workspace_items.keys():
            workspace_results[relative_path] = next(raw_results_iter)

        results[workspace_root] = workspace_results

    return results


# ----------------------------------------------------------------------
def _ExtractErrorsFromResults(
    results: Dict[str, Dict[str, Any]],
) -> Optional[
    Dict[
        str,                                # workspace root
        Dict[
            str,                            # relative path
            List[Error]
        ]
    ]
]:
    error_results: Dict[str, Dict[str, List[Error]]] = {}

    for workspace_root, workspace_items in results.items():
        these_error_results: Dict[str, List[Error]] = {}

        for relative_path, result in workspace_items.items():
            if (
                isinstance(result, list)
                and result
                and isinstance(result[0], Error)
            ):
                these_error_results[relative_path] = result

        if these_error_results:
            error_results[workspace_root] = these_error_results

    return error_results or None
