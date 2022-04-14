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
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        PhraseItem,
        OptionalPhraseItem,
    )

    from ...Parser.Common.TemplateArgumentsPhrase import (
        TemplateArgumentsPhrase,
        TemplateDecoratorArgumentPhrase,
        TemplateDecoratorExpressionPhrase,
        TemplateTypeArgumentPhrase,
        TypePhrase,
    )

    from ...Parser.Error import Error
    from ...Parser.Parser import CreateRegions, GetPhrase, Phrase


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    argument_element = PhraseItem(
        name="Template Argument",
        item=(
            # (<parameter_name> '=')? <type>
            PhraseItem(
                name="Template Type",
                item=[
                    # (<parameter_name> '=')?
                    OptionalPhraseItem(
                        name="Keyword",
                        item=[
                            CommonTokens.TemplateTypeName,
                            "=",
                        ],
                    ),

                    # <type>
                    DynamicPhrasesType.Types,
                ],
            ),

            # (<parameter_name> '=')? <template_expression>
            PhraseItem(
                name="Template Decorator",
                item=[
                    # (<parameter_name> '=')?
                    OptionalPhraseItem(
                        name="Keyword",
                        item=[
                            CommonTokens.TemplateDecoratorParameterName,
                            "=",
                        ],
                    ),

                    # <template_expression>
                    DynamicPhrasesType.TemplateDecoratorExpressions,
                ],
            ),
        ),
    )

    return ArgumentsFragmentImpl.Create(
        "Template Arguments",
        "<", ">",
        argument_element,
        allow_empty=True,
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> Union[
    List[Error],
    bool,
    TemplateArgumentsPhrase,
]:
    return ArgumentsFragmentImpl.Extract(
        TemplateArgumentsPhrase,
        _ExtractElement,
        node,
        allow_empty=True,
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractElement(
    node: AST.Node,
) -> Tuple[Phrase, bool]:
    node = cast(AST.Node, ExtractOr(node))
    assert node.type is not None

    if node.type.name == "Template Type":
        dynamic_phrase_type = TypePhrase
        element_type = TemplateTypeArgumentPhrase

    elif node.type.name == "Template Decorator":
        dynamic_phrase_type = TemplateDecoratorExpressionPhrase
        element_type = TemplateDecoratorArgumentPhrase

    else:
        assert False, node.type  # pragma: no cover

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
        keyword_info = ExtractToken(keyword_node)

    # <type> | <template_expression>
    value_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[1])))
    value_info = cast(dynamic_phrase_type, GetPhrase(value_node))

    return (
        element_type.Create(
            CreateRegions(node, value_node, keyword_node),
            value_info,
            keyword_info,
        ),
        keyword_info is not None,
    )
