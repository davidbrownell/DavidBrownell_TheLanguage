# ----------------------------------------------------------------------
# |
# |  StandardType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 11:31:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardType object"""

import os

from typing import cast, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ..Common import TypeModifier

    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import SetLexerInfo
    from ....Lexer.ParserInterfaces.Types.StandardTypeLexerInfo import (
        StandardTypeLexerData,
        StandardTypeLexerInfo,
        StandardTypeLexerRegions,
    )

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        ExtractOptional,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class StandardType(GrammarPhrase):
    """\
    Type declaration.

    <type_name> <modifier>?

    Examples:
        Int
        Int var
    """

    PHRASE_NAME                             = "Standard Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(StandardType, self).__init__(
            GrammarPhrase.Type.Type,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <type_name>
                    CommonTokens.TypeName,

                    # <modifier>?
                    PhraseItem(
                        name="Modifier",
                        item=TypeModifier.CreatePhraseItem(),
                        arity="?",
                    ),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractLexerInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 2

        # <type_name>
        type_leaf = cast(Leaf, nodes[0])
        type_name = cast(str, ExtractToken(type_leaf))

        # <modifier>?
        modifier_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[1])))

        if modifier_node is not None:
            modifier = TypeModifier.Extract(modifier_node)
        else:
            modifier = None

        # pylint: disable=too-many-function-args
        SetLexerInfo(
            node,
            StandardTypeLexerInfo(
                StandardTypeLexerData(
                    type_name,
                    modifier,  # type: ignore
                ),
                CreateLexerRegions(
                    StandardTypeLexerRegions,  # type: ignore
                    node,
                    type_leaf,
                    modifier_node,
                ),
            ),
        )
