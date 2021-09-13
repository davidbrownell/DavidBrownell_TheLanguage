# ----------------------------------------------------------------------
# |
# |  FuncInvocationBase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 19:45:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationBase object"""

import os

from typing import cast, Optional, Type

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import ArgumentsPhraseItem
    from .. import Tokens as CommonTokens

    from ....GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from .....Lexer.LexerInfo import (
        LexerData,
        LexerInfo,
        LexerRegions,
        SetLexerInfo,
    )

    from .....Parser.Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
    )


# ----------------------------------------------------------------------
class FuncInvocationBase(GrammarPhrase):
    """\
    Base class for function invocations.

    <generic_name> <<Arguments>> <function_name> <function_args>

    Examples:
        Func1()
        Func2(a,)
        Func3(a, b, c)
        Func4(a, b, c=foo)
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrase_name: str,
        grammar_phrase_type: GrammarPhrase.Type,
    ):
        phrase_items = [
            # <generic_name>
            CommonTokens.GenericName,

            ArgumentsPhraseItem.Create(),
        ]

        if grammar_phrase_type == GrammarPhrase.Type.Statement:
            phrase_items.append(CommonTokens.Newline)

        super(FuncInvocationBase, self).__init__(
            grammar_phrase_type,
            CreatePhrase(
                name=phrase_name,
                item=phrase_items,
            ),
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _ExtractLexerInfoImpl(
        lexer_data_type: Type[LexerData],
        lexer_info_type: Type[LexerInfo],
        lexer_regions_type: Type[LexerRegions],
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) in [2, 3], nodes

            # Func Name
            leaf = cast(Leaf, nodes[0])
            name = cast(str, ExtractToken(leaf))

            # Arguments
            arguments_node, arguments_info = ArgumentsPhraseItem.Extract(cast(Node, nodes[1]))

            # pylint: disable=too-many-function-args
            SetLexerInfo(
                node,
                lexer_info_type(
                    lexer_data_type(
                        name,  # type: ignore
                        arguments_info,
                    ),
                    CreateLexerRegions(
                        lexer_regions_type,  # type: ignore
                        node,
                        leaf,
                        arguments_node,
                    ),
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
