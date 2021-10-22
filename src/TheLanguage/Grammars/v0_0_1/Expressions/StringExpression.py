# ----------------------------------------------------------------------
# |
# |  StringExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-22 10:28:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StringExpression object"""

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

    from ....Parser.Literals.StringLiteralParserInfo import StringLiteralParserInfo


# ----------------------------------------------------------------------
class StringExpression(GrammarPhrase):
    """\
    A single-line string.

    "<content>"

    Examples:
        "Hello, World!"
    """

    PHRASE_NAME                             = "String Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(StringExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # Note that this must be a sequence so that ExtractParserInfo will be called.
                    RegexToken(
                        "<string>",
                        re.compile(r'\"(?P<value>(?:\\\"|[^\"])*)\"'),
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

        # <string>
        string_node = cast(AST.Leaf, nodes[0])
        string_info = cast(str, ExtractToken(string_node))

        string_info = string_info.replace(r'\"', '"')

        return StringLiteralParserInfo(
            CreateParserRegions(node),  # type: ignore
            string_info,
        )
