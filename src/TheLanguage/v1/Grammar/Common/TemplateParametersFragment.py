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

from typing import cast, List, Optional, Tuple

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
        PhraseItem,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import (
        CreateError,
        CreateRegion,
        CreateRegions,
        Error,
        ErrorException,
        GetParserInfo,
        ParserInfo,
    )

    from ...Parser.ParserInfos.Common.TemplateParametersParserInfo import (
        ExpressionParserInfo,
        TemplateDecoratorParameterParserInfo,
        TemplateParametersParserInfo,
        TemplateTypeParameterParserInfo,
    )


# ----------------------------------------------------------------------
InvalidParameterNameError                   = CreateError(
    "'{name}' is not a valid template parameter name",
    name=str,
)


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
                            DynamicPhrasesType.Expressions,
                            CommonTokens.PopIgnoreWhitespaceControl,
                        ],
                    ),
                ],
            ),

            # <type> <name> ('=' <expression>)?
            PhraseItem(
                name="Template Decorator",
                item=[
                    # <type>
                    DynamicPhrasesType.Expressions,

                    # <name>
                    CommonTokens.ParameterName,

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
) -> TemplateParametersParserInfo:
    result = ParametersFragmentImpl.Extract(
        TemplateParametersParserInfo,
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
) -> Tuple[ParserInfo, bool]:
    node = cast(AST.Node, ExtractOr(node))
    assert node.type is not None

    if node.type.name == "Template Type":
        return _ExtractTypeElement(node)
    elif node.type.name == "Template Decorator":
        return  _ExtractDecoratorElement(node)

    assert False, node.type  # pragma: no cover


# ----------------------------------------------------------------------
def _ExtractTypeElement(
    node: AST.Node,
) -> Tuple[ParserInfo, bool]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 3

    # <template_type_name>
    type_leaf = cast(AST.Leaf, nodes[0])
    type_info = CommonTokens.TemplateTypeName.Extract(type_leaf)  # type: ignore

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
        default_info = cast(ExpressionParserInfo, GetParserInfo(default_node))

    return (
        TemplateTypeParameterParserInfo.Create(
            CreateRegions(node, type_leaf, variadic_node),
            type_info,
            variadic_info,
            default_info,
        ),
        default_info is not None,
    )


# ----------------------------------------------------------------------
def _ExtractDecoratorElement(
    node: AST.Node,
) -> Tuple[ParserInfo, bool]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 3

    errors: List[Error] = []

    # <type>
    type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
    type_info = cast(ExpressionParserInfo, GetParserInfo(type_node))

    # <name>
    name_leaf = cast(AST.Leaf, nodes[1])
    name_info = CommonTokens.ParameterName.Extract(name_leaf)  # type: ignore

    if not CommonTokens.ParameterName.IsCompileTime(name_info):  # type: ignore
        errors.append(
            InvalidParameterNameError.Create(
                region=CreateRegion(name_leaf),
                name=name_info,
            ),
        )

    # ('=' <expression>)?
    default_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
    if default_node is None:
        default_info = None
    else:
        default_nodes = ExtractSequence(default_node)
        assert len(default_nodes) == 4

        default_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, default_nodes[2])))
        default_info = cast(ExpressionParserInfo, GetParserInfo(default_node))

    if errors:
        raise ErrorException(*errors)

    return (
        TemplateDecoratorParameterParserInfo.Create(
            CreateRegions(node, name_leaf),
            type_info,
            name_info,
            default_info,
        ),
        default_info is not None,
    )
