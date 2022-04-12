# ----------------------------------------------------------------------
# |
# |  ConcreteTypeFragment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 10:46:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that Creates and Lexes concrete types"""

import itertools
import os

from typing import cast, List

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens as CommonTokens
    from ..GrammarPhrase import AST

    from ...Lexer.Phrases.DSL import (
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ...Parser.Common.ConcreteTypePhrase import ConcreteTypePhrase, ConcreteTypeItemPhrase
    from ...Parser.Parser import CreateRegions


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    concrete_type_element = PhraseItem(
        name="Concrete Type Element",
        item=[
            # <type_name>
            CommonTokens.RuntimeTypeName,

            # TODO: <template_arguments>?
            # TODO: <constraint_arguments>?
        ],
    )

    return PhraseItem(
        name="Concrete Type",
        item=[
            # <concrete_type_element>
            concrete_type_element,

            # ('.' <concrete_type_element>)*
            ZeroOrMorePhraseItem(
                name="Dot and Element",
                item=[
                    ".",
                    concrete_type_element,
                ],
            ),
        ],
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> ConcreteTypePhrase:
    nodes = ExtractSequence(node)
    assert len(nodes) == 2

    concrete_type_items: List[ConcreteTypeItemPhrase] = []

    for node_item in itertools.chain(
        [cast(AST.Node, nodes[0])],
        [
            ExtractSequence(delimited_node)[1]
            for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, nodes[1])))
        ],
    ):
        this_nodes = ExtractSequence(cast(AST.Node, node_item))
        assert len(this_nodes) == 1

        # <type_name>
        type_name_node = cast(AST.Leaf, this_nodes[0])
        type_name_info = ExtractToken(type_name_node)

        concrete_type_items.append(
            ConcreteTypeItemPhrase.Create(
                CreateRegions(node_item, type_name_node),
                type_name_info,
            ),
        )

    return ConcreteTypePhrase.Create(
        CreateRegions(node, node),
        concrete_type_items,
    )
