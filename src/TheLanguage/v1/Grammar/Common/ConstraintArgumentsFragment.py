# ----------------------------------------------------------------------
# |
# |  ConstraintArgumentsFragment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 10:32:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when processing constraint arguments"""

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
        ExtractToken,
        PhraseItem,
        OptionalPhraseItem,
    )

    from ...Parser.Common.ConstraintArgumentsPhrase import (
        ConstraintArgumentPhrase,
        ConstraintArgumentsPhrase,
        ConstraintExpressionPhrase,
    )

    from ...Parser.Error import Error
    from ...Parser.Parser import CreateRegions, GetPhrase, Phrase


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    argument_element = PhraseItem(
        name="Argument",
        item=[
            # (<parameter_name> '=')?
            OptionalPhraseItem(
                name="Keyword",
                item=[
                    CommonTokens.ConstraintParameterName,
                    "=",
                ],
            ),

            # <constraint_expression>
            DynamicPhrasesType.ConstraintExpressions,
        ],
    )

    return ArgumentsFragmentImpl.Create(
        "Constraint Arguments",
        "{", "}",
        argument_element,
        allow_empty=True,
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> Union[
    List[Error],
    bool,
    ConstraintArgumentsPhrase,
]:
    return ArgumentsFragmentImpl.Extract(
        ConstraintArgumentsPhrase,
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

    # <constraint_expression>
    expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[1])))
    expression_info = cast(ConstraintExpressionPhrase, GetPhrase(expression_node))

    return (
        ConstraintArgumentPhrase.Create(
            CreateRegions(node, expression_node, keyword_node),
            expression_info,
            keyword_info,
        ),
        keyword_info is not None,
    )