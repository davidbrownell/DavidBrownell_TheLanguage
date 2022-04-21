# ----------------------------------------------------------------------
# |
# |  ConstraintParametersFragment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 10:19:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when processing constraint parameters"""

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
        PhraseItem,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import (
        CreateError,
        CreateRegion,
        CreateRegions,
        Error,
        GetParserInfo,
        ParserInfo,
    )

    from ...Parser.ParserInfos.Common.ConstraintParametersParserInfo import (
        ExpressionParserInfo,
        ConstraintParameterParserInfo,
        ConstraintParametersParserInfo,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
InvalidParameterNameError                   = CreateError(
    "'{name}' is not a valid constraint parameter name",
    name=str,
)


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    parameter_element = PhraseItem(
        name="Constraint Parameter",
        item=[
            # <type>
            DynamicPhrasesType.Types,

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
    )

    return ParametersFragmentImpl.Create(
        "Constraint Parameters",
        "{", "}",
        parameter_element,
        allow_empty=False,
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> Union[
    List[Error],
    ConstraintParametersParserInfo,
]:
    result = ParametersFragmentImpl.Extract(
        ConstraintParametersParserInfo,
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
) -> Union[
    List[Error],
    Tuple[ParserInfo, bool],
]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 3

    errors: List[Error] = []

    # <type>
    type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
    type_info = cast(TypeParserInfo, GetParserInfo(type_node))

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
        return errors

    return (
        ConstraintParameterParserInfo.Create(
            CreateRegions(node, name_leaf),
            type_info,
            name_info,
            default_info,
        ),
        default_info is not None,
    )
