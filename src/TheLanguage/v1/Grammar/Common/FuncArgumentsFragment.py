# ----------------------------------------------------------------------
# |
# |  FuncArgumentsFragment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 13:15:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when processing function arguments"""

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

    from .Impl import ArgumentsFragmentImpl

    from ..GrammarPhrase import AST

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        PhraseItem,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import (
        CreateRegions,
        Error,
        GetParserInfo,
        ParserInfo,
    )

    from ...Parser.ParserInfos.Common.FuncArgumentsParserInfo import (
        ExpressionParserInfo,
        ParserInfoType,
        FuncArgumentParserInfo,
        FuncArgumentsParserInfo,
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    argument_element = PhraseItem(
        name="Argument",
        item=[
            # (<parameter_name> '=')?
            OptionalPhraseItem(
                name="Keyword",
                item=[
                    CommonTokens.ParameterName,
                    "=",
                ],
            ),

            # <expression>
            DynamicPhrasesType.Expressions,
        ],
    )

    return ArgumentsFragmentImpl.Create(
        "Function Arguments",
        "(", ")",
        argument_element,
        allow_empty=True,
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> Union[
    List[Error],
    bool,
    FuncArgumentsParserInfo,
]:
    return ArgumentsFragmentImpl.Extract(
        FuncArgumentsParserInfo,
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
    assert len(nodes) == 2

    # (<parameter_name> '=')?
    keyword_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[0])))
    if keyword_node is None:
        keyword_info = None
    else:
        keyword_nodes = ExtractSequence(keyword_node)
        assert len(keyword_nodes) == 2

        keyword_node = cast(AST.Leaf, keyword_nodes[0])
        keyword_info = CommonTokens.ParameterName.Extract(keyword_node)  # type: ignore

    # <expression>
    expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[1])))
    expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

    return (
        FuncArgumentParserInfo.Create(
            CreateRegions(node, keyword_node),
            expression_info,
            keyword_info,
        ),
        keyword_info is not None,
    )
