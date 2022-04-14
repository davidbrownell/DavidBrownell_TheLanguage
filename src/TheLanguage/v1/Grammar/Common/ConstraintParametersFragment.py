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
        ExtractToken,
        PhraseItem,
        OptionalPhraseItem,
    )

    from ...Parser.Common.ConstraintParametersPhrase import (
        ConstraintExpressionPhrase,
        ConstraintParametersPhrase,
        ConstraintParameterPhrase,
        ConstraintTypePhrase,
    )

    from ...Parser.Error import Error
    from ...Parser.Parser import CreateRegions, GetPhrase, Phrase


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    parameter_element = PhraseItem(
        name="Constraint Parameter",
        item=[
            # <constraint_type>
            DynamicPhrasesType.ConstraintTypes,

            # <name>
            CommonTokens.ConstraintParameterName,

            # ('=' <constraint_expression>)?
            OptionalPhraseItem(
                name="Default",
                item=[
                    "=",
                    CommonTokens.PushIgnoreWhitespaceControl,
                    DynamicPhrasesType.ConstraintExpressions,
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
    ConstraintParametersPhrase,
]:
    result = ParametersFragmentImpl.Extract(
        ConstraintParametersPhrase,
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
    nodes = ExtractSequence(node)
    assert len(nodes) == 3

    # <constraint_type>
    type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
    type_info = cast(ConstraintTypePhrase, GetPhrase(type_node))

    # <name>
    name_leaf = cast(AST.Leaf, nodes[1])
    name_info = ExtractToken(name_leaf)

    # ('=' <constraint_expression>)?
    default_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
    if default_node is None:
        default_info = None
    else:
        default_nodes = ExtractSequence(default_node)
        assert len(default_nodes) == 4

        default_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, default_nodes[2])))
        default_info = cast(ConstraintExpressionPhrase, GetPhrase(default_node))

    return (
        ConstraintParameterPhrase.Create(
            CreateRegions(node, type_node, name_leaf, default_node),
            type_info,
            name_info,
            default_info,
        ),
        default_info is not None,
    )
