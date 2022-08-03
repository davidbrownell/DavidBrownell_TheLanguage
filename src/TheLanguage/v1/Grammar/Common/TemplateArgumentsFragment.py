# ----------------------------------------------------------------------
# |
# |  TemplateArgumentsFragment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 09:37:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when processing template arguments"""

import os

from typing import cast, Optional, Tuple, Union

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
        GetParserInfo,
        ParserInfo,
    )

    from ...Parser.ParserInfos.Common.TemplateArgumentsParserInfo import (
        ExpressionParserInfo,
        TemplateArgumentsParserInfo,
        TemplateArgumentParserInfo,
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    argument_element = PhraseItem(
        name="Template Argument",
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
        "Template Arguments",
        # TODO: Change these to: "<", ">" when lexer is updated
        "<TEMPLATE", "TEMPLATE>",
        argument_element,
        allow_empty=True,
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> Union[
    bool,
    TemplateArgumentsParserInfo,
]:
    return ArgumentsFragmentImpl.Extract(
        TemplateArgumentsParserInfo,
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

    # <type> | <template_expression>
    value_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[1])))
    value_info = cast(ExpressionParserInfo, GetParserInfo(value_node))

    return (
        TemplateArgumentParserInfo.Create(
            CreateRegions(node, keyword_node),
            value_info,
            keyword_info,
        ),
        keyword_info is not None,
    )
