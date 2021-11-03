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

    from ....Lexer.Phrases.DSL import (
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions

    from ....Parser.Names.VariableNameParserInfo import VariableNameParserInfo


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    variable_phrase_item = CommonTokens.GenericLowerName

    return PhraseItem.Create(
        name="Captured Variables",
        item=[
            # '|'
            "|",
            CommonTokens.PushIgnoreWhitespaceControl,

            # <variable_phrase_item>
            variable_phrase_item,

            # (',' <variable_phrase_item>)*
            ZeroOrMorePhraseItem.Create(
                name="Comma and Variable",
                item=[
                    ",",
                    variable_phrase_item,
                ],
            ),

            # ','
            OptionalPhraseItem.Create(
                name="Trailing Comma",
                item=",",
            ),

            # '|'
            CommonTokens.PopIgnoreWhitespaceControl,
            "|",
        ],
    )


# ----------------------------------------------------------------------
def ExtractParserInfo(
    node: Node,
) -> List[VariableNameParserInfo]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 7

    results: List[VariableNameParserInfo] = []

    for variable_node in itertools.chain(
        [nodes[2]],
        (
            ExtractSequence(delimited_node)[1]
            for delimited_node in cast(List[Node], ExtractRepeat(cast(Node, nodes[3])))
        ),
    ):
        # <variable_phrase_name>
        variable_leaf = cast(Leaf, variable_node)
        variable_info = cast(str, ExtractToken(variable_leaf))

        if not CommonTokens.VariableNameRegex.match(variable_info):
            raise CommonTokens.InvalidTokenError.FromNode(variable_leaf, variable_info, "variable")

        results.append(
            VariableNameParserInfo(
                CreateParserRegions(variable_leaf),  # type: ignore
                variable_info,
            ),
        )

    assert results
    return results
