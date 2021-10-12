# ----------------------------------------------------------------------
# |
# |  VariableExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 13:14:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableExpression object"""

import os

from typing import Callable, cast, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    # TODO from ..Names.TupleName import TupleName

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo
    from ....Parser.Expressions.VariableExpressionParserInfo import (
        NameParserInfo,
        VariableExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class VariableExpression(GrammarPhrase):
    """\
    A variable name.

    <name>

    Example:
        foo
        bar
        (a, b)
    """

    PHRASE_NAME                             = "Variable Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                # <name>
                PhraseItem.Create(
                    name=self.PHRASE_NAME,
                    item=DynamicPhrasesType.Names,

                    # Ambiguity is introduced between this statement and TupleName without this
                    # explicit exclusion. For example, is "(a, b, c)" a tuple name or tuple
                    # expression? In this context, "tuple expression" is correct, so remove tuple
                    # name as a viable candidate.
                    # TODO: exclude=[TupleName.PHRASE_NAME],
                ),
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
        # ----------------------------------------------------------------------
        def Impl():
            # <name>
            name_node = ExtractDynamic(node)
            name_info = cast(NameParserInfo, GetParserInfo(name_node))

            return VariableExpressionParserInfo(
                CreateParserRegions(node, name_node),  # type: ignore
                name_info,
            )

        # ----------------------------------------------------------------------

        return Impl
