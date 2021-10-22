# ----------------------------------------------------------------------
# |
# |  NoneExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-22 11:01:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NoneExpression object"""

import os
import re

from typing import Callable, Tuple, Union

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
    )

    from ....Parser.Parser import CreateParserRegions

    from ....Parser.Literals.NoneLiteralParserInfo import NoneLiteralParserInfo


# ----------------------------------------------------------------------
class NoneExpression(GrammarPhrase):
    """\
    None.

    Examples:
        None
    """

    PHRASE_NAME                             = "None Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(NoneExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # Note that this must be a sequence so that ExtractParserInfo will be called.
                    RegexToken(
                        "'None'",
                        re.compile(r"None"),
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

        return NoneLiteralParserInfo(
            CreateParserRegions(node),  # type: ignore
        )
