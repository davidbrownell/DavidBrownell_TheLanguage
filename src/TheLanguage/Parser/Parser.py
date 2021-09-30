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
    from ..Lexer.Phrases.DynamicPhrase import DynamicPhrase
    from ..Lexer.Phrases.OrPhrase import OrPhrase


# ----------------------------------------------------------------------
CreateParserInfoFuncType                    = Callable[
    [
        AST.Node,
    ],
    Union[
        None,                               # No parser info associated with the node
        bool,                               # True to continue processing, False to terminate
        ParserInfo,                         # The result; implies that we should continue processing
        Callable[[], ParserInfo],           # A callback that must be invoked before the ParserInfo is available; implies that we should continue processing
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

                if isinstance(result, bool):
                    if not result:
                        return None

                elif isinstance(result, ParserInfo):
                    _SetParserInfo(node, result)

                elif callable(result):
                    funcs.append((node, result))

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
) -> Optional[ParserInfo]:
    return getattr(obj, "Info", None)


# ----------------------------------------------------------------------
def CreateParserRegion(
    node: Union[AST.Leaf, AST.Node],
) -> Region:
    """Uses information in a node to create a Region"""

    # ----------------------------------------------------------------------
    def CreateLocation(
        iter: Optional[Phrase.NormalizedIterator],
        adjust_for_whitespace=False,
    ) -> Location:
        if iter is None:
            line = -1
            column = -1
        else:
            line = iter.Line
            column = iter.Column

            if (
                isinstance(node, AST.Leaf)
                and adjust_for_whitespace
                and node.Whitespace is not None
            ):
                column += node.Whitespace[1] - node.Whitespace[0] - 1

        return Location(line, column)

    # ----------------------------------------------------------------------

    return Region(
        CreateLocation(
            node.IterBegin,
            adjust_for_whitespace=True,
        ),
        CreateLocation(node.IterEnd),
    )


# ----------------------------------------------------------------------
def CreateParserRegions(
    *nodes: Union[AST.Leaf, AST.Node, Region, None],
) -> List[Optional[Region]]:
    """Creates regions for the provided input"""

    # TODO: Ensure that TheLanguage can handle statements formatted like this
    return [
        None if node is None else
            node if isinstance(node, Region) else
                CreateParserRegion(node)
        for node in nodes
    ]


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
    parser_info = GetParserInfo(node)

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
