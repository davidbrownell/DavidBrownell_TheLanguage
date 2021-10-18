# ----------------------------------------------------------------------
# |
# |  Parser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-29 10:36:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Creates and extracts parser information from nodes"""

import os

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, cast, Dict, List, Optional, Tuple, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ParserInfo import Location, ParserInfo, Region
    from .RootParserInfo import RootParserInfo

    from ..Lexer.Lexer import AST, Phrase


# ----------------------------------------------------------------------
CreateParserInfoFuncType                    = Callable[
    [
        AST.Node,
    ],
    Union[
        None,                                           # No parser info associated with the node
        bool,                                           # True to continue processing, False to terminate
        ParserInfo,                                     # The result; implies that we should continue processing
        Callable[[], ParserInfo],                       # A callback that must be invoked before the ParserInfo is available; implies that we should continue processing
        Tuple[ParserInfo, Callable[[], ParserInfo]],    # A combination of the previous 2 items
    ]
]


# ----------------------------------------------------------------------
def Parse(
    roots: Dict[str, AST.Node],
    create_parser_info_func: CreateParserInfoFuncType,
    *,
    max_num_threads: Optional[int]=None,
) -> Union[
    None,                                   # Cancellation
    Dict[str, RootParserInfo],              # Successful results
    List[Exception],                        # Errors
]:

    single_threaded = max_num_threads == 1 or len(roots) == 1

    # ----------------------------------------------------------------------
    def CreateAndExtract(
        fully_qualified_name: str,
        root: AST.Node,
    ) -> Optional[RootParserInfo]:
        try:
            # Create the parser info
            funcs: List[Tuple[AST.Node, Callable[[], ParserInfo]]] = []

            for node in root.Enum(nodes_only=True):
                assert isinstance(node, AST.Node)

                result = create_parser_info_func(node)
                if result is None:
                    continue

                elif isinstance(result, bool):
                    if not result:
                        return None

                elif isinstance(result, ParserInfo):
                    _SetParserInfo(node, result)

                elif callable(result):
                    funcs.append((node, result))

                elif isinstance(result, tuple):
                    parser_info, callback = result

                    _SetParserInfo(node, parser_info)
                    funcs.append((node, callback))

                else:
                    assert False, result  # pragma: no cover

            for node, func in reversed(funcs):
                _SetParserInfo(node, func())

            # Extract the info
            children = []

            for child in root.Children:
                if isinstance(child, AST.Leaf):
                    continue

                children.append(_Extract(cast(AST.Node, child)))

            # pylint: disable=too-many-function-args
            return RootParserInfo(
                CreateParserRegions(root),  # type: ignore
                children,
            )

        except Exception as ex:
            if not hasattr(ex, "FullyQualifiedName"):
                object.__setattr__(ex, "FullyQualifiedName", fully_qualified_name)

            raise

    # ----------------------------------------------------------------------

    errors: List[Exception] = []

    if single_threaded:
        results = []

        for k, v in roots.items():
            try:
                results.append(CreateAndExtract(k, v))
            except Exception as ex:
                errors.append(ex)

    else:
        with ThreadPoolExecutor(
            max_workers=max_num_threads,
        ) as executor:
            futures = [
                executor.submit(CreateAndExtract, k, v)
                for k, v in roots.items()
            ]

            results = []

            for future in futures:
                try:
                    results.append(future.result())
                except Exception as ex:
                    errors.append(ex)

    if any(result is None for result in results):
        return None

    if errors:
        return errors

    return {
        fully_qualified_name : cast(RootParserInfo, result)
        for fully_qualified_name, result in zip(roots.keys(), results)
    }


# ----------------------------------------------------------------------
def GetParserInfo(
    obj: Any,
    *,
    allow_none: bool=False,
) -> Optional[ParserInfo]:
    result = getattr(obj, "Info", None)
    assert allow_none or result is not None

    return result


# ----------------------------------------------------------------------
def CreateLocation(
    iter: Optional[Phrase.NormalizedIterator],
) -> Location:
    if iter is None:
        line = -1
        column = -1
    else:
        line = iter.Line
        column = iter.Column

    return Location(line, column)


# ----------------------------------------------------------------------
def CreateParserRegion(
    node: Union[AST.Leaf, AST.Node],
) -> Region:
    """Uses information in a node to create a Region"""

    location_begin = CreateLocation(node.IterBegin)

    if isinstance(node, AST.Leaf) and node.Whitespace is not None:
        location_begin = Location(
            location_begin.Line,
            location_begin.Column + node.Whitespace[1] - node.Whitespace[0] - 1,
        )

    return Region(location_begin, CreateLocation(node.IterEnd))


# ----------------------------------------------------------------------
def CreateParserRegions(
    *nodes: Union[
        AST.Leaf,
        AST.Node,
        Region,
        Tuple[Phrase.NormalizedIterator, Phrase.NormalizedIterator],
        None,
    ],
) -> List[Optional[Region]]:
    """Creates regions for the provided input"""

    results: List[Optional[Region]] = []

    for node in nodes:
        if node is None:
            results.append(None)
        elif isinstance(node, Region):
            results.append(node)
        elif isinstance(node, tuple):
            results.append(Region(CreateLocation(node[0]), CreateLocation(node[1])))
        else:
            results.append(CreateParserRegion(node))

    return results


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _SetParserInfo(
    obj: Any,
    arg: Optional[ParserInfo],
):
    object.__setattr__(obj, "Info", arg)


# ----------------------------------------------------------------------
def _Extract(
    node: AST.Node,
) -> Optional[ParserInfo]:
    parser_info = GetParserInfo(
        node,
        allow_none=True,
    )

    if parser_info is not None:
        return parser_info

    children: List[ParserInfo] = []

    for child in node.Children:
        if isinstance(child, AST.Leaf):
            continue

        child_parser_info = _Extract(child)
        if child_parser_info is not None:
            children.append(child_parser_info)

    if not children:
        return None

    assert len(children) == 1
    return children[0]
