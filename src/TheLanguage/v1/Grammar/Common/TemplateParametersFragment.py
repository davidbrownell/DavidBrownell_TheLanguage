# ----------------------------------------------------------------------
# |
# |  TemplateParametersFragment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 07:58:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when processing template parameters"""

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
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        PhraseItem,
        OptionalPhraseItem,
    )

    from ...Parser.Error import Error
    from ...Parser.Parser import CreateRegions, GetPhrase, Phrase

    from ...Parser.Common.TemplateParametersPhrase import (
        TemplateDecoratorParameterPhrase,
        TemplateParametersPhrase,
        TemplateTypeParameterPhrase,
        TypePhrase,
    )

    from ...Parser.TemplateDecoratorExpressions.TemplateDecoratorExpressionPhrase import TemplateDecoratorExpressionPhrase
    from ...Parser.TemplateDecoratorTypes.TemplateDecoratorTypePhrase import TemplateDecoratorTypePhrase


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    parameter_element = PhraseItem(
        name="Template Parameter",
        item=(
            # <template_type_name> '...'? ('=' <type>)?
            PhraseItem(
                name="Template Type",
                item=[
                    # <template_type_name>
                    CommonTokens.TemplateTypeName,

                    # '...'?
                    OptionalPhraseItem(
                        name="Variadic",
                        item="...",
                    ),

                    # ('=' <type>)?
                    OptionalPhraseItem(
                        name="Default",
                        item=[
                            "=",
                            CommonTokens.PushIgnoreWhitespaceControl,
                            DynamicPhrasesType.Types,
                            CommonTokens.PopIgnoreWhitespaceControl,
                        ],
                    ),
                ],
            ),

            # <template_decorator_type> <template_decorator_name> ('=' <template_decorator_expression>)?
            PhraseItem(
                name="Template Decorator",
                item=[
                    # <template_decorator_type>
                    DynamicPhrasesType.TemplateDecoratorTypes,

                    # <template_decorator_name>
                    CommonTokens.TemplateDecoratorParameterName,

                    # ('=' <template_decorator_expression>)?
                    OptionalPhraseItem(
                        name="Default",
                        item=[
                            "=",
                            CommonTokens.PushIgnoreWhitespaceControl,
                            DynamicPhrasesType.TemplateDecoratorExpressions,
                            CommonTokens.PopIgnoreWhitespaceControl,
                        ],
                    ),
                ],
            ),
        ),
    )

    return ParametersFragmentImpl.Create(
        "Template Parameters",
        "<", ">",
        parameter_element,
        allow_empty=False,
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> Union[
    List[Error],
    TemplateParametersPhrase,
]:
    result = ParametersFragmentImpl.Extract(
        TemplateParametersPhrase,
        _ExtractElement,
        node,
        allow_empty=False,
    )

    assert not isinstance(result, bool)
    return result


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractElement(
    node: AST.Node,
) -> Tuple[Phrase, bool]:
    node = cast(AST.Node, ExtractOr(node))
    assert node.type is not None

    if node.type.name == "Template Type":
        nodes = ExtractSequence(node)
        assert len(nodes) == 3

        # <template_type_name>
        type_leaf = cast(AST.Leaf, nodes[0])
        type_info = ExtractToken(type_leaf)

        # '...'?
        variadic_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
        if variadic_node is None:
            variadic_info = None
        else:
            variadic_info = True

        # ('=' <type>)?
        default_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
        if default_node is None:
            default_info = None
        else:
            default_nodes = ExtractSequence(default_node)
            assert len(default_nodes) == 4

            default_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, default_nodes[2])))
            default_info = cast(TypePhrase, GetPhrase(default_node))

        return (
            TemplateTypeParameterPhrase.Create(
                CreateRegions(node, type_leaf, variadic_node, default_node),
                type_info,
                variadic_info,
                default_info,
            ),
            default_info is not None,
        )

    elif node.type.name == "Template Decorator":
        nodes = ExtractSequence(node)
        assert len(nodes) == 3

        # <template_decorator_type>
        type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
        type_info = cast(TemplateDecoratorTypePhrase, GetPhrase(type_node))

        # <template_decorator_name>
        name_leaf = cast(AST.Leaf, nodes[1])
        name_info = ExtractToken(name_leaf)

        # ('=' <template_decorator_expression>)?
        default_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
        if default_node is None:
            default_info = None
        else:
            default_nodes = ExtractSequence(default_node)
            assert len(default_nodes) == 4

            default_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, default_nodes[2])))
            default_info = cast(TemplateDecoratorExpressionPhrase, GetPhrase(default_node))

        return (
            TemplateDecoratorParameterPhrase.Create(
                CreateRegions(node, type_node, name_leaf, default_node),
                type_info,
                name_info,
                default_info,
            ),
            default_info is not None,
        )
    else:
        assert False, node.type  # pragma: no cover