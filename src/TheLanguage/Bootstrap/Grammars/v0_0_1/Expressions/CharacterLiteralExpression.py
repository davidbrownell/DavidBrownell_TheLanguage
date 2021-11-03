# ----------------------------------------------------------------------
# |
# |  CharacterLiteralExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-28 14:45:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CharacterLiteralExpression object"""

import os
import re

from typing import Callable, cast, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Tokens import RegexToken

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        ExtractToken,
    )

    from ....Parser.Parser import CreateParserRegions

    from ....Parser.Literals.CharacterLiteralParserInfo import CharacterLiteralParserInfo


# ----------------------------------------------------------------------
class CharacterLiteralExpression(GrammarPhrase):
    """\
    A single character.

    '<char>'

    Examples:
        'a'
        'A'
    """

    # TODO: Allow for unicode chars

    PHRASE_NAME                             = "Character Literal Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(CharacterLiteralExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # Note that this must be a sequence so that ExtractParserInfo will be called.
                    RegexToken(
                        "<char>",
                        re.compile(r"'(?P<value>\\?(?:\\'|.))'"),
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
        assert len(nodes) == 1

        # <char>
        char_node = cast(AST.Leaf, nodes[0])
        char_info = cast(str, ExtractToken(char_node))

        char_info = char_info.replace(r"\'", "'")

        return CharacterLiteralParserInfo(
            CreateParserRegions(node),  # type: ignore
            char_info,
        )
