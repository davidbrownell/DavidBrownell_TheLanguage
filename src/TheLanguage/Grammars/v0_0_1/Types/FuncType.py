# ----------------------------------------------------------------------
# |
# |  FuncType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 14:51:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncType object"""

import itertools
import os

from typing import cast, List, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo
    from ....Lexer.ParserInterfaces.Types.FuncTypeLexerInfo import (
        TypeLexerInfo,
        FuncTypeLexerData,
        FuncTypeLexerInfo,
        FuncTypeLexerRegions,
    )

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class FuncType(GrammarPhrase):
    """\
    A first-class function type.

    '(' <type> '(' (<type> (',' <type>)* ','?)? ')' ')'

    Examples:
        (Int ())
        (Int (Char, Bool))
    """

    # <TODOS> pylint: disable=W0511
    # TODO: Add exception and coroutine decorations

    PHRASE_NAME                               = "Func Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncType, self).__init__(
            GrammarPhrase.Type.Type,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # '(' (outer)
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <type> (return)
                    DynamicPhrasesType.Types,

                    # TODO: This phrase needs some work; make close to other parameters

                    # '(' (inner)
                    "(",

                    PhraseItem(
                        name="Parameters",
                        item=[
                            # <type> (parameter)
                            DynamicPhrasesType.Types,

                            # (',' <type>)*
                            PhraseItem(
                                name="Comma and Type",
                                item=[
                                    ",",
                                    DynamicPhrasesType.Types,
                                ],
                                arity="*",
                            ),

                            # ',' (trailing parameter)
                            PhraseItem(
                                item=",",
                                arity="?",
                            ),
                        ],
                        arity="?",
                    ),

                    # ')' (inner)
                    ")",

                    # ')' (outer)
                    CommonTokens.PopIgnoreWhitespaceControl,
                    ")",
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateSyntax(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ValidateSyntaxResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 8

            # <type>
            return_type_node = ExtractDynamic(cast(Node, nodes[2]))

            # <parameters>
            parameters = []
            parameters_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[4])))

            if parameters_node is not None:
                parameters_nodes = ExtractSequence(parameters_node)
                assert len(parameters_nodes) == 3

                for parameter_node in itertools.chain(
                    [parameters_nodes[0]],
                    [
                        ExtractSequence(parameter_node)[1]
                        for parameter_node in cast(
                            List[Node],
                            ExtractRepeat(cast(Node, parameters_nodes[1])),
                        )
                    ],
                ):
                    parameter_node = ExtractDynamic(cast(Node, parameter_node))
                    parameters.append(GetLexerInfo(parameter_node))

            # pylint: disable=too-many-function-args
            SetLexerInfo(
                node,
                FuncTypeLexerInfo(
                    FuncTypeLexerData(
                        cast(TypeLexerInfo, GetLexerInfo(return_type_node)),
                        parameters or None,
                    ),
                    CreateLexerRegions(
                        FuncTypeLexerRegions,  # type: ignore
                        node,
                        return_type_node,
                        parameters_node,
                    ),
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ValidateSyntaxResult(CreateLexerInfo)
