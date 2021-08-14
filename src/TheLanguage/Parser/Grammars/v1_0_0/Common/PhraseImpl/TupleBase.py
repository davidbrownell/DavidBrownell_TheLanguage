# ----------------------------------------------------------------------
# |
# |  TupleBase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 16:34:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleBase object"""

import os

from typing import cast, Generator, List, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import Tokens as CommonTokens
    from ....GrammarPhrase import GrammarPhrase, Leaf, Node
    from .....Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class TupleBase(GrammarPhrase):
    """Base class for Tuple expressions, names, statements, and types"""

    MULTIPLE_NODE_NAME                      = "Multiple"
    SINGLE_NODE_NAME                        = "Single"

    # ----------------------------------------------------------------------
    def __init__(
        self,
        grammar_phrase_type: GrammarPhrase.Type,
    ):
        if grammar_phrase_type == GrammarPhrase.Type.Expression:
            name_suffix = "Expression"
            tuple_element_item = DynamicPhrasesType.Expressions

        elif grammar_phrase_type == GrammarPhrase.Type.Name:
            name_suffix = "Name"
            tuple_element_item = DynamicPhrasesType.Names

        elif grammar_phrase_type == GrammarPhrase.Type.Type:
            name_suffix = "Type"
            tuple_element_item = DynamicPhrasesType.Types

        else:
            assert False, grammar_phrase_type  # pragma: no cover


        super(TupleBase, self).__init__(
            grammar_phrase_type,
            CreatePhrase(
                name="Tuple {}".format(name_suffix),
                item=(
                    # Multiple Elements
                    #   '(' <tuple_element> (',' <tuple_element>)+ ','? ')'
                    PhraseItem(
                        name=self.MULTIPLE_NODE_NAME,
                        item=[
                            # '('
                            "(",
                            CommonTokens.PushIgnoreWhitespaceControl,

                            # <tuple_element> (',' <tuple_element>)+ ','?
                            tuple_element_item,

                            PhraseItem(
                                name="Comma and Element",
                                item=[
                                    ",",
                                    tuple_element_item,
                                ],
                                arity="+",
                            ),

                            PhraseItem(
                                name="Trailing Comma",
                                item=",",
                                arity="?",
                            ),

                            # ')'
                            CommonTokens.PopIgnoreWhitespaceControl,
                            ")",
                        ],
                    ),

                    # Single Element
                    #   '(' <tuple_element> ',' ')'
                    PhraseItem(
                        name=self.SINGLE_NODE_NAME,
                        item=[
                            # '('
                            "(",
                            CommonTokens.PushIgnoreWhitespaceControl,

                            # <tuple_element> ','
                            tuple_element_item,
                            ",",

                            # ')'
                            CommonTokens.PopIgnoreWhitespaceControl,
                            ")",
                        ],
                    ),
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    def EnumNodeValues(
        cls,
        node: Node,
    ) -> Generator[
        Union[Leaf, Node],
        None,
        None,
    ]:
        node = cast(Node, ExtractOr(node))
        assert node.Type

        values = ExtractSequence(node)

        if node.Type.Name == cls.MULTIPLE_NODE_NAME:
            assert len(values) == 7
            yield cast(Node, values[2])

            for value in cast(List[Node], ExtractRepeat(cast(Node, values[3]))):
                value = ExtractSequence(value)
                yield cast(Node, value[0])

        elif node.Type.Name == cls.SINGLE_NODE_NAME:
            assert len(values) == 6
            yield cast(Node, values[2])

        else:
            assert False, node.Type  # pragma: no cover
