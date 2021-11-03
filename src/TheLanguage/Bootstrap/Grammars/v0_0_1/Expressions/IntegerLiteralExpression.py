# ----------------------------------------------------------------------
# |
# |  IntegerLiteralExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-25 09:41:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IntegerLiteralExpression object"""

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

    from ....Parser.Literals.IntLiteralParserInfo import IntLiteralParserInfo


# ----------------------------------------------------------------------
class IntegerLiteralExpression(GrammarPhrase):
    """\
    An integer value.

    Examples:
        1
        123
        -1
        +45678
    """

    PHRASE_NAME                             = "Integer Literal Expression"
    INTEGER_REGEX                           = r"[+-]?[0-9]+" # TODO: Enhance with optional delimiters

    # ----------------------------------------------------------------------
    def __init__(self):
        super(IntegerLiteralExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # Note that this must be a sequence so that ExtractParserInfo will be called.
                    RegexToken(
                        "<integer>",
                        re.compile(r"(?P<value>{})".format(self.INTEGER_REGEX)),
                    ),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def FromString(
        value: str,
    ) -> int:
        return int(value) # TODO: Enhance this when INTEGER_REGEX is updated

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 1

        # <integer>
        integer_leaf = cast(AST.Leaf, nodes[0])
        integer_value = cast(str, ExtractToken(integer_leaf))
        integer_info = cls.FromString(integer_value)

        return IntLiteralParserInfo(
            CreateParserRegions(node),  # type: ignore
            integer_info,
        )
