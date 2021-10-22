# ----------------------------------------------------------------------
# |
# |  NumberExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-22 13:38:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NumberExpression object"""

import os
import re
import textwrap

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

    from ....Parser.Literals.NumberLiteralParserInfo import NumberLiteralParserInfo


# ----------------------------------------------------------------------
class NumberExpression(GrammarPhrase):
    """\
    An integer or decimal.

    Examples:
        123
        3.14
        -13
        -1.2324
    """

    PHRASE_NAME                             = "Number Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(NumberExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # Note that this must be a sequence so that ExtractParserInfo will be called.
                    RegexToken(
                        "<number>",
                        re.compile(
                            textwrap.dedent(
                                r"""(?P<value>(?#
                                    +/- [opt]           )(?:[+-])?(?#
                                    Integer             )\d+(?#
                                    Decimal begin [opt] )(?:(?#
                                        Dot             )\.(?#
                                        Mantissa        )\d+(?#
                                    Decimal end [opt]   ))?(?#
                                ))""",
                            ),
                        ),
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

        # <number>
        number_leaf = cast(AST.Leaf, nodes[0])
        number_info = cast(str, ExtractToken(number_leaf))

        number_info = float(number_info)

        return NumberLiteralParserInfo(
            CreateParserRegions(node),  # type: ignore
            number_info,
        )
