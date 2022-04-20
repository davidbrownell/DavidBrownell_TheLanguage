# ----------------------------------------------------------------------
# |
# |  FuncParametersFragment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 16:30:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when processing function parameters"""

import os

from typing import cast, List, Optional, Tuple, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens as CommonTokens

    from .Impl import ParametersFragmentImpl

    from ..GrammarPhrase import AST

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        ExtractToken,
        PhraseItem,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import (
        CreateRegions,
        Error,
        GetParserInfo,
        ParserInfo,
    )

    from ...Parser.ParserInfos.Common.FuncParametersParserInfo import (
        ExpressionParserInfo,
        FuncParameterParserInfo,
        FuncParametersParserInfo,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    parameter_element = PhraseItem(
        name="Function Parameter",
        item=[
            # <type>
            DynamicPhrasesType.Types,

            # '...'?
            OptionalPhraseItem(
                name="Variadic",
                item="...",
            ),

            # <name>
            CommonTokens.RuntimeParameterName,

            # ('=' <expression>)?
            OptionalPhraseItem(
                name="Default",
                item=[
                    "=",
                    CommonTokens.PushIgnoreWhitespaceControl,
                    DynamicPhrasesType.Expressions,
                    CommonTokens.PopIgnoreWhitespaceControl,
                ],
            ),
        ],
    )

    return ParametersFragmentImpl.Create(
        "Function Parameters",
        "(", ")",
        parameter_element,
        allow_empty=True,
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> Union[
    List[Error],
    bool,
    FuncParametersParserInfo,
]:
    return ParametersFragmentImpl.Extract(
        FuncParametersParserInfo,
        _ExtractElement,
        node,
        allow_empty=True,
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractElement(
    node: AST.Node,
) -> Tuple[ParserInfo, bool]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 4

    # <type>
    type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
    type_info = cast(TypeParserInfo, GetParserInfo(type_node))

    # '...'?
    is_variadic_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
    if is_variadic_node is None:
        is_variadic_info = None
    else:
        is_variadic_info = True

    # <name>
    name_leaf = cast(AST.Leaf, nodes[2])
    name_info = ExtractToken(name_leaf)

    # ('=' <expression>)?
    default_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[3])))
    if default_node is None:
        default_info = None
    else:
        default_nodes = ExtractSequence(default_node)
        assert len(default_nodes) == 4

        default_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, default_nodes[2])))
        default_info = cast(ExpressionParserInfo, GetParserInfo(default_node))

    return (
        FuncParameterParserInfo.Create(
            CreateRegions(node, is_variadic_node, name_leaf),
            type_info,
            is_variadic_info,
            name_info,
            default_info,
        ),
        default_info is not None,
    )
