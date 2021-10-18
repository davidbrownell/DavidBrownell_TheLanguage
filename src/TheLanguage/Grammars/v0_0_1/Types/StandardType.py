# ----------------------------------------------------------------------
# |
# |  StandardType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 12:17:36
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

from typing import Callable, cast, Optional, Tuple, Union

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

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractOptional,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions
    from ....Parser.Types.StandardTypeParserInfo import StandardTypeParserInfo


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
            DynamicPhrasesType.Types,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <type_name>
                    CommonTokens.TypeName,

                    # <modifier>?
                    OptionalPhraseItem.Create(
                        name="Modifier",
                        item=TypeModifier.CreatePhraseItem(),
                    ),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 2

        # <type_name>
        type_leaf = cast(AST.Leaf, nodes[0])
        type_info = cast(str, ExtractToken(type_leaf))

        # <modifier>?
        modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))

        if modifier_node is None:
            modifier_info = None
        else:
            modifier_info = TypeModifier.Extract(modifier_node)

        return StandardTypeParserInfo(
            CreateParserRegions(node, type_leaf, modifier_node),  # type: ignore
            type_info,
            modifier_info,
        )
